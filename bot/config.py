"""Lectura de parámetros e interruptores.

Interruptores (variables de entorno; en GitHub se ponen en Settings → Secrets and variables → Actions):
- METACULUS_TOKEN (secreto): sin él, el bot termina limpio sin hacer nada.
- ENVIO_REAL (variable): solo con el valor exacto "true" se envían pronósticos. Por defecto: apagado.
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
    return m["con_clave_propia"] if hay("OPENROUTER_API_KEY") else m["proxy_metaculus"]
