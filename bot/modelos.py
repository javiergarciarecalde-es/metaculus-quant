"""Comprueba que los modelos de `config/params.yaml` existen en OpenRouter.

La lista de modelos de OpenRouter es pública (no hace falta clave ni gasta créditos).
Si un modelo desaparece, el bot no daría error rojo: pronosticaría peor o sin noticias.
Por eso se comprueba al empezar cada ejecución y se avisa en amarillo.

Además (28/09/2026, pedido por el usuario): `--clave` pregunta a OpenRouter qué modelos deja
usar la clave de créditos (`GET /api/v1/models/user`: la lista filtrada por las preferencias,
privacidad y restricciones de la cuenta; gratis, no genera nada). Se lanza a mano con el flujo
`modelos_clave.yaml`. Solo imprime nombres de modelos y empresas, nunca la clave.

Uso: python -m bot.modelos [--clave]
"""

from __future__ import annotations

import os
import sys

import requests

from bot import config as cfg
from bot import params as ajustes

URL_MODELOS = "https://openrouter.ai/api/v1/models"
URL_MODELOS_CLAVE = "https://openrouter.ai/api/v1/models/user"


def nombres_openrouter(params: dict) -> list[str]:
    """Modelos del bloque «openrouter», sin el prefijo `openrouter/` ni sufijos como `:online`."""
    m = ajustes.p("modelos.openrouter", params)
    nombres = [m["investigacion"], m["lector"], m["director"], m["buscador"]]
    for x in [*m["pronostico"], m["un_modelo"]]:
        puesto = cfg.puesto(x)
        nombres += [puesto["nombre"], puesto["respaldo"]]
    limpios = [n.removeprefix("openrouter/").split(":")[0] for n in nombres if n]
    return list(dict.fromkeys(limpios))  # sin repetidos, en orden


def faltan(params: dict, disponibles: set[str]) -> list[str]:
    return [n for n in nombres_openrouter(params) if n not in disponibles]


def ids_de(respuesta) -> set[str]:
    """Los nombres de modelo de una respuesta de OpenRouter ({"data": [{"id": ...}]})."""
    if not isinstance(respuesta, dict) or not isinstance(respuesta.get("data"), list):
        raise TypeError("la respuesta de OpenRouter no trae «data»")
    ids = {x.get("id") for x in respuesta["data"] if isinstance(x, dict)}
    if None in ids or not ids:
        raise ValueError("la respuesta de OpenRouter trae modelos sin «id»")
    return ids


def por_empresa(ids: set[str]) -> dict[str, list[str]]:
    """{"openai": [...], "deepseek": [...]} a partir de «empresa/modelo»."""
    res: dict[str, list[str]] = {}
    for i in sorted(ids):
        res.setdefault(i.split("/")[0], []).append(i)
    return res


def informe_clave(permitidos: set[str], publicos: set[str], params: dict) -> list[str]:
    """Texto en llano: qué empresas deja usar la clave y si están nuestros modelos."""
    empresas = por_empresa(permitidos)
    lineas = [
        f"La clave deja usar {len(permitidos)} modelos de {len(empresas)} empresas "
        f"(la lista pública tiene {len(publicos)}).",
        "Por empresa: " + ", ".join(f"{e} ({len(v)})" for e, v in sorted(empresas.items())),
    ]
    if permitidos >= publicos:
        lineas.append(
            "OJO: la clave no filtra nada (misma lista que la pública). Eso NO prueba que se "
            "puedan pagar otras empresas con los créditos: la clave gasta con las cuentas de "
            "Metaculus en cada empresa («byok») y eso no sale en esta lista."
        )
    fuera = faltan(params, permitidos)
    lineas.append(
        "Nuestros modelos: " + ("todos permitidos." if not fuera else f"NO permitidos: {fuera}")
    )
    otras = {e: v for e, v in empresas.items() if e not in ("openai", "anthropic", "google")}
    for e, v in sorted(otras.items()):
        lineas.append(f"  {e}: {', '.join(v[:15])}{' …' if len(v) > 15 else ''}")
    return lineas


def precios(publica: dict) -> dict[str, tuple[float, float]]:
    """{modelo: ($ por millón de tokens de entrada, de salida)} de la lista pública."""
    res = {}
    for x in publica.get("data") or []:
        try:
            p = x["pricing"]
            res[x["id"]] = (float(p["prompt"]) * 1e6, float(p["completion"]) * 1e6)
        except (KeyError, TypeError, ValueError):
            continue
    return res


def lista_con_precios(permitidos: set[str], tarifa: dict, empresas: tuple[str, ...]) -> list[str]:
    """Modelos permitidos de esas empresas con su precio (para elegir modelo con datos)."""
    lineas = []
    for i in sorted(x for x in permitidos if x.split("/")[0] in empresas):
        entrada, salida = tarifa.get(i, (None, None))
        precio = "precio desconocido" if entrada is None else f"{entrada:g} $ / {salida:g} $"
        lineas.append(f"  {i}: {precio} por millón de tokens (entrada / salida)")
    return lineas


def listado_completo(permitidos: set[str], publicos: set[str]) -> list[str]:
    """Todos los modelos (públicos y los de la clave), por empresa; «[CLAVE]» = la clave lo deja
    usar (28/09/2026: el usuario pidió la lista en bruto de todas las empresas)."""
    lineas = []
    for empresa, ids in sorted(por_empresa(permitidos | publicos).items()):
        n = sum(i in permitidos for i in ids)
        lineas.append(f"== {empresa}: {len(ids)} modelos ({n} permitidos por la clave)")
        lineas += [f"  {i}{'  [CLAVE]' if i in permitidos else ''}" for i in ids]
    return lineas


def consultar_clave(params: dict, get=requests.get) -> int:
    """Pregunta a OpenRouter qué modelos deja usar la clave (gratis). Solo lee."""
    if not cfg.hay("OPENROUTER_API_KEY"):
        print("::notice::Falta OPENROUTER_API_KEY: no hay clave que consultar.")
        return 0
    espera = float(ajustes.p("red.tiempo_espera_segundos", params))
    cab = {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY'].strip()}"}
    r = get(URL_MODELOS_CLAVE, headers=cab, timeout=espera)
    if r.status_code != 200:  # sin el texto de la respuesta: podría repetir algo de la cuenta
        print(f"::error::OpenRouter no contestó a la consulta de la clave (HTTP {r.status_code}).")
        return 1
    permitidos = ids_de(r.json())
    publica = get(URL_MODELOS, timeout=espera)
    publica.raise_for_status()
    datos = publica.json()
    for linea in informe_clave(permitidos, ids_de(datos), params):
        print(linea)
    print("LISTADO COMPLETO (todas las empresas):")
    for linea in listado_completo(permitidos, ids_de(datos)):
        print(linea)
    print("Modelos de Google permitidos (28/09/2026: el usuario propone Gemini Flash 3.8):")
    for linea in lista_con_precios(permitidos, precios(datos), ("google",)):
        print(linea)
    print("Precio de los modelos que usa hoy el bot:")
    nuestros = {f"{n}" for n in nombres_openrouter(params)}
    for linea in lista_con_precios(
        nuestros & permitidos, precios(datos), ("openai", "anthropic", "google")
    ):
        print(linea)
    return 0


def main(argv=None) -> int:
    params = cfg.cargar_params()
    if "--clave" in (sys.argv[1:] if argv is None else argv):
        return consultar_clave(params)
    try:
        r = requests.get(
            URL_MODELOS, timeout=float(ajustes.p("red.tiempo_espera_segundos", params))
        )
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
