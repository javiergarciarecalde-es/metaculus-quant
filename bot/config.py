"""Lectura de parámetros e interruptores.

Interruptores (variables de entorno; en GitHub se ponen en
Settings → Secrets and variables → Actions):
- METACULUS_TOKEN (secreto): sin él, el bot termina limpio sin hacer nada.
- ENVIO_REAL (variable): solo con el valor exacto "true" se envían pronósticos. Si no: apagado.
- OPENROUTER_API_KEY (secreto, opcional): si está, se usan modelos con clave propia.
"""

from __future__ import annotations

import copy
import os

from bot import params as ajustes

RAIZ = ajustes.RAIZ

_FALSOS = {"", "REPLACE_ME", "1234567890", "your-token-here", "your-api-key-here"}


def cargar_params() -> dict:
    """Copia de los parámetros de config/params.yaml (quien la retoque no toca el original)."""
    return copy.deepcopy(ajustes.todos())


def hay(nombre: str) -> bool:
    v = (os.getenv(nombre) or "").strip()
    return v not in _FALSOS


def envio_real_encendido() -> bool:
    return (os.getenv("ENVIO_REAL") or "").strip().lower() == "true"


def es_ejecucion_programada() -> bool:
    """True si GitHub Actions lanzó esto por el reloj (cada 20 min), no a mano."""
    return os.getenv("GITHUB_EVENT_NAME") == "schedule"


def bloque_modelos(params: dict) -> dict:
    if hay("OPENROUTER_API_KEY"):
        return ajustes.p("modelos.openrouter", params)
    return ajustes.p("modelos.proxy_metaculus", params)


MODOS = ("tres_empresas", "un_modelo")
CAMPOS_PUESTO = ("nombre", "esfuerzo", "respaldo")  # esfuerzo y respaldo pueden ser null


def puesto(x: dict) -> dict:
    """Un puesto de pronóstico con sus tres campos; si falta alguno, error claro (sin adivinar)."""
    faltan = [c for c in CAMPOS_PUESTO if c not in x]
    if faltan:
        raise ajustes.ParametroDesconocidoError(
            f"al puesto de pronóstico {x!r} le falta {faltan} en config/params.yaml"
        )
    return {c: x[c] for c in CAMPOS_PUESTO}


def lista_pronosticadores(params: dict) -> list[dict]:
    """Puestos de pronóstico según `pronostico.modo`: [{nombre, esfuerzo, respaldo}, ...]."""
    modo = ajustes.p("pronostico.modo", params)
    if modo not in MODOS:
        raise ValueError(f"pronostico.modo inválido: {modo!r}; usa uno de {MODOS}")
    m = bloque_modelos(params)
    if modo == "un_modelo":
        return [puesto(m["un_modelo"]) for _ in range(len(m["pronostico"]))]
    return [puesto(x) for x in m["pronostico"]]
