"""Los documentos que son la ventana del usuario al proyecto no se quedan atrás.

Un documento que crece sin control no da ningún error: simplemente deja de servir, y ocupa
contexto en cada sesión. Los topes se leen de la tabla de CLAUDE.md («Límites de tamaño de los
documentos») en vez de copiarlos aquí, porque un tope escrito en dos sitios deja de ser un tope en
cuanto uno de los dos cambia.

**De dónde sale.** Copia de `cripto-quant/tests/test_documentacion.py` (versión d4cbd77,
2026-09-25), con la forma de la tabla de quiniela-quant. Cambios: aquí la tabla incluye
HALLAZGOS.md, y no se comprueban los apartados de ESTADO (este proyecto usa otros títulos).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
RUTAS = {
    "CLAUDE.md": RAIZ / "CLAUDE.md",
    "ESTADO.md": RAIZ / "docs" / "ESTADO.md",
    "FUENTES.md": RAIZ / "docs" / "FUENTES.md",
    "HALLAZGOS.md": RAIZ / "docs" / "HALLAZGOS.md",
}
FILA_DE_TOPE = re.compile(
    r"^\|\s*`(?P<fichero>[A-Z]+\.md)`\s*\|\s*~(?P<tope>[\d.]+)\s*(?P<unidad>líneas|palabras)",
    re.M,
)


def _topes() -> dict[str, tuple[int, str]]:
    texto = RUTAS["CLAUDE.md"].read_text(encoding="utf-8")
    return {
        m["fichero"]: (int(m["tope"].replace(".", "")), m["unidad"])
        for m in FILA_DE_TOPE.finditer(texto)
    }


def _cuanto_mide(ruta: Path, unidad: str) -> int:
    texto = ruta.read_text(encoding="utf-8")
    return len(texto.split()) if unidad == "palabras" else len(texto.splitlines())


def test_la_tabla_de_topes_se_puede_leer():
    """Si la tabla cambia de forma, la prueba de abajo dejaría de comprobar nada."""
    assert set(_topes()) == set(RUTAS), "la tabla de límites de CLAUDE.md ha cambiado de forma"


@pytest.mark.parametrize("fichero", sorted(RUTAS))
def test_cada_documento_cabe_en_su_tope(fichero: str):
    tope, unidad = _topes()[fichero]
    medida = _cuanto_mide(RUTAS[fichero], unidad)
    assert medida <= tope, (
        f"{fichero} va por {medida} {unidad} de un tope de {tope}. No es un fallo del código: "
        "hay que recortarlo (el relato va a HALLAZGOS.md; en HALLAZGOS, lo viejo a docs/archivo/), "
        "o subir el tope en la tabla de CLAUDE.md con fecha y motivo y decírselo al usuario "
        "(permiso permanente, comunes §7)."
    )
