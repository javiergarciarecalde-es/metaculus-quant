"""Lógica pura de agregación y límites (sin red, sin librerías externas).

Todo lo que decide cómo combinar varias pasadas del modelo vive aquí para poder
probarlo sin llamar a ninguna API.
"""

from __future__ import annotations

import math
import re
from statistics import median

# Los límites (nunca 0 % ni 100 %: con peer score logarítmico, un 0 % o 100 % equivocado es
# catastrófico) y el mínimo por opción viven en config/params.yaml (`pronostico.prob_min`,
# `pronostico.prob_max`, `pronostico.minimo_por_opcion`): aquí se reciben siempre de fuera.


def acotar(p: float, lo: float, hi: float) -> float:
    if p is None or math.isnan(p):
        raise ValueError("probabilidad inválida")
    return max(lo, min(hi, float(p)))


def logit(p: float) -> float:
    return math.log(p / (1 - p))


def sigmoide(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def extremizar(p: float, factor: float) -> float:
    """Extremiza en escala log-odds (factor 1.0 = sin cambio).

    Se aplica a la mediana de varias pasadas: la media de pronósticos independientes
    tiende a quedarse demasiado cerca del 50 %. El factor está en params (hoy 1.0: apagado).
    """
    if factor == 1.0:
        return p
    p = min(max(p, 1e-6), 1 - 1e-6)
    return sigmoide(logit(p) * factor)


def agregar_binaria(probs: list[float], factor_extremizar: float, lo: float, hi: float) -> float:
    """Mediana de las pasadas -> extremizar con cuidado -> acotar."""
    validas = [float(p) for p in probs if p is not None and 0 <= p <= 1]
    if not validas:
        raise ValueError("ninguna probabilidad válida")
    return acotar(extremizar(median(validas), factor_extremizar), lo, hi)


def agregar_opciones(
    listas: list[dict[str, float]], opciones: list[str], minimo: float
) -> dict[str, float]:
    """Mediana por opción, suelo mínimo por opción y renormalizado a 1."""
    if not listas:
        raise ValueError("sin pronósticos de opciones")
    res = {}
    for op in opciones:
        vals = [float(lista.get(op, 0.0)) for lista in listas]
        res[op] = median(vals)
    return normalizar_opciones(res, minimo)


def normalizar_opciones(probs: dict[str, float], minimo: float) -> dict[str, float]:
    total = sum(max(v, 0.0) for v in probs.values())
    n = len(probs)
    if total <= 0:
        return {k: 1 / n for k in probs}
    p = {k: max(v, 0.0) / total for k, v in probs.items()}
    # suelo: mezcla con uniforme lo justo para que ninguna opción quede bajo el mínimo
    peor = min(p.values())
    if peor < minimo and minimo * n < 1:
        w = (minimo - peor) / (1 / n - peor)
        p = {k: (1 - w) * v + w / n for k, v in p.items()}
    s = sum(p.values())
    return {k: v / s for k, v in p.items()}


def agregar_percentiles(listas: list[dict[float, float]]) -> dict[float, float]:
    """Mediana por percentil entre pasadas y forzado a orden creciente.

    Cada lista: {percentil(0-1): valor}. Solo se usan los percentiles comunes a todas.
    """
    if not listas:
        raise ValueError("sin percentiles")
    comunes = set(listas[0])
    for lista in listas[1:]:
        comunes &= set(lista)
    if not comunes:
        raise ValueError("percentiles sin coincidencias")
    res = {pc: median(lista[pc] for lista in listas) for pc in sorted(comunes)}
    return monotono(res)


def monotono(d: dict[float, float]) -> dict[float, float]:
    """Garantiza valores estrictamente crecientes con el percentil."""
    out, ultimo = {}, None
    for pc in sorted(d):
        v = float(d[pc])
        if ultimo is not None and v <= ultimo:
            v = ultimo + max(abs(ultimo) * 1e-6, 1e-9)
        out[pc] = v
        ultimo = v
    return out


# ---------------------- lectura de respuestas del modelo ----------------------
# Se lee primero con expresiones regulares (gratis). Solo si falla se usa el
# «parser» de forecasting-tools, que cuesta una llamada extra al modelo.

_RE_PROB = re.compile(r"probabilit(?:y|dad)\s*[:=]\s*([0-9]+(?:[.,][0-9]+)?)\s*%", re.I)
_RE_NUM = r"-?[0-9][0-9,]*(?:\.[0-9]+)?"
_RE_PCT = re.compile(r"percentile\s*([0-9]{1,2})\s*[:=]\s*(" + _RE_NUM + r")", re.I)


def leer_probabilidad(texto: str) -> float | None:
    m = _RE_PROB.findall(texto or "")
    if not m:
        return None
    v = float(m[-1].replace(",", ".")) / 100
    return v if 0 <= v <= 1 else None


def leer_percentiles(texto: str) -> dict[float, float] | None:
    m = _RE_PCT.findall(texto or "")
    if len(m) < 3:
        return None
    d = {}
    for pc, val in m:  # si se repite, vale el último
        d[int(pc) / 100] = float(val.replace(",", ""))
    return d


def leer_opciones(texto: str, opciones: list[str]) -> dict[str, float] | None:
    res = {}
    for op in opciones:
        pat = re.compile(
            r"(?:option[_ ]?)?" + re.escape(op) + r"\s*[:=]\s*([0-9]+(?:\.[0-9]+)?)\s*%?", re.I
        )
        m = pat.findall(texto or "")
        if not m:
            return None
        res[op] = float(m[-1])
    total = sum(res.values())
    if total <= 0:
        return None
    if total > 1.5:  # vienen en porcentaje
        res = {k: v / 100 for k, v in res.items()}
    return res
