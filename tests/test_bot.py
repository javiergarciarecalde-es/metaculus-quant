import json
import subprocess
import sys
from pathlib import Path

import pytest
from forecasting_tools import NumericDistribution, PredictedOptionList

import main
from bot import config as cfg
from tests.conftest import MetaculusFalso, preguntas_ejemplo

RAIZ = Path(__file__).resolve().parent.parent


def _ejecutar(monkeypatch, llms, envio: bool, evento: str = "workflow_dispatch", modo="test_questions"):
    monkeypatch.setenv("METACULUS_TOKEN", "token-de-prueba")
    monkeypatch.setenv("GITHUB_EVENT_NAME", evento)
    if envio:
        monkeypatch.setenv("ENVIO_REAL", "true")
    falso = MetaculusFalso(preguntas_ejemplo())
    codigo = main.ejecutar(modo, cliente=falso, llms=llms)
    return codigo, falso


async def test_tres_tipos_dan_pronostico_valido(llms):
    params = cfg.cargar_params()
    bot = main.construir_bot(params, publicar=False, llms=llms)
    bot.metaculus_client = MetaculusFalso([])
    informes = await bot.forecast_questions(preguntas_ejemplo(), return_exceptions=True)
    assert not any(isinstance(r, BaseException) for r in informes), informes
    binaria, opciones, numerica = [r.prediction for r in informes]

    assert params["pronostico"]["prob_min"] <= binaria <= params["pronostico"]["prob_max"]
    assert binaria == pytest.approx(0.72)  # mediana de las pasadas (extremizar apagado)

    assert isinstance(opciones, PredictedOptionList)
    probs = {o.option_name: o.probability for o in opciones.predicted_options}
    assert set(probs) == {"Rojo", "Verde", "Azul"}
    assert sum(probs.values()) == pytest.approx(1.0)
    assert probs["Rojo"] == pytest.approx(0.5, abs=0.01)

    assert isinstance(numerica, NumericDistribution)
    cdf = [p.percentile for p in numerica.get_cdf()]
    assert all(b >= a for a, b in zip(cdf, cdf[1:]))
    assert len(cdf) == 201


def test_varias_pasadas_por_pregunta(llms, modelo):
    params = cfg.cargar_params()
    bot = main.construir_bot(params, publicar=False, llms=llms)
    bot.metaculus_client = MetaculusFalso([])
    import asyncio
    asyncio.run(bot.forecast_questions(preguntas_ejemplo()[:1]))
    # 1 investigación + N pasadas
    assert modelo.llamadas == 1 + params["pronostico"]["pasadas_por_pregunta"]


def test_ensayo_no_envia_nada(monkeypatch, llms):
    codigo, falso = _ejecutar(monkeypatch, llms, envio=False)
    assert codigo == 0
    assert falso.envios == []


def test_con_interruptor_encendido_si_envia(monkeypatch, llms):
    codigo, falso = _ejecutar(monkeypatch, llms, envio=True)
    assert codigo == 0
    tipos = {t for t, _ in falso.envios}
    assert {"binaria", "opciones", "numerica", "comentario"} <= tipos


def test_programada_con_envio_apagado_no_gasta(monkeypatch, llms, modelo):
    codigo, falso = _ejecutar(monkeypatch, llms, envio=False, evento="schedule")
    assert codigo == 0
    assert modelo.llamadas == 0 and falso.envios == []


def test_sin_token_termina_limpio(capsys, llms, modelo):
    assert main.ejecutar("tournament", llms=llms) == 0
    assert "Falta METACULUS_TOKEN" in capsys.readouterr().out
    assert modelo.llamadas == 0


def test_sin_token_proceso_real_sale_con_0():
    """Como en GitHub Actions: se lanza main.py de verdad, sin secretos."""
    import os
    env = {k: v for k, v in os.environ.items()
           if k not in ("METACULUS_TOKEN", "ENVIO_REAL", "OPENROUTER_API_KEY")}
    r = subprocess.run([sys.executable, "main.py"], cwd=RAIZ, env=env,
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    assert "::notice::" in r.stdout


def test_registro_se_escribe(monkeypatch, llms, tmp_path):
    _ejecutar(monkeypatch, llms, envio=False)
    ficheros = list((tmp_path / "registro").glob("*.jsonl"))
    assert ficheros
    lineas = [json.loads(l) for l in ficheros[0].read_text(encoding="utf-8").splitlines()]
    assert len(lineas) == 3
    for l in lineas:
        assert {"url", "pregunta", "pronostico", "coste_usd", "razonamiento", "enviado"} <= set(l)
        assert l["enviado"] is False


def test_envio_real_solo_con_true_exacto(monkeypatch):
    for v, esperado in [("true", True), ("TRUE", True), ("1", False), ("yes", False), ("", False)]:
        monkeypatch.setenv("ENVIO_REAL", v)
        assert cfg.envio_real_encendido() is esperado


def test_puerta_intacta():
    texto = cfg.cargar_params()["puerta_fase0"]["texto"]
    assert texto.startswith("Se suma la puntuación de pares de todas las rondas de la fase 0")
    assert "entre los 20\nprimeros" in texto or "entre los 20 primeros" in texto


def test_no_hay_claves_en_el_repo():
    import re
    patron = re.compile(r"(sk-[A-Za-z0-9]{20,}|sk-or-v1-[a-f0-9]{20,}|Token [a-f0-9]{30,})")
    for f in RAIZ.rglob("*"):
        if ".venv" in f.parts or ".git" in f.parts or not f.is_file() or f.suffix in (".pyc",):
            continue
        assert not patron.search(f.read_text(encoding="utf-8", errors="ignore")), f


def test_ensayo_nunca_toca_el_torneo(monkeypatch, llms):
    """Las reglas prohíben previsualizar pronósticos en preguntas del torneo."""
    _, falso = _ejecutar(monkeypatch, llms, envio=False, modo="tournament")
    assert falso.torneos_pedidos == ["bot-testing-area"]


def test_envio_real_va_a_temporada_y_minibench(monkeypatch, llms):
    _, falso = _ejecutar(monkeypatch, llms, envio=True, evento="schedule", modo="tournament")
    assert falso.torneos_pedidos == [33121, "minibench"]


def test_extremizar_configurable(llms):
    params = cfg.cargar_params()
    params["pronostico"]["factor_extremizar"] = 1.3
    bot = main.construir_bot(params, publicar=False, llms=llms)
    bot.metaculus_client = MetaculusFalso([])
    import asyncio
    [r] = asyncio.run(bot.forecast_questions(preguntas_ejemplo()[:1]))
    assert 0.72 < r.prediction <= params["pronostico"]["prob_max"]


def test_modelos_reales_se_configuran_sin_llamar(monkeypatch):
    """Se construyen los modelos de verdad (sin llamarlos): con clave de OpenRouter y sin ella."""
    params = cfg.cargar_params()
    monkeypatch.setenv("OPENROUTER_API_KEY", "clave-falsa")
    bot = main.construir_bot(params, publicar=False)
    nombres = [m.model for m in bot._modelos]
    assert all(n.startswith("openrouter/") for n in nombres) and len(nombres) == 3
    assert bot._modelos[0].litellm_kwargs["extra_body"] == {"reasoning": {"effort": "high"}}
    monkeypatch.delenv("OPENROUTER_API_KEY")
    bot = main.construir_bot(params, publicar=False)
    assert all(m.model.startswith("metaculus/") for m in bot._modelos)


def test_dos_tandas_seguidas_no_fallan(monkeypatch, llms):
    """Temporada y MiniBench van en dos asyncio.run seguidos: la segunda no debe fallar."""
    _, falso = _ejecutar(monkeypatch, llms, envio=True, evento="schedule", modo="tournament")
    tipos = [t for t, _ in falso.envios]
    assert tipos.count("binaria") == 2 and tipos.count("numerica") == 2
