"""Comparador de formas de juntar a los 3 modelos (decisión del usuario del 25/09/2026)."""

from __future__ import annotations

import math

import pytest

from bot import comparador as cmp
from bot import marcador as mc

CONF = mc.conf_comparador()


def _fila(valor, miembros, tipo="binary", cuando="2026-10-01T00:00:00+00:00"):
    return {"tipo": tipo, "valor": valor, "miembros": miembros, "cuando_utc": cuando}


TRES = [
    {"modelo": "openrouter/openai/gpt-6-sol", "valor": 0.9},
    {"modelo": "openrouter/anthropic/claude-opus-5.5", "valor": 0.7},
    {"modelo": "openrouter/google/gemini-3.5-flash", "valor": 0.2},
]


def test_empresa_de_cada_modelo():
    assert cmp.empresa("openrouter/openai/gpt-5.6-sol") == "openai"
    assert cmp.empresa("metaculus/gpt-5") == "metaculus"


def test_la_forma_actual_da_cambio_cero():
    """Control: recalcular la mediana debe dar exactamente lo que enviamos."""
    cambios = cmp.cambios_por_pregunta(_fila(0.7, TRES), "yes", CONF)
    assert cambios[cmp.ACTUAL] == pytest.approx(0.0)


def test_cambios_de_cada_variante():
    cambios = cmp.cambios_por_pregunta(_fila(0.7, TRES), "yes", CONF)
    assert cambios["media"] == pytest.approx(100 * math.log(0.6 / 0.7))
    assert cambios["sin google"] == pytest.approx(100 * math.log(0.8 / 0.7))
    assert cambios["solo openai"] == pytest.approx(100 * math.log(0.9 / 0.7))
    assert set(CONF["preregistradas"]) <= set(cambios)


def test_limites_alternativos_solo_importan_en_los_extremos():
    miembros = [{"modelo": f"openrouter/{e}/m", "valor": 0.999} for e in ("a", "b", "c")]
    cambios = cmp.cambios_por_pregunta(_fila(0.98, miembros), "yes", CONF)
    assert cambios["límites 1%-99%"] == pytest.approx(100 * math.log(0.99 / 0.98))


def test_opciones():
    miembros = [
        {"modelo": "openrouter/openai/x", "valor": {"A": 0.6, "B": 0.4}},
        {"modelo": "openrouter/anthropic/y", "valor": {"A": 0.5, "B": 0.5}},
        {"modelo": "openrouter/google/z", "valor": {"A": 0.1, "B": 0.9}},
    ]
    valor = {"A": 0.5, "B": 0.5}
    cambios = cmp.cambios_por_pregunta(_fila(valor, miembros, "multiple_choice"), "A", CONF)
    assert cambios[cmp.ACTUAL] == pytest.approx(0.0)
    assert "sin google" in cambios and cambios["sin google"] > 0


def test_numericas_y_sin_miembros_no_entran():
    assert cmp.cambios_por_pregunta(_fila({"0.1": 1}, TRES, "numeric"), "3", CONF) == {}
    assert cmp.cambios_por_pregunta(_fila(0.7, []), "yes", CONF) == {}


def test_regla_de_decision():
    conf = {**CONF, "minimo_preguntas": 4}
    datos = [
        (f"2026-10-0{i}", {"media": 5.0, "sin google": -1.0 if i < 3 else 3.0}) for i in range(1, 5)
    ]
    filas = {f["variante"]: f for f in cmp.resumir(datos, conf)}
    assert filas["media"]["cumple_la_regla"] is True
    assert filas["sin google"]["cumple_la_regla"] is False  # pierde en la mitad antigua
    pocas = {f["variante"]: f for f in cmp.resumir(datos[:3], conf)}
    assert pocas["media"]["cumple_la_regla"] is False  # menos preguntas que el mínimo
    texto = "\n".join(cmp.informe_md(list(filas.values()), conf))
    assert "decidida de antemano" in texto


def test_aligerar_guarda_el_texto_largo_aparte(tmp_path):
    fila = {
        "url": "https://www.metaculus.com/questions/5/",
        "id_post": 5,
        "id_pregunta": 6,
        "investigacion": {"base": "texto largo"},
        "criterios": "c",
        "miembros": [{"modelo": "m", "valor": 0.5, "razonamiento": "largo"}],
    }
    ligera = mc.aligerar(fila, tmp_path)
    assert "investigacion" not in ligera and "razonamiento" not in ligera["miembros"][0]
    assert (tmp_path / "5_6.json").exists() and ligera["detalle"].endswith("5_6.json")
    assert mc.aligerar(ligera, tmp_path) == ligera  # ya ligera: no cambia
