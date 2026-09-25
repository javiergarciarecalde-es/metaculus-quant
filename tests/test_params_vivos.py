"""Todo parámetro del YAML lo lee alguien, o está declarado como pendiente.

Un parámetro que nadie lee no da ningún error: se queda en el fichero aparentando que gobierna
algo. Esta prueba lo caza. Los de piezas que aún no existen se declaran aquí con la pieza que los
usará, **y esa lista solo puede encoger**: cuando la pieza llega y lo lee, su línea se borra.

**De dónde sale.** Copia de `cripto-quant/tests/test_params_vivos.py` (versión d4cbd77,
2026-09-25), idea de betfair-quant. Cambios: aquí el código vive en `main.py` y `bot/` (estructura
de la plantilla oficial de Metaculus) y hay un apartado para lo que no es un ajuste (la puerta).
"""

from __future__ import annotations

from pathlib import Path

from bot import params

RAIZ = Path(__file__).resolve().parent.parent

# Parámetro -> pieza que lo leerá, para los que aún no lee nadie. Solo encoge.
PENDIENTES: dict[str, str] = {}

# Lo que está en el YAML sin ser un ajuste que lea el bot, con el porqué.
NO_SON_AJUSTES: dict[str, str] = {
    "puerta_fase0": "copia literal de la puerta de la fase 0 (CLAUDE.md); la comprueba test_bot",
}


def _hojas(arbol: dict, prefijo: str = "") -> list[str]:
    rutas = []
    for clave, valor in arbol.items():
        ruta = f"{prefijo}{clave}"
        rutas.extend(_hojas(valor, f"{ruta}.") if isinstance(valor, dict) else [ruta])
    return rutas


def _codigo() -> str:
    ficheros = [RAIZ / "main.py", *sorted((RAIZ / "bot").glob("*.py"))]
    return "\n".join(f.read_text(encoding="utf-8") for f in ficheros)


def _se_lee(ruta: str, codigo: str) -> bool:
    """Un parámetro vive si alguien lo pide a él o a la tabla entera en la que está."""
    tramos = ruta.split(".")
    return any(f'"{".".join(tramos[:n])}"' in codigo for n in range(2, len(tramos) + 1))


def _es_ajuste(ruta: str) -> bool:
    return ruta.split(".")[0] not in NO_SON_AJUSTES


def test_todo_parametro_lo_lee_alguien_o_esta_pendiente():
    codigo = _codigo()
    huerfanos = [
        r
        for r in _hojas(params.todos())
        if _es_ajuste(r) and not _se_lee(r, codigo) and r not in PENDIENTES
    ]
    assert not huerfanos, f"parámetros que nadie lee ni están declarados pendientes: {huerfanos}"


def test_la_lista_de_pendientes_solo_encoge():
    codigo = _codigo()
    ya_leidos = [r for r in PENDIENTES if _se_lee(r, codigo)]
    assert not ya_leidos, f"ya se leen; bórralos de PENDIENTES: {ya_leidos}"
    inexistentes = [r for r in PENDIENTES if r not in _hojas(params.todos())]
    assert not inexistentes, f"pendientes que no existen en el YAML: {inexistentes}"


def test_lo_que_no_es_ajuste_existe():
    assert set(NO_SON_AJUSTES) <= set(params.todos())
