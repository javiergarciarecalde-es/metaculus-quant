"""Preguntas perdidas: las que cerraron sin pronóstico nuestro (mejora 1c de docs/ESTUDIO_BOTS.md;
decisión del usuario del 27/09/2026 ~22:40).

Una pregunta sin pronóstico vale 0 puntos. La vigilancia (bot/vigilancia.py) intenta que no pase;
esta lista semanal es la prueba de si lo consigue. El marcador de cada lunes pide a Metaculus (solo
lectura) las preguntas de la MiniBench y de la temporada que cerraron en los últimos
`marcador.dias_preguntas_perdidas` días y separa las que no tienen pronóstico nuestro en:
- **por el tope de gasto** (a propósito: el bot las dejó para no gastar el dinero antes de tiempo;
  lo apunta en `registro/presupuesto_*.jsonl`, consulta «dejadas»);
- **sin explicar**: estas son las que la vigilancia debería haber evitado.
"""

from __future__ import annotations

from datetime import UTC, datetime

from . import params as ajustes


def buscar_cerradas(torneos: list, desde: datetime, hasta: datetime) -> list[tuple]:
    """Solo lectura: [(torneo, [preguntas cerradas en el intervalo])]. Necesita METACULUS_TOKEN
    para saber cuáles pronosticó el bot («already_forecasted»)."""
    from forecasting_tools import ApiFilter, MetaculusClient

    cliente = MetaculusClient()
    res = []
    for t in torneos:
        filtro = ApiFilter(
            allowed_tournaments=[t],
            allowed_statuses=["closed", "resolved"],
            close_time_gt=desde,
            close_time_lt=hasta,
            group_question_mode="unpack_subquestions",
        )
        res.append((t, cliente.get_questions_matching_filter(filtro)))
    return res


def dejadas_a_proposito(filas: list[dict]) -> tuple[set, bool]:
    """(ids de preguntas que el tope dejó a propósito, ¿hubo momentos sin dinero?) según el
    registro. Cada id es (id del post, id de la pregunta), como en el resto del registro."""
    ids, sin_dinero = set(), False
    for f in filas:
        if f.get("consulta") != "dejadas":
            continue
        sin_dinero |= f.get("motivo") == "sin_dinero"
        for par in f.get("preguntas") or []:
            if isinstance(par, list) and len(par) == 2:
                ids.add(tuple(par))
    return ids, sin_dinero


def _fecha(q) -> str:
    c = getattr(q, "close_time", None)
    if c is None:
        return "?"
    c = c if c.tzinfo else c.replace(tzinfo=UTC)
    return f"{c:%d/%m %H:%M}"


def resumir(cerradas: list[tuple] | None, filas: list[dict], params: dict) -> dict:
    """Cuenta y lista las perdidas. `cerradas` None = no se pudo preguntar a Metaculus."""
    dias = float(ajustes.p("marcador.dias_preguntas_perdidas", params))
    if cerradas is None:
        return {"dias": dias, "consultado": False}
    dejadas, sin_dinero = dejadas_a_proposito(filas)
    total = hechas = 0
    por_tope, sin_explicar = [], []
    for torneo, preguntas in cerradas:
        for q in preguntas:
            total += 1
            if q.already_forecasted:
                hechas += 1
                continue
            item = {"url": q.page_url, "cierre_utc": _fecha(q), "torneo": str(torneo)}
            if (q.id_of_post, q.id_of_question) in dejadas:
                por_tope.append(item)
            else:
                sin_explicar.append(item)
    return {
        "dias": dias,
        "consultado": True,
        "cerradas": total,
        "con_pronostico": hechas,
        "perdidas_por_el_tope": por_tope,
        "perdidas_sin_explicar": sin_explicar,
        "hubo_momentos_sin_dinero": sin_dinero,
    }


def informe_md(r: dict) -> list[str]:
    lineas = ["", f"## Preguntas perdidas (cerradas en los últimos {r['dias']:.0f} días)", ""]
    if not r.get("consultado"):
        return [
            *lineas,
            "No se pudo preguntar a Metaculus (¿sin token?): esta semana no hay lista.",
        ]
    perdidas = r["perdidas_sin_explicar"]
    lineas += [
        "Una pregunta sin pronóstico vale 0 puntos. «Por el tope» = el bot la dejó a propósito "
        "para no gastar el dinero antes de tiempo. «Sin explicar» = la vigilancia debió evitarla: "
        "si hay alguna, hay que mirar por qué.",
        "",
        "| Dato | Valor |",
        "|---|---|",
        f"| Preguntas cerradas | {r['cerradas']} |",
        f"| Con pronóstico nuestro | {r['con_pronostico']} |",
        f"| Perdidas por el tope de gasto (a propósito) | {len(r['perdidas_por_el_tope'])} |",
        f"| **Perdidas sin explicar** | **{len(perdidas)}** |",
    ]
    if r["hubo_momentos_sin_dinero"]:
        lineas += [
            "",
            "Ojo: en estos días hubo momentos **sin dinero**; entonces el bot no mira el segundo "
            "torneo y sus preguntas salen aquí como «sin explicar» aunque fueran a propósito.",
        ]
    if perdidas:
        lineas += ["", "| Cierre (UTC) | Torneo | Pregunta |", "|---|---|---|"]
        lineas += [f"| {p['cierre_utc']} | {p['torneo']} | {p['url']} |" for p in perdidas[:30]]
    return lineas
