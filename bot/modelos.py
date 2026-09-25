"""Comprueba que los modelos de `config/params.yaml` existen en OpenRouter.

La lista de modelos de OpenRouter es pública (no hace falta clave ni gasta créditos).
Si un modelo desaparece, el bot no daría error rojo: pronosticaría peor o sin noticias.
Por eso se comprueba al empezar cada ejecución y se avisa en amarillo.

Uso: python -m bot.modelos
"""

from __future__ import annotations

import sys

import requests

from bot import config as cfg

URL_MODELOS = "https://openrouter.ai/api/v1/models"


def nombres_openrouter(params: dict) -> list[str]:
    """Modelos del bloque «openrouter», sin el prefijo `openrouter/` ni sufijos como `:online`."""
    m = params["modelos"]["openrouter"]
    nombres = [m["investigacion"], m["lector"], m.get("director"), m.get("buscador")]
    for x in m["pronostico"] + [m.get("un_modelo") or {}]:
        nombres += [x.get("nombre"), x.get("respaldo")]
    limpios = [n.removeprefix("openrouter/").split(":")[0] for n in nombres if n]
    return list(dict.fromkeys(limpios))  # sin repetidos, en orden


def faltan(params: dict, disponibles: set[str]) -> list[str]:
    return [n for n in nombres_openrouter(params) if n not in disponibles]


def main() -> int:
    params = cfg.cargar_params()
    try:
        r = requests.get(URL_MODELOS, timeout=30)
        r.raise_for_status()
        disponibles = {x["id"] for x in r.json()["data"]}
    except Exception as e:  # sin red no se bloquea el bot: solo se avisa
        print(f"::notice::No se pudo leer la lista de modelos de OpenRouter: {e}")
        return 0
    perdidos = faltan(params, disponibles)
    if perdidos:
        print(
            f"::warning::Modelos que ya NO existen en OpenRouter: {', '.join(perdidos)}. "
            "Hay que cambiarlos en config/params.yaml."
        )
    else:
        print(f"Modelos comprobados en OpenRouter: {', '.join(nombres_openrouter(params))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
