"""En qué se va el dinero: resumen semanal del gasto frente a la línea de ritmo (orden 26 del mando,
decisión del usuario del 27/09/2026 ~21:55: «medir en qué se va el dinero para estirar los 100 $»).

No cambia nada del bot: solo lee lo que ya queda en el registro.
- **Lo que mide la librería**, por pregunta y por parte (`coste_partes` de cada línea de
  `registro/pronosticos_*.jsonl`): búsqueda de noticias, cada modelo que pronostica, el lector.
- **Lo que dice la clave de OpenRouter** (`registro/presupuesto_*.jsonl`, una consulta gratuita al
  empezar cada torneo de cada ejecución): la cifra buena, porque incluye la búsqueda «:online», que
  la librería no sabe medir (1.er ensayo del 27/09: la clave 0,906 $ y la librería 0,551 $ para 3
  preguntas).
- **La diferencia** entre las dos es lo que la librería no ve: casi todo, la búsqueda.

El cambio de modelos NO se decide aquí: se propone con estos datos tras la primera semana, en una
fecha anunciada. El marcador de cada lunes añade este resumen a docs/MARCADOR.md.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from . import params as ajustes
from . import presupuesto


def _cuando(fila: dict) -> datetime | None:
    try:
        c = datetime.fromisoformat(str(fila["cuando_utc"]))
    except (KeyError, ValueError):
        return None
    return c if c.tzinfo else c.replace(tzinfo=UTC)


def _gastado_clave(fila: dict) -> tuple[float, float | None] | None:
    """(gastado, límite) de una consulta archivada de la clave; None si no tiene la forma."""
    if fila.get("consulta") != "openrouter_clave":
        return None
    try:
        estado = presupuesto.leer_estado(fila.get("respuesta"))
    except presupuesto.EsquemaClaveError:
        return None
    return estado.gastado, estado.limite


def resumen(filas: list[dict], params: dict, ahora: datetime) -> dict:
    """Resumen de los últimos `marcador.dias_resumen_gasto` días. `filas`: todas las líneas de los
    registros descargados (pronósticos y consultas de la clave, mezcladas)."""
    dias = float(ajustes.p("marcador.dias_resumen_gasto", params))
    desde = ahora - timedelta(days=dias)
    recientes = [(c, f) for f in filas if (c := _cuando(f)) is not None and desde <= c <= ahora]

    preguntas = [f for _, f in recientes if "coste_partes" in f or f.get("coste_usd") is not None]
    por_parte: dict[str, float] = {}
    libreria = 0.0
    for f in preguntas:
        libreria += float(f.get("coste_usd") or 0.0)
        for parte, usd in (f.get("coste_partes") or {}).items():
            # «pronostico <modelo>»: se agrupa por modelo; las demás, por su nombre
            por_parte[parte] = por_parte.get(parte, 0.0) + float(usd or 0.0)

    consultas = sorted(
        (c, g) for c, f in recientes if (g := _gastado_clave(f)) is not None
    )  # por fecha
    clave: dict = {"consultas": len(consultas)}
    if consultas:
        gastado_ahora, limite = consultas[-1][1]
        total = limite if limite is not None else float(ajustes.p("presupuesto.total_usd", params))
        linea = presupuesto.linea_de_ritmo(total, params, consultas[-1][0])
        semana = gastado_ahora - consultas[0][1][0] if len(consultas) > 1 else None
        reserva = float(ajustes.p("presupuesto.reserva_usd", params))
        queda = total - gastado_ahora - reserva
        clave |= {
            "gastado_total": round(gastado_ahora, 2),
            "presupuesto": round(total, 2),
            "linea_de_ritmo": round(linea, 2),
            "sobre_la_linea": round(gastado_ahora - linea, 2),
            "gastado_en_el_periodo": None if semana is None else round(semana, 2),
            # a este ritmo, cuántas semanas quedan hasta tocar la reserva
            "semanas_que_quedan": (
                round(queda / (semana * 7 / dias), 1) if semana and semana > 0 else None
            ),
        }
        if semana is not None:
            clave["sin_medir_por_la_libreria"] = round(max(0.0, semana - libreria), 2)
    n = len(preguntas)
    return {
        "dias": dias,
        "preguntas": n,
        "libreria_total": round(libreria, 2),
        "libreria_por_pregunta": round(libreria / n, 3) if n else None,
        "por_parte": {k: round(v, 3) for k, v in sorted(por_parte.items())},
        "por_parte_por_pregunta": {k: round(v / n, 4) for k, v in sorted(por_parte.items())}
        if n
        else {},
        "clave": clave,
    }


def informe_md(r: dict) -> list[str]:
    """Sección en llano para docs/MARCADOR.md."""
    c = r["clave"]
    lineas = [
        "",
        f"## En qué se va el dinero (últimos {r['dias']:.0f} días)",
        "",
        "Dos cifras: lo que dice la **clave** de OpenRouter (la buena: lo que de verdad se ha "
        "gastado) y lo que mide la **librería** del bot pregunta a pregunta (no ve la búsqueda de "
        "noticias «:online», así que se queda corta). La diferencia es, casi toda, la búsqueda.",
        "",
        "| Dato | Valor |",
        "|---|---|",
        f"| Preguntas hechas en el periodo | {r['preguntas']} |",
    ]
    if c.get("consultas"):
        sobre = c["sobre_la_linea"]
        lineas += [
            f"| Gastado en total (clave) | {c['gastado_total']} $ de {c['presupuesto']} $ |",
            f"| Línea de ritmo a esta fecha | {c['linea_de_ritmo']} $ "
            f"({'por ENCIMA' if sobre > 0 else 'por debajo'}: {sobre:+} $) |",
        ]
        if c.get("gastado_en_el_periodo") is not None:
            por_pregunta = (
                round(c["gastado_en_el_periodo"] / r["preguntas"], 3) if r["preguntas"] else "—"
            )
            lineas += [
                f"| Gastado en el periodo (clave) | {c['gastado_en_el_periodo']} $ "
                f"(~{por_pregunta} $ por pregunta) |",
                f"| De eso, medido por la librería | {r['libreria_total']} $ |",
                f"| Sin medir por la librería (≈ búsqueda) | {c['sin_medir_por_la_libreria']} $ |",
            ]
        if c.get("semanas_que_quedan") is not None:
            lineas.append(
                f"| A este ritmo, el dinero llega para | ~{c['semanas_que_quedan']} semanas más |"
            )
    else:
        lineas.append("| Consultas de la clave en el periodo | ninguna (¿sin clave?) |")
    if r["por_parte_por_pregunta"]:
        lineas += [
            "",
            "Por parte (lo que mide la librería, media por pregunta):",
            "",
            "| Parte | $ por pregunta | $ en el periodo |",
            "|---|---|---|",
        ]
        for parte, media in r["por_parte_por_pregunta"].items():
            lineas.append(f"| {parte} | {media} | {r['por_parte'][parte]} |")
    lineas += [
        "",
        "El cambio de modelos no se hace solo: se propone con estos datos tras la primera semana, "
        "en una fecha anunciada.",
    ]
    return lineas
