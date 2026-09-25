"""Los parámetros del bot, leídos de config/params.yaml.

**De dónde sale.** Copia de `cripto-quant/src/params.py` (versión d4cbd77, 2026-09-25), que a su
vez viene de betfair-quant y quiniela-quant. Si allí se corrige algo, se trae. Único cambio: `p()`
acepta además el árbol de parámetros ya cargado (`arbol`), porque el bot recibe los parámetros
como dato en cada función (sin estado global) y las pruebas le pasan una copia retocada.

Existe para que no haya ni un número discutible escondido en el código. La norma es que todo lo
que sea una elección —un modelo, un tope, un límite— viva en un solo fichero, donde se pueda ver
junto, cambiar sin tocar programas y dejar registro (CHANGELOG.md) de por qué cambió.

Uso:
    from bot import params as ajustes
    ajustes.p("pronostico.prob_min")                # 0.02, leído del fichero
    ajustes.p("pronostico.prob_min", parametros)    # el mismo, de un árbol ya cargado

Si el parámetro no existe, falla en el acto y dice cuál falta: un parámetro mal escrito que
devolviera un valor por defecto silencioso cambiaría el comportamiento del bot sin que nadie se
enterara.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

RAIZ = Path(__file__).resolve().parent.parent
FICHERO = RAIZ / "config" / "params.yaml"


class ParametroDesconocidoError(KeyError):
    """Se ha pedido un parámetro que no está en config/params.yaml."""


@lru_cache(maxsize=1)
def todos() -> dict[str, Any]:
    """Lee el fichero una sola vez por ejecución. No se modifica: quien quiera retocarlo, copia."""
    if not FICHERO.exists():
        raise FileNotFoundError(f"falta {FICHERO}: el bot no tiene parámetros que usar")
    contenido = yaml.safe_load(FICHERO.read_text(encoding="utf-8"))
    if not isinstance(contenido, dict):
        raise TypeError(f"{FICHERO} no contiene un diccionario de parámetros")
    return contenido


def p(ruta: str, arbol: dict[str, Any] | None = None) -> Any:
    """Devuelve un parámetro por su camino, como 'pronostico.prob_min'.

    Sin `arbol`, lo lee de config/params.yaml; con `arbol`, de esos parámetros ya cargados.
    """
    actual: Any = todos() if arbol is None else arbol
    recorrido: list[str] = []
    for tramo in ruta.split("."):
        recorrido.append(tramo)
        if not isinstance(actual, dict) or tramo not in actual:
            raise ParametroDesconocidoError(
                f"no existe el parámetro '{ruta}' (falla en '{'.'.join(recorrido)}'). "
                f"Los parámetros viven en {FICHERO.relative_to(RAIZ).as_posix()}."
            )
        actual = actual[tramo]
    return actual
