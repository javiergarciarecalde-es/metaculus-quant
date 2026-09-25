"""Modos de pronóstico, respaldo automático, registro por miembro e investigación ampliada."""

import asyncio
import json

import pytest

import main
from bot import config as cfg
from bot import investigacion as inv
from tests.conftest import MetaculusFalso, ModeloFalso, preguntas_ejemplo


def test_tres_empresas_da_tres_modelos_distintos(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "clave-falsa")
    puestos = cfg.lista_pronosticadores(cfg.cargar_params())
    nombres = [p["nombre"] for p in puestos]
    assert len(set(nombres)) == 3
    assert "openrouter/anthropic/claude-opus-5.5" in nombres
    assert all(p.get("respaldo") for p in puestos)


def test_un_modelo_repite_opus_tres_veces(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "clave-falsa")
    params = cfg.cargar_params()
    params["pronostico"]["modo"] = "un_modelo"
    bot = main.construir_bot(params, publicar=False)
    assert [m.model for m in bot._modelos] == ["openrouter/anthropic/claude-opus-5.5"] * 3
    assert bot._modelos[0].litellm_kwargs["extra_body"] == {"reasoning": {"effort": "high"}}


def test_modo_invalido_da_error_claro():
    params = cfg.cargar_params()
    params["pronostico"]["modo"] = "agentes"
    with pytest.raises(ValueError, match=r"pronostico\.modo"):
        cfg.lista_pronosticadores(params)


class ModeloRoto(ModeloFalso):
    def __init__(self, fallo):
        super().__init__()
        self.fallo = fallo

    async def invoke(self, prompt):  # type: ignore[override]
        self.llamadas += 1
        if self.fallo == "vacio":
            return "   "
        raise RuntimeError("proveedor caído")


def _bot_con_puestos(llms, puestos, respaldos):
    params = cfg.cargar_params()
    bot = main.construir_bot(
        params, publicar=False, llms={**llms, "_puestos": puestos, "_respaldos": respaldos}
    )
    bot.metaculus_client = MetaculusFalso([])
    return bot


@pytest.mark.parametrize("fallo", ["vacio", "excepcion"])
def test_respaldo_responde_si_el_principal_falla(llms, fallo):
    roto, respaldo = ModeloRoto(fallo), ModeloFalso()
    bot = _bot_con_puestos(llms, [roto], [respaldo])
    [r] = asyncio.run(bot.forecast_questions(preguntas_ejemplo()[:1]))
    assert r.prediction == pytest.approx(0.72)
    assert roto.llamadas == 3 and respaldo.llamadas == 3


def test_si_fallan_dos_de_tres_puestos_no_se_envia(llms):
    bueno = ModeloFalso()
    bot = _bot_con_puestos(
        llms, [ModeloRoto("excepcion"), ModeloRoto("vacio"), bueno], [None, None, None]
    )
    bot.publish_reports_to_metaculus = True
    [r] = asyncio.run(bot.forecast_questions(preguntas_ejemplo()[:1], return_exceptions=True))
    assert isinstance(r, BaseException)
    assert bot.metaculus_client.envios == []


def test_registro_guarda_cada_miembro(monkeypatch, llms, tmp_path):
    monkeypatch.setenv("METACULUS_TOKEN", "token-de-prueba")
    main.ejecutar("test_questions", cliente=MetaculusFalso(preguntas_ejemplo()), llms=llms)
    [f] = list((tmp_path / "registro").glob("*.jsonl"))
    lineas = [json.loads(linea) for linea in f.read_text(encoding="utf-8").splitlines()]
    for linea in lineas:
        assert len(linea["miembros"]) == 3 and linea["modo"] == "tres_empresas"
        assert linea["investigacion_modo"] == "claude_max"
        assert linea["claude_max_usd_equivalente"] is None  # sin secreto no se usa
    primero = lineas[0]["miembros"][0]
    assert (primero["modelo"], primero["valor"]) == ("falso/modelo", 0.72)
    assert primero["razonamiento"]  # el texto completo del modelo (registro completo, 25/09)


# ---------------------------- investigación ampliada ----------------------------


class Director(ModeloFalso):
    def __init__(self, respuesta):
        super().__init__()
        self.respuesta = respuesta

    async def invoke(self, prompt):  # type: ignore[override]
        self.llamadas += 1
        return self.respuesta


JSON_OK = (
    '[{"dato": "fuente de resolución", "busqueda": "q1"}, {"dato": "tasa base", "busqueda": "q2"}]'
)


def _ampliar(director, buscador, tope=5):
    return asyncio.run(
        inv.ampliar(
            "INFORME BASE",
            "¿X?",
            "criterios",
            director,
            buscador,
            n=2,
            tope_segundos=tope,
            max_caracteres=6000,
        )
    )


def test_ampliada_anade_al_final_sin_reescribir():
    director, buscador = Director(JSON_OK), ModeloFalso()
    out = _ampliar(director, buscador)
    assert out.startswith("INFORME BASE") and inv.CABECERA in out
    assert director.llamadas == 1 and buscador.llamadas == 2


def test_ampliada_json_malo_devuelve_base():
    assert _ampliar(Director("no sé"), ModeloFalso()) == "INFORME BASE"


def test_ampliada_un_buscador_falla_queda_el_otro():
    class MedioRoto(ModeloFalso):
        async def invoke(self, prompt):  # type: ignore[override]
            self.llamadas += 1
            if "q1" in prompt:
                raise RuntimeError("caído")
            return "dato comprobado"

    out = _ampliar(Director(JSON_OK), MedioRoto())
    assert "tasa base" in out and "fuente de resolución" not in out


def test_ampliada_sin_tiempo_devuelve_base():
    class Lento(ModeloFalso):
        async def invoke(self, prompt):  # type: ignore[override]
            await asyncio.sleep(1)
            return JSON_OK

    assert _ampliar(Lento(), ModeloFalso(), tope=0.01) == "INFORME BASE"


def test_basica_no_hace_llamadas_extra(llms, modelo):
    bot = main.construir_bot(cfg.cargar_params(), publicar=False, llms=llms)
    bot.metaculus_client = MetaculusFalso([])
    asyncio.run(bot.forecast_questions(preguntas_ejemplo()[:1]))
    assert modelo.llamadas == 1 + 3  # 1 búsqueda + 3 pasadas


def test_ampliada_integrada_en_el_bot(llms, modelo):
    params = cfg.cargar_params()
    params["investigacion"]["modo"] = "ampliada"
    director = Director(JSON_OK)
    bot = main.construir_bot(params, publicar=False, llms={**llms, "director": director})
    bot.metaculus_client = MetaculusFalso([])
    [r] = asyncio.run(bot.forecast_questions(preguntas_ejemplo()[:1]))
    assert director.llamadas == 1
    assert modelo.llamadas == 1 + 2 + 3  # búsqueda base + 2 buscadores + 3 pasadas
    assert r.prediction == pytest.approx(0.72)


def test_puestos_por_pregunta_sin_desalinear(llms):
    """La pasada n de cada pregunta usa el puesto n aunque otras fallen o sean de grupo."""
    a, b = ModeloFalso(), ModeloFalso()
    bot = _bot_con_puestos(llms, [a, b], [None, None])
    asyncio.run(bot.forecast_questions(preguntas_ejemplo()[:1] * 1))
    asyncio.run(bot.forecast_questions(preguntas_ejemplo()[:1]))
    assert (a.llamadas, b.llamadas) == (4, 2)  # 3 pasadas por pregunta: a, b, a  (+ la 2.ª igual)


def test_proxy_tiene_respaldo_en_cada_puesto():
    puestos = cfg.lista_pronosticadores(cfg.cargar_params())  # sin OPENROUTER_API_KEY -> proxy
    assert puestos and all(p.get("respaldo") for p in puestos)


def test_subpreguntas_de_grupo_no_mezclan_miembros(monkeypatch, llms, tmp_path):
    from forecasting_tools import BinaryQuestion

    monkeypatch.setenv("METACULUS_TOKEN", "t")
    grupo = [
        BinaryQuestion(
            question_text=f"sub {i}",
            id_of_post=50,
            id_of_question=500 + i,
            page_url="https://ejemplo/50",
        )
        for i in range(3)
    ]
    main.ejecutar("test_questions", cliente=MetaculusFalso(grupo), llms=llms)
    [f] = list((tmp_path / "registro").glob("*.jsonl"))
    assert [
        len(json.loads(linea)["miembros"]) for linea in f.read_text(encoding="utf-8").splitlines()
    ] == [
        3,
        3,
        3,
    ]


def test_pasada_colgada_se_corta(llms):
    class Colgado(ModeloFalso):
        async def invoke(self, prompt):  # type: ignore[override]
            await asyncio.sleep(10)

    params = cfg.cargar_params()
    params["tiempos"]["tope_pasada_segundos"] = 0.05
    bot = main.construir_bot(
        params,
        publicar=False,
        llms={
            **llms,
            "_puestos": [Colgado(), ModeloFalso(), ModeloFalso()],
            "_respaldos": [None] * 3,
        },
    )
    bot.metaculus_client = MetaculusFalso([])
    [r] = asyncio.run(bot.forecast_questions(preguntas_ejemplo()[:1]))
    assert r.prediction == pytest.approx(0.72)  # sale con 2 de 3


def test_sin_tiempo_no_empieza_preguntas(llms, modelo):
    params = cfg.cargar_params()
    params["tiempos"]["dejar_de_empezar_tras_minutos"] = 0
    bot = main.construir_bot(params, publicar=False, llms=llms)
    bot.metaculus_client = MetaculusFalso([])
    [r] = asyncio.run(bot.forecast_questions(preguntas_ejemplo()[:1], return_exceptions=True))
    assert isinstance(r, BaseException) and modelo.llamadas == 0


def test_registro_por_pregunta_aunque_la_tanda_no_termine(monkeypatch, llms, tmp_path):
    """Cada pregunta se apunta al acabar, no al final de la tanda."""
    monkeypatch.setenv("METACULUS_TOKEN", "t")
    apuntadas = []
    orig = main.registrar
    monkeypatch.setattr(
        main, "registrar", lambda inf, *a, **k: apuntadas.append(len(inf)) or orig(inf, *a, **k)
    )
    main.ejecutar("test_questions", cliente=MetaculusFalso(preguntas_ejemplo()), llms=llms)
    assert apuntadas[:3] == [1, 1, 1]


# -------------------- aviso de fallo total (ensayo real del 25/09/2026) --------------------


def test_si_fallan_todas_acaba_en_rojo(monkeypatch, llms, capsys):
    """El primer ensayo real acabó en verde con 0 pronósticos: ahora tiene que verse."""
    monkeypatch.setenv("METACULUS_TOKEN", "t")
    roto = ModeloRoto("excepcion")
    codigo = main.ejecutar(
        "test_questions",
        cliente=MetaculusFalso(preguntas_ejemplo()),
        llms={**llms, "default": roto, "researcher": roto},
    )
    salida = capsys.readouterr().out
    assert codigo == 1 and "::error::" in salida and "OPENROUTER_API_KEY" in salida


def test_si_todo_va_bien_acaba_en_verde(monkeypatch, llms, capsys):
    monkeypatch.setenv("METACULUS_TOKEN", "t")
    monkeypatch.setenv("OPENROUTER_API_KEY", "clave-falsa")
    codigo = main.ejecutar("test_questions", cliente=MetaculusFalso(preguntas_ejemplo()), llms=llms)
    salida = capsys.readouterr().out
    assert codigo == 0 and "::error::" not in salida and "::warning::" not in salida
