"""Mejoras A, B y C del 25/09/2026 (decisión del usuario; ver docs/ESTUDIO_BOTS.md).

A: registro completo (investigación entera y su estado, criterios, razonamiento de cada modelo).
B: primero lo que cierra antes; sin investigación de Claude si la pregunta cierra pronto.
C: enlaces de resolución «para consultar primero», regla de citar mercados, reglas de lectura
   para los 3 modelos y «verificar primero» en Claude.
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime, timedelta

import pytest
from forecasting_tools import BinaryQuestion

import main
from bot import claude_max as cm
from bot import config as cfg
from bot import investigacion as inv
from tests.conftest import MetaculusFalso, ModeloFalso, preguntas_ejemplo
from tests.test_claude_max import ClaudeFalso

# orden 82 (07/10/2026): config/params.yaml apaga el plan de Claude; aquí se prueba encendido
pytestmark = pytest.mark.usefixtures("claude_encendido")


class ModeloQueApunta(ModeloFalso):
    """Como ModeloFalso, pero guarda cada prompt que recibe."""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.prompts: list[str] = []

    async def invoke(self, prompt):  # type: ignore[override]
        self.prompts.append(prompt)
        return await super().invoke(prompt)


def _binaria(
    cierre_en_min: float | None, criterios: str = "Resolves per https://ejemplo.org/datos."
) -> BinaryQuestion:
    cierre = None if cierre_en_min is None else datetime.now(UTC) + timedelta(minutes=cierre_en_min)
    return BinaryQuestion(
        question_text="¿Pasará X?",
        id_of_post=11,
        id_of_question=12,
        page_url="https://www.metaculus.com/questions/11/",
        resolution_criteria=criterios,
        fine_print="Ver también https://otra.org/x, y https://ejemplo.org/datos.",
        background_info="",
        close_time=cierre,
    )


# ------------------------------------------------------------------ C: enlaces y textos


def test_enlaces_de_resolucion_sin_repetir_ni_puntuacion():
    q = _binaria(120)
    enlaces = inv.enlaces_de(q.resolution_criteria, q.fine_print, maximo=5)
    assert enlaces == ["https://ejemplo.org/datos", "https://otra.org/x"]
    assert inv.enlaces_de(q.resolution_criteria, q.fine_print, maximo=1) == [
        "https://ejemplo.org/datos"
    ]
    assert inv.bloque_enlaces([]) == ""


def test_prompt_de_claude_verifica_primero_y_da_los_enlaces():
    texto = cm.prompt_investigacion("¿X?", "crit", "letra", "INFORME", 3, 6000, ["https://a.org"])
    assert "VERIFY FIRST" in texto and "https://a.org" in texto
    assert "Do NOT forecast" in texto and "trading volume" in texto


def test_busqueda_y_pronosticadores_reciben_enlaces_y_reglas(llms):
    modelo = ModeloQueApunta()
    todos = {k: modelo for k in llms}
    bot = main.construir_bot(cfg.cargar_params(), publicar=False, llms=todos)
    bot.metaculus_client = MetaculusFalso([])
    [r] = asyncio.run(bot.forecast_questions([_binaria(120)], return_exceptions=True))
    assert not isinstance(r, BaseException), r
    busqueda = [p for p in modelo.prompts if "assistant to a superforecaster" in p]
    pronosticos = [p for p in modelo.prompts if "Probability: ZZ%" in p]
    assert (
        busqueda and "https://ejemplo.org/datos" in busqueda[0] and "trading volume" in busqueda[0]
    )
    assert len(pronosticos) == 3 and all(main.REGLAS_LECTURA in p for p in pronosticos)


# ------------------------------------------------------------------ B: orden y cierre cercano


def test_primero_lo_que_cierra_antes():
    tarde, pronto, sin = _binaria(300), _binaria(40), _binaria(None)
    assert main._primero_lo_que_cierra_antes([tarde, sin, pronto]) == [pronto, tarde, sin]


def test_sin_claude_si_la_pregunta_cierra_pronto(monkeypatch, llms):
    monkeypatch.setenv(cm.SECRETO, "token-falso")
    falso = ClaudeFalso()
    bot = main.construir_bot(
        cfg.cargar_params(), publicar=False, llms={**llms, "_claude_ejecutar": falso}
    )
    bot.metaculus_client = MetaculusFalso([])
    q = _binaria(10)  # cierra en 10 min (< 30)
    asyncio.run(bot.forecast_questions([q]))
    assert falso.llamadas == []
    assert bot._investigacion[main._clave(q)]["claude_estado"] == "saltada_poco_tiempo"


def test_con_margen_si_hay_claude_y_se_guarda_aparte(monkeypatch, llms):
    monkeypatch.setenv(cm.SECRETO, "token-falso")
    falso = ClaudeFalso()
    bot = main.construir_bot(
        cfg.cargar_params(), publicar=False, llms={**llms, "_claude_ejecutar": falso}
    )
    bot.metaculus_client = MetaculusFalso([])
    q = _binaria(120)
    asyncio.run(bot.forecast_questions([q]))
    assert len(falso.llamadas) == 1 and "https://ejemplo.org/datos" in falso.llamadas[0]["entrada"]
    datos = bot._investigacion[main._clave(q)]
    assert datos["claude_estado"] == "ok" and "NOTAS DE OPUS" in datos["claude"]
    # opción A del usuario (28/09/2026): con Claude, no hay búsqueda de pago en esta pregunta
    assert datos["base_estado"] == "sustituida_por_claude" and datos["base"] == ""


def test_estado_de_claude_si_falla(monkeypatch, llms):
    monkeypatch.setenv(cm.SECRETO, "token-falso")
    bot = main.construir_bot(
        cfg.cargar_params(),
        publicar=False,
        llms={**llms, "_claude_ejecutar": ClaudeFalso(is_error=True, resultado="Error interno")},
    )
    bot.metaculus_client = MetaculusFalso([])
    q = _binaria(120)
    asyncio.run(bot.forecast_questions([q]))
    assert bot._investigacion[main._clave(q)]["claude_estado"] == "fallo"


# ------------------------------------------------------------------ A: registro completo


def test_registro_completo(monkeypatch, llms, tmp_path):
    monkeypatch.setenv("METACULUS_TOKEN", "t")
    main.ejecutar("test_questions", cliente=MetaculusFalso(preguntas_ejemplo()), llms=llms)
    [f] = list((tmp_path / "registro").glob("*.jsonl"))
    lineas = [json.loads(linea) for linea in f.read_text(encoding="utf-8").splitlines()]
    for linea in lineas:
        assert linea["investigacion"]["base_estado"] == "ok"
        # una de cada dos (27/09/2026): las de número impar quedan fuera del reparto
        par = linea["id_pregunta"] % 2 == 0
        esperado = "sin_secreto" if par else "fuera_del_reparto"
        assert linea["investigacion"]["claude_estado"] == esperado
        assert "Noticias simuladas" in linea["investigacion"]["base"]
        assert "criterios" in linea and "letra_pequena" in linea and "cierre_utc" in linea
        assert linea["fecha_para_modelos"] == datetime.now(UTC).strftime("%Y-%m-%d")
        assert all(m["razonamiento"] for m in linea["miembros"])


# ---------------------------------------- reparto de Claude: una de cada dos (27/09/2026)


def test_claude_solo_en_las_preguntas_de_numero_par(monkeypatch, llms):
    monkeypatch.setenv(cm.SECRETO, "token-falso")
    falso = ClaudeFalso()
    bot = main.construir_bot(
        cfg.cargar_params(), publicar=False, llms={**llms, "_claude_ejecutar": falso}
    )
    bot.metaculus_client = MetaculusFalso([])
    par, impar = _binaria(120), _binaria(120)
    impar.id_of_question, impar.id_of_post, impar.page_url = 13, 13, "https://ejemplo/13"
    asyncio.run(bot.forecast_questions([par, impar]))
    assert len(falso.llamadas) == 1  # solo la par
    assert bot._investigacion[main._clave(par)]["claude_estado"] == "ok"
    assert bot._investigacion[main._clave(impar)]["claude_estado"] == "fuera_del_reparto"


def test_con_una_de_cada_1_claude_investiga_todas(monkeypatch, llms):
    monkeypatch.setenv(cm.SECRETO, "token-falso")
    params = cfg.cargar_params()
    params["investigacion"]["claude_max"]["una_de_cada"] = 1
    falso = ClaudeFalso()
    bot = main.construir_bot(params, publicar=False, llms={**llms, "_claude_ejecutar": falso})
    bot.metaculus_client = MetaculusFalso([])
    impar = _binaria(120)
    impar.id_of_question, impar.id_of_post = 13, 13
    asyncio.run(bot.forecast_questions([impar]))
    assert len(falso.llamadas) == 1


def test_pausa_de_claude_con_fecha_de_vuelta(monkeypatch, llms):
    monkeypatch.setenv(cm.SECRETO, "token-falso")
    for hasta, llamadas, estado in [
        ("2999-01-01T00:00:00+00:00", 0, "pausada"),  # pausa en vigor
        ("2000-01-01T00:00:00+00:00", 1, "ok"),  # pausa pasada: vuelve sola
        (None, 1, "ok"),  # sin pausa
    ]:
        params = cfg.cargar_params()
        params["investigacion"]["claude_max"]["pausada_hasta_utc"] = hasta
        falso = ClaudeFalso()
        bot = main.construir_bot(params, publicar=False, llms={**llms, "_claude_ejecutar": falso})
        bot.metaculus_client = MetaculusFalso([])
        q = _binaria(120)  # número par: le toca Claude
        asyncio.run(bot.forecast_questions([q]))
        assert len(falso.llamadas) == llamadas
        assert bot._investigacion[main._clave(q)]["claude_estado"] == estado
