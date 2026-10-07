"""Orden 82 (decisión del usuario del 07/10/2026): el bot no usa el plan de Claude del usuario.

Con config/params.yaml tal cual: ninguna pieza llama a Claude Code aunque esté el secreto, todas
las preguntas van con la búsqueda de pago, la vigilancia relanza pero no despierta a Claude y el
flujo de GitHub ni instala Claude Code ni le pasa el secreto al bot."""

import asyncio
from pathlib import Path

import pytest
import yaml

import main
from bot import claude_max as cm
from bot import config as cfg
from bot import plan_claude as pc
from bot import vigilancia as vg
from tests.conftest import MetaculusFalso, encender_claude, preguntas_ejemplo
from tests.test_claude_max import ClaudeFalso
from tests.test_vigilancia import AHORA, _relanzada, _run

RAIZ = Path(__file__).resolve().parent.parent


def test_ninguna_pieza_usa_el_plan_de_claude():
    assert pc.piezas_encendidas(cfg.cargar_params()) == []


def test_al_encenderlas_se_ven_las_tres():
    assert len(pc.piezas_encendidas(encender_claude(cfg.cargar_params()))) == 3


@pytest.mark.parametrize("encendido,esperado", [(False, "usa=no"), (True, "usa=si")])
def test_el_paso_del_flujo_dice_si_usa_el_plan(monkeypatch, tmp_path, encendido, esperado):
    original = cfg.cargar_params
    if encendido:
        monkeypatch.setattr(cfg, "cargar_params", lambda: encender_claude(original()))
    salida = tmp_path / "salida.txt"
    monkeypatch.setenv("GITHUB_OUTPUT", str(salida))
    assert pc.main() == 0
    assert salida.read_text(encoding="utf-8").strip() == esperado


def test_pregunta_par_con_secreto_no_llama_a_claude(monkeypatch, llms, modelo):
    monkeypatch.setenv(cm.SECRETO, "token-falso")
    investiga, clasifica = ClaudeFalso(), ClaudeFalso()
    todos = {**llms, "_claude_ejecutar": investiga, "_claude_clasificar": clasifica}
    bot = main.construir_bot(cfg.cargar_params(), publicar=False, llms=todos)
    bot.metaculus_client = MetaculusFalso([])
    # la de número par (12): hasta el 07/10/2026 la investigaba Claude
    [r] = asyncio.run(bot.forecast_questions(preguntas_ejemplo()[1:2]))
    assert r.prediction is not None
    assert investiga.llamadas == [] and clasifica.llamadas == []
    [inv] = bot._investigacion.values()
    assert inv["claude_estado"] == "no_usada" and inv["base"]  # búsqueda de pago


def test_la_vigilancia_relanza_pero_no_despierta_a_claude():
    runs = [_relanzada(30), _relanzada(60), _run(200, "failure")]
    ejecuciones = vg.leer_ejecuciones({"workflow_runs": runs})

    class Gh:
        def ejecuciones(self, flujo, cuantas):
            return ejecuciones

        def issues(self):
            return []

        def gastado_plan(self, desde):
            return {}

        def relanzar(self, flujo, rama):
            self.relanzado = True

    gh = Gh()
    d = vg.revisar(cfg.cargar_params(), gh, AHORA, "main", contar=lambda: 0, hay_claude=True)
    assert d.accion == "relanzar" and gh.relanzado
    assert "apagada en config/params.yaml" in d.motivo


def test_el_flujo_del_bot_no_instala_claude_ni_pasa_el_secreto_si_no_se_usa():
    flujo = yaml.safe_load(
        (RAIZ / ".github/workflows/run_bot_on_tournament.yaml").read_text(encoding="utf-8")
    )
    pasos = flujo["jobs"]["pronosticar"]["steps"]
    [plan] = [p for p in pasos if p.get("id") == "plan"]
    assert plan["run"] == "python -m bot.plan_claude"
    nodo = [p for p in pasos if "setup-node" in str(p.get("uses", ""))]
    instalar = [p for p in pasos if "claude-code" in str(p.get("run", ""))]
    for paso in nodo + instalar:
        assert "steps.plan.outputs.usa == 'si'" in paso["if"]
    [bot] = [p for p in pasos if "main.py" in str(p.get("run", ""))]
    assert bot["env"]["CLAUDE_CODE_OAUTH_TOKEN"].startswith("${{ steps.plan.outputs.usa == 'si' &&")
