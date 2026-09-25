"""El bot se configura exactamente igual que antes de la orden 14 del mando (25/09/2026).

La orden 14 cambió CÓMO se leen los ajustes (sin valores por defecto escondidos en el código),
la versión de Python y el formato del código, pero no debía cambiar QUÉ hace el bot. Esta prueba
lo demuestra: construye el bot con el `config/params.yaml` real y compara su configuración
efectiva con la foto `tests/datos/configuracion_efectiva.json`, sacada con el código de antes
(commit 0f5cbc2, antes de tocar nada).

Qué entra en la foto: modelos de cada puesto con su respaldo, esfuerzo, intentos, temperatura y
tiempo máximo; pasadas e informes por pregunta; límites (2-98 %, 1 % por opción) comprobados
agregando pronósticos extremos; topes de tiempo; investigación con Claude; torneos que se piden en
cada modo; cuántas preguntas se ensayan; y los horarios de los flujos de GitHub.

Si el usuario cambia un ajuste A PROPÓSITO, esta prueba falla: se regenera la foto
(`python -m tests.test_configuracion_igual`) en el mismo commit que la entrada de CHANGELOG.md.
"""

from __future__ import annotations

import asyncio
import json
import os
import tempfile
from pathlib import Path

import pytest
import yaml
from forecasting_tools import BinaryQuestion, MultipleChoiceQuestion

import main
from bot import claude_max
from bot import config as cfg
from tests.conftest import MetaculusFalso, ModeloFalso, preguntas_ejemplo

RAIZ = Path(__file__).resolve().parent.parent
FOTO = RAIZ / "tests" / "datos" / "configuracion_efectiva.json"
CLAVES_LLM = ("model", "temperature", "timeout", "extra_body", "reasoning_effort")


def _llm(llm) -> dict | None:
    if llm is None:
        return None
    kw = {k: llm.litellm_kwargs.get(k) for k in CLAVES_LLM}
    return {"nombre": llm.model, "intentos": llm.allowed_tries, **kw}


def _bot(params: dict) -> dict:
    bot = main.construir_bot(params, publicar=False)
    binaria = BinaryQuestion(question_text="x", id_of_post=1, id_of_question=1, page_url="u")
    opciones = MultipleChoiceQuestion(
        question_text="x", id_of_post=2, id_of_question=2, page_url="v", options=["A", "B", "C"]
    )
    agregar = bot._aggregate_predictions
    reparto = asyncio.run(
        agregar(
            [main._a_lista({"A": 1.0, "B": 0.0, "C": 0.0})] * 3,
            opciones,
        )
    )
    return {
        "puestos": [[_llm(a), _llm(b)] for a, b in bot._puestos],
        "llms": {
            k: _llm(bot.get_llm(k, "llm"))
            for k in ("default", "summarizer", "researcher", "parser", "director", "buscador")
        },
        "informes_por_pregunta": bot.research_reports_per_question,
        "pasadas_por_informe": bot.predictions_per_research_report,
        "resumen_de_investigacion": bot.enable_summarize_research,
        "saltar_ya_pronosticadas": bot.skip_previously_forecasted_questions,
        "factor_extremizar": bot.factor_extremizar,
        "binaria_todos_0": asyncio.run(agregar([0.0, 0.0, 0.0], binaria)),
        "binaria_todos_1": asyncio.run(agregar([1.0, 1.0, 1.0], binaria)),
        "binaria_mediana": asyncio.run(agregar([0.3, 0.6, 0.9], binaria)),
        "opciones_minimo": round(min(o.probability for o in reparto.predicted_options), 6),
        "tope_pasada_s": bot._tope_pasada,
        "tope_busqueda_s": bot._tope_busqueda,
        "dejar_de_empezar_s": bot._limite_ejecucion,
        "busquedas_a_la_vez": bot._max_concurrent_questions,
        "validaciones_lector": bot._structure_output_validation_samples,
        "claude_max_orden": claude_max.orden(bot._claude_max.conf),
        "claude_max_tope_s": float(bot._claude_max.conf["tope_segundos"]),
        "claude_max_agentes": int(bot._claude_max.conf["agentes"]),
        "claude_max_simultaneas": int(bot._claude_max.conf["simultaneas"]),
    }


def _ejecucion(monkeypatch, llms: dict, envio: bool, modo: str, evento: str) -> dict:
    monkeypatch.setenv("METACULUS_TOKEN", "t")
    monkeypatch.setenv("GITHUB_EVENT_NAME", evento)
    if envio:
        monkeypatch.setenv("ENVIO_REAL", "true")
    else:
        monkeypatch.delenv("ENVIO_REAL", raising=False)
    falso = MetaculusFalso(preguntas_ejemplo() * 2)  # 6 preguntas
    registro_antes = _lineas_registro()
    codigo = main.ejecutar(modo, cliente=falso, llms=llms)
    return {
        "codigo": codigo,
        "torneos_pedidos": falso.torneos_pedidos,
        "preguntas_pronosticadas": _lineas_registro() - registro_antes,
    }


def _lineas_registro() -> int:
    import bot.registro as r

    return sum(len(f.read_text(encoding="utf-8").splitlines()) for f in r.CARPETA.glob("*.jsonl"))


def _flujos() -> dict:
    res = {}
    for f in sorted((RAIZ / ".github" / "workflows").glob("*.yaml")):
        if f.name == "pruebas.yaml":  # el de las pruebas no es del bot: la orden 14 le añade ruff
            continue
        datos = yaml.safe_load(f.read_text(encoding="utf-8"))
        disparo = datos.get("on", datos.get(True)) or {}
        res[f.name] = {
            "horarios": [c["cron"] for c in (disparo.get("schedule") or [])],
            "trabajos": {
                n: {"si": t.get("if"), "tope_minutos": t.get("timeout-minutes")}
                for n, t in datos["jobs"].items()
            },
        }
    return res


def configuracion_efectiva(monkeypatch) -> dict:
    foto: dict = {}
    for clave in ("sin_clave_openrouter", "con_clave_openrouter"):
        if clave == "con_clave_openrouter":
            monkeypatch.setenv("OPENROUTER_API_KEY", "clave-falsa")
        else:
            monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        for modo in ("tres_empresas", "un_modelo"):
            params = cfg.cargar_params()
            params["pronostico"]["modo"] = modo
            foto[f"{clave}/{modo}"] = _bot(params)
    monkeypatch.setenv("OPENROUTER_API_KEY", "clave-falsa")
    modelo = ModeloFalso()
    llms = {"default": modelo, "summarizer": modelo, "researcher": modelo, "parser": modelo}
    casos = [
        (False, "test_questions", "workflow_dispatch"),
        (False, "tournament", "workflow_dispatch"),
        (False, "tournament", "schedule"),
        (True, "tournament", "schedule"),
        (True, "test_questions", "workflow_dispatch"),
    ]
    foto["ejecuciones"] = {
        f"envio={e}/{m}/{ev}": _ejecucion(monkeypatch, llms, e, m, ev) for e, m, ev in casos
    }
    foto["flujos_github"] = _flujos()
    # ida y vuelta por JSON: tuplas -> listas, claves -> texto (igual que la foto guardada)
    return json.loads(json.dumps(foto, ensure_ascii=False, sort_keys=True))


def test_configuracion_efectiva_igual_que_antes(monkeypatch):
    esperada = json.loads(FOTO.read_text(encoding="utf-8"))
    actual = configuracion_efectiva(monkeypatch)
    for clave in sorted(set(esperada) | set(actual)):
        assert actual.get(clave) == esperada.get(clave), f"ha cambiado: {clave}"


if __name__ == "__main__":  # regenerar la foto (solo tras un cambio de ajuste decidido)
    os.environ.pop("CLAUDE_CODE_OAUTH_TOKEN", None)
    with pytest.MonkeyPatch.context() as mp:
        import bot.registro as r

        mp.setattr(r, "CARPETA", Path(tempfile.mkdtemp()) / "registro")
        for v in ("METACULUS_TOKEN", "ENVIO_REAL", "OPENROUTER_API_KEY", "GITHUB_EVENT_NAME"):
            mp.delenv(v, raising=False)
        FOTO.parent.mkdir(parents=True, exist_ok=True)
        texto = json.dumps(configuracion_efectiva(mp), ensure_ascii=False, indent=1, sort_keys=True)
        FOTO.write_text(texto + "\n", encoding="utf-8")
        print(f"Foto guardada en {FOTO}")
