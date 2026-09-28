"""Tope del plan de Claude del usuario (orden 27 del mando, aprobada por el usuario el 28/09/2026).

El plan Max del usuario lo comparten todos sus proyectos. El bot lo gasta en tres sitios: la
investigación de las preguntas pares (`bot/claude_max.py`), el clasificador en sombra con Opus
«xhigh» (`bot/clasificador.py`) y la vigilancia cuando despierta a Claude (`bot/vigilancia.py`).
La revisión semanal de los lunes (rutina en la nube) también gasta, pero fuera del bot: se le
guarda una reserva fija.

Cómo se lleva la cuenta: cada uso apunta una línea en `plan/plan_claude_AAAA-MM.jsonl` con lo que
costaría por la API («$ equivalentes», lo que dice Claude Code; si no lo dice, el freno de ese
uso). El flujo sube esa carpeta como artefacto `plan-claude-<ejecución>` y, antes de usar Claude,
el bot suma las líneas de la **semana del plan** (se renueva los lunes a las 09:00 UTC).

Qué se apaga y en qué orden (propuesta del mando):
1. Pasado `apagar_opus_desde` del tope: el clasificador en sombra con Opus (no decide nada).
2. Pasado el tope entero: también la investigación con Claude (las pares van con la búsqueda de
   pago, como cuando Claude no tiene cupo) y la vigilancia ya no despierta a Claude.
Si no se puede leer la cuenta: el clasificador con Opus se apaga (no decide nada) y lo demás sigue
con sus frenos de siempre.

`ContadorPlan` y las sumas son puras; la red (GitHub) va aparte, en `leer_de_github`.
"""

from __future__ import annotations

import io
import json
import zipfile
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any

import requests

from bot import params as ajustes
from bot import registro
from bot.config import RAIZ

API = "https://api.github.com"
CARPETA = RAIZ / "plan"  # la sube el flujo como artefacto «plan-claude-<id>»
NOMBRE = "plan_claude"
PREFIJO_ARTEFACTO = "plan-claude-"
PARTES = ("investigacion", "clasificador_opus", "vigilancia")


class EsquemaGithubError(ValueError):
    """La respuesta de GitHub sobre los artefactos no tiene la forma esperada."""


def inicio_semana(ahora: datetime, params: dict) -> datetime:
    """Último reinicio semanal del plan antes de `ahora` (lunes 09:00 UTC, visto en la tarjeta de
    uso de la aplicación el 28/09/2026)."""
    dia = int(ajustes.p("plan_claude.reinicio_semanal.dia", params))  # 0 = lunes
    hora = int(ajustes.p("plan_claude.reinicio_semanal.hora_utc", params))
    base = ahora.astimezone(UTC).replace(hour=hora, minute=0, second=0, microsecond=0)
    base -= timedelta(days=(base.weekday() - dia) % 7)
    return base if base <= ahora else base - timedelta(days=7)


def tope_usd(params: dict) -> float:
    """Lo que el bot puede gastar por semana del plan, en $ equivalentes: su parte del tope semanal
    menos la reserva para la revisión de los lunes."""
    fraccion = float(ajustes.p("plan_claude.tope_fraccion_semanal", params))
    por_punto = float(ajustes.p("plan_claude.usd_por_punto_semanal", params))
    reserva = float(ajustes.p("plan_claude.reserva_revision_usd", params))
    return fraccion * 100 * por_punto - reserva


def sumar(filas: list[dict], desde: datetime, hasta: datetime | None = None) -> dict[str, float]:
    """{parte: $ equivalentes} de las líneas del plan desde `desde` (y antes de `hasta`, si se da);
    las demás líneas se ignoran."""
    res: dict[str, float] = {}
    for f in filas:
        if f.get("consulta") != NOMBRE:
            continue
        try:
            cuando = datetime.fromisoformat(str(f["cuando_utc"]))
            usd = float(f["usd"])
        except (KeyError, TypeError, ValueError):
            continue
        cuando = cuando if cuando.tzinfo else cuando.replace(tzinfo=UTC)
        if cuando >= desde and (hasta is None or cuando < hasta):
            parte = str(f.get("parte"))
            res[parte] = res.get(parte, 0.0) + usd
    return res


def apuntar(parte: str, usd: float, detalle: str = "", carpeta=None) -> None:
    """Una línea en plan/plan_claude_AAAA-MM.jsonl (el flujo la sube como artefacto)."""
    registro.anotar(
        {"consulta": NOMBRE, "parte": parte, "usd": round(float(usd), 6), "detalle": detalle},
        carpeta=carpeta or CARPETA,
        nombre=NOMBRE,
    )


@dataclass
class ContadorPlan:
    """Cuenta del plan en una ejecución. `leer`: función sin argumentos que da lo gastado en la
    semana del plan ({parte: $}) o lanza un error si no se puede saber; se llama una sola vez y
    solo si hace falta (sin preguntas, ni se mira)."""

    tope: float
    umbral_opus: float  # $: por encima, el clasificador con Opus se apaga
    leer: Any = None
    carpeta: Any = None  # dónde se apuntan las líneas (en las pruebas, una temporal)
    en_esta_ejecucion: float = 0.0
    en_vuelo: float = 0.0  # frenos de los usos que han empezado y aún no han dicho cuánto
    _semana: float | None = field(default=None, init=False)
    _leido: bool = field(default=False, init=False)
    error: str | None = field(default=None, init=False)

    def gastado_semana(self) -> float | None:
        if not self._leido:
            self._leido = True
            try:
                self._semana = sum((self.leer() if self.leer else {}).values())
            except Exception as e:  # sin cuenta: se sigue con los frenos de siempre
                self.error = f"{type(e).__name__}: {e}"[:200]
                print(f"::warning::No se pudo leer lo gastado del plan de Claude ({self.error}).")
        return self._semana

    def total(self) -> float:
        return (self.gastado_semana() or 0.0) + self.en_esta_ejecucion + self.en_vuelo

    def empezar(self, parte: str, freno: float) -> bool:
        """¿Se puede empezar un uso que como mucho cuesta `freno`? Si sí, lo reserva."""
        if parte == "clasificador_opus":
            if self.gastado_semana() is None:
                return False  # no decide nada: sin cuenta, mejor no gastar
            limite = self.umbral_opus
        else:
            limite = self.tope
        if self.total() + freno > limite:
            return False
        self.en_vuelo += freno
        return True

    def terminar(self, parte: str, freno: float, usd: float | None, detalle: str = "") -> None:
        """Cierra un uso empezado: apunta lo que costó (si no se sabe, el freno)."""
        self.en_vuelo = max(0.0, self.en_vuelo - freno)
        coste = float(usd) if usd is not None else float(freno)
        self.en_esta_ejecucion += coste
        apuntar(parte, coste, detalle, self.carpeta)


def contador(params: dict, leer=None, carpeta=None) -> ContadorPlan:
    return ContadorPlan(
        tope=tope_usd(params),
        umbral_opus=tope_usd(params) * float(ajustes.p("plan_claude.apagar_opus_desde", params)),
        leer=leer,
        carpeta=carpeta,
    )


def sin_limite() -> ContadorPlan:
    """Para las pruebas que no miran el tope: cuenta de 0 $ y tope enorme."""
    return ContadorPlan(tope=float("inf"), umbral_opus=float("inf"), leer=dict)


def resumen(filas: list[dict], params: dict, ahora: datetime) -> dict:
    """Para el marcador de los lunes: lo gastado del plan en la semana del plan que acaba (el
    marcador sale el lunes a las 06:30 UTC, antes del reinicio de las 09:00) y en la anterior."""
    inicio = inicio_semana(ahora, params)
    por_punto = float(ajustes.p("plan_claude.usd_por_punto_semanal", params))
    semanas = {}
    for nombre, (a, b) in {
        "esta": (inicio, ahora),
        "anterior": (inicio - timedelta(days=7), inicio),
    }.items():
        partes = sumar(filas, a, b)
        total = sum(partes.values())
        semanas[nombre] = {
            "desde": a.isoformat(timespec="minutes"),
            "partes": {k: round(v, 2) for k, v in sorted(partes.items())},
            "total_usd": round(total, 2),
            "puntos_del_tope_semanal": round(total / por_punto, 1),
        }
    return {
        "tope_usd": round(tope_usd(params), 2),
        "tope_puntos": round(
            100 * float(ajustes.p("plan_claude.tope_fraccion_semanal", params)), 1
        ),
        "usd_por_punto": por_punto,
        "semanas": semanas,
    }


def informe_md(r: dict) -> list[str]:
    """Sección en llano para docs/MARCADOR.md."""
    esta, antes = r["semanas"]["esta"], r["semanas"]["anterior"]
    lineas = [
        "",
        "## Plan de Claude del usuario (lo que gasta el bot)",
        "",
        f"El bot no pasa del {r['tope_puntos']} % del tope semanal del plan ({r['tope_usd']} $ "
        "equivalentes, ya descontada la reserva para la revisión de los lunes). Pasado el 80 %, se "
        "apaga el clasificador con Opus; pasado el tope, también la investigación con Claude (las "
        "pares van con la búsqueda de pago). «Puntos» = % del tope semanal, estimado a "
        f"{r['usd_por_punto']} $ por punto (medido el 27/09).",
        "",
        "| Parte | Semana del plan que acaba ($) | Semana anterior ($) |",
        "|---|---|---|",
    ]
    for parte in sorted(set(esta["partes"]) | set(antes["partes"]) | set(PARTES)):
        lineas.append(
            f"| {parte} | {esta['partes'].get(parte, 0)} | {antes['partes'].get(parte, 0)} |"
        )
    lineas += [
        f"| **Total** | **{esta['total_usd']}** | **{antes['total_usd']}** |",
        f"| Puntos del tope semanal (≈ %) | {esta['puntos_del_tope_semanal']} "
        f"| {antes['puntos_del_tope_semanal']} |",
    ]
    return lineas


##################################### RED (GitHub) #####################################


def _artefactos(respuesta: Any) -> list[dict]:
    """Valida `GET /repos/{repo}/actions/artifacts` (campos vistos en la respuesta real del
    28/09/2026: id, name, expired, created_at; lo más nuevo primero)."""
    if not isinstance(respuesta, dict) or not isinstance(respuesta.get("artifacts"), list):
        raise EsquemaGithubError("la respuesta de GitHub no trae «artifacts»")
    for a in respuesta["artifacts"]:
        if not isinstance(a, dict) or not {"id", "name", "expired", "created_at"} <= set(a):
            raise EsquemaGithubError(
                "un artefacto de GitHub no trae id, name, expired o created_at"
            )
    return respuesta["artifacts"]


def leer_de_github(repo: str, token: str, desde: datetime, espera: float, get=requests.get):
    """Suma por parte las líneas del plan de los artefactos «plan-claude-*» creados desde `desde`.
    GitHub los da de más nuevo a más viejo: se deja de pedir páginas al pasar de `desde`."""
    cab = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    filas: list[dict] = []
    pagina = 1
    while True:
        r = get(
            f"{API}/repos/{repo}/actions/artifacts",
            headers=cab,
            params={"per_page": 100, "page": pagina},
            timeout=espera,
        )
        r.raise_for_status()
        lista = _artefactos(r.json())
        viejos = 0
        for a in lista:
            creado = datetime.fromisoformat(str(a["created_at"]).replace("Z", "+00:00"))
            if creado < desde:
                viejos += 1
                continue
            if a["expired"] or not str(a["name"]).startswith(PREFIJO_ARTEFACTO):
                continue
            z = get(
                f"{API}/repos/{repo}/actions/artifacts/{a['id']}/zip", headers=cab, timeout=espera
            )
            z.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(z.content)) as zf:
                for nombre in zf.namelist():
                    if nombre.endswith(".jsonl"):
                        for linea in zf.read(nombre).decode("utf-8", "replace").splitlines():
                            if linea.strip():
                                filas.append(json.loads(linea))
        if len(lista) < 100 or viejos:
            break
        pagina += 1
    return sumar(filas, desde)
