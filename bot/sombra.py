"""Curva numérica suave (PCHIP) «en sombra»: se calcula y se guarda, NO se envía.

Mejora 3 de docs/ESTUDIO_BOTS.md; decisión del usuario del 27/09/2026 (~21:55, orden 26).

Qué cambia y qué no. Hoy la librería convierte los 6 percentiles de cada modelo (10, 20, 40, 60, 80
y 90) en una curva de 201 puntos **uniéndolos con rectas** (`NumericDistribution._get_cdf_at`), y
luego toma la mediana de las tres curvas. La sombra hace exactamente lo mismo, con los mismos
puntos (incluidos los que la librería añade en los extremos) y en la misma escala (la logarítmica
en las preguntas que la usan), pero los une con **PCHIP**: una curva suave que pasa por todos los
puntos y nunca baja (Fritsch y Carlson, 1980; la misma que `scipy.interpolate.PchipInterpolator`).
Nada más cambia: no se piden percentiles 1 % y 99 % (nadie lo ha medido y puede adelgazar las
colas justo donde están los desastres).

Solo se activará si nuestros propios datos lo confirman (ESTUDIO_BOTS, capa 1: ≥150 preguntas
resueltas y ganar en las dos mitades). Si algo falla aquí, el pronóstico real no se entera.
"""

from __future__ import annotations

import numpy as np
from forecasting_tools import NumericDistribution, Percentile


def _pendiente_extremo(h0: float, h1: float, d0: float, d1: float) -> float:
    """Pendiente en un extremo (fórmula de tres puntos, como scipy)."""
    m = ((2 * h0 + h1) * d0 - h0 * d1) / (h0 + h1)
    if np.sign(m) != np.sign(d0):
        return 0.0
    if np.sign(d0) != np.sign(d1) and abs(m) > abs(3 * d0):
        return 3 * d0
    return m


def pchip(xs: list[float], ys: list[float], puntos: list[float]) -> list[float]:
    """Interpolación PCHIP de (xs, ys) en `puntos`. `xs` estrictamente creciente; si `ys` nunca
    baja, el resultado tampoco. Fuera de [xs[0], xs[-1]] se queda en el valor del extremo."""
    x = np.asarray(xs, dtype=float)
    y = np.asarray(ys, dtype=float)
    if len(x) < 2 or np.any(np.diff(x) <= 0):
        raise ValueError("PCHIP necesita al menos 2 puntos con x estrictamente creciente")
    h = np.diff(x)
    delta = np.diff(y) / h
    n = len(x)
    d = np.zeros(n)
    if n == 2:
        d[:] = delta[0]
    else:
        for k in range(1, n - 1):
            if delta[k - 1] * delta[k] <= 0:
                d[k] = 0.0
            else:  # media armónica ponderada (Fritsch-Carlson)
                w1, w2 = 2 * h[k] + h[k - 1], h[k] + 2 * h[k - 1]
                d[k] = (w1 + w2) / (w1 / delta[k - 1] + w2 / delta[k])
        d[0] = _pendiente_extremo(h[0], h[1], delta[0], delta[1])
        d[-1] = _pendiente_extremo(h[-1], h[-2], delta[-1], delta[-2])
    t = np.clip(np.asarray(puntos, dtype=float), x[0], x[-1])
    k = np.clip(np.searchsorted(x, t, side="right") - 1, 0, n - 2)
    s = (t - x[k]) / h[k]
    h00, h10 = 2 * s**3 - 3 * s**2 + 1, s**3 - 2 * s**2 + s
    h01, h11 = -2 * s**3 + 3 * s**2, s**3 - s**2
    res = h00 * y[k] + h10 * h[k] * d[k] + h01 * y[k + 1] + h11 * h[k] * d[k + 1]
    return res.tolist()


def curva_pchip(dist: NumericDistribution) -> list[Percentile]:
    """La curva de 201 puntos de UN modelo, como `dist.get_cdf()` pero uniendo con PCHIP."""
    puntos = dist._add_explicit_upper_lower_bound_percentiles(dist.declared_percentiles)
    xs, ys = [], []
    for p in puntos:  # en la escala de la librería (0 = mínimo, 1 = máximo; log si toca)
        x = dist._nominal_location_to_cdf_location(p.value)
        if xs and x <= xs[-1]:
            continue  # la librería tampoco puede unir dos puntos en el mismo sitio
        xs.append(x)
        ys.append(p.percentile)
    tam = dist.cdf_size or 201
    lugares = [i / (tam - 1) for i in range(tam)]
    alturas = pchip(xs, ys, lugares)
    if dist.standardize_cdf:
        alturas = dist._standardize_cdf(alturas)
    valores = [dist._cdf_location_to_nominal_location(u) for u in lugares]
    return [Percentile(value=v, percentile=a) for v, a in zip(valores, alturas, strict=True)]


def sombra(predicciones: list[NumericDistribution], question) -> dict:
    """Lo mismo que hace la librería al juntar (mediana punto a punto y `from_question`), con las
    curvas PCHIP. Devuelve lo que se guarda en el registro, junto a la curva enviada."""
    curvas = [curva_pchip(p) for p in predicciones]
    valores = [p.value for p in curvas[0]]
    mediana = np.median(np.array([[p.percentile for p in c] for c in curvas]), axis=0).tolist()
    juntada = [Percentile(value=v, percentile=a) for v, a in zip(valores, mediana, strict=True)]
    final = NumericDistribution.from_question(juntada, question).get_cdf()  # valida como la real
    return {"cdf": [round(p.percentile, 6) for p in final]}
