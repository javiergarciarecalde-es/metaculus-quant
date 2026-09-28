"""Vigilancia que reacciona sola (bot/vigilancia.py), probada con fallos simulados.

La alarma de otro bot falló en silencio dos veces antes de funcionar: aquí se simula cada fallo
(reloj de GitHub parado, ejecución en rojo, preguntas olvidadas, GitHub que rechaza el relanzamiento
o cambia de forma) y se comprueba qué hace la vigilancia. Nada sale a internet.
"""

from __future__ import annotations

import io
import itertools
import zipfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from bot import config as cfg
from bot import vigilancia as vg
from bot.presupuesto import EstadoClave

RAIZ = Path(__file__).resolve().parent.parent
AHORA = datetime(2026, 10, 5, 12, 0, tzinfo=UTC)


def _run(
    minutos_atras: float,
    conclusion: str | None = "success",
    estado: str = "completed",
    evento: str = "schedule",
    titulo: str = "Pronosticar (tournament, schedule)",
    lanzador: str = "Kyou",
    id_: int | None = None,
    dura: float = 10,
) -> dict:
    creada = AHORA - timedelta(minutes=minutos_atras)
    return {
        "id": id_ or int(minutos_atras * 10) + 1,
        "status": estado,
        "conclusion": conclusion,
        "event": evento,
        "display_title": titulo,
        "created_at": creada.isoformat().replace("+00:00", "Z"),
        "updated_at": (creada + timedelta(minutes=dura)).isoformat().replace("+00:00", "Z"),
        "triggering_actor": {"login": lanzador},
    }


def _relanzada(minutos_atras: float, conclusion="failure") -> dict:
    return _run(
        minutos_atras,
        conclusion,
        evento="workflow_dispatch",
        titulo="Pronosticar (tournament, workflow_dispatch)",
        lanzador=vg.ACTOR_VIGILANCIA,
    )


def _decidir(runs: list[dict], pendientes=0, claude=True):
    ejecuciones = vg.leer_ejecuciones({"workflow_runs": runs})
    return vg.decidir(ejecuciones, pendientes, AHORA, cfg.cargar_params(), claude)


# --------------------------------------------------------------------------- decisión (pura)


def test_todo_en_orden_no_hace_nada():
    d = _decidir([_run(15), _run(35), _run(55)])
    assert d.accion == "nada" and not d.problemas


def test_reloj_de_github_parado_relanza():
    # la última buena terminó hace 60 min (> 45): el reloj de GitHub no lanzó las siguientes
    d = _decidir([_run(70), _run(90)])
    assert d.accion == "relanzar"
    assert any("silencio" in p for p in d.problemas)


def test_sin_ninguna_ejecucion_relanza():
    d = _decidir([])
    assert d.accion == "relanzar"


def test_ultima_en_rojo_relanza_y_guarda_su_id():
    d = _decidir([_run(15, "failure", id_=777), _run(35)])
    assert d.accion == "relanzar"
    assert any("fallo" in p for p in d.problemas)
    assert d.ultimas_fallidas == [777]


def test_se_acabo_el_tiempo_cuenta_como_fallo():
    assert _decidir([_run(15, "timed_out"), _run(35)]).accion == "relanzar"


def test_canceladas_y_omitidas_no_dicen_nada():
    # una cancelada (sustituida en la cola) encima de una buena reciente: todo bien
    d = _decidir([_run(5, "cancelled"), _run(8, "skipped"), _run(20)])
    assert d.accion == "nada"


def test_pruebas_a_mano_no_cuentan_como_ejecucion_buena():
    prueba = _run(
        10,
        evento="workflow_dispatch",
        titulo="Pronosticar (test_questions, workflow_dispatch)",
    )
    d = _decidir([prueba, _run(80)])
    assert d.accion == "relanzar"


def test_ejecuciones_viejas_sin_modo_en_el_titulo():
    # antes del 27/09 el título no llevaba el modo: las del reloj siguen contando como de torneo
    d = _decidir([_run(15, titulo="Pronosticar en el torneo")])
    assert d.accion == "nada"


def test_preguntas_olvidadas_relanzan_aunque_todo_este_verde():
    d = _decidir([_run(15)], pendientes=2)
    assert d.accion == "relanzar"
    assert any("olvidadas" in p for p in d.problemas)


def test_sin_poder_contar_preguntas_decide_con_lo_demas():
    assert _decidir([_run(15)], pendientes=None).accion == "nada"


def test_con_el_bot_en_marcha_espera():
    d = _decidir([_run(3, None, estado="in_progress"), _run(80)])
    assert d.accion == "esperar"
    d = _decidir([_run(1, None, estado="queued"), _run(15, "failure")])
    assert d.accion == "esperar"


def test_varios_relanzamientos_sin_arreglo_despiertan_a_claude():
    runs = [_relanzada(30), _relanzada(60), _run(200, "failure")]
    d = _decidir(runs)
    assert d.accion == "relanzar_y_claude"


def test_claude_no_permitido_solo_relanza():
    runs = [_relanzada(30), _relanzada(60), _run(200, "failure")]
    assert _decidir(runs, claude=False).accion == "relanzar"


def test_relanzamientos_viejos_no_cuentan():
    # fuera de la ventana de 3 h: se empieza de nuevo por el nivel 1
    runs = [_relanzada(200), _relanzada(230), _run(250, "failure")]
    assert _decidir(runs).accion == "relanzar"


def test_un_solo_relanzamiento_aun_no_despierta_a_claude():
    assert _decidir([_relanzada(30), _run(200, "failure")]).accion == "relanzar"


def test_relanzada_buena_cuenta_como_ejecucion_buena():
    assert _decidir([_relanzada(10, "success")]).accion == "nada"


# --------------------------------------------------------------------------- esquema de GitHub


@pytest.mark.parametrize(
    "respuesta",
    [None, {}, {"workflow_runs": "x"}, {"workflow_runs": [{"id": 1}]}, {"workflow_runs": [3]}],
)
def test_respuesta_de_github_con_otra_forma_es_error_claro(respuesta):
    with pytest.raises(vg.EsquemaGithubError):
        vg.leer_ejecuciones(respuesta)


def test_claude_reciente_por_issue():
    hace = (AHORA - timedelta(hours=2)).isoformat()
    issues = [
        {"title": "Otra cosa", "created_at": hace},
        {"title": "[vigilancia] El bot no se recupera solo", "created_at": hace},
    ]
    assert vg.claude_reciente(issues, AHORA, 12)
    assert not vg.claude_reciente(issues, AHORA, 1)
    assert not vg.claude_reciente(issues[:1], AHORA, 12)
    with pytest.raises(vg.EsquemaGithubError):
        vg.claude_reciente({"no": "lista"}, AHORA, 12)


def test_claude_en_pausa_usa_la_misma_pausa_que_la_investigacion():
    params = cfg.cargar_params()
    params["investigacion"]["claude_max"]["pausada_hasta_utc"] = "2026-10-05T13:00:00+00:00"
    assert vg.claude_en_pausa(params, AHORA)
    params["investigacion"]["claude_max"]["pausada_hasta_utc"] = None
    assert not vg.claude_en_pausa(params, AHORA)


# --------------------------------------------------------------------------- preguntas olvidadas


_NUMERO = itertools.count(1)


def _q(horas_abierta: float, ya=False, cierra_en_h: float = 48):
    n = next(_NUMERO)
    return SimpleNamespace(
        id_of_question=n,
        id_of_post=n,
        page_url=f"https://ejemplo/{n}",
        # como la respuesta de Metaculus (bot/normas.py): el historial de nuestros pronósticos
        api_json={"question": {"my_forecasts": {"history": [{"t": 1}] if ya else []}}},
        already_forecasted=ya,
        open_time=AHORA - timedelta(hours=horas_abierta),
        close_time=AHORA + timedelta(hours=cierra_en_h),
    )


def test_cuenta_solo_las_viejas_sin_pronostico():
    params = cfg.cargar_params()
    preguntas = [_q(3), _q(3, ya=True), _q(0.5)]  # vieja, ya hecha, recién abierta
    assert vg.contar_pendientes([("minibench", preguntas)], params, None, AHORA) == 1


def test_misma_regla_que_el_bot_para_saber_si_ya_esta_pronosticada():
    """Orden 27: la vigilancia no cuenta como olvidada una pregunta que el historial de Metaculus
    da por pronosticada aunque la librería diga que no (ni una que no se puede saber)."""
    params = cfg.cargar_params()
    hecha = _q(3, ya=True)
    hecha.already_forecasted = False
    rara = _q(3)
    rara.api_json = {"question": {}}
    assert vg.contar_pendientes([("minibench", [hecha, rara, _q(3)])], params, None, AHORA) == 1


def test_las_que_el_tope_deja_a_proposito_no_cuentan():
    params = cfg.cargar_params()
    # quedan 3,90 $: con 3 $ de reserva y 0,40 por pregunta caben 2
    estado = EstadoClave(gastado=96.1, limite=100.0, restante=3.9)
    preguntas = [_q(5, cierra_en_h=h) for h in (1, 2, 3, 4, 5)]
    assert vg.contar_pendientes([("minibench", preguntas)], params, estado, AHORA) == 2


def test_sin_dinero_no_hay_olvidadas():
    params = cfg.cargar_params()
    estado = EstadoClave(gastado=98.0, limite=100.0, restante=2.0)
    assert vg.contar_pendientes([("minibench", [_q(5)])], params, estado, AHORA) == 0


def test_la_temporada_va_al_ritmo_como_el_bot():
    params = cfg.cargar_params()
    temporada = params["torneos"]["temporada"]
    # 5/10: la línea de ritmo permite ~30 $; llevamos 40 $: la temporada espera a propósito
    estado = EstadoClave(gastado=40.0, limite=100.0, restante=60.0)
    assert vg.contar_pendientes([(temporada, [_q(5)])], params, estado, AHORA) == 0
    # la MiniBench no va al ritmo: esa sí cuenta
    assert vg.contar_pendientes([("minibench", [_q(5)])], params, estado, AHORA) == 1


# --------------------------------------------------------------------------- GitHub simulado


class Respuesta:
    def __init__(self, status=200, datos=None, contenido=b""):
        self.status_code, self._datos, self.content = status, datos, contenido

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._datos


class GithubFalso:
    def __init__(self, runs, issues=(), estado_post=204):
        self.runs, self.issues_, self.estado_post = runs, list(issues), estado_post
        self.posts = []

    def get(self, url, **k):
        if url.endswith("/runs"):
            return Respuesta(datos={"workflow_runs": self.runs})
        if url.endswith("/issues"):
            return Respuesta(datos=self.issues_)
        raise AssertionError(url)

    def post(self, url, **k):
        self.posts.append((url, k["json"]))
        return Respuesta(self.estado_post)


def _revisar(falso, monkeypatch, tmp_path, contar=lambda: 0, claude=True):
    salida = tmp_path / "salida.txt"
    monkeypatch.setenv("GITHUB_OUTPUT", str(salida))
    gh = vg.Github("yo/repo", "t", 5, get=falso.get, post=falso.post)
    d = vg.revisar(cfg.cargar_params(), gh, AHORA, "main", contar=contar, hay_claude=claude)
    return d, salida.read_text(encoding="utf-8")


def test_revisar_relanza_el_flujo_del_bot_en_modo_torneo(monkeypatch, tmp_path):
    falso = GithubFalso([_run(90)])
    d, salida = _revisar(falso, monkeypatch, tmp_path)
    assert d.accion == "relanzar"
    url, cuerpo = falso.posts[0]
    assert url.endswith("/actions/workflows/run_bot_on_tournament.yaml/dispatches")
    assert cuerpo == {"ref": "main", "inputs": {"modo": "tournament"}}
    assert "accion=relanzar" in salida


def test_revisar_sin_problema_no_relanza(monkeypatch, tmp_path):
    falso = GithubFalso([_run(15)])
    d, salida = _revisar(falso, monkeypatch, tmp_path)
    assert d.accion == "nada" and not falso.posts
    assert "accion=nada" in salida


def test_github_rechaza_el_relanzamiento_sale_en_rojo(monkeypatch, tmp_path):
    # que no falle en silencio: sin permiso (403) la vigilancia termina con error
    falso = GithubFalso([_run(90)], estado_post=403)
    with pytest.raises(RuntimeError, match="403"):
        _revisar(falso, monkeypatch, tmp_path)


def test_fallo_al_contar_preguntas_no_tumba_la_vigilancia(monkeypatch, tmp_path):
    def roto():
        raise ConnectionError("metaculus.com bloqueado")

    d, _ = _revisar(GithubFalso([_run(90)]), monkeypatch, tmp_path, contar=roto)
    assert d.accion == "relanzar"


def test_issue_reciente_evita_despertar_otra_vez_a_claude(monkeypatch, tmp_path):
    reciente = {"title": "[vigilancia] x", "created_at": (AHORA - timedelta(hours=1)).isoformat()}
    runs = [_relanzada(30), _relanzada(60), _run(200, "failure")]
    d, _ = _revisar(GithubFalso(runs, [reciente]), monkeypatch, tmp_path)
    assert d.accion == "relanzar"
    d, salida = _revisar(GithubFalso(runs, []), monkeypatch, tmp_path)
    assert d.accion == "relanzar_y_claude" and "accion=relanzar_y_claude" in salida


def test_errores_de_solo_baja_lineas_de_error():
    registro = (
        "2026-10-05T11:00:00.1Z Investigación para https://q/1:\n"
        "2026-10-05T11:00:00.2Z La inflación de octubre será del 3 % según el informe\n"
        "2026-10-05T11:00:01.0Z Traceback (most recent call last):\n"
        '2026-10-05T11:00:01.1Z   File "main.py", line 5, in <module>\n'
        "2026-10-05T11:00:01.2Z KeyError: 'x'\n"
        "2026-10-05T11:00:02.0Z ::error::Fallaron las 3 preguntas\n"
    )
    zbytes = io.BytesIO()
    with zipfile.ZipFile(zbytes, "w") as z:
        z.writestr("0_pronosticar.txt", registro)
        z.writestr("pronosticar/1_paso.txt", registro)  # repetido dentro: no se lee dos veces
    gh = vg.Github("yo/repo", "t", 5, get=lambda *a, **k: Respuesta(contenido=zbytes.getvalue()))
    texto = gh.errores_de(1, 10_000)
    assert "Traceback" in texto and "KeyError: 'x'" in texto and "::error::Fallaron" in texto
    assert 'File "main.py"' in texto
    assert "inflación" not in texto  # nada del contenido de las preguntas ni la investigación
    assert texto.count("::error::Fallaron") == 1


# --------------------------------------------------------------------------- límites de Claude


def test_rutas_prohibidas_para_el_arreglo_de_claude():
    assert vg.rutas_fuera_de_limites([".github/workflows/x.yaml", "bot/registro.py"]) == []
    malas = vg.rutas_fuera_de_limites(
        ["config/params.yaml", "main.py", "bot/agregacion.py", "tests/datos/f.json", "README.md"]
    )
    assert malas == ["config/params.yaml", "main.py", "bot/agregacion.py", "tests/datos/f.json"]


def test_orden_de_claude_con_topes_y_sin_internet_ni_push():
    orden = vg.orden_claude(cfg.cargar_params())
    assert orden[orden.index("--max-turns") + 1] == "40"
    assert orden[orden.index("--max-budget-usd") + 1] == "5"
    permitidas = orden[orden.index("--allowedTools") + 1 : orden.index("--disallowedTools")]
    assert "WebSearch" not in permitidas and "WebFetch" not in permitidas
    assert not any("push" in x or x.startswith("Bash(gh") for x in permitidas)
    assert "Bash(git push:*)" in orden[orden.index("--disallowedTools") :]


def test_prompt_de_claude_lleva_las_reglas_duras():
    d = vg.Diagnostico("relanzar_y_claude", ["fallo: x"], "sigue")
    texto = vg.prompt_claude(d, "KeyError: 'x'")
    for regla in ("Never forecast", "config/params.yaml", "open questions", "Never push"):
        assert regla in texto
    assert vg.FICHERO_DIAGNOSTICO in texto and "KeyError" in texto


def test_claude_no_recibe_las_claves(monkeypatch):
    for k in ("METACULUS_TOKEN", "OPENROUTER_API_KEY", "GITHUB_TOKEN"):
        monkeypatch.setenv(k, "secreto")
    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "el-de-claude")
    visto = {}

    def ejecutar(orden, **k):
        visto.update(k)
        return SimpleNamespace(returncode=0)

    vg.despertar_claude(cfg.cargar_params(), "fallo", "errores", ejecutar=ejecutar)
    entorno = visto["env"]
    assert "METACULUS_TOKEN" not in entorno and "OPENROUTER_API_KEY" not in entorno
    assert "GITHUB_TOKEN" not in entorno
    assert entorno["CLAUDE_CODE_OAUTH_TOKEN"] == "el-de-claude"
    assert "Never forecast" in visto["input"]


# --------------------------------------------------------------------------- el flujo de GitHub


def _flujo(nombre: str) -> dict:
    return yaml.safe_load((RAIZ / ".github" / "workflows" / nombre).read_text(encoding="utf-8"))


def test_flujo_de_vigilancia_inofensivo_y_con_los_permisos_justos():
    f = _flujo("vigilancia.yaml")
    revisar, claude = f["jobs"]["revisar"], f["jobs"]["claude"]
    assert revisar["if"] == "vars.ENVIO_REAL == 'true'"
    assert revisar["permissions"]["actions"] == "write"
    assert f["permissions"] == {"contents": "read"}
    assert claude["needs"] == "revisar"
    assert "relanzar_y_claude" in claude["if"]
    checkout = claude["steps"][0]
    assert checkout["with"]["persist-credentials"] is False
    todo = "\n".join(str(paso.get("run", "")) for paso in claude["steps"])
    assert "refs/heads/$rama" in todo and 'rama="vigilancia/arreglo-' in todo
    assert "HEAD:main" not in todo and "refs/heads/main" not in todo


def test_vigilancia_desfasada_del_bot():
    bot = _flujo("run_bot_on_tournament.yaml")
    vig = _flujo("vigilancia.yaml")

    def minutos(f):
        disparo = f.get("on", f.get(True))
        return {int(m) for c in disparo["schedule"] for m in c["cron"].split()[0].split(",")}

    assert not minutos(bot) & minutos(vig)
    assert len(minutos(vig)) >= 2  # el reloj de GitHub falla: más de una oportunidad por hora


def test_el_titulo_del_bot_lleva_el_modo():
    # sin esto la vigilancia no distingue una prueba a mano de una ejecución de torneo
    assert "inputs.modo" in _flujo("run_bot_on_tournament.yaml")["run-name"]


def test_prueba_manual_relanza_aunque_todo_vaya_bien_pero_nunca_despierta_a_claude(
    monkeypatch, tmp_path
):
    """Orden 27: para comprobar en GitHub de verdad que la vigilancia sabe relanzar el bot."""
    falso = GithubFalso([_run(15)])
    salida = tmp_path / "salida.txt"
    monkeypatch.setenv("GITHUB_OUTPUT", str(salida))
    gh = vg.Github("yo/repo", "t", 5, get=falso.get, post=falso.post)
    d = vg.revisar(cfg.cargar_params(), gh, AHORA, "main", contar=lambda: 0, probar=True)
    assert d.accion == "relanzar" and "prueba manual" in d.motivo
    [(url, cuerpo)] = falso.posts
    assert url.endswith("/actions/workflows/run_bot_on_tournament.yaml/dispatches")
    assert cuerpo == {"ref": "main", "inputs": {"modo": "tournament"}}
    # con una ejecución del bot en marcha, ni la prueba relanza (se espera)
    falso = GithubFalso([{**_run(15), "status": "in_progress", "conclusion": None}, _run(15)])
    gh = vg.Github("yo/repo", "t", 5, get=falso.get, post=falso.post)
    assert vg.revisar(
        cfg.cargar_params(), gh, AHORA, "main", contar=lambda: 0, probar=True
    ).accion in ("nada", "esperar")
    assert not falso.posts
