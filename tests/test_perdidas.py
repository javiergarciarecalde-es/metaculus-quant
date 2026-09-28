"""Lista semanal de preguntas perdidas (bot/perdidas.py) y el apunte de las que deja el tope."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import main
from bot import config as cfg
from bot import marcador as mc
from bot import perdidas
from bot.presupuesto import EstadoClave
from tests.conftest import MetaculusFalso, preguntas_ejemplo

AHORA = datetime(2026, 10, 12, 6, 30, tzinfo=UTC)


def _q(post, hecha, horas=24):
    return SimpleNamespace(
        id_of_post=post,
        id_of_question=post * 10,
        already_forecasted=hecha,
        page_url=f"https://www.metaculus.com/questions/{post}",
        close_time=AHORA - timedelta(hours=horas),
    )


def test_separa_las_del_tope_de_las_sin_explicar():
    cerradas = [("minibench", [_q(1, True), _q(2, False), _q(3, False)]), (33121, [_q(4, False)])]
    filas = [
        {"consulta": "dejadas", "motivo": "tope", "preguntas": [[2, 20]]},
        {"consulta": "openrouter_clave"},  # ruido
    ]
    r = perdidas.resumir(cerradas, filas, cfg.cargar_params())
    assert r["cerradas"] == 4 and r["con_pronostico"] == 1
    assert [p["url"][-1] for p in r["perdidas_por_el_tope"]] == ["2"]
    assert [p["url"][-1] for p in r["perdidas_sin_explicar"]] == ["3", "4"]
    assert not r["hubo_momentos_sin_dinero"]
    texto = "\n".join(perdidas.informe_md(r))
    assert "**Perdidas sin explicar** | **2**" in texto and "questions/4" in texto


def test_aviso_si_hubo_momentos_sin_dinero():
    filas = [{"consulta": "dejadas", "motivo": "sin_dinero", "preguntas": [[5, 50]]}]
    r = perdidas.resumir([("minibench", [_q(5, False)])], filas, cfg.cargar_params())
    assert r["hubo_momentos_sin_dinero"] and len(r["perdidas_por_el_tope"]) == 1
    assert "sin dinero" in "\n".join(perdidas.informe_md(r))


def test_sin_poder_preguntar_a_metaculus():
    r = perdidas.resumir(None, [], cfg.cargar_params())
    assert r == {"dias": 7.0, "consultado": False}
    assert "No se pudo" in "\n".join(perdidas.informe_md(r))


def test_el_bot_apunta_las_que_deja_el_tope(monkeypatch, llms, tmp_path):
    import bot.presupuesto as presupuesto

    # quedan 3,90 $: con 3 $ de reserva y 0,40 $ por pregunta caben 2 de las 3
    estado = EstadoClave(gastado=96.1, limite=100.0, restante=3.9)
    monkeypatch.setattr(presupuesto, "consultar_clave", lambda *a, **k: estado)
    monkeypatch.setenv("METACULUS_TOKEN", "t")
    monkeypatch.setenv("OPENROUTER_API_KEY", "clave-falsa")
    monkeypatch.setenv("ENVIO_REAL", "true")
    monkeypatch.setenv("GITHUB_EVENT_NAME", "schedule")
    falso = MetaculusFalso(preguntas_ejemplo())
    main.ejecutar("tournament", cliente=falso, llms=llms, consulta=lambda: estado)
    [f] = list((tmp_path / "registro").glob("presupuesto_*.jsonl"))
    filas = [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines()]
    dejadas = [x for x in filas if x.get("consulta") == "dejadas"]
    assert dejadas[0]["motivo"] == "tope" and dejadas[0]["torneo"] == "minibench"
    assert len(dejadas[0]["preguntas"]) == 1


def test_el_marcador_lleva_la_lista(tmp_path, monkeypatch):
    for nombre in ("HISTORICO", "RESUELTAS", "SALIDA_JSON", "SALIDA_MD"):
        monkeypatch.setattr(mc, nombre, tmp_path / getattr(mc, nombre).name)
    monkeypatch.setenv("METACULUS_TOKEN", "t")
    pedido = {}

    def falsa(torneos, desde, hasta):
        pedido.update(torneos=torneos, dias=(hasta - desde).days)
        return [("minibench", [_q(7, False)])]

    monkeypatch.setattr(perdidas, "buscar_cerradas", falsa)
    assert mc.main(["--descargas", str(tmp_path / "nada")]) == 0
    assert pedido == {"torneos": ["minibench", 33121], "dias": 7}
    md = (tmp_path / "MARCADOR.md").read_text(encoding="utf-8")
    assert "Preguntas perdidas" in md and "questions/7" in md
    datos = json.loads((tmp_path / "marcador.json").read_text(encoding="utf-8"))
    assert len(datos["perdidas"]["perdidas_sin_explicar"]) == 1


def test_si_metaculus_falla_el_marcador_sale_igual(tmp_path, monkeypatch):
    for nombre in ("HISTORICO", "RESUELTAS", "SALIDA_JSON", "SALIDA_MD"):
        monkeypatch.setattr(mc, nombre, tmp_path / getattr(mc, nombre).name)
    monkeypatch.setenv("METACULUS_TOKEN", "t")

    def rota(*a):
        raise ConnectionError("metaculus.com bloqueado")

    monkeypatch.setattr(perdidas, "buscar_cerradas", rota)
    assert mc.main(["--descargas", str(tmp_path / "nada")]) == 0
    assert "No se pudo preguntar" in (tmp_path / "MARCADOR.md").read_text(encoding="utf-8")


class ClienteAsincrono:
    """Como MetaculusClient 0.3.1: `get_questions_matching_filter` es asíncrona. Con un cliente
    así el marcador del 28/09/2026 habría fallado igual que en GitHub."""

    def __init__(self):
        self.filtros = []

    async def get_questions_matching_filter(self, filtro):
        self.filtros.append(filtro)
        return [_q(9, False)]


def test_buscar_cerradas_espera_a_la_libreria():
    cliente = ClienteAsincrono()
    desde, hasta = AHORA - timedelta(days=7), AHORA
    res = perdidas.buscar_cerradas(["minibench", 33121], desde, hasta, cliente=cliente)
    assert [t for t, _ in res] == ["minibench", 33121]
    assert all(isinstance(qs, list) and qs[0].id_of_post == 9 for _, qs in res)
    f = cliente.filtros[0]
    assert f.allowed_tournaments == ["minibench"] and set(f.allowed_statuses) == {
        "closed",
        "resolved",
    }
    assert f.close_time_gt == desde and f.close_time_lt == hasta


def test_la_libreria_de_verdad_es_asincrona():
    """Si la librería cambia (deja de ser asíncrona), esta prueba avisa."""
    import inspect

    from forecasting_tools import MetaculusClient

    assert inspect.iscoroutinefunction(MetaculusClient.get_questions_matching_filter)


def test_una_seccion_rota_no_tumba_el_marcador(tmp_path, monkeypatch):
    for nombre in ("HISTORICO", "RESUELTAS", "SALIDA_JSON", "SALIDA_MD"):
        monkeypatch.setattr(mc, nombre, tmp_path / getattr(mc, nombre).name)
    monkeypatch.setenv("METACULUS_TOKEN", "t")

    def rota(*a, **k):
        raise TypeError("'coroutine' object is not iterable")

    monkeypatch.setattr(perdidas, "buscar_cerradas", lambda *a: [])  # nada de red en las pruebas
    monkeypatch.setattr(perdidas, "resumir", rota)
    assert mc.main(["--descargas", str(tmp_path / "nada")]) == 0
    md = (tmp_path / "MARCADOR.md").read_text(encoding="utf-8")
    assert "Esta semana falló" in md and "En qué se va el dinero" in md
    datos = json.loads((tmp_path / "marcador.json").read_text(encoding="utf-8"))
    assert "error" in datos["perdidas"]
