"""Normas del torneo que hace cumplir el código (bot/normas.py; orden 27 del mando, 28/09/2026).

«Bot makers should only submit one forecast per question» (página oficial de recursos, releída el
28/09/2026). La librería salta las preguntas ya pronosticadas, pero si Metaculus no manda el
historial las da por nuevas (falla abierta) y el bot las volvería a pronosticar cada 20 minutos.
"""

from __future__ import annotations

import pytest

import main
from bot import normas
from tests.conftest import MetaculusFalso, preguntas_ejemplo


def _con_historial(q, historial):
    q.api_json = {"question": {"my_forecasts": {"history": historial}}}
    return q


# ------------------------------------------------------------------ piezas


def test_lee_el_historial_propio():
    q = preguntas_ejemplo()[0]
    assert normas.historial_propio(_con_historial(q, [{"t": 1}])) == [{"t": 1}]
    assert normas.historial_propio(_con_historial(q, [])) == []
    assert normas.historial_propio(_con_historial(q, None)) == []  # como la librería


@pytest.mark.parametrize(
    "api_json",
    [
        {},  # la librería no guardó la respuesta
        {"question": {}},  # Metaculus dejó de mandar «my_forecasts» (p. ej., sin sesión)
        {"question": {"my_forecasts": None}},
        {"question": {"my_forecasts": {"latest": None}}},  # cambió el nombre del campo
        {"question": {"my_forecasts": {"history": "sí"}}},
    ],
)
def test_sin_historial_legible_da_error_claro(api_json):
    q = preguntas_ejemplo()[0]
    q.api_json = api_json
    with pytest.raises(normas.EsquemaMetaculusError):
        normas.historial_propio(q)


def test_no_repite_aunque_la_libreria_diga_que_no_esta_pronosticada():
    """El fallo de verdad: `already_forecasted` en False, pero el historial dice que sí."""
    binaria, opciones, numerica = preguntas_ejemplo()
    _con_historial(binaria, [{"start_time": 1, "forecast_values": [0.3, 0.7]}])
    binaria.already_forecasted = False
    opciones.already_forecasted = True  # y al revés: basta con que uno de los dos lo diga
    quedan, avisos = normas.sin_pronostico_nuestro([binaria, opciones, numerica])
    assert quedan == [numerica] and avisos == []


def test_repetidas_una_sola_vez():
    preguntas = preguntas_ejemplo()
    quedan, _ = normas.sin_pronostico_nuestro(preguntas * 3)
    assert quedan == preguntas


def test_si_no_se_sabe_no_se_pronostica_y_se_avisa():
    binaria, opciones, numerica = preguntas_ejemplo()
    binaria.api_json = {"question": {}}
    quedan, avisos = normas.sin_pronostico_nuestro([binaria, opciones, numerica])
    assert quedan == [opciones, numerica]
    assert len(avisos) == 1 and "https://ejemplo/1" in avisos[0]


# ------------------------------------------------------------------ el bot entero


def _torneo(monkeypatch, llms, preguntas):
    monkeypatch.setenv("METACULUS_TOKEN", "token-de-prueba")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "schedule")
    monkeypatch.setenv("ENVIO_REAL", "true")
    falso = MetaculusFalso(preguntas)
    return main.ejecutar("tournament", cliente=falso, llms=llms), falso


def _enviadas(falso) -> list:
    return [a[0] for t, a in falso.envios if t != "comentario"]


def test_en_el_torneo_nunca_se_pronostica_dos_veces(monkeypatch, llms):
    binaria, opciones, numerica = preguntas_ejemplo()
    _con_historial(binaria, [{"t": 1}])
    binaria.already_forecasted = (
        False  # la librería se equivoca: el bot no debe fiarse solo de ella
    )
    codigo, falso = _torneo(monkeypatch, llms, [binaria, opciones, numerica, opciones])
    assert codigo == 0
    # MiniBench y temporada reciben la misma lista falsa: 2 preguntas en cada uno, una vez cada una
    assert sorted(_enviadas(falso)) == [12, 12, 13, 13]


def test_en_el_torneo_si_metaculus_no_dice_el_historial_sale_en_rojo(monkeypatch, llms, capsys):
    binaria, opciones, numerica = preguntas_ejemplo()
    binaria.api_json = {"question": {"my_forecasts": {}}}
    codigo, falso = _torneo(monkeypatch, llms, [binaria, opciones, numerica])
    assert codigo == 1  # rojo: la vigilancia lo ve y lo relanza; si sigue, despierta a Claude
    assert 11 not in _enviadas(falso)  # 11 = la binaria: no se pronostica sin saberlo
    assert "::error::" in capsys.readouterr().out


def test_la_zona_de_pruebas_no_cambia(monkeypatch, llms):
    """La zona de pruebas no puntúa: ahí se repiten preguntas a propósito (máximo 3)."""
    monkeypatch.setenv("METACULUS_TOKEN", "token-de-prueba")
    monkeypatch.setenv("ENVIO_REAL", "true")
    preguntas = preguntas_ejemplo()
    _con_historial(preguntas[0], [{"t": 1}])
    falso = MetaculusFalso(preguntas)
    assert main.ejecutar("test_questions", cliente=falso, llms=llms) == 0
    assert falso.torneos_pedidos == ["bot-testing-area"]
    assert sorted(_enviadas(falso)) == [11, 12, 13]
