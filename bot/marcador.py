"""Marcador semanal: cruza lo que pronosticó el bot (y cada modelo) con cómo se resolvió cada
pregunta.

Pasos:
1. Junta los registros de las ejecuciones (artefactos de GitHub descargados) con el histórico
   guardado en el repositorio. Al histórico solo pasan pronósticos de hace más de 24 h Y de
   preguntas ya cerradas (su hora de cierre pasó): no se publica nada mientras se puede pronosticar.
2. Para cada pregunta pide a Metaculus su estado, su resolución y nuestra puntuación oficial
   (score_data de my_forecasts: spot_peer_score = la puntuación de pares que cuenta en el torneo).
3. Calcula, por modelo, puntuaciones propias (log y Brier) para comparar a los tres miembros.
4. Compara formas de juntar a los 3 modelos (bot/comparador.py).
5. Resume en qué se va el dinero frente a la línea de ritmo (bot/gasto.py; orden 26, 27/09/2026).
6. Lista las preguntas que cerraron sin pronóstico nuestro (bot/perdidas.py; 27/09/2026).
7. Escribe docs/MARCADOR.md (en llano) y datos/marcador.json. El texto largo de cada pregunta
   (investigación entera, razonamientos) va aparte, a datos/detalle/, un fichero por pregunta.

Uso: python -m bot.marcador [--descargas carpeta]
"""

from __future__ import annotations

import argparse
import contextlib
import json
import math
import os
import re
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import requests

from . import clasificador as clf
from . import comparador as cmp
from . import gasto, perdidas
from . import params as ajustes
from .config import RAIZ

HISTORICO = RAIZ / "datos" / "registro_historico.jsonl"
RESUELTAS = RAIZ / "datos" / "resueltas.json"  # caché: lo ya resuelto no se vuelve a pedir
SALIDA_JSON = RAIZ / "datos" / "marcador.json"
SALIDA_MD = RAIZ / "docs" / "MARCADOR.md"
DETALLE = RAIZ / "datos" / "detalle"  # texto largo de cada pregunta
API = "https://www.metaculus.com/api/posts/{}/"
ANULADAS = {"annulled", "ambiguous"}


# ------------------------------------------------------------------ registros


def leer_jsonl(carpeta: Path) -> list[dict]:
    """Lee todas las líneas JSON de una carpeta (y subcarpetas) o de un solo fichero."""
    carpeta = Path(carpeta)
    rutas = [carpeta] if carpeta.is_file() else sorted(carpeta.rglob("*.jsonl"))
    filas = []
    for ruta in rutas:
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if linea:
                with contextlib.suppress(json.JSONDecodeError):
                    filas.append(json.loads(linea))
    return filas


def clave(fila: dict) -> tuple:
    return (fila.get("url"), fila.get("id_pregunta"))


def _fecha_utc(texto) -> datetime | None:
    """Fecha del registro (`cuando_utc`, `cierre_utc` = str(close_time)); None si no hay."""
    try:
        f = datetime.fromisoformat(str(texto))
    except (TypeError, ValueError):
        return None
    return f if f.tzinfo else f.replace(tzinfo=UTC)


def juntar(historico: list[dict], nuevas: list[dict], ahora: datetime, horas: float) -> list[dict]:
    """Añade al histórico los pronósticos ENVIADOS de hace más de `horas`, sin repetir preguntas,
    y SOLO si la pregunta ya cerró (`cierre_utc` pasado). El histórico se sube a un repositorio
    público: un pronóstico de una pregunta abierta no debe verse (orden 27, 28/09/2026: la 45707
    siguió abierta ~11 h tras pronosticarla; «24 h» sola no bastaba). Sin hora de cierre, no
    entra."""
    limite = ahora - timedelta(hours=horas)
    vistos = {clave(f) for f in historico}
    salida = list(historico)
    for f in sorted(nuevas, key=lambda f: f.get("cuando_utc", "")):
        if not f.get("enviado") or not f.get("url") or clave(f) in vistos:
            continue
        cuando, cierre = _fecha_utc(f.get("cuando_utc")), _fecha_utc(f.get("cierre_utc"))
        if cuando is None or cierre is None:
            continue
        if cuando <= limite and cierre <= ahora:
            salida.append(f)
            vistos.add(clave(f))
    return salida


def aligerar(fila: dict, carpeta: Path) -> dict:
    """Guarda el texto largo de la pregunta en `carpeta` (una vez) y lo quita de la fila."""
    pesado = {k: fila[k] for k in ("investigacion", "criterios", "letra_pequena") if k in fila}
    razonamientos = [m.get("razonamiento") for m in fila.get("miembros") or []]
    if not pesado and not any(razonamientos):
        return fila
    nombre = f"{id_post(fila) or 'x'}_{fila.get('id_pregunta') or 'x'}.json"
    ruta = carpeta / nombre
    if not ruta.exists():
        carpeta.mkdir(parents=True, exist_ok=True)
        detalle = {"url": fila.get("url"), **pesado, "razonamientos": razonamientos}
        ruta.write_text(json.dumps(detalle, ensure_ascii=False, indent=1), encoding="utf-8")
    ligera = {k: v for k, v in fila.items() if k not in pesado}
    ligera["miembros"] = [
        {k: v for k, v in m.items() if k != "razonamiento"} for m in fila.get("miembros") or []
    ]
    ligera["detalle"] = f"datos/detalle/{nombre}"
    return ligera


def id_post(fila: dict) -> int | None:
    if fila.get("id_post"):
        return int(fila["id_post"])
    m = re.search(r"/questions/(\d+)", fila.get("url") or "")
    return int(m.group(1)) if m else None


# ------------------------------------------------------------------ Metaculus


def pedir_post(pid: int, token: str | None, espera: float) -> dict:
    cab = {"Authorization": f"Token {token}"} if token else {}
    r = requests.get(API.format(pid), headers=cab, timeout=espera)
    r.raise_for_status()
    return r.json()


def pregunta_del_post(post: dict, id_pregunta) -> dict | None:
    qs = (
        [post["question"]]
        if post.get("question")
        else list((post.get("group_of_questions") or {}).get("questions") or [])
    )
    if id_pregunta is not None:
        for q in qs:
            if q.get("id") == id_pregunta:
                return q
    return qs[0] if len(qs) == 1 else None


def resumen_pregunta(q: dict) -> dict:
    datos = ((q.get("my_forecasts") or {}).get("score_data")) or {}
    return {
        "estado": q.get("status"),
        "resolucion": q.get("resolution"),
        "spot_peer": datos.get("spot_peer_score"),
        "peer": datos.get("peer_score"),
        "baseline": datos.get("baseline_score"),
    }


# ------------------------------------------------------------------ puntuaciones propias


def _prob_binaria(valor) -> float | None:
    try:
        return min(max(float(valor), 1e-6), 1 - 1e-6)
    except (TypeError, ValueError):
        return None


def puntos(tipo: str, valor, resolucion) -> dict | None:
    """log = ln(prob. dada a lo que pasó) (0 es perfecto, más negativo es peor).

    brier: solo en binarias.
    """
    if valor is None or resolucion in (None, "") or str(resolucion) in ANULADAS:
        return None
    if tipo == "binary":
        p = _prob_binaria(valor)
        if p is None or str(resolucion) not in ("yes", "no"):
            return None
        o = 1.0 if resolucion == "yes" else 0.0
        return {"log": math.log(p if o else 1 - p), "brier": (p - o) ** 2}
    if tipo == "multiple_choice" and isinstance(valor, dict):
        p = valor.get(str(resolucion))
        return {"log": math.log(max(float(p), 1e-6))} if p is not None else None
    if tipo in ("numeric", "discrete") and isinstance(valor, dict):
        try:
            x = float(resolucion)
        except (TypeError, ValueError):
            return None  # por encima/debajo de los límites: no se puntúa aquí
        pares = sorted((float(k), float(v)) for k, v in valor.items())
        dentro = None
        bajo = [v for k, v in pares if abs(k - 0.1) < 1e-6]
        alto = [v for k, v in pares if abs(k - 0.9) < 1e-6]
        if bajo and alto:
            dentro = bajo[0] <= x <= alto[0]
        return {"dentro_80": dentro}
    return None


# ------------------------------------------------------------------ cálculo del marcador


def calcular(filas: list[dict], resueltas: dict, conf_comparador: dict) -> dict:
    preguntas, modelos, calib, cambios = [], {}, {}, []
    for f in filas:
        info = resueltas.get(str(clave(f)))
        if not info or info.get("estado") != "resolved":
            continue
        tipo = f.get("tipo")
        agregado = puntos(tipo, f.get("valor"), info.get("resolucion"))
        variantes = cmp.cambios_por_pregunta(f, info.get("resolucion"), conf_comparador)
        if variantes:
            cambios.append((f.get("cuando_utc", ""), variantes))
        preguntas.append(
            {
                "pregunta": f.get("pregunta"),
                "url": f.get("url"),
                "tipo": tipo,
                "torneo": f.get("torneo"),
                "resolucion": info.get("resolucion"),
                "spot_peer": info.get("spot_peer"),
                "agregado": agregado,
            }
        )
        for m in f.get("miembros") or []:
            pm = puntos(tipo, m.get("valor"), info.get("resolucion"))
            if pm is None:
                continue
            d = modelos.setdefault(m.get("modelo"), {})
            for k, v in pm.items():
                if v is not None:
                    d.setdefault(f"{tipo}:{k}", []).append(float(v))
        if tipo == "binary":
            p = _prob_binaria(f.get("valor"))
            if p is not None and info.get("resolucion") in ("yes", "no"):
                tramo = min(int(p * 10), 9)
                c = calib.setdefault(tramo, {"n": 0, "suma_p": 0.0, "si": 0})
                c["n"] += 1
                c["suma_p"] += p
                c["si"] += info["resolucion"] == "yes"
    spot = [p["spot_peer"] for p in preguntas if isinstance(p["spot_peer"], (int, float))]
    return {
        "pronosticos_enviados": len(filas),
        "resueltas": len(preguntas),
        "spot_peer_suma": round(sum(spot), 2),
        "spot_peer_media": round(sum(spot) / len(spot), 2) if spot else None,
        "spot_peer_n": len(spot),
        "por_modelo": {
            m: {k: {"n": len(v), "media": round(sum(v) / len(v), 4)} for k, v in d.items()}
            for m, d in modelos.items()
        },
        "calibracion": {
            f"{t * 10}-{t * 10 + 10} %": {
                "n": c["n"],
                "dijimos": round(100 * c["suma_p"] / c["n"], 1),
                "paso": round(100 * c["si"] / c["n"], 1),
            }
            for t, c in sorted(calib.items())
        },
        "comparador": cmp.resumir(cambios, conf_comparador),
        "peores": sorted(
            [p for p in preguntas if isinstance(p["spot_peer"], (int, float))],
            key=lambda p: p["spot_peer"],
        )[:5],
    }


def informe_md(m: dict, fecha: str, conf_comparador: dict) -> str:
    media = m["spot_peer_media"]
    lineas = [
        "# Marcador del bot (se actualiza solo cada lunes)",
        "",
        f"**Actualizado:** {fecha}. Lo genera `bot/marcador.py`; no se toca a mano.",
        "",
        "Qué es cada cosa:",
        "- **Puntuación de pares** (spot peer): la que da Metaculus y cuenta en el torneo. "
        "Positiva = mejor",
        "  que la media de los demás bots en esa pregunta; negativa = peor.",
        "- **Log** (por modelo): logaritmo de la probabilidad que el modelo dio a lo que pasó. "
        "0 es",
        "  perfecto; cuanto más negativo, peor. Sirve para comparar a los 3 modelos entre sí.",
        "- **Brier**: error al cuadrado en preguntas de sí/no. 0 es perfecto; "
        "0,25 es decir siempre 50 %.",
        "- Con pocas preguntas resueltas todo esto es **ruido**: "
        "no sacar conclusiones con menos de ~50.",
        "",
        "## Resumen",
        "",
        "| Dato | Valor |",
        "|---|---|",
        f"| Pronósticos enviados (cerrados) | {m['pronosticos_enviados']} |",
        f"| Preguntas ya resueltas | {m['resueltas']} |",
        f"| Suma de puntuación de pares | {m['spot_peer_suma']} "
        f"(en {m['spot_peer_n']} preguntas) |",
        f"| Media por pregunta | {media if media is not None else '—'} |",
        "",
        "## Cada modelo por separado",
        "",
        "| Modelo | Tipo:medida | Preguntas | Media |",
        "|---|---|---|---|",
    ]
    for mod, d in sorted(m["por_modelo"].items()):
        for k, v in sorted(d.items()):
            lineas.append(f"| {mod} | {k} | {v['n']} | {v['media']} |")
    lineas += [
        "",
        "## Calibración (preguntas de sí/no)",
        "",
        "Si el bot está bien calibrado, «pasó» se parece a «dijimos» en cada tramo.",
        "",
        "| Tramo | Preguntas | Dijimos (media) | Pasó de verdad |",
        "|---|---|---|---|",
    ]
    for tramo, c in m["calibracion"].items():
        lineas.append(f"| {tramo} | {c['n']} | {c['dijimos']} % | {c['paso']} % |")
    lineas += [
        "",
        "## Las 5 peores preguntas",
        "",
        "| Puntuación | Pregunta | Resolución |",
        "|---|---|---|",
    ]
    for p in m["peores"]:
        lineas.append(
            f"| {round(p['spot_peer'], 1)} | [{(p['pregunta'] or '')[:90]}]({p['url']}) "
            f"| {p['resolucion']} |"
        )
    lineas += cmp.informe_md(m.get("comparador", []), conf_comparador)
    return "\n".join(lineas) + "\n"


def conf_comparador(arbol: dict | None = None) -> dict:
    """Ajustes del comparador: los límites del bot y las reglas de config/params.yaml."""
    return {
        "prob_min": float(ajustes.p("pronostico.prob_min", arbol)),
        "prob_max": float(ajustes.p("pronostico.prob_max", arbol)),
        "minimo_por_opcion": float(ajustes.p("pronostico.minimo_por_opcion", arbol)),
        "alternativos": tuple(ajustes.p("marcador.comparador.limites_alternativos", arbol)),
        "preregistradas": list(ajustes.p("marcador.comparador.preregistradas", arbol)),
        "minimo_preguntas": int(ajustes.p("marcador.comparador.minimo_preguntas", arbol)),
    }


# ------------------------------------------------------------------ programa


def _cerradas(token: str | None, ahora: datetime) -> list | None:
    """Preguntas de la MiniBench y la temporada cerradas en el periodo; None si no se puede."""
    if not token:
        return None
    dias = float(ajustes.p("marcador.dias_preguntas_perdidas"))
    torneos = [ajustes.p("torneos.minibench"), ajustes.p("torneos.temporada")]
    try:
        return perdidas.buscar_cerradas(torneos, ahora - timedelta(days=dias), ahora)
    except Exception as e:  # sin la lista, el marcador sale igual
        print(f"::warning::No se pudo pedir la lista de preguntas cerradas: {e}"[:300])
        return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--descargas", default=str(RAIZ / "registro_descargas"))
    args = ap.parse_args(argv)
    ahora = datetime.now(UTC)
    historico = leer_jsonl(HISTORICO) if HISTORICO.exists() else []
    historico = [f for f in historico if f.get("url")]
    nuevas = leer_jsonl(Path(args.descargas)) if Path(args.descargas).exists() else []
    filas = juntar(historico, nuevas, ahora, float(ajustes.p("marcador.horas_de_espera")))
    filas = [aligerar(f, DETALLE) for f in filas]
    HISTORICO.parent.mkdir(parents=True, exist_ok=True)
    HISTORICO.write_text(
        "".join(json.dumps(f, ensure_ascii=False) + "\n" for f in filas), encoding="utf-8"
    )

    resueltas = json.loads(RESUELTAS.read_text(encoding="utf-8")) if RESUELTAS.exists() else {}
    token = (os.getenv("METACULUS_TOKEN") or "").strip() or None
    espera = float(ajustes.p("red.tiempo_espera_segundos"))
    pausa = float(ajustes.p("marcador.pausa_entre_preguntas_segundos"))
    fallos = 0
    for f in filas:
        k = str(clave(f))
        if resueltas.get(k, {}).get("estado") == "resolved":
            continue
        pid = id_post(f)
        if pid is None:
            continue
        try:
            q = pregunta_del_post(pedir_post(pid, token, espera), f.get("id_pregunta"))
            if q:
                resueltas[k] = resumen_pregunta(q)
        except Exception as e:  # una pregunta que no carga no para el marcador
            fallos += 1
            print(f"::warning::No se pudo leer la pregunta {pid}: {e}"[:300])
        time.sleep(pausa)  # sin prisas con la API de Metaculus
    RESUELTAS.write_text(json.dumps(resueltas, ensure_ascii=False, indent=1), encoding="utf-8")

    conf = conf_comparador()
    m = calcular(filas, resueltas, conf)
    arbol = ajustes.todos()
    # Secciones añadidas el 27-28/09/2026: si una falla, el resto del marcador sale igual (y su
    # commit semanal, que además evita que GitHub apague el reloj por 60 días sin cambios).
    secciones = [
        ("gasto", "En qué se va el dinero", lambda: gasto.resumen(nuevas, arbol, ahora),
         gasto.informe_md),
        ("perdidas", "Preguntas perdidas",
         lambda: perdidas.resumir(_cerradas(token, ahora), nuevas, arbol), perdidas.informe_md),
        ("clasificador_gemini", "Clasificador en sombra: Gemini 3.8 Flash",
         lambda: clf.resumir(filas, resueltas, clave, "clasificador"),
         lambda r: clf.informe_md(r, "Gemini 3.8 Flash")),
        ("clasificador_opus", "Clasificador en sombra: Claude Opus 5.5",
         lambda: clf.resumir(filas, resueltas, clave, "clasificador_opus"),
         lambda r: clf.informe_md(r, "Claude Opus 5.5 (xhigh, plan Max)")),
    ]  # fmt: skip
    extra: list[str] = []
    for nombre, titulo, calcular_seccion, pintar in secciones:
        try:
            m[nombre] = calcular_seccion()
            extra += pintar(m[nombre])
        except Exception as e:
            print(f"::warning::La sección «{titulo}» del marcador falló: {e!r}"[:300])
            m[nombre] = {"error": repr(e)[:300]}
            extra += ["", f"## {titulo}", "", f"**Esta semana falló:** `{repr(e)[:200]}`"]
    SALIDA_JSON.write_text(
        json.dumps(m, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    texto = informe_md(m, f"{ahora:%d/%m/%Y %H:%M} UTC", conf) + "\n".join(extra)
    SALIDA_MD.write_text(texto + "\n", encoding="utf-8")
    print(
        f"Marcador: {m['pronosticos_enviados']} pronósticos, {m['resueltas']} resueltas, "
        f"suma de pares {m['spot_peer_suma']}. Preguntas que no cargaron: {fallos}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
