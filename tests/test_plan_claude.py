"""Tope del plan de Claude del usuario (bot/plan_claude.py; orden 27 del mando, 28/09/2026).

Con los números de config/params.yaml: 15 % del tope semanal por 5 $ el punto, menos 5 $ de
reserva para la revisión de los lunes = 70 $ equivalentes por semana del plan; el clasificador con
Opus se apaga al 80 % (56 $). Nada sale a internet.
"""

from __future__ import annotations

import io
import json
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

import main
from bot import claude_max as cm
from bot import config as cfg
from bot import plan_claude as pc
from bot import vigilancia as vg
from tests.conftest import MetaculusFalso, ModeloFalso, preguntas_ejemplo
from tests.test_claude_max import ClaudeFalso
from tests.test_opcion_a_y_clasificador import BUENA

LUNES_10 = datetime(2026, 10, 5, 10, 0, tzinfo=UTC)  # lunes, una hora después del reinicio


def _params():
    return cfg.cargar_params()


# ------------------------------------------------------------------ cuentas


def test_la_semana_del_plan_empieza_el_lunes_a_las_9_utc():
    p = _params()
    assert pc.inicio_semana(LUNES_10, p) == datetime(2026, 10, 5, 9, 0, tzinfo=UTC)
    # el lunes antes de las 9 aún es la semana anterior; el domingo, también
    assert pc.inicio_semana(LUNES_10 - timedelta(hours=2), p) == datetime(
        2026, 9, 28, 9, tzinfo=UTC
    )
    assert pc.inicio_semana(LUNES_10 - timedelta(days=1), p) == datetime(2026, 9, 28, 9, tzinfo=UTC)


def test_tope_con_los_numeros_de_la_orden_27():
    p = _params()
    assert pc.tope_usd(p) == pytest.approx(70.0)  # 15 puntos a 5 $, menos 5 $ de reserva
    c = pc.contador(p)
    assert c.umbral_opus == pytest.approx(56.0)


def test_suma_solo_lo_de_esta_semana_y_solo_las_lineas_del_plan():
    desde = datetime(2026, 10, 5, 9, tzinfo=UTC)

    def fila(parte, usd, cuando, consulta="plan_claude"):
        return {"consulta": consulta, "parte": parte, "usd": usd, "cuando_utc": cuando}

    filas = [
        fila("investigacion", 2.0, "2026-10-05T09:30:00+00:00"),
        fila("investigacion", 9.0, "2026-10-05T08:59:00+00:00"),  # semana anterior
        fila("clasificador_opus", 0.3, "2026-10-06T10:00:00+00:00"),
        fila(None, 50, "2026-10-06T10:00:00+00:00", consulta="dejadas"),  # otra cosa
        fila("vigilancia", "roto", "2026-10-06T10:00:00+00:00"),
    ]
    assert pc.sumar(filas, desde) == {"investigacion": 2.0, "clasificador_opus": 0.3}


def test_primero_se_apaga_opus_y_luego_la_investigacion(tmp_path):
    c = pc.contador(_params(), leer=lambda: {"investigacion": 55.5}, carpeta=tmp_path)
    assert not c.empezar("clasificador_opus", 1.0)  # 55,5 + 1 > 56
    assert c.empezar("investigacion", 3.0)  # 55,5 + 3 <= 70
    c.terminar("investigacion", 3.0, 2.1, "pregunta")
    assert c.total() == pytest.approx(57.6)
    c2 = pc.contador(_params(), leer=lambda: {"investigacion": 68.0}, carpeta=tmp_path)
    assert not c2.empezar("investigacion", 3.0)  # 68 + 3 > 70


def test_varias_a_la_vez_no_se_pasan_del_tope(tmp_path):
    """Las 3 investigaciones simultáneas reservan su freno antes de empezar."""
    c = pc.contador(_params(), leer=lambda: {"investigacion": 62.0}, carpeta=tmp_path)
    assert c.empezar("investigacion", 3.0) and c.empezar("investigacion", 3.0)
    assert not c.empezar("investigacion", 3.0)  # 62 + 3 + 3 + 3 > 70


def test_sin_cuenta_se_apaga_solo_opus(tmp_path, capsys):
    def roto():
        raise ConnectionError("GitHub no contesta")

    c = pc.contador(_params(), leer=roto, carpeta=tmp_path)
    assert not c.empezar("clasificador_opus", 1.0)
    assert c.empezar("investigacion", 3.0)
    assert "::warning::" in capsys.readouterr().out


def test_lo_gastado_queda_apuntado_y_si_no_se_sabe_cuenta_el_freno(tmp_path):
    c = pc.contador(_params(), leer=dict, carpeta=tmp_path)
    c.empezar("investigacion", 3.0)
    c.terminar("investigacion", 3.0, None, "cortada por tiempo")
    c.empezar("clasificador_opus", 1.0)
    c.terminar("clasificador_opus", 1.0, 0.25)
    [f] = list(tmp_path.glob("plan_claude_*.jsonl"))
    filas = [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines()]
    assert pc.sumar(filas, datetime(2000, 1, 1, tzinfo=UTC)) == {
        "investigacion": 3.0,
        "clasificador_opus": 0.25,
    }


# ------------------------------------------------------------------ GitHub simulado


def _zip(filas: list[dict]) -> bytes:
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("plan_claude_2026-10.jsonl", "".join(json.dumps(f) + "\n" for f in filas))
    return b.getvalue()


class ArtefactosFalsos:
    """Imita la API de artefactos de GitHub (forma vista en la respuesta real del 28/09/2026)."""

    def __init__(self, artefactos, zips):
        self.artefactos, self.zips, self.pedidos = artefactos, zips, []

    def get(self, url, **k):
        self.pedidos.append(url)
        if url.endswith("/actions/artifacts"):
            pagina = k["params"]["page"]
            trozo = self.artefactos[(pagina - 1) * 100 : pagina * 100]
            return SimpleNamespace(raise_for_status=lambda: None, json=lambda: {"artifacts": trozo})
        if url.endswith("/zip"):
            ident = int(url.split("/")[-2])
            return SimpleNamespace(raise_for_status=lambda: None, content=self.zips[ident])
        if url.endswith("/runs") or url.endswith("/issues"):
            raise AssertionError(url)
        raise AssertionError(url)


def _artefacto(ident, nombre, horas_atras, expired=False):
    creado = (LUNES_10 - timedelta(hours=horas_atras)).isoformat().replace("+00:00", "Z")
    return {"id": ident, "name": nombre, "expired": expired, "created_at": creado}


def _linea(parte, usd, horas_atras):
    cuando = (LUNES_10 - timedelta(hours=horas_atras)).isoformat()
    return {"consulta": "plan_claude", "parte": parte, "usd": usd, "cuando_utc": cuando}


def test_lee_lo_gastado_de_los_artefactos_de_esta_semana():
    desde = LUNES_10 - timedelta(hours=1)
    falso = ArtefactosFalsos(
        [
            _artefacto(1, "plan-claude-100", 0.2),
            _artefacto(2, "registro-100", 0.2),  # otro tipo de artefacto: no se baja
            _artefacto(3, "plan-claude-99", 0.5, expired=True),
            _artefacto(4, "plan-claude-98", 30),  # de la semana pasada: se deja de mirar
        ],
        {1: _zip([_linea("investigacion", 2.5, 0.2), _linea("clasificador_opus", 0.2, 0.2)])},
    )
    gastado = pc.leer_de_github("yo/repo", "t", desde, 5, get=falso.get)
    assert gastado == {"investigacion": 2.5, "clasificador_opus": 0.2}
    assert sum(u.endswith("/zip") for u in falso.pedidos) == 1


def test_pide_mas_paginas_solo_si_hace_falta():
    desde = LUNES_10 - timedelta(days=2)
    artefactos = [_artefacto(i, f"registro-{i}", 1) for i in range(100)]
    artefactos += [_artefacto(500, "plan-claude-500", 2)]
    falso = ArtefactosFalsos(artefactos, {500: _zip([_linea("vigilancia", 5.0, 2)])})
    assert pc.leer_de_github("yo/repo", "t", desde, 5, get=falso.get) == {"vigilancia": 5.0}
    assert sum(u.endswith("/actions/artifacts") for u in falso.pedidos) == 2


def test_respuesta_de_github_con_otra_forma_da_error_claro():
    falso = SimpleNamespace(
        get=lambda url, **k: SimpleNamespace(raise_for_status=lambda: None, json=lambda: {"x": 1})
    )
    with pytest.raises(pc.EsquemaGithubError):
        pc.leer_de_github("yo/repo", "t", LUNES_10, 5, get=falso.get)


# ------------------------------------------------------------------ el bot entero


def _ejecutar(monkeypatch, tmp_path, gastado: dict, pregunta):
    monkeypatch.setenv(cm.SECRETO, "token-falso")
    monkeypatch.setenv("METACULUS_TOKEN", "t")
    modelo = ModeloFalso()
    investigador, opus = ClaudeFalso("NOTAS DE OPUS"), ClaudeFalso(BUENA)
    llms = {"default": modelo, "summarizer": modelo, "researcher": modelo, "parser": modelo}
    llms |= {"_claude_ejecutar": investigador, "_claude_clasificar": opus}
    plan = pc.contador(_params(), leer=lambda: gastado)
    main.ejecutar("test_questions", cliente=MetaculusFalso([pregunta]), llms=llms, plan=plan)
    [f] = list((tmp_path / "registro").glob("pronosticos_*.jsonl"))
    return json.loads(f.read_text(encoding="utf-8").splitlines()[0]), investigador, opus


def test_bot_por_debajo_del_tope_usa_todo_y_lo_apunta(monkeypatch, tmp_path):
    fila, _, _ = _ejecutar(monkeypatch, tmp_path, {}, preguntas_ejemplo()[1])  # par
    assert fila["investigacion"]["claude_estado"] == "ok"
    assert fila["clasificador_opus"]["estado"] == "ok"
    [f] = list((tmp_path / "plan").glob("plan_claude_*.jsonl"))
    partes = sorted(json.loads(x)["parte"] for x in f.read_text(encoding="utf-8").splitlines())
    assert partes == ["clasificador_opus", "investigacion"]


def test_bot_cerca_del_tope_apaga_primero_opus(monkeypatch, tmp_path):
    fila, inv, opus = _ejecutar(
        monkeypatch, tmp_path, {"investigacion": 60.0}, preguntas_ejemplo()[1]
    )
    assert fila["clasificador_opus"] == {"estado": "tope_plan"} and opus.llamadas == []
    assert fila["investigacion"]["claude_estado"] == "ok" and len(inv.llamadas) == 1


def test_bot_en_el_tope_las_pares_van_con_la_busqueda_de_pago(monkeypatch, tmp_path):
    fila, inv, _ = _ejecutar(monkeypatch, tmp_path, {"investigacion": 69.0}, preguntas_ejemplo()[1])
    assert fila["investigacion"]["claude_estado"] == "tope_plan" and inv.llamadas == []
    assert fila["investigacion"]["base_estado"] == "ok"  # la búsqueda de pago, como sin cupo
    assert fila["pronostico"]


def test_en_github_el_bot_siempre_lleva_la_cuenta(monkeypatch):
    """Estructural: sin cuenta simulada, `ejecutar` monta la de verdad (tope finito)."""
    visto = {}

    def construir(params, publicar, llms=None, plan=None):
        visto["plan"] = plan
        raise SystemExit

    monkeypatch.setenv("METACULUS_TOKEN", "t")
    monkeypatch.setattr(main, "construir_bot", construir)
    with pytest.raises(SystemExit):
        main.ejecutar("test_questions")
    assert visto["plan"].tope == pytest.approx(70.0)


# ------------------------------------------------------------------ vigilancia


def _issue(horas_atras):
    creado = (LUNES_10 + timedelta(days=5) - timedelta(hours=horas_atras)).isoformat()
    return {"title": "[vigilancia] x", "created_at": creado}


def test_despertares_de_esta_semana():
    desde = LUNES_10 - timedelta(hours=1)
    issues = [_issue(20), _issue(50), {"title": "otro", "created_at": LUNES_10.isoformat()}]
    issues.append(
        {"title": "[vigilancia] viejo", "created_at": (desde - timedelta(hours=1)).isoformat()}
    )
    assert vg.despertares_semana(issues, desde) == 2


def test_la_vigilancia_no_despierta_a_claude_pasado_el_tope_semanal(monkeypatch, tmp_path):
    from tests.test_vigilancia import AHORA, GithubFalso, _relanzada, _run

    runs = [_relanzada(30), _relanzada(60), _run(200, "failure")]

    def revisar(issues, gastado):
        falso = GithubFalso(runs, issues)
        monkeypatch.setattr(vg.Github, "gastado_plan", lambda self, desde: gastado)
        monkeypatch.setenv("GITHUB_OUTPUT", str(tmp_path / "salida.txt"))
        gh = vg.Github("yo/repo", "t", 5, get=falso.get, post=falso.post)
        # sin la espera de 12 h entre despertares, para ver solo el tope semanal
        params = _params()
        params["vigilancia"]["horas_entre_claude"] = 0.5
        return vg.revisar(params, gh, AHORA, "main", contar=lambda: 0, hay_claude=True)

    # AHORA es lunes a las 12:00 UTC: la semana del plan empezó a las 09:00
    semana = [
        {"title": "[vigilancia] a", "created_at": (AHORA - timedelta(hours=h)).isoformat()}
        for h in (1, 2)
    ]
    assert revisar([], {}).accion == "relanzar_y_claude"
    assert revisar(semana, {}).accion == "relanzar"  # ya van 2 esta semana
    assert revisar([], {"investigacion": 66.0}).accion == "relanzar"  # 66 + 5 > 70


def test_lo_que_gasta_un_despertar_va_a_la_cuenta(monkeypatch, tmp_path):
    salida = json.dumps({"type": "result", "result": "ok", "total_cost_usd": 1.7})
    vg.despertar_claude(
        _params(), "x", "", ejecutar=lambda *a, **k: SimpleNamespace(returncode=0, stdout=salida)
    )
    vg.despertar_claude(
        _params(), "x", "", ejecutar=lambda *a, **k: SimpleNamespace(returncode=1, stdout="")
    )
    [f] = list((tmp_path / "plan").glob("plan_claude_*.jsonl"))
    usd = [json.loads(x)["usd"] for x in f.read_text(encoding="utf-8").splitlines()]
    assert usd == [1.7, 5.0]  # sin cifra, el freno de la vigilancia


# ------------------------------------------------------------------ marcador y flujos


def test_el_marcador_resume_el_plan_por_semana():
    lunes_0630 = datetime(2026, 10, 12, 6, 30, tzinfo=UTC)  # cuando sale el marcador
    filas = [
        _linea("investigacion", 2.0, 0),  # 05/10 10:00: semana del plan que acaba
        _linea("clasificador_opus", 0.5, 0),
        _linea("investigacion", 4.0, 24 * 3),  # 02/10: semana anterior
    ]
    r = pc.resumen(filas, _params(), lunes_0630)
    assert r["tope_usd"] == 70.0 and r["tope_puntos"] == 15.0
    assert r["semanas"]["esta"]["total_usd"] == 2.5
    assert r["semanas"]["esta"]["puntos_del_tope_semanal"] == 0.5
    assert r["semanas"]["anterior"]["partes"] == {"investigacion": 4.0}
    texto = "\n".join(pc.informe_md(r))
    assert "Plan de Claude" in texto and "| vigilancia | 0 | 0 |" in texto


def test_los_flujos_guardan_y_leen_la_cuenta_del_plan():
    import yaml

    raiz = Path(__file__).resolve().parent.parent / ".github" / "workflows"
    bot = yaml.safe_load((raiz / "run_bot_on_tournament.yaml").read_text(encoding="utf-8"))
    assert bot["permissions"]["actions"] == "read"
    pasos = bot["jobs"]["pronosticar"]["steps"]
    [ejecutar] = [p for p in pasos if p.get("name") == "Ejecutar el bot"]
    assert "GITHUB_TOKEN" in ejecutar["env"]
    subidas = [p["with"] for p in pasos if "upload-artifact" in str(p.get("uses"))]
    assert {"name": "plan-claude-${{ github.run_id }}", "path": "plan/"}.items() <= subidas[
        -1
    ].items()
    vig = (raiz / "vigilancia.yaml").read_text(encoding="utf-8")
    assert "plan-claude-${{ github.run_id }}" in vig
    assert 'startswith(\\"plan-claude-\\")' in (raiz / "marcador.yaml").read_text(encoding="utf-8")
