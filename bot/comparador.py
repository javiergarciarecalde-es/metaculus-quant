"""Comparador: ¿qué forma de juntar a los 3 modelos habría puntuado mejor? Gratis: usa lo guardado.

Decisión del usuario (25/09/2026). Para cada pregunta resuelta se recalcula qué habría enviado el
bot con otra forma de juntar los pronósticos de sus 3 modelos (sin volver a preguntar a nadie) y
cuánto habría cambiado la puntuación de pares:

    cambio ≈ 100 · ln(prob. que la variante daba a lo que pasó / prob. que dimos de verdad)

Es la fórmula de Metaculus para la puntuación de pares puntual cuando solo cambia nuestro número
(el factor N/(N-1) es ~1 con muchos bots). Vale para sí/no y para opciones; las numéricas no entran
(haría falta la curva entera que se envió, no solo los percentiles).

Para no engañarnos (docs/ESTUDIO_BOTS.md, apartado 3):
- Solo 3 comparaciones se deciden de antemano (`marcador.comparador.preregistradas`); el resto
  sale como «exploratoria» y no sirve para decidir.
- Una variante solo «cumple la regla» si hay al menos `minimo_preguntas` resueltas, gana de media
  y gana también en las dos mitades (las preguntas más antiguas y las más recientes).
"""

from __future__ import annotations

import math
from statistics import mean, stdev

from . import agregacion as ag

ACTUAL = "mediana (la actual)"


def empresa(modelo: str | None) -> str:
    """«openrouter/openai/gpt-6-sol» -> «openai». El respaldo cuenta como su empresa."""
    trozos = (modelo or "?").split("/")
    return trozos[1] if trozos[0] == "openrouter" and len(trozos) > 2 else trozos[0]


def _odds_geometricas(ps: list[float]) -> float:
    ps = [min(max(p, 1e-6), 1 - 1e-6) for p in ps]
    x = mean(math.log(p / (1 - p)) for p in ps)
    return 1 / (1 + math.exp(-x))


def variantes_binaria(miembros: list[dict], lo: float, hi: float, alt: tuple) -> dict[str, float]:
    ps = [
        (empresa(m.get("modelo")), float(m["valor"]))
        for m in miembros
        if m.get("valor") is not None
    ]
    if len(ps) < 2:
        return {}
    vals = [p for _, p in ps]
    salida = {
        ACTUAL: ag.agregar_binaria(vals, 1.0, lo, hi),
        "media": ag.acotar(mean(vals), lo, hi),
        "media geométrica de odds": ag.acotar(_odds_geometricas(vals), lo, hi),
        f"límites {alt[0]:.0%}-{alt[1]:.0%}": ag.agregar_binaria(vals, 1.0, alt[0], alt[1]),
    }
    for e in sorted({e for e, _ in ps}):
        resto = [p for x, p in ps if x != e]
        solo = [p for x, p in ps if x == e]
        if resto:
            salida[f"sin {e}"] = ag.agregar_binaria(resto, 1.0, lo, hi)
        salida[f"solo {e}"] = ag.agregar_binaria(solo, 1.0, lo, hi)
    return salida


def variantes_opciones(miembros: list[dict], opciones: list[str], minimo: float) -> dict[str, dict]:
    listas = [
        (empresa(m.get("modelo")), m["valor"]) for m in miembros if isinstance(m.get("valor"), dict)
    ]
    if len(listas) < 2:
        return {}
    todas = [v for _, v in listas]
    salida = {
        ACTUAL: ag.agregar_opciones(todas, opciones, minimo),
        "media": ag.normalizar_opciones(
            {op: mean(float(v.get(op, 0.0)) for v in todas) for op in opciones}, minimo
        ),
    }
    for e in sorted({e for e, _ in listas}):
        resto = [v for x, v in listas if x != e]
        solo = [v for x, v in listas if x == e]
        if resto:
            salida[f"sin {e}"] = ag.agregar_opciones(resto, opciones, minimo)
        salida[f"solo {e}"] = ag.agregar_opciones(solo, opciones, minimo)
    return salida


def _prob_de_lo_que_paso(tipo: str, valor, resolucion) -> float | None:
    try:
        if tipo == "binary":
            p = float(valor)
            return p if resolucion == "yes" else 1 - p if resolucion == "no" else None
        if tipo == "multiple_choice" and isinstance(valor, dict):
            p = valor.get(str(resolucion))
            return float(p) if p is not None else None
    except (TypeError, ValueError):
        return None
    return None


def cambios_por_pregunta(fila: dict, resolucion, conf: dict) -> dict[str, float]:
    """Para una pregunta resuelta: variante -> cambio de puntuación respecto a lo que enviamos."""
    tipo = fila.get("tipo")
    real = _prob_de_lo_que_paso(tipo, fila.get("valor"), resolucion)
    if not real or real <= 0:
        return {}
    miembros = fila.get("miembros") or []
    if tipo == "binary":
        vs = variantes_binaria(miembros, conf["prob_min"], conf["prob_max"], conf["alternativos"])
    elif tipo == "multiple_choice" and isinstance(fila.get("valor"), dict):
        vs = variantes_opciones(miembros, list(fila["valor"]), conf["minimo_por_opcion"])
    else:
        return {}
    salida = {}
    for nombre, valor in vs.items():
        p = _prob_de_lo_que_paso(tipo, valor, resolucion)
        if p and p > 0:
            salida[nombre] = 100 * math.log(p / real)
    return salida


def resumir(por_pregunta: list[tuple[str, dict[str, float]]], conf: dict) -> list[dict]:
    """`por_pregunta` = [(fecha, {variante: cambio})], en cualquier orden."""
    ordenadas = sorted(por_pregunta, key=lambda x: x[0])
    mitad = len(ordenadas) // 2
    variantes = sorted({v for _, d in ordenadas for v in d})
    filas = []
    for v in variantes:
        todos = [d[v] for _, d in ordenadas if v in d]
        antiguas = [d[v] for _, d in ordenadas[:mitad] if v in d]
        recientes = [d[v] for _, d in ordenadas[mitad:] if v in d]
        media = mean(todos)
        margen = 1.96 * stdev(todos) / math.sqrt(len(todos)) if len(todos) > 1 else None
        prereg = v in conf["preregistradas"]
        cumple = (
            prereg
            and len(todos) >= conf["minimo_preguntas"]
            and media > 0
            and bool(antiguas)
            and bool(recientes)
            and mean(antiguas) > 0
            and mean(recientes) > 0
        )
        filas.append(
            {
                "variante": v,
                "preguntas": len(todos),
                "cambio_medio": round(media, 2),
                "margen_95": round(margen, 2) if margen is not None else None,
                "mitad_antigua": round(mean(antiguas), 2) if antiguas else None,
                "mitad_reciente": round(mean(recientes), 2) if recientes else None,
                "tipo": "decidida de antemano" if prereg else "exploratoria",
                "cumple_la_regla": cumple,
            }
        )
    return sorted(filas, key=lambda f: (f["tipo"] != "decidida de antemano", -f["cambio_medio"]))


def informe_md(filas: list[dict], conf: dict) -> list[str]:
    lineas = [
        "",
        "## ¿Qué forma de juntar a los 3 modelos habría ido mejor?",
        "",
        "Se recalcula, sin preguntar de nuevo a nadie, qué habríamos enviado con otra forma de",
        "juntar los pronósticos de los 3 modelos. «Cambio medio» = puntos de pares por pregunta",
        "que habríamos ganado (+) o perdido (-) frente a lo que enviamos. «Margen 95 %»: si el",
        "cambio medio es menor que el margen, la diferencia puede ser suerte. Solo las «decididas",
        "de antemano» sirven para decidir, y solo si **cumplen la regla**: al menos",
        f"{conf['minimo_preguntas']} preguntas resueltas, ganar de media y ganar en las dos",
        "mitades (preguntas antiguas y recientes). Preguntas numéricas: no entran.",
        "",
        "| Variante | Tipo | Preguntas | Cambio medio | Margen 95 % | Mitad antigua "
        "| Mitad reciente | ¿Cumple la regla? |",
        "|---|---|---|---|---|---|---|---|",
    ]
    if not filas:
        lineas.append("| — | — | 0 | — | — | — | — | — |")
    for f in filas:
        lineas.append(
            f"| {f['variante']} | {f['tipo']} | {f['preguntas']} | {f['cambio_medio']} | "
            f"{f['margen_95'] if f['margen_95'] is not None else '—'} | "
            f"{f['mitad_antigua'] if f['mitad_antigua'] is not None else '—'} | "
            f"{f['mitad_reciente'] if f['mitad_reciente'] is not None else '—'} | "
            f"{'sí' if f['cumple_la_regla'] else 'no'} |"
        )
    return lineas
