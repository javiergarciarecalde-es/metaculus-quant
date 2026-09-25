import pytest

from bot import agregacion as ag
from bot import params as ajustes

# Los límites reales de config/params.yaml (2 % y 98 %; 1 % por opción)
LO = ajustes.p("pronostico.prob_min")
HI = ajustes.p("pronostico.prob_max")
MINIMO = ajustes.p("pronostico.minimo_por_opcion")


def test_los_limites_son_los_de_siempre():
    assert (LO, HI, MINIMO) == (0.02, 0.98, 0.01)


def test_binaria_mediana_y_limites():
    assert ag.agregar_binaria([0.6, 0.7, 0.8], 1.0, LO, HI) == pytest.approx(0.7)
    assert ag.agregar_binaria([0.0, 0.0, 0.0], 1.0, LO, HI) == LO
    assert ag.agregar_binaria([1.0, 1.0], 1.0, LO, HI) == HI


def test_extremizar_aleja_del_50_sin_pasarse():
    p = ag.agregar_binaria([0.7], 1.15, LO, HI)
    assert 0.7 < p < 0.8
    assert ag.agregar_binaria([0.5], 1.5, LO, HI) == pytest.approx(0.5)
    assert ag.agregar_binaria([0.999], 3, LO, HI) == HI


def test_opciones_suman_1_y_suelo():
    r = ag.agregar_opciones([{"A": 1.0, "B": 0.0, "C": 0.0}] * 3, ["A", "B", "C"], MINIMO)
    assert sum(r.values()) == pytest.approx(1.0)
    assert min(r.values()) >= MINIMO - 1e-9


def test_percentiles_mediana_y_monotonos():
    r = ag.agregar_percentiles(
        [{0.1: 1, 0.5: 5, 0.9: 9}, {0.1: 3, 0.5: 3, 0.9: 20}, {0.1: 2, 0.5: 4, 0.9: 10}]
    )
    assert list(r.values()) == sorted(r.values())
    assert r[0.5] == 4


def test_lectores():
    assert ag.leer_probabilidad("bla Probability: 35%") == pytest.approx(0.35)
    assert ag.leer_probabilidad("sin número") is None
    assert ag.leer_opciones("A: 60%\nB: 40%", ["A", "B"]) == pytest.approx({"A": 0.6, "B": 0.4})
    assert ag.leer_opciones("A: 60%", ["A", "B"]) is None
    d = ag.leer_percentiles("Percentile 10: 1,000\nPercentile 50: 2000\nPercentile 90: 3000.5")
    assert d == {0.1: 1000.0, 0.5: 2000.0, 0.9: 3000.5}
