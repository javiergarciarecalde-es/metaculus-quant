"""Investigación con agentes de Opus 5.5 vía Claude Max (Claude Code simulado: no gasta cupo)."""

import asyncio
import json

import pytest

import main
from bot import claude_max as cm
from bot import config as cfg
from tests.conftest import MetaculusFalso, preguntas_ejemplo


class ClaudeFalso:
    """Hace de `claude -p`: apunta cómo se le llamó y devuelve lo que se le diga."""

    def __init__(self, resultado="NOTAS DE OPUS", is_error=False, codigo=0, lento=0.0, salida=None):
        self.llamadas = []
        self.resultado, self.is_error, self.codigo = resultado, is_error, codigo
        self.lento, self.salida = lento, salida

    async def __call__(self, args, entrada, env, tope):
        self.llamadas.append({"args": args, "entrada": entrada, "env": env})
        if self.lento:
            await asyncio.wait_for(asyncio.sleep(self.lento), tope)
        if self.salida is not None:
            return self.codigo, self.salida, ""
        return (
            self.codigo,
            json.dumps(
                {
                    "type": "result",
                    "is_error": self.is_error,
                    "result": self.resultado,
                    "total_cost_usd": 0.8,
                }
            ),
            "",
        )


def _ampliar(inv, clave="q1"):
    return asyncio.run(inv.ampliar("INFORME BASE", "¿X?", "criterios", "letra", clave=clave))


@pytest.fixture
def con_secreto(monkeypatch):
    monkeypatch.setenv(cm.SECRETO, "token-falso")


def test_sin_secreto_no_llama_y_deja_el_informe():
    falso = ClaudeFalso()
    assert _ampliar(cm.InvestigadorClaudeMax({}, falso)) == "INFORME BASE"
    assert falso.llamadas == []


def test_anade_al_final_y_apunta_el_coste(con_secreto):
    falso = ClaudeFalso()
    inv = cm.InvestigadorClaudeMax({"agentes": 3}, falso)
    out = _ampliar(inv)
    assert out == "INFORME BASE" + cm.CABECERA + "NOTAS DE OPUS"
    assert inv.costes["q1"] == 0.8


def test_orden_segura_y_texto_largo_por_la_entrada(con_secreto, monkeypatch):
    monkeypatch.setenv("METACULUS_TOKEN", "no-debe-pasar")
    monkeypatch.setenv("OPENROUTER_API_KEY", "tampoco")
    falso = ClaudeFalso()
    _ampliar(cm.InvestigadorClaudeMax({"modelo": "claude-opus-5-5"}, falso))
    [llamada] = falso.llamadas
    args = llamada["args"]
    assert args[:2] == ["claude", "-p"] and "claude-opus-5-5" in args
    # sin poder tocar ficheros ni ejecutar órdenes
    assert {"Bash", "Edit", "Write"} <= set(args[args.index("--disallowedTools") :])
    # el texto de la pregunta va por la entrada, no en la orden (límite de longitud de Windows)
    assert "¿X?" in llamada["entrada"] and all("¿X?" not in a for a in args)
    # solo recibe su propio secreto, no el resto de claves
    assert llamada["env"][cm.SECRETO] == "token-falso"
    assert "METACULUS_TOKEN" not in llamada["env"] and "OPENROUTER_API_KEY" not in llamada["env"]


@pytest.mark.parametrize(
    "falso",
    [
        ClaudeFalso(is_error=True, resultado="Error interno"),
        ClaudeFalso(resultado="   "),
        ClaudeFalso(codigo=1, salida=""),
        ClaudeFalso(salida="esto no es JSON"),
    ],
)
def test_cualquier_fallo_devuelve_el_informe_base(con_secreto, falso):
    assert _ampliar(cm.InvestigadorClaudeMax({}, falso)) == "INFORME BASE"


def test_sin_tiempo_devuelve_el_informe_base(con_secreto):
    falso = ClaudeFalso(lento=1)
    assert _ampliar(cm.InvestigadorClaudeMax({"tope_segundos": 0.01}, falso)) == "INFORME BASE"


def test_cupo_agotado_no_vuelve_a_llamar(con_secreto):
    falso = ClaudeFalso(is_error=True, resultado="Claude AI usage limit reached|1759000000")
    inv = cm.InvestigadorClaudeMax({}, falso)
    assert _ampliar(inv) == "INFORME BASE" and inv.sin_cupo
    assert _ampliar(inv, "q2") == "INFORME BASE"
    assert len(falso.llamadas) == 1


def test_integrado_en_el_bot(con_secreto, llms, modelo):
    falso = ClaudeFalso()
    params = cfg.cargar_params()
    assert params["investigacion"]["modo"] == "claude_max"
    bot = main.construir_bot(params, publicar=False, llms={**llms, "_claude_ejecutar": falso})
    bot.metaculus_client = MetaculusFalso([])
    [r] = asyncio.run(bot.forecast_questions(preguntas_ejemplo()[:1]))
    assert len(falso.llamadas) == 1
    assert modelo.llamadas == 1 + 3  # búsqueda base (créditos) + 3 pasadas
    assert r.prediction == pytest.approx(0.72)


def test_sin_programa_claude_se_sigue(con_secreto, monkeypatch):
    monkeypatch.setattr(cm.shutil, "which", lambda _: None)
    assert _ampliar(cm.InvestigadorClaudeMax({})) == "INFORME BASE"
