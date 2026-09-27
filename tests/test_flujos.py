"""Las piezas de GitHub que usan los flujos van en versiones que funcionan con Node 24.

GitHub quitó Node 20 de sus máquinas el 23/09/2026: las piezas viejas avisaban y se ejecutaban
forzadas con Node 24. Se actualizaron el 27/09/2026; esta prueba evita volver atrás sin querer."""

from __future__ import annotations

import re
from pathlib import Path

FLUJOS = Path(__file__).resolve().parent.parent / ".github" / "workflows"
MINIMAS = {  # primera versión de cada pieza que se ejecuta con Node 24
    "actions/checkout": 5,
    "actions/setup-python": 6,
    "actions/setup-node": 5,
    "actions/upload-artifact": 6,
}


def test_piezas_de_github_sobre_node_24():
    vistas = set()
    for f in FLUJOS.glob("*.yaml"):
        for pieza, version in re.findall(r"uses:\s*([\w-]+/[\w-]+)@v(\d+)", f.read_text("utf-8")):
            assert pieza in MINIMAS, f"{f.name}: pieza nueva {pieza}; añadir su versión mínima"
            assert int(version) >= MINIMAS[pieza], f"{f.name}: {pieza}@v{version} es de Node 20"
            vistas.add(pieza)
    assert vistas == set(MINIMAS)
