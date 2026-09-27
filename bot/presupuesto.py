"""Tope de gasto de los créditos de Metaculus (orden 26 del mando, 27/09/2026).

Metaculus dio **100 $** en una clave de OpenRouter para pronosticar en FutureEval y MiniBench
(correo del 27/09/2026). Si el bot rinde por encima de la media en MiniBench, la clave sube sola.
Este módulo decide, al empezar cada torneo de cada ejecución, **cuántas preguntas nuevas** se pueden
pronosticar sin agotar el dinero antes de tiempo:

- **Cuánto se ha gastado y cuánto queda** se lee de la propia clave (consulta gratuita a
  OpenRouter, `GET /api/v1/key`; verificado en su documentación el 27/09/2026, ver
  docs/FUENTES.md). Es la cifra de verdad: incluye todo lo gastado con esa clave, y si Metaculus
  sube el límite, el bot lo ve solo.
- **Reserva:** si lo que queda baja de `presupuesto.reserva_usd`, no se empieza nada (aviso
  amarillo, sin error rojo cada 20 minutos).
- **MiniBench primero** (es la que decide si llega más dinero): solo la para la reserva.
- **Temporada con ritmo:** solo si lo gastado va por debajo de una línea que reparte el presupuesto
  entre el inicio y el final de la temporada (con un colchón inicial). Si la MiniBench gasta mucho,
  la temporada espera.
- **Cuántas preguntas caben:** lo que se puede gastar dividido por `coste_previsto_por_pregunta_usd`
  (a la baja).

Sin estado global: `decidir` es pura (recibe el estado de la clave, los parámetros y la hora). La
red va solo en `consultar_clave`, que valida el esquema y archiva la respuesta (sin la etiqueta de
la clave, que puede llevar trozos de ella; regla común 5).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import requests

from bot import params as ajustes
from bot import registro

URL_CLAVE = "https://openrouter.ai/api/v1/key"
# Campos que usamos de la respuesta (docs de OpenRouter, «API Key Status», 27/09/2026). La clave
# de Metaculus gasta como «byok» (con claves de las empresas que pone Metaculus): en la consulta
# real del 27/09 «usage» daba 0 y lo gastado salía en «byok_usage», que cuenta en el límite
# («include_byok_in_limit»: true). Por eso lo gastado es la suma de los dos.
CAMPOS_NUMERICOS = ("usage", "byok_usage")
CAMPOS_OPCIONALES = ("limit", "limit_remaining")  # null = la clave no tiene límite propio
# Nunca se guardan ni se muestran: la etiqueta puede contener parte de la clave; los demás son
# identificadores de la cuenta de Metaculus en OpenRouter (el registro sale como artefacto público).
CAMPOS_PROHIBIDOS = ("label", "creator_user_id", "organization_id", "workspace_id")
# Cómo dice OpenRouter que no queda saldo: HTTP 402 «Payment Required» / «insufficient credits».
SIN_SALDO = re.compile(
    r"\b402\b|payment required|insufficient credits|insufficient_quota|more credits", re.I
)


class EsquemaClaveError(ValueError):
    """La respuesta de OpenRouter sobre la clave no tiene la forma documentada."""


@dataclass(frozen=True)
class EstadoClave:
    gastado: float  # $ gastados con la clave desde que existe («usage» + «byok_usage»)
    limite: float | None  # límite de la clave en $ («limit»); None = sin límite propio
    restante: float | None  # $ que quedan según OpenRouter («limit_remaining»)


@dataclass(frozen=True)
class Decision:
    max_preguntas: int  # preguntas NUEVAS que se pueden empezar en este torneo
    motivo: str  # frase en español para el aviso de GitHub
    sin_dinero: bool  # True = ya no queda más que la reserva: el bot no pronostica nada


def leer_estado(respuesta: Any) -> EstadoClave:
    """Valida la respuesta de `GET /api/v1/key` y saca las cifras. Error claro si cambia."""
    if not isinstance(respuesta, dict) or not isinstance(respuesta.get("data"), dict):
        raise EsquemaClaveError("la respuesta de OpenRouter sobre la clave no trae «data»")
    datos = respuesta["data"]
    for campo in CAMPOS_NUMERICOS:
        if not isinstance(datos.get(campo), (int, float)) or isinstance(datos.get(campo), bool):
            raise EsquemaClaveError(f"OpenRouter no da el campo numérico «{campo}» de la clave")
    for campo in CAMPOS_OPCIONALES:
        if campo not in datos:
            raise EsquemaClaveError(f"OpenRouter no da el campo «{campo}» de la clave")
        valor = datos[campo]
        if valor is not None and (not isinstance(valor, (int, float)) or isinstance(valor, bool)):
            raise EsquemaClaveError(f"el campo «{campo}» de la clave no es un número")
    return EstadoClave(
        gastado=float(datos["usage"]) + float(datos["byok_usage"]),
        limite=None if datos["limit"] is None else float(datos["limit"]),
        restante=None if datos["limit_remaining"] is None else float(datos["limit_remaining"]),
    )


def sin_campos_prohibidos(respuesta: Any) -> Any:
    """Copia de la respuesta sin la etiqueta ni los identificadores (para archivarla)."""
    if isinstance(respuesta, dict) and isinstance(respuesta.get("data"), dict):
        datos = {k: v for k, v in respuesta["data"].items() if k not in CAMPOS_PROHIBIDOS}
        return {**respuesta, "data": datos}
    return respuesta


def consultar_clave(clave: str, tiempo_espera: float, get=requests.get) -> EstadoClave:
    """Pregunta a OpenRouter cuánto se ha gastado con la clave (gratis). Archiva la respuesta."""
    r = get(URL_CLAVE, headers={"Authorization": f"Bearer {clave}"}, timeout=tiempo_espera)
    r.raise_for_status()
    respuesta = r.json()
    registro.anotar(
        {"consulta": "openrouter_clave", "respuesta": sin_campos_prohibidos(respuesta)},
        nombre="presupuesto",
    )
    return leer_estado(respuesta)


def presupuesto_total(estado: EstadoClave, params: dict) -> float:
    """Dinero total de la clave: su propio límite si lo tiene (sube solo si Metaculus recarga);
    si no, el del correo (`presupuesto.total_usd`)."""
    if estado.limite is not None:
        return estado.limite
    return float(ajustes.p("presupuesto.total_usd", params))


def restante(estado: EstadoClave, params: dict) -> float:
    if estado.restante is not None:
        return estado.restante
    return presupuesto_total(estado, params) - estado.gastado


def linea_de_ritmo(total: float, params: dict, ahora: datetime) -> float:
    """Lo máximo que se debería llevar gastado a esta hora: un colchón al principio y el resto
    repartido por igual hasta el final de la temporada."""
    inicio = _fecha(ajustes.p("presupuesto.ritmo.inicio", params))
    fin = _fecha(ajustes.p("presupuesto.ritmo.fin", params))
    colchon = float(ajustes.p("presupuesto.ritmo.colchon_inicial", params))
    avance = (ahora - inicio).total_seconds() / (fin - inicio).total_seconds()
    avance = min(1.0, max(0.0, avance))
    return total * min(1.0, colchon + (1 - colchon) * avance)


def decidir(
    estado: EstadoClave,
    params: dict,
    ahora: datetime,
    con_ritmo: bool,
    gastado_en_esta_ejecucion: float = 0.0,
) -> Decision:
    """Cuántas preguntas nuevas se pueden empezar en este torneo, y por qué.

    `con_ritmo`: False para la MiniBench (y el ensayo en la zona de pruebas), que solo para la
    reserva; True para la temporada, que además va al ritmo de la línea de gasto.
    `gastado_en_esta_ejecucion`: lo que el bot sabe que ya ha gastado en esta ejecución y que la
    clave quizá aún no refleja (OpenRouter tarda un poco en sumarlo).
    """
    reserva = float(ajustes.p("presupuesto.reserva_usd", params))
    coste = float(ajustes.p("presupuesto.coste_previsto_por_pregunta_usd", params))
    total = presupuesto_total(estado, params)
    queda = restante(estado, params) - gastado_en_esta_ejecucion
    gastado = total - queda
    if queda <= reserva:
        return Decision(
            0,
            f"Sin dinero: quedan {queda:.2f} $ de {total:.2f} $ (reserva {reserva:.2f} $). El bot "
            "no pronostica hasta que Metaculus recargue la clave.",
            sin_dinero=True,
        )
    margen = queda - reserva
    if not con_ritmo:
        n = math.floor(margen / coste)
        return Decision(n, f"Quedan {queda:.2f} $ de {total:.2f} $; caben {n} preguntas.", False)
    permitido = linea_de_ritmo(total, params, ahora)
    margen = min(margen, permitido - gastado)
    if margen < coste:
        return Decision(
            0,
            f"Temporada en espera: llevamos {gastado:.2f} $ gastados y el ritmo permite "
            f"{permitido:.2f} $ a esta fecha (la MiniBench va primero).",
            False,
        )
    n = math.floor(margen / coste)
    return Decision(
        n,
        f"Temporada: llevamos {gastado:.2f} $ de {permitido:.2f} $ permitidos a esta fecha; "
        f"caben {n} preguntas.",
        False,
    )


def es_falta_de_saldo(error: BaseException) -> bool:
    """True si el error es que OpenRouter no tiene saldo (402): no es un fallo del bot."""
    return bool(SIN_SALDO.search(f"{type(error).__name__} {error}"))


def _fecha(texto: str) -> datetime:
    return datetime.fromisoformat(str(texto)).replace(tzinfo=UTC)
