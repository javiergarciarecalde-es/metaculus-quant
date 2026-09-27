"""Tope de gasto de los créditos de Metaculus (orden 26, 27/09/2026).

Todo con la clave simulada: ninguna prueba pregunta a OpenRouter ni gasta un céntimo. La respuesta
de ejemplo es la de la documentación de OpenRouter («API Key Status», leída el 27/09/2026).
"""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime

import pytest
from forecasting_tools import MonetaryCostManager

import main
from bot import config as cfg
from bot import presupuesto
from bot.presupuesto import EsquemaClaveError, EstadoClave
from bot.presupuesto import (
    consultar_clave as consultar_de_verdad,
)  # antes de que conftest la cambie
from tests.conftest import MetaculusFalso, ModeloFalso, preguntas_ejemplo

# Respuesta documentada de GET https://openrouter.ai/api/v1/key (ejemplo literal de sus docs).
RESPUESTA_DOCS = {
    "data": {
        "label": "sk-or-v1-abc...xyz",
        "limit": 10,
        "limit_reset": "monthly",
        "limit_remaining": 7,
        "include_byok_in_limit": False,
        "usage": 3,
        "usage_daily": 1,
        "usage_weekly": 2,
        "usage_monthly": 3,
        "byok_usage": 0,
        "byok_usage_daily": 0,
        "byok_usage_weekly": 0,
        "byok_usage_monthly": 0,
        "is_free_tier": False,
        "free_model_daily_requests": {"used": 5, "limit": 50, "remaining": 45},
    }
}
INICIO = datetime(2026, 9, 28, tzinfo=UTC)
MITAD = datetime(2026, 11, 17, tzinfo=UTC)  # 50 de 100 días de temporada


def _estado(gastado: float, limite: float | None = 100.0) -> EstadoClave:
    restante = None if limite is None else limite - gastado
    return EstadoClave(gastado=gastado, limite=limite, restante=restante)


# ------------------------------ lectura de la clave ------------------------------


def test_lee_la_respuesta_documentada():
    e = presupuesto.leer_estado(RESPUESTA_DOCS)
    assert (e.gastado, e.limite, e.restante) == (3.0, 10.0, 7.0)


# Respuesta real de la clave de Metaculus (27/09/2026, 18:06 UTC, ya sin etiqueta ni
# identificadores): gasta como «byok», así que «usage» da 0 y lo gastado va en «byok_usage».
RESPUESTA_REAL_27_09 = {
    "data": {
        "is_management_key": False,
        "is_provisioning_key": False,
        "limit": 100,
        "limit_reset": None,
        "limit_remaining": 99.0942706,
        "include_byok_in_limit": True,
        "usage": 0,
        "usage_daily": 0,
        "usage_weekly": 0,
        "usage_monthly": 0,
        "byok_usage": 0.9057294,
        "byok_usage_daily": 0.9057294,
        "byok_usage_weekly": 0.9057294,
        "byok_usage_monthly": 0.9057294,
        "is_free_tier": False,
        "expires_at": None,
        "allowed_data_regions": ["global"],
        "free_model_daily_requests": {"used": 0, "limit": 1000, "remaining": 1000},
    }
}


def test_lee_la_respuesta_real_de_la_clave_de_metaculus():
    e = presupuesto.leer_estado(RESPUESTA_REAL_27_09)
    assert e.gastado == pytest.approx(0.9057294)  # lo gastado en «byok», no en «usage»
    assert (e.limite, e.restante) == (100.0, pytest.approx(99.0942706))
    d = presupuesto.decidir(e, cfg.cargar_params(), INICIO, con_ritmo=True)
    assert "llevamos 0.91 $" in d.motivo


def test_sin_limite_propio_cuenta_tambien_lo_gastado_en_byok():
    datos = {"data": {**RESPUESTA_REAL_27_09["data"], "limit": None, "limit_remaining": None}}
    e = presupuesto.leer_estado(datos)
    assert presupuesto.restante(e, cfg.cargar_params()) == pytest.approx(100 - 0.9057294)


def test_clave_sin_limite_propio_usa_el_del_correo():
    datos = {"data": {**RESPUESTA_DOCS["data"], "limit": None, "limit_remaining": None}}
    e = presupuesto.leer_estado(datos)
    assert e.limite is None and e.restante is None
    assert presupuesto.restante(e, cfg.cargar_params()) == 100 - 3


@pytest.mark.parametrize(
    "cambio",
    [
        {"usage": None},
        {"usage": "3"},
        {"byok_usage": True},
        {"limit": "10"},
    ],
)
def test_respuesta_con_otra_forma_da_error_claro(cambio):
    with pytest.raises(EsquemaClaveError):
        presupuesto.leer_estado({"data": {**RESPUESTA_DOCS["data"], **cambio}})


@pytest.mark.parametrize("respuesta", [[], {"error": "x"}, {"data": {"usage": 1}}])
def test_respuesta_rota_da_error_claro(respuesta):
    with pytest.raises(EsquemaClaveError):
        presupuesto.leer_estado(respuesta)


class _Respuesta:
    def __init__(self, datos):
        self.datos = datos

    def raise_for_status(self):
        pass

    def json(self):
        return self.datos


def test_consulta_archiva_la_respuesta_sin_la_etiqueta_de_la_clave(tmp_path):
    pedido = {}

    def get(url, headers, timeout):
        pedido.update(url=url, headers=headers, timeout=timeout)
        datos = {**RESPUESTA_DOCS["data"], "creator_user_id": "user_x", "workspace_id": "w"}
        return _Respuesta({"data": datos})

    e = consultar_de_verdad("CLAVE-SECRETA-DE-PRUEBA", 30, get=get)
    assert e.gastado == 3.0
    assert pedido["url"] == "https://openrouter.ai/api/v1/key"
    assert pedido["headers"] == {"Authorization": "Bearer CLAVE-SECRETA-DE-PRUEBA"}
    [f] = list((tmp_path / "registro").glob("presupuesto_*.jsonl"))
    texto = f.read_text(encoding="utf-8")
    assert "CLAVE-SECRETA" not in texto and "sk-or" not in texto and "label" not in texto
    assert "user_x" not in texto and "workspace_id" not in texto
    assert json.loads(texto)["respuesta"]["data"]["usage"] == 3


# ------------------------------ decisión ------------------------------


def test_sin_dinero_no_se_empieza_nada():
    params = cfg.cargar_params()
    d = presupuesto.decidir(_estado(97.5), params, MITAD, con_ritmo=False)
    assert d.sin_dinero and d.max_preguntas == 0
    assert "Sin dinero" in d.motivo


def test_minibench_solo_la_para_la_reserva():
    params = cfg.cargar_params()
    conf = params["presupuesto"]
    # a principio de temporada, con 80 $ gastados (muy por encima del ritmo): la MiniBench sigue
    d = presupuesto.decidir(_estado(80.0), params, INICIO, con_ritmo=False)
    esperado = int((20.0 - conf["reserva_usd"]) // conf["coste_previsto_por_pregunta_usd"])
    assert not d.sin_dinero and d.max_preguntas == esperado


def test_temporada_espera_si_va_por_delante_del_ritmo():
    params = cfg.cargar_params()
    # colchón 25 %: el primer día se permiten 25 $; con 30 $ gastados, la temporada espera
    d = presupuesto.decidir(_estado(30.0), params, INICIO, con_ritmo=True)
    assert d.max_preguntas == 0 and not d.sin_dinero
    assert "Temporada en espera" in d.motivo


def test_temporada_avanza_al_ritmo():
    params = cfg.cargar_params()
    conf = params["presupuesto"]
    # a mitad de temporada se permiten 25 + 75/2 = 62,5 $; con 50 gastados caben 12,5 $
    d = presupuesto.decidir(_estado(50.0), params, MITAD, con_ritmo=True)
    assert d.max_preguntas == int(12.5 // conf["coste_previsto_por_pregunta_usd"])


def test_lo_gastado_en_esta_ejecucion_cuenta_aunque_la_clave_vaya_por_detras():
    params = cfg.cargar_params()
    antes = presupuesto.decidir(_estado(50.0), params, MITAD, con_ritmo=True)
    despues = presupuesto.decidir(_estado(50.0), params, MITAD, True, gastado_en_esta_ejecucion=5)
    assert despues.max_preguntas < antes.max_preguntas


def test_si_metaculus_sube_el_limite_hay_mas_sitio():
    params = cfg.cargar_params()
    con_100 = presupuesto.decidir(_estado(90.0, 100.0), params, MITAD, con_ritmo=False)
    con_300 = presupuesto.decidir(_estado(90.0, 300.0), params, MITAD, con_ritmo=False)
    assert con_100.max_preguntas < con_300.max_preguntas


def test_linea_de_ritmo():
    conf = cfg.cargar_params()
    assert presupuesto.linea_de_ritmo(100, conf, datetime(2026, 9, 1, tzinfo=UTC)) == 25
    assert presupuesto.linea_de_ritmo(100, conf, INICIO) == 25
    assert presupuesto.linea_de_ritmo(100, conf, MITAD) == pytest.approx(62.5)
    assert presupuesto.linea_de_ritmo(100, conf, datetime(2027, 2, 1, tzinfo=UTC)) == 100


@pytest.mark.parametrize(
    ("texto", "sin_saldo"),
    [
        ("OpenrouterException - Error code: 402 - Payment Required", True),
        ("This request requires more credits, or fewer max_tokens", True),
        ("Insufficient credits", True),
        ("https://www.metaculus.com/questions/40234 falló", False),
        ("503 Service Unavailable", False),
    ],
)
def test_reconoce_la_falta_de_saldo(texto, sin_saldo):
    assert presupuesto.es_falta_de_saldo(RuntimeError(texto)) is sin_saldo


# ------------------------------ el bot entero ------------------------------


def _ejecutar(monkeypatch, llms, estado, envio=True, modo="tournament", preguntas=None, **kw):
    monkeypatch.setenv("METACULUS_TOKEN", "token-de-prueba")
    monkeypatch.setenv("OPENROUTER_API_KEY", "clave-falsa")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "schedule" if envio else "workflow_dispatch")
    if envio:
        monkeypatch.setenv("ENVIO_REAL", "true")
    falso = MetaculusFalso(preguntas if preguntas is not None else preguntas_ejemplo())
    consulta = estado if callable(estado) else (lambda: estado)
    codigo = main.ejecutar(modo, cliente=falso, llms=llms, consulta=consulta, **kw)
    return codigo, falso


def _pronosticadas(tmp_path) -> int:
    f = list((tmp_path / "registro").glob("pronosticos_*.jsonl"))
    return len(f[0].read_text(encoding="utf-8").splitlines()) if f else 0


def test_sin_dinero_termina_limpio_sin_pronosticar(monkeypatch, llms, tmp_path, capsys):
    codigo, falso = _ejecutar(monkeypatch, llms, _estado(99.0))
    assert codigo == 0  # amarillo, no rojo: no falla cada 20 minutos
    assert falso.envios == [] and _pronosticadas(tmp_path) == 0
    assert "::notice::Sin dinero" in capsys.readouterr().out


def test_el_tope_limita_cuantas_preguntas_se_empiezan(monkeypatch, llms, tmp_path, capsys):
    params = cfg.cargar_params()
    params["presupuesto"]["reserva_usd"] = 1.0
    params["presupuesto"]["coste_previsto_por_pregunta_usd"] = 1.0
    # quedan 3 $: 2 $ por encima de la reserva -> 2 preguntas en la MiniBench; la temporada, igual
    estado = EstadoClave(gastado=0.0, limite=3.0, restante=3.0)
    codigo, _ = _ejecutar(monkeypatch, llms, estado, params=params)
    assert codigo == 0
    salida = capsys.readouterr().out
    assert "se dejan 1 preguntas" in salida
    assert _pronosticadas(tmp_path) <= 4


def test_minibench_si_y_temporada_en_espera(monkeypatch, llms, tmp_path):
    # 40 $ gastados el primer día: por encima del ritmo (25 $) pero lejos de la reserva
    monkeypatch.setattr(main, "datetime", _Reloj)
    codigo, falso = _ejecutar(monkeypatch, llms, _estado(40.0))
    assert codigo == 0
    assert falso.torneos_pedidos == ["minibench", 33121]
    assert _pronosticadas(tmp_path) == 3  # solo las 3 de la MiniBench


class _Reloj(datetime):
    @classmethod
    def now(cls, tz=None):
        return INICIO


def test_sin_poder_leer_el_saldo_no_se_gasta(monkeypatch, llms, tmp_path, capsys):
    def caida():
        raise ConnectionError("sin red")

    codigo, _ = _ejecutar(monkeypatch, llms, caida)
    assert codigo == 0 and _pronosticadas(tmp_path) == 0
    assert "::warning::No se pudo leer el saldo" in capsys.readouterr().out


def test_respuesta_de_openrouter_con_otra_forma_da_error_rojo(monkeypatch, llms, tmp_path):
    def rara():
        return presupuesto.leer_estado({"data": {"usage": "mucho"}})

    codigo, _ = _ejecutar(monkeypatch, llms, rara)
    assert codigo == 1 and _pronosticadas(tmp_path) == 0


def test_las_ya_enviadas_no_ocupan_sitio(monkeypatch, llms, tmp_path):
    params = cfg.cargar_params()
    params["presupuesto"]["reserva_usd"] = 1.0
    params["presupuesto"]["coste_previsto_por_pregunta_usd"] = 1.0
    preguntas = preguntas_ejemplo()
    preguntas[0].already_forecasted = True
    preguntas[1].already_forecasted = True
    # cabe 1 pregunta por torneo: debe ser la que falta, no una de las ya enviadas
    estado = EstadoClave(gastado=0.0, limite=2.5, restante=2.5)
    _ejecutar(monkeypatch, llms, estado, preguntas=preguntas, params=params)
    lineas = (tmp_path / "registro").glob("pronosticos_*.jsonl")
    urls = {
        json.loads(x)["url"] for f in lineas for x in f.read_text(encoding="utf-8").splitlines()
    }
    assert urls == {"https://ejemplo/3"}


class ModeloSinSaldo(ModeloFalso):
    async def invoke(self, prompt):  # type: ignore[override]
        if "Probability: ZZ%" in prompt:
            raise RuntimeError("OpenrouterException - Error code: 402 - Payment Required")
        return await super().invoke(prompt)


def test_sin_saldo_a_mitad_no_es_un_fallo_rojo(monkeypatch, tmp_path, capsys):
    m = ModeloSinSaldo()
    llms = {"default": m, "summarizer": m, "researcher": m, "parser": m}
    preguntas = preguntas_ejemplo()[:1]  # solo la binaria, que es la que falla
    codigo, _ = _ejecutar(monkeypatch, llms, _estado(0.0), envio=False, preguntas=preguntas)
    assert codigo == 0
    assert "la clave no tiene saldo" in capsys.readouterr().out


class ModeloDeUnDolar(ModeloFalso):
    """Cada llamada «cuesta» 1 $ y antes mira el freno, como hace la librería con litellm."""

    async def invoke(self, prompt):  # type: ignore[override]
        if "Probability: ZZ%" in prompt:
            MonetaryCostManager.raise_error_if_limit_would_be_reached()
            MonetaryCostManager.increase_current_usage_in_parent_managers(1.0)
        return await super().invoke(prompt)


def test_freno_por_pregunta(llms):
    params = cfg.cargar_params()
    params["presupuesto"]["tope_por_pregunta_usd"] = 0.5
    caro = ModeloDeUnDolar()
    bot = main.construir_bot(params, publicar=False, llms={**llms, "_puestos": [caro]})
    bot.metaculus_client = MetaculusFalso([])
    [r] = asyncio.run(bot.forecast_questions(preguntas_ejemplo()[:1], return_exceptions=True))
    # la 1.ª pasada gasta 1 $ (pasa el tope de 0,5 $): las otras dos se cortan y no hay pronóstico
    assert isinstance(r, BaseException)
    assert caro.llamadas == 1


def test_sin_freno_alcanzado_se_pronostica_normal(llms):
    params = cfg.cargar_params()
    params["presupuesto"]["tope_por_pregunta_usd"] = 10
    caro = ModeloDeUnDolar()
    bot = main.construir_bot(params, publicar=False, llms={**llms, "_puestos": [caro]})
    bot.metaculus_client = MetaculusFalso([])
    [r] = asyncio.run(bot.forecast_questions(preguntas_ejemplo()[:1]))
    assert r.prediction == pytest.approx(0.72)
