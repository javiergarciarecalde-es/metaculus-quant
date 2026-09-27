"""Curva numérica suave (PCHIP) en sombra: se calcula y se guarda, nunca se envía (mejora 3 de
docs/ESTUDIO_BOTS.md, orden 26 del 27/09/2026)."""

from __future__ import annotations

import itertools
import json

import numpy as np
import pytest
from forecasting_tools import NumericDistribution, NumericQuestion, Percentile

import main
from bot import sombra
from tests.conftest import MetaculusFalso, preguntas_ejemplo


def _pregunta(**cambios) -> NumericQuestion:
    datos = {
        "question_text": "¿Cuántos?",
        "id_of_post": 3,
        "id_of_question": 13,
        "page_url": "https://ejemplo/3",
        "upper_bound": 100,
        "lower_bound": 0,
        "open_upper_bound": True,
        "open_lower_bound": False,
    }
    return NumericQuestion(**(datos | cambios))


def _dist(valores, q=None) -> NumericDistribution:
    pct = [0.1, 0.2, 0.4, 0.6, 0.8, 0.9]
    return NumericDistribution.from_question(
        [Percentile(percentile=p, value=v) for p, v in zip(pct, valores, strict=True)],
        q or _pregunta(),
    )


def test_pchip_igual_que_la_de_referencia():
    scipy = pytest.importorskip("scipy.interpolate")  # solo en las pruebas, si está instalada
    xs = [0.0, 0.1, 0.35, 0.4, 0.7, 1.0]
    ys = [0.0, 0.1, 0.2, 0.6, 0.8, 1.0]
    puntos = np.linspace(0, 1, 201)
    esperado = scipy.PchipInterpolator(xs, ys)(puntos)
    assert sombra.pchip(xs, ys, puntos) == pytest.approx(esperado.tolist(), abs=1e-12)


def test_pchip_pasa_por_los_puntos_y_nunca_baja():
    xs, ys = [0, 1, 2, 5, 6], [0.0, 0.3, 0.31, 0.9, 1.0]
    assert sombra.pchip(xs, ys, xs) == pytest.approx(ys)
    curva = sombra.pchip(xs, ys, np.linspace(-1, 7, 500))
    assert all(b >= a - 1e-15 for a, b in itertools.pairwise(curva))
    assert curva[0] == 0.0 and curva[-1] == 1.0  # fuera de los puntos, el valor del extremo


def test_pchip_en_linea_recta_es_la_recta():
    assert sombra.pchip([0, 1, 2], [0, 0.5, 1], [0.25, 1.5]) == pytest.approx([0.125, 0.75])


def test_pchip_rechaza_puntos_desordenados():
    with pytest.raises(ValueError):
        sombra.pchip([0, 0, 1], [0, 0.5, 1], [0.5])


def test_curva_de_un_modelo_mismos_puntos_y_sin_escalones():
    d = _dist([12, 20, 35, 48, 65, 80])
    recta = [p.percentile for p in d.get_cdf()]
    suave = [p.percentile for p in sombra.curva_pchip(d)]
    assert len(suave) == len(recta) == 201
    assert all(b >= a for a, b in itertools.pairwise(suave))
    assert [p.value for p in sombra.curva_pchip(d)] == [p.value for p in d.get_cdf()]
    # en cada percentil declarado, la suave pasa por lo que dijo el modelo (como la de rectas)
    for valor, pct in ((20, 0.2), (48, 0.6), (80, 0.9)):
        i = round(valor / 100 * 200)
        assert suave[i] == pytest.approx(recta[i], abs=0.01) == pytest.approx(pct, abs=0.01)
    assert max(abs(a - b) for a, b in zip(suave, recta, strict=True)) > 1e-4  # cambia algo


def test_escala_logaritmica_como_la_libreria():
    q = _pregunta(lower_bound=1, upper_bound=10_000, zero_point=0, open_lower_bound=True)
    d = _dist([5, 20, 100, 400, 2000, 5000], q)
    suave = sombra.curva_pchip(d)
    assert [p.value for p in suave] == pytest.approx([p.value for p in d.get_cdf()])
    assert all(b.percentile >= a.percentile for a, b in itertools.pairwise(suave))


def test_sombra_junta_como_la_libreria_y_valida():
    q = _pregunta()
    ds = [
        _dist(v)
        for v in ([12, 20, 35, 48, 65, 80], [5, 15, 30, 45, 60, 90], [18, 25, 33, 41, 55, 70])
    ]
    res = sombra.sombra(ds, q)
    assert len(res["cdf"]) == 201
    assert all(b >= a for a, b in itertools.pairwise(res["cdf"]))


def test_el_registro_guarda_la_sombra_y_no_la_envia(monkeypatch, llms, tmp_path):
    monkeypatch.setenv("METACULUS_TOKEN", "t")
    monkeypatch.setenv("ENVIO_REAL", "true")
    falso = MetaculusFalso(preguntas_ejemplo())
    main.ejecutar("test_questions", cliente=falso, llms=llms)
    [f] = list((tmp_path / "registro").glob("pronosticos_*.jsonl"))
    binaria, opciones, numerica = [
        json.loads(x) for x in f.read_text(encoding="utf-8").splitlines()
    ]
    assert binaria["sombra_pchip"] is None and opciones["sombra_pchip"] is None
    s = numerica["sombra_pchip"]
    assert s["estado"] == "ok"
    assert len(s["cdf_pchip"]) == len(s["cdf_enviada"]) == len(s["valores"]) == 201
    # lo enviado es la curva de rectas de siempre, no la sombra
    [envio] = [a for tipo, a in falso.envios if tipo == "numerica"]
    enviada = next(x for x in envio if isinstance(x, list) and len(x) == 201)
    assert enviada == pytest.approx(s["cdf_enviada"], abs=1e-6)
    assert enviada != pytest.approx(s["cdf_pchip"], abs=1e-6)


def test_si_la_sombra_falla_el_pronostico_real_sigue(monkeypatch, llms, tmp_path):
    def rota(*a, **k):
        raise RuntimeError("fallo simulado")

    monkeypatch.setattr(sombra, "sombra", rota)
    monkeypatch.setenv("METACULUS_TOKEN", "t")
    assert (
        main.ejecutar("test_questions", cliente=MetaculusFalso(preguntas_ejemplo()), llms=llms) == 0
    )
    [f] = list((tmp_path / "registro").glob("pronosticos_*.jsonl"))
    numerica = json.loads(f.read_text(encoding="utf-8").splitlines()[2])
    assert numerica["sombra_pchip"]["estado"] == "fallo"
    assert numerica["pronostico"]  # el pronóstico real salió igual
