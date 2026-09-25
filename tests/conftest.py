"""Piezas simuladas: un modelo falso (no llama a ninguna IA) y un Metaculus falso (no envía
nada)."""

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

RESPUESTA_BINARIA = "(a) ... razonamiento ...\nProbability: 72%"
RESPUESTA_OPCIONES = "razonamiento\nRojo: 50%\nVerde: 30%\nAzul: 20%"
RESPUESTA_NUMERICA = (
    "razonamiento\nPercentile 10: 12\nPercentile 20: 20\nPercentile 40: 35\n"
    "Percentile 60: 48\nPercentile 80: 65\nPercentile 90: 80"
)


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


def preguntas_ejemplo():
    return [
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
    import bot.registro as r

    monkeypatch.setattr(r, "CARPETA", tmp_path / "registro")
    yield
