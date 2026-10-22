"""Lanzamientos del bot por día y huecos alrededor de las preguntas perdidas (orden 174)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import yaml

from bot import lanzamientos as lanz
from bot import marcador as mc
from bot import vigilancia as vg
from bot.config import RAIZ


def _e(cuando: str, evento="schedule", conclusion="success", titulo="tournament", i=0):
    t = datetime.fromisoformat(cuando).replace(tzinfo=UTC)
    return vg.Ejecucion(i, "completed", conclusion, evento, titulo, t, t, "x")


DESDE = datetime(2026, 10, 11, tzinfo=UTC)
HASTA = datetime(2026, 10, 12, 12, tzinfo=UTC)
# Lo que pasó de verdad el 10-11/10/2026 (gh run list): 4,9 h sin lanzar; la 45956 cerró a las 06:00
BOT = [
    _e("2026-10-10T22:24"),
    _e("2026-10-10T23:34", "workflow_dispatch"),
    _e("2026-10-11T01:05"),
    _e("2026-10-11T02:13", "workflow_dispatch"),
    _e("2026-10-11T07:05"),
    _e("2026-10-11T09:01", "workflow_dispatch", "failure"),
    _e("2026-10-11T09:30", "workflow_dispatch", titulo="test_questions"),  # no es de torneo
]


def test_cuenta_por_dia_y_hueco():
    r = lanz.resumir(BOT, [_e("2026-10-11T02:12")], [], DESDE, HASTA)
    d11, d12 = r["bot"]
    assert d11 == {"dia": "2026-10-11", "reloj": 2, "a_mano": 2, "bien": 3, "hueco_max_h": 4.9}
    assert d12["reloj"] == d12["a_mano"] == 0 and d12["hueco_max_h"] is None
    assert r["vigilancia"][0]["reloj"] == 1


def test_la_pregunta_perdida_cae_en_el_hueco():
    perdida = {
        "url": "u/45956",
        "cierre_utc": "11/10 06:00",
        "cierre_iso": "2026-10-11T06:00:00+00:00",
    }
    r = lanz.resumir(BOT, [], [perdida, {"url": "sin fecha", "cierre_utc": "?"}], DESDE, HASTA)
    (p,) = r["perdidas"]
    assert (p["antes"], p["despues"], p["hueco_h"]) == ("11/10 02:13", "11/10 07:05", 4.9)
    texto = "\n".join(lanz.informe_md(r))
    assert "| 2026-10-11 | 2 de 72 | 2 | 3 | 4.9 | 0 de 48 |" in texto
    assert "| 11/10 06:00 | u/45956 | 11/10 02:13 | 11/10 07:05 | 4.9 |" in texto


def test_previstas_cuadran_con_el_cron():
    def por_dia(fichero: str) -> int:
        flujo = yaml.safe_load((RAIZ / ".github/workflows" / fichero).read_text(encoding="utf-8"))
        disparo = flujo.get("on") or flujo.get(True)  # YAML lee «on» como True
        (cron,) = [c["cron"] for c in disparo["schedule"]]
        minutos, horas, *resto = cron.split()
        assert horas == "*" and resto == ["*", "*", "*"]
        return len(minutos.split(",")) * 24

    assert por_dia("run_bot_on_tournament.yaml") == lanz.PREVISTAS_BOT_DIA
    assert por_dia(lanz.FLUJO_VIGILANCIA) == lanz.PREVISTAS_VIGILANCIA_DIA


class _Respuesta:
    def __init__(self, datos):
        self.datos = datos

    def raise_for_status(self):
        pass

    def json(self):
        return self.datos


def _run(i: int, t: datetime) -> dict:
    s = t.strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"id": i, "status": "completed", "conclusion": "success", "event": "schedule",
            "created_at": s, "updated_at": s}  # fmt: skip


def test_github_pide_todas_las_paginas():
    t0 = datetime(2026, 10, 15, tzinfo=UTC)
    pedidas = []

    def get(url, headers, params, timeout):
        pedidas.append(params)
        n = 100 if params["page"] == 1 else 3
        return _Respuesta(
            {
                "workflow_runs": [
                    _run(params["page"] * 1000 + k, t0 + timedelta(minutes=k)) for k in range(n)
                ]
            }
        )

    gh = vg.Github("a/b", "tok", 5, get=get)
    res = gh.ejecuciones_desde("bot.yaml", t0)
    assert len(res) == 103 and res[0].creada > res[-1].creada
    assert [p["page"] for p in pedidas] == [1, 2]
    assert pedidas[0]["created"] == ">=2026-10-15T00:00:00Z" and pedidas[0]["per_page"] == 100


def test_el_marcador_cruza_perdidas_y_lanzamientos():
    class GithubFalso:
        def ejecuciones_desde(self, flujo, desde):
            assert desde == datetime(2026, 10, 5, tzinfo=UTC)
            return BOT if flujo == "run_bot_on_tournament.yaml" else []

    perdidas = {
        "perdidas_sin_explicar": [
            {"url": "u", "cierre_utc": "x", "cierre_iso": "2026-10-11T06:00:00+00:00"}
        ]
    }
    r = mc._lanzamientos(perdidas, datetime(2026, 10, 12, 8, tzinfo=UTC), GithubFalso())
    assert r["perdidas"][0]["hueco_h"] == 4.9 and len(r["bot"]) == 8


def test_sin_token_la_seccion_avisa(monkeypatch):
    monkeypatch.delenv("GH_TOKEN", raising=False)
    try:
        mc._lanzamientos({}, datetime.now(UTC))
    except RuntimeError as e:
        assert "GH_TOKEN" in str(e)
    else:
        raise AssertionError("debió fallar sin token")
