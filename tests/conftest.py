"""Piezas simuladas: un modelo falso (no llama a ninguna IA) y un Metaculus falso (no envía
nada)."""

import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from forecasting_tools import (
    BinaryQuestion,
    GeneralLlm,
    MultipleChoiceQuestion,
    NumericQuestion,
)

from bot.presupuesto import EstadoClave

RESPUESTA_BINARIA = "(a) ... razonamiento ...\nProbability: 72%"
RESPUESTA_OPCIONES = "razonamiento\nRojo: 50%\nVerde: 30%\nAzul: 20%"
RESPUESTA_NUMERICA = (
    "razonamiento\nPercentile 10: 12\nPercentile 20: 20\nPercentile 40: 35\n"
    "Percentile 60: 48\nPercentile 80: 65\nPercentile 90: 80"
)


CLAVE_NUEVA = EstadoClave(gastado=0.0, limite=100.0, restante=100.0)


class ModeloFalso(GeneralLlm):
    """Devuelve texto fijo según el tipo de pregunta; cuenta llamadas; nunca sale a internet."""

    def __init__(self, **kw):
        super().__init__(model="falso/modelo", **kw)
        self.llamadas = 0

    async def invoke(self, prompt):  # type: ignore[override]
        self.llamadas += 1
        if "Percentile 10" in prompt:
            return RESPUESTA_NUMERICA
        if "The options are" in prompt:
            return RESPUESTA_OPCIONES
        if "Probability: ZZ%" in prompt:
            return RESPUESTA_BINARIA
        return "Noticias simuladas: nada relevante."


class MetaculusFalso:
    """Imita MetaculusClient: da preguntas y apunta cualquier intento de envío."""

    def __init__(self, preguntas):
        self.preguntas = preguntas
        self.envios = []
        self.torneos_pedidos = []

    def get_all_open_questions_from_tournament(self, torneo):
        self.torneos_pedidos.append(torneo)
        return list(self.preguntas)

    def post_binary_question_prediction(self, *a, **k):
        self.envios.append(("binaria", a))

    def post_numeric_question_prediction(self, *a, **k):
        self.envios.append(("numerica", a))

    def post_multiple_choice_question_prediction(self, *a, **k):
        self.envios.append(("opciones", a))

    def post_question_comment(self, *a, **k):
        self.envios.append(("comentario", a))


def sin_historial() -> dict:
    """Lo que Metaculus manda de una pregunta aún sin pronóstico nuestro (bot/normas.py)."""
    return {"question": {"my_forecasts": {"history": []}}}


def preguntas_ejemplo():
    preguntas = [
        BinaryQuestion(
            question_text="¿Pasará X antes de 2027?",
            id_of_post=1,
            id_of_question=11,
            page_url="https://ejemplo/1",
        ),
        MultipleChoiceQuestion(
            question_text="¿Qué color ganará?",
            id_of_post=2,
            id_of_question=12,
            page_url="https://ejemplo/2",
            options=["Rojo", "Verde", "Azul"],
        ),
        NumericQuestion(
            question_text="¿Cuántos serán?",
            id_of_post=3,
            id_of_question=13,
            page_url="https://ejemplo/3",
            upper_bound=100,
            lower_bound=0,
            open_upper_bound=True,
            open_lower_bound=False,
            unit_of_measure="unidades",
        ),
    ]
    for q in preguntas:
        q.api_json = sin_historial()
    return preguntas


@pytest.fixture
def modelo():
    return ModeloFalso()


@pytest.fixture
def llms(modelo):
    return {"default": modelo, "summarizer": modelo, "researcher": modelo, "parser": modelo}


@pytest.fixture(autouse=True)
def entorno_limpio(monkeypatch, tmp_path):
    for v in [
        "METACULUS_TOKEN",
        "ENVIO_REAL",
        "OPENROUTER_API_KEY",
        "GITHUB_EVENT_NAME",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "ASKNEWS_CLIENT_ID",
        "ASKNEWS_SECRET",
        "CLAUDE_CODE_OAUTH_TOKEN",
    ]:
        monkeypatch.delenv(v, raising=False)
    import bot.params as ajustes
    import bot.presupuesto as presupuesto
    import bot.registro as r

    monkeypatch.setattr(r, "CARPETA", tmp_path / "registro")
    # Ninguna prueba pregunta a OpenRouter de verdad: la clave simulada tiene 100 $ sin gastar.
    monkeypatch.setattr(presupuesto, "consultar_clave", lambda *a, **k: CLAVE_NUEVA)
    # Las pausas de Claude con fecha (p. ej. la del 27/09/2026 hasta las 11:00 del 28/09) son
    # temporales: las pruebas no dependen del día en que se ejecutan (la pausa tiene su prueba).
    sin_pausa = copy.deepcopy(ajustes.todos())
    sin_pausa["investigacion"]["claude_max"]["pausada_hasta_utc"] = None
    monkeypatch.setattr(ajustes, "todos", lambda: sin_pausa)
    yield
