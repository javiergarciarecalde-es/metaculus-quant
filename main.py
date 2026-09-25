"""metaculus-quant: bot para los torneos de bots de Metaculus (FutureEval + MiniBench).

Basado en la plantilla oficial (github.com/Metaculus/metac-bot-template, main.py) y en la
librería forecasting-tools. Cambios respecto a la plantilla:
- Varias pasadas repartidas entre VARIOS modelos (conjunto) en vez de uno solo.
- Agregación propia en binarias y de opciones: mediana -> extremizar suave -> límites
  (nunca 0 %/100 %); suelo mínimo por opción. Numéricas: mediana de CDF de la librería.
- Lectura de la respuesta con expresiones regulares primero (gratis); el «parser» por
  modelo solo si falla.
- Interruptores de seguridad: sin token termina limpio; sin ENVIO_REAL=true no envía nada;
  la ejecución programada (cada 20 min) no gasta nada con el envío apagado.
- Registro de cada pronóstico en registro/*.jsonl.

Modos:
  python main.py                      -> torneo de temporada + MiniBench
  python main.py --mode test_questions -> zona de pruebas de Metaculus (bot-testing-area)
"""
from __future__ import annotations

import argparse
import asyncio
import itertools
import logging
import sys
import warnings
from datetime import datetime

import dotenv

warnings.filterwarnings("ignore", message=r".*does not support cost tracking.*")

from forecasting_tools import (  # noqa: E402
    AskNewsSearcher,
    BinaryQuestion,
    DateQuestion,
    DatePercentile,
    ForecastBot,
    GeneralLlm,
    MetaculusClient,
    MetaculusQuestion,
    MultipleChoiceQuestion,
    NumericDistribution,
    NumericQuestion,
    Percentile,
    PredictedOption,
    PredictedOptionList,
    BinaryPrediction,
    ReasonedPrediction,
    clean_indents,
    structure_output,
)

from bot import agregacion as ag  # noqa: E402
from bot import config as cfg  # noqa: E402
from bot import investigacion as inv  # noqa: E402
from bot import registro  # noqa: E402

dotenv.load_dotenv()
logger = logging.getLogger(__name__)
logging.getLogger("LiteLLM").setLevel(logging.WARNING)


class QuantBot(ForecastBot):
    """Bot de metaculus-quant. Misma estructura que SummerTemplateBot2026."""

    _max_concurrent_questions = 1
    _concurrency_limiter = asyncio.Semaphore(_max_concurrent_questions)
    _structure_output_validation_samples = 2

    def __init__(self, *args, params: dict, modelos_pronostico: list, respaldos: list | None = None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.params = params
        p = params["pronostico"]
        self.factor_extremizar = float(p["factor_extremizar"])
        self.prob_min = float(p["prob_min"])
        self.prob_max = float(p["prob_max"])
        self.minimo_por_opcion = float(p["minimo_por_opcion"])
        self._modelos = list(modelos_pronostico)
        respaldos = respaldos or [None] * len(self._modelos)
        self._rueda = itertools.cycle(list(zip(self._modelos, respaldos)))
        self._miembros: dict[str, list[dict]] = {}  # pronósticos individuales por pregunta

    # Rueda de puestos: cada pasada usa el siguiente puesto (modelo + respaldo).
    async def _pensar(self, prompt: str) -> tuple[str, str]:
        llm, respaldo = next(self._rueda)
        try:
            texto = await llm.invoke(prompt)
            if texto and texto.strip():
                return texto, llm.model
            motivo = "respuesta vacía"
        except Exception as e:
            if respaldo is None:
                raise
            motivo = repr(e)
        if respaldo is None:
            raise ValueError(f"{llm.model}: {motivo}")
        logger.warning(f"{llm.model} falló ({motivo}); responde el respaldo {respaldo.model}")
        texto = await respaldo.invoke(prompt)
        if not (texto and texto.strip()):
            raise ValueError(f"{llm.model} y su respaldo {respaldo.model} sin respuesta")
        return texto, respaldo.model

    @classmethod
    def _llm_config_defaults(cls):
        base = super()._llm_config_defaults()
        return {**base, "director": base["default"], "buscador": base["researcher"]}

    def _anotar_miembro(self, question: MetaculusQuestion, modelo: str, valor) -> None:
        self._miembros.setdefault(question.page_url, []).append({"modelo": modelo, "valor": valor})

    ##################################### INVESTIGACIÓN #####################################

    async def run_research(self, question: MetaculusQuestion) -> str:
        async with self._concurrency_limiter:
            researcher = self.get_llm("researcher")
            if not researcher or researcher in ("None", "no_research"):
                return ""
            prompt = clean_indents(
                f"""
                You are an assistant to a superforecaster.
                The superforecaster will give you a question they intend to forecast on.
                Generate a concise but detailed rundown of the most relevant and most RECENT news
                (with dates), relevant base rates / historical frequencies, the current status quo,
                any scheduled events before the resolution date, and whether the question would
                resolve Yes or No based on current information. You do not produce forecasts yourself.

                Question:
                {question.question_text}

                This question's outcome will be determined by the specific criteria below:
                {question.resolution_criteria}

                {question.fine_print}
                """
            )
            try:
                if cfg.hay("ASKNEWS_CLIENT_ID") and cfg.hay("ASKNEWS_SECRET"):
                    # AskNews (noticias): lo usa como fuente principal nostreambot
                    research = await AskNewsSearcher().call_preconfigured_version(
                        "asknews/news-summaries", prompt
                    )
                elif isinstance(researcher, GeneralLlm):
                    research = await researcher.invoke(prompt)
                else:
                    research = await self.get_llm("researcher", "llm").invoke(prompt)
            except Exception as e:  # sin investigación se sigue pronosticando
                logger.warning(f"Investigación fallida en {question.page_url}: {e}")
                research = ""
            ci = self.params.get("investigacion", {})
            if ci.get("modo") == "ampliada":
                research = await inv.ampliar(
                    research, question.question_text, question.resolution_criteria or "",
                    director=self.get_llm("director", "llm"),
                    buscador=self.get_llm("buscador", "llm"),
                    n=int(ci.get("max_datos_clave", 2)),
                    tope_segundos=float(ci.get("tope_total_segundos", 240)),
                )
            logger.info(f"Investigación para {question.page_url}:\n{research[:2000]}")
            return research

    ##################################### BINARIAS #####################################

    async def _run_forecast_on_binary(
        self, question: BinaryQuestion, research: str
    ) -> ReasonedPrediction[float]:
        prompt = clean_indents(
            f"""
            You are a professional forecaster with an excellent calibration track record.

            Question:
            {question.question_text}

            Question background:
            {question.background_info}

            This question's outcome will be determined by the specific criteria below. These criteria have not yet been satisfied:
            {question.resolution_criteria}

            {question.fine_print}

            Your research assistant says:
            {research}

            Today is {datetime.now().strftime("%Y-%m-%d")}.

            Before answering you write:
            (a) The time left until the outcome to the question is known.
            (b) The status quo outcome if nothing changed.
            (c) A reference class and its base rate for events like this.
            (d) A brief description of a scenario that results in a No outcome.
            (e) A brief description of a scenario that results in a Yes outcome.
            (f) Read the resolution criteria literally: note any technicality that could decide it.

            Good forecasters put extra weight on the status quo since the world changes slowly,
            and they do not hedge towards 50% when the evidence is clear.

            The last thing you write is your final answer as: "Probability: ZZ%", 0-100
            """
        )
        texto, modelo = await self._pensar(prompt)
        p = ag.leer_probabilidad(texto)
        if p is None:
            pred: BinaryPrediction = await structure_output(
                texto,
                BinaryPrediction,
                model=self.get_llm("parser", "llm"),
                num_validation_samples=self._structure_output_validation_samples,
            )
            p = pred.prediction_in_decimal
        p = max(0.001, min(0.999, p))
        self._anotar_miembro(question, modelo, round(p, 4))
        logger.info(f"{question.page_url} [{modelo}] -> {p:.3f}")
        return ReasonedPrediction(prediction_value=p, reasoning=f"[{modelo}]\n{texto}")

    ##################################### OPCIONES #####################################

    async def _run_forecast_on_multiple_choice(
        self, question: MultipleChoiceQuestion, research: str
    ) -> ReasonedPrediction[PredictedOptionList]:
        prompt = clean_indents(
            f"""
            You are a professional forecaster with an excellent calibration track record.

            Question:
            {question.question_text}

            The options are: {question.options}

            Background:
            {question.background_info}

            {question.resolution_criteria}

            {question.fine_print}

            Your research assistant says:
            {research}

            Today is {datetime.now().strftime("%Y-%m-%d")}.

            Before answering you write:
            (a) The time left until the outcome to the question is known.
            (b) The status quo outcome if nothing changed.
            (c) Base rates or historical frequencies relevant to the options.
            (d) A description of a scenario that results in an unexpected outcome.

            Good forecasters put extra weight on the status quo, and leave some moderate
            probability on most options to account for unexpected outcomes.

            The last thing you write is your final probabilities (in %) for the N options in this order {question.options} as:
            Option_A: Probability_A
            Option_B: Probability_B
            ...
            Option_N: Probability_N
            """
        )
        texto, modelo = await self._pensar(prompt)
        leidas = ag.leer_opciones(texto, question.options)
        if leidas is None:
            lista: PredictedOptionList = await structure_output(
                text_to_structure=texto,
                output_type=PredictedOptionList,
                model=self.get_llm("parser", "llm"),
                num_validation_samples=self._structure_output_validation_samples,
                additional_instructions=(
                    f"Make sure that all option names are one of the following: {question.options}. "
                    "Remove any 'Option' prefix not part of the names. Keep options with 0%."
                ),
            )
            leidas = {o.option_name: o.probability for o in lista.predicted_options}
        probs = ag.normalizar_opciones(
            {op: leidas.get(op, 0.0) for op in question.options}, minimo=0.0
        )
        self._anotar_miembro(question, modelo, {k: round(v, 4) for k, v in probs.items()})
        return ReasonedPrediction(
            prediction_value=_a_lista(probs), reasoning=f"[{modelo}]\n{texto}"
        )

    ##################################### NUMÉRICAS #####################################

    async def _run_forecast_on_numeric(
        self, question: NumericQuestion, research: str
    ) -> ReasonedPrediction[NumericDistribution]:
        sup, inf = self._mensajes_limites(question)
        prompt = clean_indents(
            f"""
            You are a professional forecaster with an excellent calibration track record.

            Question:
            {question.question_text}

            Background:
            {question.background_info}

            {question.resolution_criteria}

            {question.fine_print}

            Units for answer: {question.unit_of_measure if question.unit_of_measure else "Not stated (please infer this)"}

            Your research assistant says:
            {research}

            Today is {datetime.now().strftime("%Y-%m-%d")}.

            {inf}
            {sup}

            Formatting Instructions:
            - Give your answer in the units requested. Never use scientific notation.
            - Percentile values must strictly increase: percentile 10 < percentile 20 < ... < percentile 90.

            Before answering you write:
            (a) The time left until the outcome to the question is known.
            (b) The outcome if nothing changed.
            (c) The outcome if the current trend continued.
            (d) The expectations of experts and markets.
            (e) An unexpected scenario that results in a low outcome.
            (f) An unexpected scenario that results in a high outcome.

            Good forecasters are humble and set wide 90/10 intervals to account for unknown unknowns.

            The last thing you write is your final answer as:
            "
            Percentile 10: XX (lowest number value)
            Percentile 20: XX
            Percentile 40: XX
            Percentile 60: XX
            Percentile 80: XX
            Percentile 90: XX (highest number value)
            "
            """
        )
        texto, modelo = await self._pensar(prompt)
        leidos = ag.leer_percentiles(texto)
        if leidos is not None:
            leidos = ag.monotono(leidos)
            percentiles = [Percentile(percentile=k, value=v) for k, v in leidos.items()]
        else:
            percentiles = await structure_output(
                texto,
                list[Percentile],
                model=self.get_llm("parser", "llm"),
                additional_instructions=(
                    f"Parse percentile values for the question '{question.question_text}' "
                    f"in units '{question.unit_of_measure}'. No scientific notation."
                ),
                num_validation_samples=self._structure_output_validation_samples,
            )
        pred = NumericDistribution.from_question(percentiles, question)
        self._anotar_miembro(question, modelo, {p.percentile: p.value for p in percentiles})
        return ReasonedPrediction(prediction_value=pred, reasoning=f"[{modelo}]\n{texto}")

    ##################################### FECHAS #####################################
    # FutureEval usa binarias, numéricas y de opciones; las de fecha se mantienen
    # por compatibilidad con la plantilla (misma lógica que ella).

    async def _run_forecast_on_date(
        self, question: DateQuestion, research: str
    ) -> ReasonedPrediction[NumericDistribution]:
        sup, inf = self._mensajes_limites(question)
        prompt = clean_indents(
            f"""
            You are a professional forecaster.

            Question:
            {question.question_text}

            Background:
            {question.background_info}

            {question.resolution_criteria}

            {question.fine_print}

            Your research assistant says:
            {research}

            Today is {datetime.now().strftime("%Y-%m-%d")}.

            {inf}
            {sup}

            Dates must be YYYY-MM-DD and in chronological order. Set wide intervals.
            The last thing you write is your final answer as:
            Percentile 10: YYYY-MM-DD
            Percentile 20: YYYY-MM-DD
            Percentile 40: YYYY-MM-DD
            Percentile 60: YYYY-MM-DD
            Percentile 80: YYYY-MM-DD
            Percentile 90: YYYY-MM-DD
            """
        )
        texto, modelo = await self._pensar(prompt)
        fechas: list[DatePercentile] = await structure_output(
            texto,
            list[DatePercentile],
            model=self.get_llm("parser", "llm"),
            num_validation_samples=self._structure_output_validation_samples,
        )
        percentiles = [
            Percentile(percentile=f.percentile, value=f.value.timestamp()) for f in fechas
        ]
        pred = NumericDistribution.from_question(percentiles, question)
        return ReasonedPrediction(prediction_value=pred, reasoning=f"[{modelo}]\n{texto}")

    def _mensajes_limites(self, question: NumericQuestion | DateQuestion) -> tuple[str, str]:
        if isinstance(question, DateQuestion):
            hi = question.upper_bound.date().isoformat()
            lo = question.lower_bound.date().isoformat()
            unidad = ""
        else:
            hi = question.nominal_upper_bound if question.nominal_upper_bound is not None else question.upper_bound
            lo = question.nominal_lower_bound if question.nominal_lower_bound is not None else question.lower_bound
            unidad = question.unit_of_measure or ""
        sup = (
            f"The question creator thinks the number is likely not higher than {hi} {unidad}."
            if question.open_upper_bound
            else f"The outcome can not be higher than {hi} {unidad}."
        )
        inf = (
            f"The question creator thinks the number is likely not lower than {lo} {unidad}."
            if question.open_lower_bound
            else f"The outcome can not be lower than {lo} {unidad}."
        )
        return sup, inf

    ##################################### AGREGACIÓN #####################################

    async def _aggregate_predictions(self, predictions, question: MetaculusQuestion):
        if not predictions:
            raise ValueError("No hay pronósticos que agregar")
        if isinstance(question, BinaryQuestion):
            return ag.agregar_binaria(
                predictions, self.factor_extremizar, self.prob_min, self.prob_max
            )
        if isinstance(question, MultipleChoiceQuestion):
            listas = [
                {o.option_name: o.probability for o in p.predicted_options}
                for p in predictions
            ]
            probs = ag.agregar_opciones(listas, question.options, self.minimo_por_opcion)
            return _a_lista(probs)
        # numéricas y fechas: mediana de las CDF (función de la librería)
        return await super()._aggregate_predictions(predictions, question)


def _a_lista(probs: dict[str, float]) -> PredictedOptionList:
    opciones = [PredictedOption(option_name=k, probability=v) for k, v in probs.items()]
    # ajuste final para que sume exactamente 1 (validación de la librería)
    resto = 1.0 - sum(o.probability for o in opciones)
    opciones[-1].probability = max(0.0, opciones[-1].probability + resto)
    return PredictedOptionList(predicted_options=opciones)


##################################### EJECUCIÓN #####################################


def _crear_llm(nombre: str, esfuerzo: str | None, temp, tmax) -> GeneralLlm:
    extra = {}
    if esfuerzo and nombre.startswith("openrouter/"):
        # campo «reasoning» de la API de OpenRouter (cuánto piensa el modelo)
        extra["extra_body"] = {"reasoning": {"effort": esfuerzo}}
    elif esfuerzo:
        extra["reasoning_effort"] = esfuerzo
    return GeneralLlm(model=nombre, temperature=temp, timeout=tmax, allowed_tries=2, **extra)


def construir_bot(params: dict, publicar: bool, llms: dict | None = None) -> QuantBot:
    m = cfg.bloque_modelos(params)
    temp = params["modelos"]["temperatura"]
    tmax = params["modelos"]["tiempo_max_segundos"]
    if llms is None:
        puestos = cfg.lista_pronosticadores(params)
        pronosticadores = [_crear_llm(x["nombre"], x.get("esfuerzo"), temp, tmax) for x in puestos]
        respaldos = [_crear_llm(x["respaldo"], x.get("esfuerzo"), temp, tmax) if x.get("respaldo")
                     else None for x in puestos]
        llms = {
            "default": pronosticadores[0],
            "summarizer": GeneralLlm(model=m["lector"], temperature=0.3),
            "researcher": _crear_llm(m["investigacion"], m.get("investigacion_esfuerzo"), None, tmax),
            "parser": GeneralLlm(model=m["lector"], temperature=0.0),
            "director": GeneralLlm(model=m["director"], temperature=temp, timeout=tmax),
            "buscador": _crear_llm(m["buscador"], m.get("investigacion_esfuerzo"), None, tmax),
        }
    else:  # pruebas: modelos simulados
        pronosticadores = llms.get("_puestos") or [llms["default"]]
        respaldos = llms.get("_respaldos")
        llms = {k: v for k, v in llms.items() if not k.startswith("_")}
        for extra in ("director", "buscador"):
            llms.setdefault(extra, llms["default"])
    p = params["pronostico"]
    return QuantBot(
        research_reports_per_question=int(p["informes_investigacion"]),
        predictions_per_research_report=int(p["pasadas_por_pregunta"]),
        use_research_summary_to_forecast=False,
        enable_summarize_research=False,  # no se usa el resumen: ahorra una llamada por pregunta
        publish_reports_to_metaculus=publicar,
        folder_to_save_reports_to=None,
        skip_previously_forecasted_questions=True,
        extra_metadata_in_explanation=True,
        llms=llms,
        params=params,
        modelos_pronostico=pronosticadores,
        respaldos=respaldos,
    )


def registrar(informes, torneo, publicado: bool, bot: "QuantBot | None" = None) -> int:
    ok = 0
    for r in informes:
        if isinstance(r, BaseException):
            registro.anotar({"torneo": torneo, "error": registro.resumir(str(r), 300)})
            continue
        ok += 1
        q = r.question
        registro.anotar({
            "torneo": torneo,
            "enviado": publicado,
            "url": q.page_url,
            "tipo": getattr(q, "question_type", type(q).__name__),
            "pregunta": q.question_text,
            "pronostico": r.make_readable_prediction(r.prediction),
            "coste_usd": r.price_estimate,
            "minutos": r.minutes_taken,
            "razonamiento": registro.resumir(r.explanation),
            "modo": bot.params["pronostico"].get("modo") if bot else None,
            "investigacion_modo": bot.params.get("investigacion", {}).get("modo") if bot else None,
            "miembros": bot._miembros.pop(q.page_url, []) if bot else [],
        })
    return ok


def aviso(msg: str) -> None:
    """Aviso visible en GitHub Actions (amarillo, no rojo) y en consola."""
    print(f"::notice::{msg}")


def ejecutar(modo: str, params: dict | None = None, cliente=None, llms=None) -> int:
    """Devuelve el código de salida (0 = limpio)."""
    params = params or cfg.cargar_params()
    if not cfg.hay("METACULUS_TOKEN"):
        aviso("Falta METACULUS_TOKEN: el bot no hace nada (esto es normal hasta que el usuario lo ponga).")
        return 0

    envio = cfg.envio_real_encendido()
    if not envio and cfg.es_ejecucion_programada():
        aviso("ENVIO_REAL apagado: la ejecución programada no pronostica ni gasta créditos.")
        return 0

    bot = construir_bot(params, publicar=envio, llms=llms)
    if cliente is not None:
        bot.metaculus_client = cliente
    cliente = bot.metaculus_client
    t = params["torneos"]
    if envio and modo == "tournament":
        torneos = [t["temporada"], t["minibench"]]
    else:
        # En ensayo NUNCA se tocan preguntas del torneo: las reglas prohíben «previsualizar»
        # pronósticos en preguntas del torneo. Solo la zona de pruebas oficial.
        torneos = [t["prueba"]]
    print(f"Modo {modo}. Envío real: {'SÍ' if envio else 'NO (ensayo)'}. Torneos: {torneos}")

    total = 0
    for torneo in torneos:
        preguntas = cliente.get_all_open_questions_from_tournament(torneo)
        if not envio:
            # Ensayo: no hay nada enviado, así que no sirve «saltar las ya pronosticadas»;
            # se limita el número de preguntas para no gastar créditos.
            bot.skip_previously_forecasted_questions = False
            preguntas = preguntas[: int(params["pronostico"]["max_preguntas_ensayo"])]
        if modo == "test_questions":
            bot.skip_previously_forecasted_questions = False
        informes = asyncio.run(bot.forecast_questions(preguntas, return_exceptions=True))
        total += registrar(informes, torneo, publicado=envio, bot=bot)
        bot.log_report_summary(informes, raise_errors=False)
    print(f"Terminado: {total} pronósticos {'ENVIADOS' if envio else 'de ensayo (no enviados)'}.")
    return 0


def main(argv=None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(description="Bot de metaculus-quant")
    parser.add_argument("--mode", choices=["tournament", "test_questions"], default="tournament")
    args = parser.parse_args(argv)
    return ejecutar(args.mode)


if __name__ == "__main__":
    sys.exit(main())
