"""Los parámetros se leen del YAML y uno que no existe falla en el acto (sin valor por defecto).

**De dónde sale.** Forma de `cripto-quant/tests/test_params.py` (versión d4cbd77, 2026-09-25).
"""

from __future__ import annotations

import pytest

import main
from bot import config as cfg
from bot import params


def test_un_parametro_se_lee_del_fichero_o_de_un_arbol():
    assert params.p("pronostico.prob_min") == 0.02
    assert params.p("pronostico.prob_min", {"pronostico": {"prob_min": 0.5}}) == 0.5


def test_un_parametro_que_no_existe_falla_diciendo_cual():
    with pytest.raises(params.ParametroDesconocidoError, match=r"pronostico\.no_existe"):
        params.p("pronostico.no_existe")


def test_cargar_params_da_una_copia_que_se_puede_retocar():
    copia = cfg.cargar_params()
    copia["pronostico"]["prob_min"] = 0.4
    assert params.p("pronostico.prob_min") == 0.02


@pytest.mark.parametrize(
    "ruta",
    [
        "tiempos.tope_pasada_segundos",
        "modelos.intentos",
        "investigacion.busquedas_a_la_vez",
        "investigacion.claude_max",
        "pronostico.pasadas_por_pregunta",
    ],
)
def test_el_bot_no_arranca_si_falta_un_ajuste(ruta):
    """Antes, sin estos ajustes el código usaba un valor escondido; ahora para y dice cuál falta."""
    arbol = cfg.cargar_params()
    *camino, hoja = ruta.split(".")
    nodo = arbol
    for tramo in camino:
        nodo = nodo[tramo]
    del nodo[hoja]
    with pytest.raises(params.ParametroDesconocidoError, match=ruta.replace(".", r"\.")):
        main.construir_bot(arbol, publicar=False)


def test_un_puesto_sin_respaldo_declarado_falla():
    arbol = cfg.cargar_params()
    del arbol["modelos"]["proxy_metaculus"]["pronostico"][0]["respaldo"]
    with pytest.raises(params.ParametroDesconocidoError, match="respaldo"):
        cfg.lista_pronosticadores(arbol)
