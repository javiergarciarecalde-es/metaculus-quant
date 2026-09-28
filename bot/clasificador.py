"""Clasificador de preguntas «en sombra» (decisión del usuario del 28/09/2026).

Idea del usuario: un primer agente que calibre cuánto esfuerzo merece cada pregunta y, según eso,
decida qué modelos y con cuánto razonamiento actúan. Nadie ha medido que un agente así acierte,
así que primero se hace **en sombra**: antes de investigar, un modelo barato
(`modelos.*.clasificador`, hoy Gemini 3.8 Flash) mira la pregunta y dice si es fácil, normal o
difícil, qué esfuerzo pediría y si merece investigación a fondo. **Se guarda en el registro y no
decide nada.**

Además se calcula una señal gratuita y objetiva: **cuánto discrepan los 3 modelos** en su
pronóstico (si uno dice 20 % y otro 70 %, la pregunta seguramente era difícil).

El marcador de cada lunes cruza las dos cosas con la puntuación de las preguntas resueltas
(`resumir`). Regla escrita ANTES de ver resultados (docs/HALLAZGOS.md, 28/09/2026): el clasificador
solo pasa a decidir si las «difíciles» puntúan claramente peor que las «fáciles» (diferencia mayor
que su margen del 95 %) con al menos 30 preguntas resueltas en cada grupo.
"""

from __future__ import annotations

import json
import math
import re
from statistics import mean, stdev

DIFICULTAD = {"easy": "facil", "medium": "normal", "hard": "dificil"}
ESFUERZO = {"low": "bajo", "medium": "medio", "high": "alto"}


def prompt(
    tipo: str, pregunta: str, criterios: str, letra_pequena: str, max_caracteres: int
) -> str:
    texto = f"{pregunta}\n\nResolution criteria: {criterios}\n\nFine print: {letra_pequena}"
    return (
        "You triage questions for an automated forecasting bot BEFORE it researches them. Do NOT "
        "forecast and do NOT give probabilities. Judge only how hard it will be to forecast this "
        "question well:\n"
        "- easy: the outcome is almost settled by the status quo, a schedule, or a mechanical/"
        "official figure that is easy to look up;\n"
        "- medium: normal uncertainty, a standard news search should be enough;\n"
        "- hard: depends on genuinely uncertain future events, ambiguous or technical resolution "
        "criteria, specialised or very fresh data, or a wide numeric range.\n"
        "Reply ONLY with JSON, no other text: "
        '{"difficulty": "easy|medium|hard", "reasoning_effort": "low|medium|high", '
        '"deep_research": true|false, "reason": "<one short sentence>"}\n\n'
        f"Question type: {tipo}\n\n{texto[:max_caracteres]}"
    )


def leer(texto: str) -> dict:
    """La respuesta del modelo -> {"estado": "ok", "dificultad", "esfuerzo", "a_fondo", "motivo"}
    o {"estado": "ilegible"}."""
    m = re.search(r"\{.*\}", texto or "", re.DOTALL)
    if not m:
        return {"estado": "ilegible"}
    try:
        datos = json.loads(m.group(0))
    except json.JSONDecodeError:
        return {"estado": "ilegible"}
    dif = DIFICULTAD.get(str(datos.get("difficulty", "")).lower())
    esf = ESFUERZO.get(str(datos.get("reasoning_effort", "")).lower())
    a_fondo = datos.get("deep_research")
    if dif is None or esf is None or not isinstance(a_fondo, bool):
        return {"estado": "ilegible"}
    return {
        "estado": "ok",
        "dificultad": dif,
        "esfuerzo": esf,
        "a_fondo": a_fondo,
        "motivo": str(datos.get("reason", ""))[:300],
    }


def _centro_y_ancho(valor: dict) -> tuple[float, float] | None:
    """Numéricas: centro (media de los percentiles 40 y 60) y ancho (90 menos 10)."""
    try:
        v = {round(float(k), 2): float(x) for k, x in valor.items()}
        return (v[0.4] + v[0.6]) / 2, v[0.9] - v[0.1]
    except (KeyError, TypeError, ValueError, AttributeError):
        return None


def discrepancia(fila: dict) -> float | None:
    """Cuánto discrepan los modelos de una pregunta (0 = igual). Sí/no: diferencia entre la
    probabilidad más alta y la más baja. Opciones: la mayor de esas diferencias entre opciones.
    Numéricas: distancia entre el centro más alto y el más bajo, dividida por el ancho medio."""
    valores = [m.get("valor") for m in fila.get("miembros") or [] if m.get("valor") is not None]
    if len(valores) < 2:
        return None
    tipo = fila.get("tipo")
    try:
        if tipo == "binary":
            ps = [float(v) for v in valores]
            return round(max(ps) - min(ps), 4)
        if tipo == "multiple_choice":
            opciones = set().union(*(v.keys() for v in valores))
            return round(
                max(
                    max(float(v.get(o, 0)) for v in valores)
                    - min(float(v.get(o, 0)) for v in valores)
                    for o in opciones
                ),
                4,
            )
        if tipo in ("numeric", "discrete"):
            pares = [c for v in valores if (c := _centro_y_ancho(v)) is not None]
            anchos = [a for _, a in pares if a > 0]
            if len(pares) < 2 or not anchos:
                return None
            centros = [c for c, _ in pares]
            return round((max(centros) - min(centros)) / mean(anchos), 4)
    except (TypeError, ValueError, AttributeError):
        return None
    return None


def _media_y_margen(xs: list[float]) -> tuple[float | None, float | None]:
    if not xs:
        return None, None
    margen = 1.96 * stdev(xs) / math.sqrt(len(xs)) if len(xs) > 1 else None
    return round(mean(xs), 2), (round(margen, 2) if margen is not None else None)


def resumir(filas: list[dict], resueltas: dict, clave) -> dict:
    """Por etiqueta del clasificador: cuántas preguntas, discrepancia media de los modelos y, en
    las resueltas, puntuación de pares media (con su margen del 95 %)."""
    grupos: dict[str, dict] = {}
    for f in filas:
        c = f.get("clasificador") or {}
        etiqueta = c.get("dificultad") if c.get("estado") == "ok" else "sin_clasificar"
        g = grupos.setdefault(etiqueta, {"n": 0, "discrepancias": [], "puntos": []})
        g["n"] += 1
        d = discrepancia(f)
        if d is not None:
            g["discrepancias"].append(d)
        info = resueltas.get(str(clave(f))) or {}
        if info.get("estado") == "resolved" and isinstance(info.get("spot_peer"), (int, float)):
            g["puntos"].append(float(info["spot_peer"]))
    salida = {}
    for etiqueta in ("facil", "normal", "dificil", "sin_clasificar"):
        g = grupos.get(etiqueta)
        if not g:
            continue
        media, margen = _media_y_margen(g["puntos"])
        salida[etiqueta] = {
            "preguntas": g["n"],
            "discrepancia_media": round(mean(g["discrepancias"]), 3)
            if g["discrepancias"]
            else None,
            "resueltas": len(g["puntos"]),
            "puntos_media": media,
            "puntos_margen_95": margen,
        }
    return salida


def informe_md(r: dict) -> list[str]:
    lineas = [
        "",
        "## Clasificador en sombra (¿sabe qué preguntas son difíciles?)",
        "",
        "Antes de investigar, un modelo barato dice si cada pregunta es fácil, normal o difícil. "
        "**No decide nada todavía**: aquí se mira si acierta. Si acierta, las «difíciles» deberían "
        "tener más discrepancia entre los 3 modelos y peor puntuación de pares. Solo pasará a "
        "decidir si las difíciles puntúan claramente peor que las fáciles (más que el margen) con "
        "al menos 30 resueltas en cada grupo.",
        "",
        "| Etiqueta | Preguntas | Discrepancia media de los modelos | Resueltas | Puntos de pares "
        "(media) | Margen 95 % |",
        "|---|---|---|---|---|---|",
    ]
    if not r:
        lineas.append("| — | 0 | — | 0 | — | — |")
    for etiqueta, g in r.items():
        lineas.append(
            f"| {etiqueta} | {g['preguntas']} | {_o_raya(g['discrepancia_media'])} | "
            f"{g['resueltas']} | {_o_raya(g['puntos_media'])} | {_o_raya(g['puntos_margen_95'])} |"
        )
    return lineas


def _o_raya(x) -> str:
    return "—" if x is None else str(x)
