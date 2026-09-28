"""Búsqueda de noticias con respaldo (28/09/2026): si la principal (Opus 5.5) falla, se agota el
tiempo o sale vacía, busca el respaldo (GPT-6 Sol) en vez de pronosticar sin noticias."""

from __future__ import annotations

import json

import main
from bot import config as cfg
from tests.conftest import MetaculusFalso, ModeloFalso, preguntas_ejemplo


class BuscadorRoto(ModeloFalso):
    def __init__(self, como="error", **kw):
        super().__init__(**kw)
        self.como = como

    async def invoke(self, prompt):  # type: ignore[override]
        self.llamadas += 1
        if self.como == "vacio":
            return "   "
        raise RuntimeError("proveedor caído (simulado)")


def _estado_busqueda(monkeypatch, tmp_path, principal, respaldo):
    modelo = ModeloFalso()
    llms = {"default": modelo, "summarizer": modelo, "researcher": principal, "parser": modelo}
    if respaldo is not None:
        llms["_respaldo_busqueda"] = respaldo
    monkeypatch.setenv("METACULUS_TOKEN", "t")
    main.ejecutar("test_questions", cliente=MetaculusFalso(preguntas_ejemplo()[:1]), llms=llms)
    [f] = list((tmp_path / "registro").glob("pronosticos_*.jsonl"))
    fila = json.loads(f.read_text(encoding="utf-8").splitlines()[0])
    return fila["investigacion"], fila


def test_si_la_principal_falla_busca_el_respaldo(monkeypatch, tmp_path):
    respaldo = ModeloFalso()
    inv, fila = _estado_busqueda(monkeypatch, tmp_path, BuscadorRoto(), respaldo)
    assert inv["base_estado"] == "respaldo"
    assert "Noticias simuladas" in inv["base"]
    assert "busqueda respaldo" in fila["coste_partes"]
    assert respaldo.llamadas == 1


def test_si_la_principal_sale_vacia_tambien(monkeypatch, tmp_path):
    inv, _ = _estado_busqueda(monkeypatch, tmp_path, BuscadorRoto("vacio"), ModeloFalso())
    assert inv["base_estado"] == "respaldo"


def test_si_fallan_las_dos_se_pronostica_igual_y_queda_apuntado(monkeypatch, tmp_path):
    inv, fila = _estado_busqueda(monkeypatch, tmp_path, BuscadorRoto(), BuscadorRoto())
    assert inv["base_estado"] == "fallo_sin_respaldo"
    assert fila["pronostico"]  # el pronóstico sale igual, sin noticias


def test_si_la_principal_va_bien_el_respaldo_no_se_usa(monkeypatch, tmp_path):
    respaldo = ModeloFalso()
    inv, _ = _estado_busqueda(monkeypatch, tmp_path, ModeloFalso(), respaldo)
    assert inv["base_estado"] == "ok" and respaldo.llamadas == 0


def test_sin_respaldo_configurado_como_antes(monkeypatch, tmp_path):
    inv, _ = _estado_busqueda(monkeypatch, tmp_path, BuscadorRoto(), None)
    assert inv["base_estado"] == "fallo"


def test_modelos_elegidos_por_el_usuario_el_28_09(monkeypatch):
    """De Anthropic solo Opus 5.5; de OpenAI solo GPT-6 Sol y Astra; de Google, 3.8 Flash."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "clave-falsa")
    params = cfg.cargar_params()
    bot = main.construir_bot(params, publicar=False)
    usados = [llm.model for par in bot._puestos for llm in par if llm is not None]
    usados += [bot.get_llm("researcher", "llm").model, bot._respaldo_busqueda.model]
    usados.append(bot.get_llm("parser", "llm").model)  # el lector: GPT-6 Sol desde el 28/09
    assert bot.get_llm("parser", "llm").model == "openrouter/openai/gpt-6-sol"
    claude = {u for u in usados if "anthropic/" in u}
    openai = {u for u in usados if "openai/" in u}
    google = {u for u in usados if "google/" in u}
    assert claude == {
        "openrouter/anthropic/claude-opus-5.5",
        "openrouter/anthropic/claude-opus-5.5:online",
    }
    assert {u.split(":")[0] for u in openai} <= {
        "openrouter/openai/gpt-6-sol",
        "openrouter/openai/gpt-6-astra",
    }
    assert google == {"openrouter/google/gemini-3.8-flash"}
