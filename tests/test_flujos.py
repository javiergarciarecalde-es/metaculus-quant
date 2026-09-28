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


def test_la_instalacion_aguanta_un_corte_de_pypi():
    """28/09/2026 (orden 27): pypi.org no contestaba a las máquinas de GitHub (esperas de 15 s
    agotadas en python-dateutil) y dos ejecuciones del bot salieron en rojo. Los flujos que van
    solos reintentan con más paciencia y, si aun así falla, otra vez al minuto."""
    for nombre in ("run_bot_on_tournament.yaml", "vigilancia.yaml", "marcador.yaml"):
        texto = (FLUJOS / nombre).read_text("utf-8")
        instalaciones = re.findall(r"run: (pip install .*-r requirements.*)", texto)
        assert instalaciones, nombre
        for orden in instalaciones:
            assert "--retries 10 --timeout 60" in orden and "|| (sleep 60 &&" in orden, nombre
