"""Registro de cada pronóstico (una línea JSON por pregunta) para medir la puerta después."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from .config import RAIZ

CARPETA = RAIZ / "registro"


def resumir(texto: str, n: int) -> str:
    texto = " ".join((texto or "").split())
    return texto if len(texto) <= n else texto[: n - 1] + "…"


def anotar(entrada: dict, carpeta: Path | None = None, nombre: str = "pronosticos") -> Path:
    """`nombre`: «pronosticos» (una línea por pregunta) o «presupuesto» (consultas de la clave)."""
    carpeta = carpeta or CARPETA
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{nombre}_{datetime.now(UTC):%Y-%m}.jsonl"
    entrada = {"cuando_utc": datetime.now(UTC).isoformat(timespec="seconds"), **entrada}
    with open(ruta, "a", encoding="utf-8") as f:
        f.write(json.dumps(entrada, ensure_ascii=False, default=str) + "\n")
    return ruta
