"""Investigación con agentes de Claude Opus 5.5 pagada con la suscripción Claude Max del usuario.

Decisión del usuario (25/09/2026, esquema mixto): los 3 pronosticadores van con los créditos de
Metaculus; esta investigación extra va con su Claude Max, usando Claude Code (`claude -p`) en
GitHub Actions con el secreto CLAUDE_CODE_OAUTH_TOKEN (lo genera el usuario con
`claude setup-token`).

Reglas (las mismas que la investigación ampliada):
- Lo que encuentra se AÑADE al final del informe base; nunca lo sustituye.
- Sin secreto, sin el programa `claude`, con error, sin tiempo o sin cupo -> informe base intacto.
- Si se agota el cupo de Max, se deja de llamar durante el resto de la ejecución (no insiste).
- Nunca puede tocar ficheros ni ejecutar órdenes: solo buscar y leer páginas web.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import os
import shutil
import tempfile

logger = logging.getLogger(__name__)

CABECERA = "\n\n## Investigación con agentes (Claude Opus 5.5; añadido; puede contener errores)\n"
SECRETO = "CLAUDE_CODE_OAUTH_TOKEN"
ORDEN_CORTA = "Follow the research brief given on stdin. Reply only with the final research notes."
PALABRAS_CUPO = ("usage limit", "rate limit", "limit reached", "quota")
# Claves que Claude Code no necesita: no se le pasan (aunque no puede ejecutar órdenes).
OTRAS_CLAVES = (
    "METACULUS_TOKEN",
    "OPENROUTER_API_KEY",
    "ASKNEWS_CLIENT_ID",
    "ASKNEWS_SECRET",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
)


def prompt_investigacion(
    pregunta: str,
    criterios: str,
    letra_pequena: str,
    informe: str,
    agentes: int,
    max_caracteres: int,
) -> str:
    return (
        "You lead a small research team for a superforecaster. Do NOT forecast.\n"
        f"Launch up to {agentes} research subagents IN PARALLEL (Agent tool), each on a different "
        "angle, using web search and by reading the pages themselves:\n"
        "1. What the resolution source currently says/shows, and how close the question is to "
        "resolving (dates, exact figures).\n"
        "2. The latest news that could change the outcome before the resolution date, with dates.\n"
        "3. Base rates / historical frequency of similar events, and any scheduled events.\n"
        "Also check the report below for facts that look wrong or outdated.\n"
        "Return brief notes: each fact with its date and source URL. Mark anything uncertain.\n\n"
        f"Question: {pregunta}\n\nResolution criteria: {criterios}\n\n"
        f"Fine print: {letra_pequena}\n\n"
        f"Current research report:\n{informe[:max_caracteres]}"
    )


def orden(conf: dict) -> list[str]:
    return [
        "claude",
        "-p",
        ORDEN_CORTA,
        "--model",
        str(conf["modelo"]),
        "--output-format",
        "json",
        "--max-turns",
        str(int(conf["max_turnos"])),
        "--max-budget-usd",
        str(conf["tope_usd_por_pregunta"]),
        "--allowedTools",
        "WebSearch",
        "WebFetch",
        "Agent",
        "Task",
        "--disallowedTools",
        "Bash",
        "Edit",
        "Write",
        "NotebookEdit",
        "--no-session-persistence",
    ]


def leer_salida(texto: str) -> tuple[str, float | None]:
    """Devuelve (notas, coste equivalente en $) o lanza error si Claude Code falló."""
    datos = json.loads(texto)
    if not isinstance(datos, dict):
        raise TypeError("salida de Claude Code sin formato esperado")
    notas = datos.get("result")
    if datos.get("is_error") or not isinstance(notas, str) or not notas.strip():
        raise RuntimeError(f"Claude Code sin resultado: {str(notas or datos.get('subtype'))[:300]}")
    return notas.strip(), datos.get("total_cost_usd")


def comprobar_salida(codigo: int, salida: str, error: str) -> tuple[str, float | None]:
    """Como `leer_salida`, pero antes da error si Claude Code terminó mal y sin decir nada."""
    if codigo != 0 and not salida.strip():
        raise RuntimeError(f"Claude Code terminó con código {codigo}: {error[-300:]}")
    return leer_salida(salida)


async def _ejecutar_de_verdad(args: list[str], entrada: str, env: dict, tope: float):
    ejecutable = shutil.which(args[0])
    if not ejecutable:
        raise FileNotFoundError("no está instalado el programa «claude» (Claude Code)")
    with tempfile.TemporaryDirectory() as carpeta:  # carpeta vacía: no lee el CLAUDE.md del repo
        proc = await asyncio.create_subprocess_exec(
            ejecutable,
            *args[1:],
            cwd=carpeta,
            env=env,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            salida, error = await asyncio.wait_for(proc.communicate(entrada.encode("utf-8")), tope)
        except BaseException:
            with contextlib.suppress(ProcessLookupError):
                proc.kill()
            await proc.wait()
            raise
    return proc.returncode, salida.decode("utf-8", "replace"), error.decode("utf-8", "replace")


class InvestigadorClaudeMax:
    """`conf` = `investigacion.claude_max` de config/params.yaml, completo (sin valores por
    defecto).

    `max_caracteres` = `investigacion.max_caracteres_informe`: cuánto del informe base se le pasa.
    """

    CAMPOS = ("modelo", "agentes", "max_turnos", "tope_segundos", "simultaneas")
    CAMPOS += ("tope_usd_por_pregunta",)

    def __init__(self, conf: dict, max_caracteres: int, ejecutar=_ejecutar_de_verdad):
        faltan = [c for c in self.CAMPOS if c not in conf]
        if faltan:
            raise KeyError(f"a investigacion.claude_max le falta {faltan} en config/params.yaml")
        self.conf = conf
        self.max_caracteres = max_caracteres
        self._ejecutar = ejecutar
        self._turnos: dict = {}  # un semáforo por bucle (el bot abre uno por torneo)
        self.sin_cupo = False
        self.costes: dict[str, float | None] = {}  # por pregunta: lo que costaría en $ por API

    def _turno(self) -> asyncio.Semaphore:
        bucle = asyncio.get_running_loop()
        if bucle not in self._turnos:
            self._turnos = {bucle: asyncio.Semaphore(int(self.conf["simultaneas"]))}
        return self._turnos[bucle]

    def disponible(self) -> bool:
        return bool((os.getenv(SECRETO) or "").strip()) and not self.sin_cupo

    async def ampliar(
        self,
        informe_base: str,
        pregunta: str,
        criterios: str,
        letra_pequena: str = "",
        clave: str = "",
    ) -> str:
        if not self.disponible():
            return informe_base
        tope = float(self.conf["tope_segundos"])
        entrada = prompt_investigacion(
            pregunta,
            criterios,
            letra_pequena,
            informe_base,
            int(self.conf["agentes"]),
            self.max_caracteres,
        )
        try:
            async with self._turno():
                if self.sin_cupo:
                    return informe_base
                env = {k: v for k, v in os.environ.items() if k not in OTRAS_CLAVES}
                codigo, salida, error = await self._ejecutar(orden(self.conf), entrada, env, tope)
            notas, coste = comprobar_salida(codigo, salida, error)
        except Exception as e:  # incluye tiempo agotado: se sigue con el informe base
            if any(p in str(e).lower() for p in PALABRAS_CUPO):
                self.sin_cupo = True
                logger.warning("Cupo de Claude Max agotado: se sigue sin esta investigación.")
            logger.warning(f"Investigación con Claude Max descartada: {e!r}"[:500])
            return informe_base
        self.costes[clave] = coste
        logger.info(
            f"Investigación con Claude Max: {len(notas)} caracteres; "
            f"{coste} $ equivalentes de API. Empieza así: {notas[:600]}"
        )
        return informe_base + CABECERA + notas
