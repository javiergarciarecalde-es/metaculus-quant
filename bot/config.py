"""Lectura de parámetros e interruptores.

Interruptores (variables de entorno; en GitHub se ponen en
Settings → Secrets and variables → Actions):
- METACULUS_TOKEN (secreto): sin él, el bot termina limpio sin hacer nada.
- ENVIO_REAL (variable): solo con el valor exacto "true" se envían pronósticos. Si no: apagado.
- OPENROUTER_API_KEY (secreto, opcional): si está, se usan modelos con clave propia.
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
PARAMS = RAIZ / "config" / "params.yaml"

_FALSOS = {"", "REPLACE_ME", "1234567890", "your-token-here", "your-api-key-here"}


def cargar_params(ruta: Path = PARAMS) -> dict:
    with open(ruta, encoding="utf-8") as f:
        return yaml.safe_load(f)


def hay(nombre: str) -> bool:
    v = (os.getenv(nombre) or "").strip()
    return v not in _FALSOS


def envio_real_encendido() -> bool:
    return (os.getenv("ENVIO_REAL") or "").strip().lower() == "true"


def es_ejecucion_programada() -> bool:
    """True si GitHub Actions lanzó esto por el reloj (cada 20 min), no a mano."""
    return os.getenv("GITHUB_EVENT_NAME") == "schedule"


def bloque_modelos(params: dict) -> dict:
    m = params["modelos"]
    return m["openrouter"] if hay("OPENROUTER_API_KEY") else m["proxy_metaculus"]


MODOS = ("tres_empresas", "un_modelo")


def lista_pronosticadores(params: dict) -> list[dict]:
    """Puestos de pronóstico según `pronostico.modo`: [{nombre, esfuerzo, respaldo}, ...]."""
    modo = params["pronostico"].get("modo", "tres_empresas")
    if modo not in MODOS:
        raise ValueError(f"pronostico.modo inválido: {modo!r}; usa uno de {MODOS}")
    m = bloque_modelos(params)
    if modo == "un_modelo":
        return [dict(m["un_modelo"]) for _ in range(len(m["pronostico"]))]
    return [dict(x) for x in m["pronostico"]]
