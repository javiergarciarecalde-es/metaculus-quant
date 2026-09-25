from bot import config as cfg
from bot import modelos


def test_nombres_sin_prefijo_ni_sufijo():
    nombres = modelos.nombres_openrouter(cfg.cargar_params())
    assert nombres and all(not n.startswith("openrouter/") and ":" not in n for n in nombres)


def test_detecta_modelos_desaparecidos():
    params = cfg.cargar_params()
    todos = set(modelos.nombres_openrouter(params))
    assert modelos.faltan(params, todos) == []
    quitado = sorted(todos)[0]
    assert modelos.faltan(params, todos - {quitado}) == [quitado]
