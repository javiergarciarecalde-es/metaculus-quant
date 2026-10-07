"""Vigilancia que reacciona sola (orden 26 del mando; decisión del usuario del 27/09/2026 ~21:55).

El usuario no quiere alarmas: si el bot se calla o falla, algo automático tiene que arreglarlo sin
avisarle. La hace el flujo `.github/workflows/vigilancia.yaml` (dos veces por hora, desfasado del
bot), y solo con `ENVIO_REAL=true`. Mira tres cosas:

(a) **Silencio:** el bot lleva más de `vigilancia.minutos_sin_ejecucion_buena` sin terminar bien
    una ejecución de torneo (p. ej. el reloj de GitHub no lo lanzó: a otro bot le pasó 78 % de las
    veces).
(b) **Fallo:** la última ejecución de torneo terminada salió en rojo.
(c) **Preguntas olvidadas:** hay preguntas abiertas hace más de
    `vigilancia.minutos_margen_pregunta_nueva` sin pronóstico nuestro **que el tope de gasto sí
    dejaría hacer**. Las que el tope deja fuera a propósito no cuentan (misma cuenta que el bot,
    `presupuesto.decidir`, con el mismo orden: primero lo que cierra antes).

Si hay problema y no hay ya una ejecución del bot en marcha:
- **Nivel 1:** relanza el flujo del bot a mano (`workflow_dispatch`, modo torneo).
- **Nivel 2:** si ya van `vigilancia.relanzamientos_antes_de_claude` relanzamientos en las últimas
  `vigilancia.ventana_horas_relanzamientos` horas y el problema sigue, despierta a Claude Code (con
  el plan del usuario, topes de turnos y de dinero) para que diagnostique con las líneas de error
  del registro. Como mucho una vez cada `vigilancia.horas_entre_claude` horas y
  `vigilancia.max_despertares_semana` veces por semana del plan, nunca mientras la investigación
  con Claude esté en pausa ni pasado el tope semanal del plan (`bot/plan_claude.py`, orden 27).
  Lo que gasta cada despertar se apunta en la cuenta del plan.

Lo que Claude NUNCA puede hacer aquí (reglas del torneo y del usuario): pronosticar ni tocar
pronósticos, cambiar `config/params.yaml` o lo que decide los pronósticos (`RUTAS_PROHIBIDAS`), ni
mirar preguntas abiertas para retocar el bot. Solo ve líneas de error (no el texto de las
preguntas ni la investigación). Como mucho deja un arreglo de infraestructura en una rama (nunca en
`main`) y un issue con el diagnóstico para la siguiente sesión o el mando.

Todo lo que decide es puro (`decidir`, `rutas_fuera_de_limites`...) y se prueba con fallos
simulados: la alarma de otro bot falló en silencio dos veces antes de funcionar. La red va aparte
(`Github`), con el esquema de las respuestas comprobado: si GitHub cambia de forma, sale en rojo.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import subprocess
import sys
import zipfile
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import requests

from bot import normas, plan_claude, presupuesto
from bot import params as ajustes

API = "https://api.github.com"
ACTOR_VIGILANCIA = "github-actions[bot]"  # quien lanza con el GITHUB_TOKEN del flujo
PREFIJO_ISSUE = "[vigilancia]"
FICHERO_DIAGNOSTICO = "diagnostico_vigilancia.md"  # lo escribe Claude; nunca se sube (.gitignore)
# Conclusiones de GitHub que son un fallo del bot. «cancelled» no: pasa cuando una ejecución en
# cola se sustituye por otra más nueva (concurrency del flujo). «skipped»: envío apagado.
FALLOS = ("failure", "timed_out", "startup_failure")
EN_MARCHA = ("queued", "in_progress", "waiting", "requested", "pending")
# Lo que decide los pronósticos, la configuración y la foto que lo vigila: Claude no lo toca.
RUTAS_PROHIBIDAS = (
    "config/",
    "main.py",
    "bot/agregacion.py",
    "bot/investigacion.py",
    "bot/claude_max.py",
    "bot/modelos.py",
    "bot/presupuesto.py",
    "bot/params.py",
    "bot/config.py",
    "tests/datos/",
    "tests/test_configuracion_igual.py",
    "CHANGELOG.md",
    "docs/DECISIONES.md",
    "CLAUDE.md",
)
# Claves que Claude no necesita para diagnosticar: no se le pasan (ni el token de GitHub).
CLAVES_OCULTAS = (
    "METACULUS_TOKEN",
    "OPENROUTER_API_KEY",
    "ASKNEWS_CLIENT_ID",
    "ASKNEWS_SECRET",
    "GITHUB_TOKEN",
    "GH_TOKEN",
)
# Líneas del registro de GitHub que se le enseñan a Claude: solo errores y avisos (no el texto de
# las preguntas ni la investigación, que el bot también escribe en el registro).
LINEA_DE_ERROR = re.compile(
    r"::error|::warning| - ERROR - | - WARNING - | - CRITICAL - |Traceback|"
    r"Process completed with exit code|Error:|Exception:"
)


class EsquemaGithubError(ValueError):
    """La respuesta de la API de GitHub no tiene la forma esperada."""


@dataclass(frozen=True)
class Ejecucion:
    """Una ejecución del flujo del bot, según la API de GitHub."""

    id: int
    estado: str  # «status»: queued, in_progress, completed...
    conclusion: str | None  # success, failure, cancelled, skipped, timed_out... (None si no acabó)
    evento: str  # schedule, workflow_dispatch...
    titulo: str  # «display_title» (lleva el modo desde el 27/09/2026, `run-name` del flujo)
    creada: datetime
    actualizada: datetime
    lanzador: str  # «triggering_actor.login»

    @property
    def de_torneo(self) -> bool:
        """Las del reloj siempre son de torneo; las manuales, solo si el título lo dice."""
        return self.evento == "schedule" or "tournament" in self.titulo

    @property
    def de_la_vigilancia(self) -> bool:
        return self.evento == "workflow_dispatch" and self.lanzador == ACTOR_VIGILANCIA


@dataclass
class Diagnostico:
    accion: str  # nada | esperar | relanzar | relanzar_y_claude
    problemas: list[str] = field(default_factory=list)
    motivo: str = ""
    ultimas_fallidas: list[int] = field(default_factory=list)  # ids para bajar sus errores


def _fecha_github(texto: Any) -> datetime:
    if not isinstance(texto, str):
        raise EsquemaGithubError(f"fecha de GitHub sin formato: {texto!r}")
    return datetime.fromisoformat(texto.replace("Z", "+00:00"))


def leer_ejecuciones(respuesta: Any) -> list[Ejecucion]:
    """Valida `GET /actions/workflows/{flujo}/runs` y saca lo necesario. Error claro si cambia."""
    if not isinstance(respuesta, dict) or not isinstance(respuesta.get("workflow_runs"), list):
        raise EsquemaGithubError("la respuesta de GitHub no trae «workflow_runs»")
    res = []
    for r in respuesta["workflow_runs"]:
        if not isinstance(r, dict):
            raise EsquemaGithubError("una ejecución de GitHub no es un objeto")
        for campo in ("id", "status", "event", "created_at", "updated_at"):
            if campo not in r:
                raise EsquemaGithubError(f"a una ejecución de GitHub le falta «{campo}»")
        actor = r.get("triggering_actor") or r.get("actor") or {}
        res.append(
            Ejecucion(
                id=int(r["id"]),
                estado=str(r["status"]),
                conclusion=r.get("conclusion"),
                evento=str(r["event"]),
                titulo=str(r.get("display_title") or r.get("name") or ""),
                creada=_fecha_github(r["created_at"]),
                actualizada=_fecha_github(r["updated_at"]),
                lanzador=str(actor.get("login", "")) if isinstance(actor, dict) else "",
            )
        )
    return sorted(res, key=lambda e: e.creada, reverse=True)  # lo más nuevo primero


def claude_reciente(issues: Any, ahora: datetime, horas: float) -> bool:
    """True si la vigilancia ya abrió un issue (es decir, ya despertó a Claude) hace poco."""
    if not isinstance(issues, list):
        raise EsquemaGithubError("la lista de issues de GitHub no es una lista")
    for i in issues:
        if not isinstance(i, dict) or not str(i.get("title", "")).startswith(PREFIJO_ISSUE):
            continue
        if ahora - _fecha_github(i.get("created_at")) < timedelta(hours=horas):
            return True
    return False


def despertares_semana(issues: Any, desde: datetime) -> int:
    """Cuántas veces se ha despertado a Claude (issues de la vigilancia) desde `desde`."""
    if not isinstance(issues, list):
        raise EsquemaGithubError("la lista de issues de GitHub no es una lista")
    return sum(
        1
        for i in issues
        if isinstance(i, dict)
        and str(i.get("title", "")).startswith(PREFIJO_ISSUE)
        and _fecha_github(i.get("created_at")) >= desde
    )


def decidir(
    ejecuciones: list[Ejecucion],
    pendientes: int | None,
    ahora: datetime,
    params: dict,
    claude_permitido: bool,
) -> Diagnostico:
    """Qué hacer ahora. `pendientes`: preguntas olvidadas que el tope sí dejaría hacer (None = no
    se pudieron contar). `claude_permitido`: hay secreto, no está en pausa y no se despertó hace
    poco."""
    silencio = float(ajustes.p("vigilancia.minutos_sin_ejecucion_buena", params))
    ventana = float(ajustes.p("vigilancia.ventana_horas_relanzamientos", params))
    necesarios = int(ajustes.p("vigilancia.relanzamientos_antes_de_claude", params))

    torneo = [e for e in ejecuciones if e.de_torneo]
    terminadas = [e for e in torneo if e.estado == "completed"]
    # «cancelled» y «skipped» no dicen nada de la salud del bot
    con_veredicto = [e for e in terminadas if e.conclusion not in ("cancelled", "skipped")]
    buenas = [e for e in con_veredicto if e.conclusion == "success"]

    problemas = []
    if not buenas:
        problemas.append("no hay ninguna ejecución de torneo terminada bien en las últimas vistas")
    else:
        minutos = (ahora - buenas[0].actualizada).total_seconds() / 60
        if minutos > silencio:
            problemas.append(
                f"silencio: la última ejecución buena terminó hace {minutos:.0f} min "
                f"(límite {silencio:.0f})"
            )
    if con_veredicto and con_veredicto[0].conclusion in FALLOS:
        problemas.append(
            f"fallo: la última ejecución terminada ({con_veredicto[0].id}) salió "
            f"«{con_veredicto[0].conclusion}»"
        )
    if pendientes:
        problemas.append(
            f"preguntas olvidadas: {pendientes} abiertas sin pronóstico que el tope sí permite"
        )
    fallidas = [e.id for e in con_veredicto if e.conclusion in FALLOS][:3]

    if not problemas:
        return Diagnostico("nada", [], "todo en orden", fallidas)
    en_marcha = [e for e in ejecuciones if e.estado in EN_MARCHA]
    if en_marcha:
        return Diagnostico(
            "esperar",
            problemas,
            f"hay una ejecución del bot en marcha ({en_marcha[0].id}): se espera a que acabe",
            fallidas,
        )
    recientes = [
        e for e in ejecuciones if e.de_la_vigilancia and ahora - e.creada < timedelta(hours=ventana)
    ]
    if len(recientes) >= necesarios:
        if claude_permitido:
            return Diagnostico(
                "relanzar_y_claude",
                problemas,
                f"el problema sigue tras {len(recientes)} relanzamientos en {ventana:.0f} h: "
                "se relanza otra vez y se despierta a Claude para diagnosticar",
                fallidas,
            )
        motivo = (
            f"el problema sigue tras {len(recientes)} relanzamientos; Claude no se despierta "
            "(apagada en config/params.yaml, sin secreto, en pausa, ya se despertó hace poco "
            "o se llegó al tope semanal de despertares o del plan): solo se relanza"
        )
        return Diagnostico("relanzar", problemas, motivo, fallidas)
    return Diagnostico("relanzar", problemas, "se relanza el bot (nivel 1)", fallidas)


def contar_pendientes(preguntas_por_torneo: list[tuple], params: dict, estado, ahora) -> int:
    """Preguntas abiertas hace más del margen, sin pronóstico nuestro, que el tope de gasto dejaría
    empezar ahora. `preguntas_por_torneo`: [(torneo, [preguntas]), ...] en el orden del bot
    (MiniBench primero). `estado`: el de la clave de OpenRouter (None = sin clave: sin tope, como
    el bot)."""
    from main import _primero_lo_que_cierra_antes  # el mismo orden que usa el bot

    margen = timedelta(minutes=float(ajustes.p("vigilancia.minutos_margen_pregunta_nueva", params)))
    coste = float(ajustes.p("presupuesto.coste_previsto_por_pregunta_usd", params))
    temporada = ajustes.p("torneos.temporada", params)
    total = 0
    previsto = 0.0  # lo que gastaría el bot en los torneos anteriores de esta misma cuenta
    for torneo, preguntas in preguntas_por_torneo:
        # la misma regla que el bot (bot/normas.py): las que no se sabe si ya pronosticamos no
        # cuentan como olvidadas (el bot sale en rojo por ellas y eso ya lo ve la vigilancia)
        sin_hacer = _primero_lo_que_cierra_antes(normas.sin_pronostico_nuestro(preguntas)[0])
        if estado is not None and sin_hacer:
            decision = presupuesto.decidir(estado, params, ahora, torneo == temporada, previsto)
            if decision.sin_dinero:
                break
            sin_hacer = sin_hacer[: decision.max_preguntas]
        previsto += len(sin_hacer) * coste
        for q in sin_hacer:
            abierta = getattr(q, "open_time", None)
            if abierta is not None and abierta.tzinfo is None:
                abierta = abierta.replace(tzinfo=UTC)
            if abierta is not None and ahora - abierta > margen:
                total += 1
    return total


def rutas_fuera_de_limites(cambiadas: list[str]) -> list[str]:
    """Ficheros de un arreglo de Claude que tocan lo prohibido (vacía = se puede subir)."""
    malas = []
    for ruta in cambiadas:
        r = ruta.strip().replace("\\", "/")
        if r and any(r == p or r.startswith(p) for p in RUTAS_PROHIBIDAS):
            malas.append(r)
    return malas


def filtrar_errores(texto: str, max_caracteres: int) -> str:
    """Solo las líneas de error y aviso del registro de GitHub (y las de cada «Traceback»)."""
    salida = []
    en_traza = False
    for linea in texto.splitlines():
        # quita la marca de hora que GitHub pone delante de cada línea
        limpia = re.sub(r"^\d{4}-\d\d-\d\dT[\d:.]+Z ", "", linea)
        if LINEA_DE_ERROR.search(limpia):
            salida.append(limpia)
            en_traza = "Traceback" in limpia
        elif en_traza and (limpia.startswith((" ", "\t")) or re.match(r"^\w+(\.\w+)*: ", limpia)):
            salida.append(limpia)
        else:
            en_traza = False
    texto = "\n".join(salida)
    return texto[-max_caracteres:]  # lo último es lo que más importa


def prompt_claude(diag: Diagnostico, errores: str) -> str:
    return (
        "You are the on-call engineer for an autonomous Metaculus forecasting bot (this "
        "repository). An automatic watchdog found a problem that relaunching the bot did not fix.\n"
        "HARD RULES (tournament rules and the owner's rules; breaking any of them is worse than "
        "not fixing):\n"
        "- Never forecast, never submit or edit a forecast, never contact Metaculus.\n"
        "- Do not change config/params.yaml or anything that decides forecasts (prompts, "
        f"aggregation, models, budget). Forbidden paths: {', '.join(RUTAS_PROHIBIDAS)}.\n"
        "- Do not look at open questions or their content to tune the bot.\n"
        "- Never push. At most, commit a small INFRASTRUCTURE fix (workflow, dependency, crash in "
        "logging/registry code) on the current branch with tests passing (python -m pytest -q, "
        "ruff format --check ., ruff check .). A later step checks the paths and pushes it to a "
        "separate branch; it never reaches main without a human session.\n"
        f"- Write your diagnosis in Spanish, in plain words, to the file {FICHERO_DIAGNOSTICO}: "
        "what failed, the likely cause, what you changed (if anything) and what the next session "
        "should do. It is read by a non-programmer, so explain each technical term.\n\n"
        f"Watchdog findings: {'; '.join(diag.problemas)}. {diag.motivo}.\n\n"
        "Error and warning lines from the latest failed bot runs (the rest of the log is hidden "
        "on purpose):\n"
        f"{errores or '(no failed runs with error lines: the bot may not be running at all; check the workflow files and the schedule)'}\n"  # noqa: E501 (texto para el modelo)
    )


def orden_claude(params: dict) -> list[str]:
    """Claude Code sin internet y sin `git push` ni `gh`: lee el repositorio, prueba y, como
    mucho, hace commit en local."""
    return [
        "claude",
        "-p",
        "Follow the brief given on stdin.",
        "--model",
        str(ajustes.p("vigilancia.claude.modelo", params)),
        "--max-turns",
        str(int(ajustes.p("vigilancia.claude.max_turnos", params))),
        "--max-budget-usd",
        str(ajustes.p("vigilancia.claude.tope_usd", params)),
        "--output-format",
        "json",
        "--allowedTools",
        "Read",
        "Grep",
        "Glob",
        "Edit",
        "Write",
        "Bash(git status:*)",
        "Bash(git diff:*)",
        "Bash(git log:*)",
        "Bash(git add:*)",
        "Bash(git commit:*)",
        "Bash(python -m pytest:*)",
        "Bash(ruff:*)",
        "--disallowedTools",
        "WebSearch",
        "WebFetch",
        "Bash(git push:*)",
        "Bash(gh:*)",
        "Bash(curl:*)",
        "--no-session-persistence",
    ]


def claude_en_pausa(params: dict, ahora: datetime) -> bool:
    """La misma pausa que la investigación con Claude: si se cuida el plan, tampoco aquí."""
    hasta = ajustes.p("investigacion.claude_max.pausada_hasta_utc", params)
    return hasta is not None and ahora < datetime.fromisoformat(str(hasta))


##################################### RED (GitHub) #####################################


class Github:
    """Lo mínimo de la API de GitHub, con el GITHUB_TOKEN del flujo. `get`/`post` se cambian en
    las pruebas por unos simulados."""

    def __init__(self, repo: str, token: str, espera: float, get=requests.get, post=requests.post):
        self.repo, self.espera = repo, espera
        self._get, self._post = get, post
        self._token = token
        self._cab = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _leer(self, ruta: str, **query) -> Any:
        r = self._get(f"{API}/repos/{self.repo}/{ruta}", headers=self._cab, params=query,
                      timeout=self.espera)  # fmt: skip
        r.raise_for_status()
        return r.json()

    def ejecuciones(self, flujo: str, cuantas: int) -> list[Ejecucion]:
        return leer_ejecuciones(self._leer(f"actions/workflows/{flujo}/runs", per_page=cuantas))

    def issues(self) -> Any:
        return self._leer("issues", state="all", per_page=30, sort="created", direction="desc")

    def gastado_plan(self, desde: datetime) -> dict[str, float]:
        """Lo gastado del plan de Claude desde `desde` (artefactos «plan-claude-*»)."""
        return plan_claude.leer_de_github(self.repo, self._token, desde, self.espera, self._get)

    def relanzar(self, flujo: str, rama: str) -> None:
        """Nivel 1. GitHub contesta 204 sin cuerpo si lo acepta; cualquier otra cosa es un error
        rojo (que no falle en silencio, como la alarma de otro bot)."""
        r = self._post(
            f"{API}/repos/{self.repo}/actions/workflows/{flujo}/dispatches",
            headers=self._cab,
            json={"ref": rama, "inputs": {"modo": "tournament"}},
            timeout=self.espera,
        )
        if r.status_code != 204:
            raise RuntimeError(f"GitHub no aceptó el relanzamiento (HTTP {r.status_code})")

    def errores_de(self, ejecucion: int, max_caracteres: int) -> str:
        """Baja el registro de una ejecución (un zip) y se queda solo con las líneas de error."""
        r = self._get(
            f"{API}/repos/{self.repo}/actions/runs/{ejecucion}/logs",
            headers=self._cab,
            timeout=self.espera,
        )
        r.raise_for_status()
        texto = []
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            for nombre in sorted(z.namelist()):
                if (
                    "/" in nombre
                ):  # en la raíz va el registro entero de cada trabajo; dentro, repetido
                    continue
                texto.append(z.read(nombre).decode("utf-8", errors="replace"))
        return filtrar_errores("\n".join(texto), max_caracteres)


def preguntas_abiertas(params: dict) -> list[tuple]:
    """Solo lectura: las preguntas abiertas de cada torneo, en el orden del bot."""
    from forecasting_tools import MetaculusClient

    cliente = MetaculusClient()
    torneos = [ajustes.p("torneos.minibench", params), ajustes.p("torneos.temporada", params)]
    return [(t, cliente.get_all_open_questions_from_tournament(t)) for t in torneos]


##################################### ÓRDENES #####################################


def _salida(nombre: str, valor: str) -> None:
    """Deja un valor para los pasos siguientes del flujo (GITHUB_OUTPUT)."""
    ruta = os.getenv("GITHUB_OUTPUT")
    if ruta:
        with open(ruta, "a", encoding="utf-8") as f:
            f.write(f"{nombre}={valor}\n")


def _resumen(texto: str) -> None:
    ruta = os.getenv("GITHUB_STEP_SUMMARY")
    if ruta:
        with open(ruta, "a", encoding="utf-8") as f:
            f.write(texto + "\n")


def revisar(
    params: dict,
    gh: Github,
    ahora: datetime,
    rama: str,
    contar=None,
    hay_claude: bool | None = None,
    probar: bool = False,
) -> Diagnostico:
    """Lo que hace el trabajo «revisar» del flujo: mirar, decidir y (si toca) relanzar.

    `contar`: función sin argumentos que da las preguntas olvidadas (en las pruebas, simulada);
    por defecto pregunta a Metaculus y a la clave (si hay token y clave; si falla, None)."""
    from bot import config as cfg

    flujo = ajustes.p("vigilancia.flujo_bot", params)
    ejecuciones = gh.ejecuciones(flujo, int(ajustes.p("vigilancia.ejecuciones_a_mirar", params)))
    if contar is None:
        contar = _contar_de_verdad(params, ahora)
    try:
        pendientes = contar()
    except Exception as e:  # sin la cuenta de preguntas se decide con (a) y (b)
        print(f"::warning::No se pudieron contar las preguntas olvidadas ({type(e).__name__}).")
        pendientes = None
    if hay_claude is None:
        hay_claude = cfg.hay("CLAUDE_CODE_OAUTH_TOKEN")
    horas = float(ajustes.p("vigilancia.horas_entre_claude", params))
    issues = gh.issues()
    desde = plan_claude.inicio_semana(ahora, params)
    # orden 27 (28/09/2026): como mucho N despertares por semana del plan y nunca pasado su tope
    maximo = int(ajustes.p("vigilancia.max_despertares_semana", params))
    # orden 82 (07/10/2026): `vigilancia.claude.activo` = false -> nunca despierta a Claude
    permitido = (
        bool(ajustes.p("vigilancia.claude.activo", params))
        and hay_claude
        and not claude_en_pausa(params, ahora)
        and not claude_reciente(issues, ahora, horas)
        and despertares_semana(issues, desde) < maximo
        and plan_claude.contador(params, leer=lambda: gh.gastado_plan(desde)).empezar(
            "vigilancia", float(ajustes.p("vigilancia.claude.tope_usd", params))
        )
    )
    diag = decidir(ejecuciones, pendientes, ahora, params, permitido)
    if probar and diag.accion == "nada":
        # prueba manual del relanzamiento (orden 27, 28/09/2026): lo mismo que el nivel 1,
        # sin Claude. Permitido por las normas: el bot solo hace las preguntas que faltan.
        if any(e.estado in EN_MARCHA for e in ejecuciones):
            diag = Diagnostico("esperar", [], "prueba manual: hay una ejecución en marcha", [])
        else:
            diag = Diagnostico("relanzar", [], "prueba manual del relanzamiento", [])
    print(f"Vigilancia: {diag.accion}. {diag.motivo}. Problemas: {diag.problemas or 'ninguno'}")
    if diag.accion.startswith("relanzar"):
        gh.relanzar(flujo, rama)
        print("::notice::Vigilancia: bot relanzado (modo torneo).")
    _salida("accion", diag.accion)
    _salida("fallidas", ",".join(str(i) for i in diag.ultimas_fallidas))
    _resumen(
        f"**Vigilancia:** {diag.accion}. {diag.motivo}.\n\n"
        + "".join(f"- {p}\n" for p in diag.problemas)
    )
    return diag


def _contar_de_verdad(params: dict, ahora: datetime):
    from bot import config as cfg

    def contar():
        if not cfg.hay("METACULUS_TOKEN"):
            return None
        estado = None
        if cfg.hay("OPENROUTER_API_KEY"):
            espera = float(ajustes.p("red.tiempo_espera_segundos", params))
            estado = presupuesto.consultar_clave(os.environ["OPENROUTER_API_KEY"].strip(), espera)
        return contar_pendientes(preguntas_abiertas(params), params, estado, ahora)

    return contar


def despertar_claude(params: dict, diag_texto: str, errores: str, ejecutar=subprocess.run) -> int:
    """Nivel 2: lanza Claude Code con los topes. Si falla, el issue se abre igual (lo hace el flujo
    con el diagnóstico de la vigilancia)."""
    diag = Diagnostico("relanzar_y_claude", [diag_texto], "")
    entorno = {k: v for k, v in os.environ.items() if k not in CLAVES_OCULTAS}
    r = ejecutar(
        orden_claude(params),
        input=prompt_claude(diag, errores),
        text=True,
        capture_output=True,
        env=entorno,
        timeout=float(ajustes.p("vigilancia.claude.tope_segundos", params)),
    )
    print(f"Claude Code terminó con código {r.returncode}.")
    # a la cuenta del plan (orden 27): lo que dice Claude Code o, si no lo dice, su freno
    tope = float(ajustes.p("vigilancia.claude.tope_usd", params))
    plan_claude.apuntar("vigilancia", _coste_de(getattr(r, "stdout", "")) or tope, "despertar")
    return r.returncode


def _coste_de(salida: Any) -> float | None:
    """`total_cost_usd` de la salida JSON de Claude Code (None si no está)."""
    try:
        coste = json.loads(salida or "").get("total_cost_usd")
    except (TypeError, ValueError, AttributeError):
        return None
    return float(coste) if isinstance(coste, (int, float)) else None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Vigilancia del bot de metaculus-quant")
    sub = parser.add_subparsers(dest="orden", required=True)
    r = sub.add_parser("revisar", help="mirar y, si hace falta, relanzar el bot")
    r.add_argument("--rama", required=True)
    r.add_argument("--probar-relanzamiento", action="store_true")
    e = sub.add_parser("errores", help="bajar las líneas de error de las ejecuciones fallidas")
    e.add_argument("--ids", default="")
    e.add_argument("--salida", required=True)
    c = sub.add_parser("claude", help="despertar a Claude Code para diagnosticar")
    c.add_argument("--problemas", default="")
    c.add_argument("--errores", required=True)
    a = sub.add_parser("comprobar-arreglo", help="¿el arreglo de Claude toca algo prohibido?")
    a.add_argument("--base", required=True)
    args = parser.parse_args(argv)

    from bot import config as cfg

    params = cfg.cargar_params()
    espera = float(ajustes.p("red.tiempo_espera_segundos", params))
    if args.orden in ("revisar", "errores"):
        gh = Github(os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_TOKEN"], espera)
    if args.orden == "revisar":
        revisar(params, gh, datetime.now(UTC), args.rama, probar=args.probar_relanzamiento)
        return 0
    if args.orden == "errores":
        maximo = int(ajustes.p("vigilancia.max_caracteres_errores", params))
        trozos = []
        for i in [x for x in args.ids.split(",") if x.strip()]:
            try:
                trozos.append(f"### Ejecución {i}\n{gh.errores_de(int(i), maximo)}")
            except Exception as ex:
                trozos.append(f"### Ejecución {i}\n(no se pudo bajar el registro: {ex!r})")
        Path(args.salida).write_text("\n\n".join(trozos)[-maximo:], encoding="utf-8")
        return 0
    if args.orden == "claude":
        errores = Path(args.errores).read_text(encoding="utf-8")
        despertar_claude(params, args.problemas, errores)
        return 0  # el issue se abre igual; un fallo de Claude no es un fallo del bot
    # comprobar-arreglo
    cambiadas = subprocess.run(
        ["git", "diff", "--name-only", f"{args.base}...HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    if not cambiadas:
        print("Claude no dejó ningún arreglo.")
        _salida("subir", "no")
        return 0
    malas = rutas_fuera_de_limites(cambiadas)
    if malas:
        print(f"::warning::El arreglo de Claude toca lo prohibido y NO se sube: {malas}")
        _salida("subir", "no")
        return 0
    print(f"Arreglo de Claude dentro de los límites: {cambiadas}")
    _salida("subir", "si")
    return 0


if __name__ == "__main__":
    sys.exit(main())
