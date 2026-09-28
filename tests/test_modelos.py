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


class _Resp:
    def __init__(self, codigo, datos):
        self.status_code, self._datos = codigo, datos

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)

    def json(self):
        return self._datos


def _lista(ids):
    return {"data": [{"id": i} for i in ids]}


def test_consulta_de_la_clave_por_empresa(monkeypatch, capsys):
    params = cfg.cargar_params()
    nuestros = modelos.nombres_openrouter(params)
    publicos = [*nuestros, "deepseek/deepseek-v4", "qwen/qwen4"]
    permitidos = [*nuestros, "deepseek/deepseek-v4"]
    monkeypatch.setenv("OPENROUTER_API_KEY", "clave-secreta-falsa")
    vistos = []

    def get(url, headers=None, timeout=None):
        vistos.append((url, headers))
        return _Resp(200, _lista(permitidos if url.endswith("/user") else publicos))

    assert modelos.consultar_clave(params, get=get) == 0
    salida = capsys.readouterr().out
    assert "deepseek: deepseek/deepseek-v4" in salida and "qwen" not in salida
    assert "Nuestros modelos: todos permitidos." in salida
    assert "clave-secreta-falsa" not in salida  # la clave nunca se imprime
    assert vistos[0][1]["Authorization"] == "Bearer clave-secreta-falsa"
    assert vistos[1][1] is None  # la lista pública va sin clave


def test_clave_sin_filtro_avisa_de_que_no_prueba_nada():
    params = cfg.cargar_params()
    todos = set(modelos.nombres_openrouter(params)) | {"deepseek/x"}
    texto = "\n".join(modelos.informe_clave(todos, todos, params))
    assert "no filtra nada" in texto and "byok" in texto


def test_consulta_rechazada_sale_en_rojo_sin_repetir_la_respuesta(monkeypatch, capsys):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    r = modelos.consultar_clave(cfg.cargar_params(), get=lambda *a, **k: _Resp(401, {"x": "y"}))
    assert r == 1 and "401" in capsys.readouterr().out


def test_sin_clave_no_consulta(capsys):
    assert modelos.consultar_clave(cfg.cargar_params(), get=None) == 0


def test_lista_con_precios():
    publica = {
        "data": [
            {
                "id": "google/gemini-3.8-flash",
                "pricing": {"prompt": "0.0000005", "completion": "0.000003"},
            },
            {"id": "google/raro", "pricing": {}},
        ]
    }
    lineas = modelos.lista_con_precios(
        {"google/gemini-3.8-flash", "google/raro", "openai/x"},
        modelos.precios(publica),
        ("google",),
    )
    assert lineas == [
        "  google/gemini-3.8-flash: 0.5 $ / 3 $ por millón de tokens (entrada / salida)",
        "  google/raro: precio desconocido por millón de tokens (entrada / salida)",
    ]


def test_listado_completo_por_empresa():
    lineas = modelos.listado_completo({"openai/a", "~openai/b"}, {"openai/a", "deepseek/d"})
    assert lineas == [
        "== deepseek: 1 modelos (0 permitidos por la clave)",
        "  deepseek/d",
        "== openai: 1 modelos (1 permitidos por la clave)",
        "  openai/a  [CLAVE]",
        "== ~openai: 1 modelos (1 permitidos por la clave)",
        "  ~openai/b  [CLAVE]",
    ]
