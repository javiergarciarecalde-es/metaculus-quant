"""Normas del torneo que el código hace cumplir solo (orden 27 del mando, 28/09/2026).

Página oficial de recursos de FutureEval (metaculus.com/notebooks/38928, releída el 28/09/2026;
ver docs/FUENTES.md): «Bot makers should only submit one forecast per question in these bot-only
tournaments» y «A bot maker cannot decide that they don't like their bot's forecast and rerun the
bot on that question».

La librería ya salta las preguntas pronosticadas (`already_forecasted`), pero **falla abierta**: si
la respuesta de Metaculus no trae el historial de nuestros pronósticos (`my_forecasts.history`),
da la pregunta por no pronosticada y el bot la volvería a pronosticar cada 20 minutos. Aquí se
falla cerrada: una pregunta cuyo historial no se puede leer NO se pronostica y se avisa en rojo.
Además, una pregunta que llegue repetida en la misma lista solo se pronostica una vez.

Funciones puras: reciben preguntas y devuelven preguntas (sin red ni disco).
"""

from __future__ import annotations

from typing import Any


class EsquemaMetaculusError(ValueError):
    """La respuesta de Metaculus no dice si ya pronosticamos la pregunta."""


def historial_propio(pregunta: Any) -> list:
    """Nuestros pronósticos en la pregunta, según la respuesta cruda de Metaculus que la librería
    guarda en `api_json` (verificado en vivo el 27/09/2026: tras enviar la 45707, las ejecuciones
    siguientes la saltaron). `history` a null se toma como «ninguno», igual que la librería."""
    datos = getattr(pregunta, "api_json", None)
    pq = datos.get("question") if isinstance(datos, dict) else None
    mios = pq.get("my_forecasts") if isinstance(pq, dict) else None
    if not isinstance(mios, dict) or "history" not in mios:
        raise EsquemaMetaculusError("la respuesta de Metaculus no trae «my_forecasts.history»")
    historial = mios["history"]
    if historial is None:
        return []
    if not isinstance(historial, list):
        raise EsquemaMetaculusError("«my_forecasts.history» no es una lista")
    return historial


def sin_pronostico_nuestro(preguntas: list) -> tuple[list, list[str]]:
    """(preguntas que se pueden pronosticar, avisos). Se quitan: las que ya tienen pronóstico
    nuestro (según el historial O según la librería), las repetidas y las que no se sabe."""
    salida, avisos, vistas = [], [], set()
    for q in preguntas:
        nombre = getattr(q, "page_url", None) or getattr(q, "id_of_question", "?")
        try:
            ya = bool(historial_propio(q)) or bool(getattr(q, "already_forecasted", False))
        except EsquemaMetaculusError as e:
            avisos.append(f"{nombre}: {e}; no se pronostica (una sola vez por pregunta)")
            continue
        clave = (getattr(q, "id_of_question", None), getattr(q, "id_of_post", None), nombre)
        if ya or clave in vistas:
            continue
        vistas.add(clave)
        salida.append(q)
    return salida, avisos
