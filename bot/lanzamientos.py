"""Cuántas veces lanzó GitHub el bot y la vigilancia cada día (orden 174 del mando, 22/10/2026).

Desde el 10/10/2026 el reloj de GitHub lanza los dos flujos a la vez en tandas cada 3-5 h en vez
de cada 20 min (HALLAZGOS 22/10/2026), y las preguntas que abren y cierran entre dos tandas se
pierden. El marcador de cada lunes enseña:
- por día (UTC): lanzamientos del reloj, relanzamientos a mano o de la vigilancia, los que
  terminaron bien y el mayor hueco sin lanzar el bot;
- por cada pregunta perdida «sin explicar»: el último lanzamiento del bot antes de su cierre y el
  primero después. Un hueco de horas alrededor del cierre = la perdió el reloj de GitHub.

Lo que calcula es puro; la red va en `vigilancia.Github` (mismo esquema comprobado).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from .vigilancia import Ejecucion

FLUJO_VIGILANCIA = "vigilancia.yaml"
# Lo que pide el `cron` de .github/workflows/run_bot_on_tournament.yaml ("7,27,47 * * * *"):
# 3 por hora. tests/test_lanzamientos.py comprueba que siguen cuadrando.
PREVISTAS_BOT_DIA = 72
PREVISTAS_VIGILANCIA_DIA = 48  # "13,43 * * * *" de .github/workflows/vigilancia.yaml


def _dias(desde: datetime, hasta: datetime) -> list[str]:
    d, res = desde.date(), []
    while d <= hasta.date():
        res.append(d.isoformat())
        d += timedelta(days=1)
    return res


def por_dia(ejecs: list[Ejecucion], desde: datetime, hasta: datetime) -> list[dict]:
    """Una fila por día UTC entre `desde` y `hasta`. El hueco de un día es el mayor tiempo entre
    dos lanzamientos seguidos cuyo segundo cae ese día (el último del día anterior cuenta)."""
    orden = sorted(ejecs, key=lambda e: e.creada)
    filas = {
        d: {"dia": d, "reloj": 0, "a_mano": 0, "bien": 0, "hueco_max_h": None}
        for d in _dias(desde, hasta)
    }
    previa = None
    for e in orden:
        dia = e.creada.date().isoformat()
        f = filas.get(dia)
        if f is not None:
            f["reloj" if e.evento == "schedule" else "a_mano"] += 1
            f["bien"] += e.conclusion == "success"
            if previa is not None:
                h = round((e.creada - previa).total_seconds() / 3600, 1)
                f["hueco_max_h"] = h if f["hueco_max_h"] is None else max(f["hueco_max_h"], h)
        previa = e.creada
    return list(filas.values())


def alrededor(ejecs: list[Ejecucion], momento: datetime) -> tuple[datetime | None, datetime | None]:
    """Último lanzamiento antes de `momento` y primero después (None si no hay)."""
    antes = [e.creada for e in ejecs if e.creada <= momento]
    despues = [e.creada for e in ejecs if e.creada > momento]
    return (max(antes) if antes else None, min(despues) if despues else None)


def _hm(t: datetime | None) -> str:
    return f"{t:%d/%m %H:%M}" if t else "?"


def resumir(
    bot: list[Ejecucion],
    vigilancia: list[Ejecucion],
    perdidas: list[dict],
    desde: datetime,
    hasta: datetime,
) -> dict:
    """`perdidas`: las «sin explicar» del marcador, con `cierre_iso`. Solo cuenta las ejecuciones
    del bot de torneo (las del reloj y las manuales con «tournament» en el título)."""
    bot = [e for e in bot if e.de_torneo]
    huecos = []
    for p in perdidas:
        if not p.get("cierre_iso"):
            continue
        cierre = datetime.fromisoformat(p["cierre_iso"])
        cierre = cierre if cierre.tzinfo else cierre.replace(tzinfo=UTC)
        a, d = alrededor(bot, cierre)
        horas = round((d - a).total_seconds() / 3600, 1) if a and d else None
        huecos.append({**p, "antes": _hm(a), "despues": _hm(d), "hueco_h": horas})
    return {
        "bot": por_dia(bot, desde, hasta),
        "vigilancia": por_dia(vigilancia, desde, hasta),
        "perdidas": huecos,
    }


def informe_md(r: dict) -> list[str]:
    lineas = [
        "",
        "## Cuántas veces lanzó GitHub el bot",
        "",
        f"El reloj de GitHub debería lanzar el bot {PREVISTAS_BOT_DIA} veces al día (cada 20 min) "
        f"y la vigilancia {PREVISTAS_VIGILANCIA_DIA}. «A mano» = relanzado por la vigilancia o por "
        "una persona. «Hueco» = el mayor tiempo seguido sin lanzar el bot ese día: una pregunta "
        "que abre y cierra dentro de un hueco se pierde. Días en UTC.",
        "",
        "| Día | Bot: reloj | Bot: a mano | Bot: bien | Mayor hueco (h) | Vigilancia: reloj |",
        "|---|---|---|---|---|---|",
    ]
    vig = {f["dia"]: f for f in r["vigilancia"]}
    for f in r["bot"]:
        v = vig.get(f["dia"], {})
        hueco = "-" if f["hueco_max_h"] is None else f["hueco_max_h"]
        lineas.append(
            f"| {f['dia']} | {f['reloj']} de {PREVISTAS_BOT_DIA} | {f['a_mano']} | {f['bien']} "
            f"| {hueco} | {v.get('reloj', 0)} de {PREVISTAS_VIGILANCIA_DIA} |"
        )
    if r["perdidas"]:
        lineas += [
            "",
            "Preguntas perdidas sin explicar y los lanzamientos del bot alrededor de su cierre:",
            "",
            "| Cierre (UTC) | Pregunta | Último lanzamiento antes | Primero después | Hueco (h) |",
            "|---|---|---|---|---|",
        ]
        lineas += [
            f"| {p['cierre_utc']} | {p['url']} | {p['antes']} | {p['despues']} "
            f"| {'?' if p['hueco_h'] is None else p['hueco_h']} |"
            for p in r["perdidas"]
        ]
    return lineas
