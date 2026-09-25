"""Investigación ampliada con agentes (APAGADA por defecto: investigacion.modo = basica).

Un «director» elige hasta N datos clave y varios «buscadores» los comprueban a la vez.
Lo encontrado se AÑADE al final del informe base, que nunca se reescribe ni resume: así un
error del director no sustituye a la información buena (los peores fallos de nostreambot
vinieron de un dato erróneo que se creyeron todos los modelos).
Cualquier fallo o falta de tiempo -> se devuelve el informe base intacto.
"""

from __future__ import annotations

import asyncio
import json
import logging
import re

logger = logging.getLogger(__name__)

CABECERA = "\n\n## Datos clave comprobados (añadido; puede contener errores)\n"


def _prompt_director(pregunta: str, criterios: str, informe: str, n: int) -> str:
    return (
        "You direct research for a forecaster. Given the question, its resolution criteria and the "
        f"current research report, choose at most {n} KEY facts whose verification would most "
        "change the forecast. One of them MUST be: "
        "what the resolution source currently says/shows. "
        'Answer ONLY with JSON: [{"dato": "...", "busqueda": "search query"}]\n\n'
        f"Question: {pregunta}\n\nResolution criteria: {criterios}\n\nReport:\n{informe[:6000]}"
    )


def leer_datos_clave(texto: str, n: int) -> list[dict]:
    m = re.search(r"\[.*\]", texto or "", re.S)
    if not m:
        return []
    try:
        datos = json.loads(m.group(0))
    except json.JSONDecodeError:
        return []
    return [d for d in datos if isinstance(d, dict) and d.get("busqueda")][:n]


async def _comprobar(buscador, dato: dict) -> str:
    prompt = (
        "Find the most recent reliable information on the following. Give the date of each fact "
        f"and cite the source URL. Be brief.\n\nFact to verify: {dato.get('dato', '')}\n"
        f"Search: {dato['busqueda']}"
    )
    return await buscador.invoke(prompt)


async def ampliar(
    informe_base: str,
    pregunta: str,
    criterios: str,
    director,
    buscador,
    n: int = 2,
    tope_segundos: float = 240,
) -> str:
    async def _todo() -> str:
        datos = leer_datos_clave(
            await director.invoke(_prompt_director(pregunta, criterios, informe_base, n)), n
        )
        if not datos:
            return informe_base
        res = await asyncio.gather(
            *[_comprobar(buscador, d) for d in datos], return_exceptions=True
        )
        partes = [
            f"### {d.get('dato', d['busqueda'])}\n{r}"
            for d, r in zip(datos, res, strict=True)
            if isinstance(r, str) and r.strip()
        ]
        return informe_base + CABECERA + "\n\n".join(partes) if partes else informe_base

    try:
        return await asyncio.wait_for(_todo(), timeout=tope_segundos)
    except Exception as e:  # incluye tiempo agotado: se sigue con el informe base
        logger.warning(f"Investigación ampliada descartada: {e!r}")
        return informe_base
