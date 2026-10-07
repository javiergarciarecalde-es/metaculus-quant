"""Opción A (28/09/2026): en las preguntas del reparto, Claude Max busca EN LUGAR de la búsqueda
de pago; y el clasificador en sombra, que dice si una pregunta es fácil o difícil (no decide)."""

from __future__ import annotations

import json

import pytest

import main
from bot import clasificador as clf
from bot import claude_max as cm
from tests.conftest import MetaculusFalso, ModeloFalso, preguntas_ejemplo
from tests.test_claude_max import ClaudeFalso

# orden 82 (07/10/2026): config/params.yaml apaga el plan de Claude; aquí se prueba encendido
pytestmark = pytest.mark.usefixtures("claude_encendido")


class ClasificadorFalso(ModeloFalso):
    def __init__(self, respuesta, **kw):
        super().__init__(**kw)
        self.respuesta = respuesta

    async def invoke(self, prompt):  # type: ignore[override]
        self.llamadas += 1
        assert "Do NOT forecast" in prompt
        return self.respuesta


BUENA = '{"difficulty": "hard", "reasoning_effort": "high", "deep_research": true, "reason": "x"}'


def _filas(monkeypatch, tmp_path, pregunta, claude=None, clasificador=None, secreto=True):
    if secreto:
        monkeypatch.setenv(cm.SECRETO, "token-falso")
    modelo = ModeloFalso()
    llms = {"default": modelo, "summarizer": modelo, "researcher": modelo, "parser": modelo}
    if claude is not None:
        llms["_claude_ejecutar"] = claude
    if clasificador is not None:
        llms["_clasificador"] = clasificador
    monkeypatch.setenv("METACULUS_TOKEN", "t")
    main.ejecutar("test_questions", cliente=MetaculusFalso([pregunta]), llms=llms)
    [f] = list((tmp_path / "registro").glob("pronosticos_*.jsonl"))
    return json.loads(f.read_text(encoding="utf-8").splitlines()[0]), modelo


# --------------------------------------------------------------------------- opción A


def test_pregunta_par_claude_busca_en_lugar_de_la_de_pago(monkeypatch, tmp_path):
    claude = ClaudeFalso("NOTAS DE OPUS DESDE CERO")
    fila, modelo = _filas(monkeypatch, tmp_path, preguntas_ejemplo()[1], claude)  # id 12: par
    inv = fila["investigacion"]
    assert inv["claude_estado"] == "ok" and inv["base_estado"] == "sustituida_por_claude"
    assert inv["base"] == "" and "NOTAS DE OPUS DESDE CERO" in inv["claude"]
    assert modelo.llamadas == 3  # sin búsqueda de pago: solo las 3 pasadas
    # Claude recibe las instrucciones de búsqueda desde cero (no «verifica el informe»)
    entrada = claude.llamadas[0]["entrada"]
    assert "Current research report" not in entrada and "Do NOT forecast" in entrada


def test_si_claude_falla_entra_la_busqueda_de_pago(monkeypatch, tmp_path):
    claude = ClaudeFalso(is_error=True)
    fila, modelo = _filas(monkeypatch, tmp_path, preguntas_ejemplo()[1], claude)
    inv = fila["investigacion"]
    assert inv["claude_estado"] == "fallo" and inv["base_estado"] == "ok"
    assert "Noticias simuladas" in inv["base"]
    assert modelo.llamadas == 1 + 3


def test_sin_secreto_de_claude_la_busqueda_de_pago(monkeypatch, tmp_path):
    fila, modelo = _filas(monkeypatch, tmp_path, preguntas_ejemplo()[1], secreto=False)
    assert fila["investigacion"]["claude_estado"] == "sin_secreto"
    assert fila["investigacion"]["base_estado"] == "ok" and modelo.llamadas == 1 + 3


def test_pregunta_impar_solo_busqueda_de_pago(monkeypatch, tmp_path):
    claude = ClaudeFalso()
    fila, modelo = _filas(monkeypatch, tmp_path, preguntas_ejemplo()[0], claude)  # id 11: impar
    assert fila["investigacion"]["claude_estado"] == "fuera_del_reparto"
    assert claude.llamadas == [] and modelo.llamadas == 1 + 3


def test_sin_sustituir_como_antes_se_suma(monkeypatch, tmp_path):
    import bot.params as ajustes

    arbol = ajustes.todos()
    arbol["investigacion"]["claude_max"]["sustituye_busqueda"] = False
    claude = ClaudeFalso("NOTAS")
    fila, modelo = _filas(monkeypatch, tmp_path, preguntas_ejemplo()[1], claude)
    inv = fila["investigacion"]
    assert inv["base_estado"] == "ok" and inv["claude_estado"] == "ok"
    assert "Current research report" in claude.llamadas[0]["entrada"]
    assert modelo.llamadas == 1 + 3


# --------------------------------------------------------------------------- clasificador


def test_leer_respuestas_del_clasificador():
    assert clf.leer(f"Aquí va: {BUENA} fin") == {
        "estado": "ok",
        "dificultad": "dificil",
        "esfuerzo": "alto",
        "a_fondo": True,
        "motivo": "x",
    }
    assert clf.leer("sin json")["estado"] == "ilegible"
    assert clf.leer('{"difficulty": "imposible"}')["estado"] == "ilegible"
    assert clf.leer("{roto")["estado"] == "ilegible"


def test_el_clasificador_se_guarda_y_no_cambia_nada(monkeypatch, tmp_path):
    sin, _ = _filas(monkeypatch, tmp_path, preguntas_ejemplo()[0], secreto=False)
    (tmp_path / "registro").rename(tmp_path / "registro_antes")
    cla = ClasificadorFalso(BUENA)
    con, _ = _filas(monkeypatch, tmp_path, preguntas_ejemplo()[0], clasificador=cla, secreto=False)
    assert sin["clasificador"] == {"estado": "sin_modelo"}
    assert con["clasificador"]["dificultad"] == "dificil" and cla.llamadas == 1
    assert con["valor"] == sin["valor"]  # el pronóstico enviado es el mismo
    assert "clasificador" in con["coste_partes"]


def test_si_el_clasificador_falla_la_pregunta_sigue(monkeypatch, tmp_path):
    class Roto(ModeloFalso):
        async def invoke(self, prompt):  # type: ignore[override]
            raise RuntimeError("caído")

    fila, _ = _filas(monkeypatch, tmp_path, preguntas_ejemplo()[0], clasificador=Roto())
    assert fila["clasificador"]["estado"] == "fallo" and fila["pronostico"]


@pytest.mark.parametrize(
    ("tipo", "valores", "esperado"),
    [
        ("binary", [0.2, 0.7, 0.5], 0.5),
        ("multiple_choice", [{"A": 0.6, "B": 0.4}, {"A": 0.3, "B": 0.7}], 0.3),
        (
            "numeric",
            [
                {"0.1": 0, "0.4": 40, "0.6": 60, "0.9": 100},
                {"0.1": 20, "0.4": 60, "0.6": 80, "0.9": 120},
            ],
            0.2,
        ),
    ],
)
def test_discrepancia_de_los_modelos(tipo, valores, esperado):
    fila = {"tipo": tipo, "miembros": [{"valor": v} for v in valores]}
    assert clf.discrepancia(fila) == pytest.approx(esperado)


def test_discrepancia_con_un_solo_modelo():
    assert clf.discrepancia({"tipo": "binary", "miembros": [{"valor": 0.3}]}) is None


def test_resumen_por_etiqueta_para_el_marcador():
    def fila(url, dif, ps):
        return {
            "url": url,
            "id_pregunta": 1,
            "tipo": "binary",
            "clasificador": {"estado": "ok", "dificultad": dif},
            "miembros": [{"valor": p} for p in ps],
        }

    filas = [fila("a", "facil", [0.9, 0.9]), fila("b", "dificil", [0.2, 0.8]), {"url": "c"}]
    resueltas = {str(("a", 1)): {"estado": "resolved", "spot_peer": 10.0}}
    r = clf.resumir(filas, resueltas, lambda f: (f.get("url"), f.get("id_pregunta")))
    assert r["facil"] == {
        "preguntas": 1,
        "discrepancia_media": 0.0,
        "resueltas": 1,
        "puntos_media": 10.0,
        "puntos_margen_95": None,
    }
    assert r["dificil"]["discrepancia_media"] == 0.6 and r["dificil"]["resueltas"] == 0
    assert r["sin_clasificar"]["preguntas"] == 1
    assert "Clasificador en sombra" in "\n".join(clf.informe_md(r))


# --------------------------------------------------------------------------- clasificador con Opus


def _filas_opus(monkeypatch, tmp_path, claude_clasif, secreto=True, pausa=False):
    import bot.params as ajustes

    if pausa:
        ajustes.todos()["investigacion"]["claude_max"]["pausada_hasta_utc"] = (
            "2099-01-01T00:00:00+00:00"
        )
    if secreto:
        monkeypatch.setenv(cm.SECRETO, "token-falso")
    modelo = ModeloFalso()
    llms = {"default": modelo, "summarizer": modelo, "researcher": modelo, "parser": modelo}
    llms["_claude_clasificar"] = claude_clasif
    llms["_clasificador"] = ClasificadorFalso(BUENA.replace("hard", "easy"))
    monkeypatch.setenv("METACULUS_TOKEN", "t")
    # pregunta impar: sin investigación de Claude, para ver solo al clasificador
    main.ejecutar("test_questions", cliente=MetaculusFalso(preguntas_ejemplo()[:1]), llms=llms)
    [f] = list((tmp_path / "registro").glob("pronosticos_*.jsonl"))
    return json.loads(f.read_text(encoding="utf-8").splitlines()[0])


def test_opus_clasifica_en_paralelo_con_esfuerzo_extra_y_sin_herramientas(monkeypatch, tmp_path):
    claude = ClaudeFalso(BUENA)
    fila = _filas_opus(monkeypatch, tmp_path, claude)
    assert fila["clasificador_opus"]["estado"] == "ok"
    assert fila["clasificador_opus"]["dificultad"] == "dificil"
    assert fila["clasificador_opus"]["usd_equivalente"] == 0.8  # lo que dice Claude Code
    assert fila["clasificador"]["dificultad"] == "facil"  # Gemini, por su lado
    [llamada] = claude.llamadas
    args = llamada["args"]
    assert args[args.index("--effort") + 1] == "xhigh"
    assert args[args.index("--model") + 1] == "claude-opus-5-5"
    assert args[args.index("--disallowedTools") + 1] == "*"
    assert "Do NOT forecast" in llamada["entrada"]
    assert "METACULUS_TOKEN" not in llamada["env"]  # no recibe otras claves


def test_opus_sin_secreto_o_en_pausa_no_llama(monkeypatch, tmp_path):
    claude = ClaudeFalso(BUENA)
    fila = _filas_opus(monkeypatch, tmp_path, claude, secreto=False)
    assert fila["clasificador_opus"] == {"estado": "sin_secreto"} and claude.llamadas == []


def test_opus_en_pausa_no_llama(monkeypatch, tmp_path):
    claude = ClaudeFalso(BUENA)
    fila = _filas_opus(monkeypatch, tmp_path, claude, pausa=True)
    assert fila["clasificador_opus"] == {"estado": "pausada"} and claude.llamadas == []


def test_si_opus_falla_la_pregunta_sigue_igual(monkeypatch, tmp_path):
    fila = _filas_opus(monkeypatch, tmp_path, ClaudeFalso(is_error=True, resultado="Error"))
    assert fila["clasificador_opus"]["estado"] == "fallo"
    assert fila["pronostico"] and fila["clasificador"]["estado"] == "ok"


def test_opus_sin_cupo_no_insiste(monkeypatch, tmp_path):
    claude = ClaudeFalso(is_error=True, resultado="Claude AI usage limit reached")
    fila = _filas_opus(monkeypatch, tmp_path, claude)
    assert fila["clasificador_opus"]["estado"] == "sin_cupo"


def test_el_marcador_muestra_los_dos_clasificadores(tmp_path, monkeypatch):
    from bot import marcador as mc

    for nombre in ("HISTORICO", "RESUELTAS", "SALIDA_JSON", "SALIDA_MD"):
        monkeypatch.setattr(mc, nombre, tmp_path / getattr(mc, nombre).name)
    assert mc.main(["--descargas", str(tmp_path / "nada")]) == 0
    md = (tmp_path / "MARCADOR.md").read_text(encoding="utf-8")
    assert "Clasificador en sombra: Gemini 3.8 Flash" in md
    assert "Clasificador en sombra: Claude Opus 5.5 (xhigh, plan Max)" in md
