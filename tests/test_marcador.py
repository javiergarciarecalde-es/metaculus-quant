"""Marcador semanal (Metaculus simulado: no sale a internet)."""

import json
import math
from datetime import UTC, datetime, timedelta

import pytest

from bot import marcador as mc

AHORA = datetime(2026, 10, 20, 12, tzinfo=UTC)


def _fila(url, tipo, valor, miembros, horas=48, enviado=True, idq=None):
    return {
        "cuando_utc": (AHORA - timedelta(hours=horas)).isoformat(),
        "enviado": enviado,
        "url": url,
        "id_pregunta": idq,
        "tipo": tipo,
        "pregunta": f"¿{url}?",
        "valor": valor,
        "miembros": miembros,
        "torneo": 33121,
    }


def test_juntar_solo_enviados_de_hace_mas_de_un_dia_y_sin_repetir():
    viejas = [_fila("https://m/questions/1", "binary", 0.7, [])]
    nuevas = [
        _fila("https://m/questions/1", "binary", 0.7, []),  # repetida
        _fila("https://m/questions/2", "binary", 0.3, [], horas=2),  # aún puede estar abierta
        _fila("https://m/questions/3", "binary", 0.3, [], enviado=False),  # ensayo
        _fila("https://m/questions/4", "binary", 0.4, []),
    ]
    urls = [f["url"] for f in mc.juntar(viejas, nuevas, AHORA)]
    assert urls == ["https://m/questions/1", "https://m/questions/4"]


def test_puntos_binaria_opciones_y_numerica():
    assert mc.puntos("binary", 0.8, "yes")["log"] == pytest.approx(math.log(0.8))
    assert mc.puntos("binary", 0.8, "no")["brier"] == pytest.approx(0.64)
    assert mc.puntos("multiple_choice", {"A": 0.6, "B": 0.4}, "B")["log"] == pytest.approx(
        math.log(0.4)
    )
    num = {"0.1": 10, "0.5": 20, "0.9": 30}
    assert mc.puntos("numeric", num, "25")["dentro_80"] is True
    assert mc.puntos("numeric", num, "31")["dentro_80"] is False
    assert mc.puntos("binary", 0.8, "annulled") is None
    assert mc.puntos("numeric", num, "above_upper_bound") is None


def test_pregunta_de_un_grupo_por_su_id():
    post = {
        "group_of_questions": {
            "questions": [{"id": 5, "status": "open"}, {"id": 6, "status": "resolved"}]
        }
    }
    assert mc.pregunta_del_post(post, 6)["status"] == "resolved"
    assert mc.pregunta_del_post(post, None) is None  # ambiguo: no se adivina
    assert mc.pregunta_del_post({"question": {"id": 9}}, None)["id"] == 9


def test_resumen_lee_la_puntuacion_oficial():
    q = {
        "status": "resolved",
        "resolution": "yes",
        "my_forecasts": {"score_data": {"spot_peer_score": 12.5, "peer_score": 10.0}},
    }
    assert mc.resumen_pregunta(q) == {
        "estado": "resolved",
        "resolucion": "yes",
        "spot_peer": 12.5,
        "peer": 10.0,
        "baseline": None,
    }


def test_calcular_por_modelo_calibracion_y_peores():
    filas = [
        _fila("u1", "binary", 0.8, [{"modelo": "a", "valor": 0.9}, {"modelo": "b", "valor": 0.6}]),
        _fila("u2", "binary", 0.2, [{"modelo": "a", "valor": 0.1}, {"modelo": "b", "valor": 0.4}]),
        _fila("u3", "binary", 0.5, []),  # sin resolver todavía
    ]
    resueltas = {
        str(mc.clave(filas[0])): {"estado": "resolved", "resolucion": "yes", "spot_peer": 20.0},
        str(mc.clave(filas[1])): {"estado": "resolved", "resolucion": "yes", "spot_peer": -40.0},
        str(mc.clave(filas[2])): {"estado": "open"},
    }
    m = mc.calcular(filas, resueltas)
    assert m["resueltas"] == 2 and m["spot_peer_suma"] == -20.0
    assert m["por_modelo"]["a"]["binary:log"]["n"] == 2
    assert m["por_modelo"]["a"]["binary:log"]["media"] == pytest.approx(
        round((math.log(0.9) + math.log(0.1)) / 2, 4)
    )
    assert m["calibracion"]["80-90 %"] == {"n": 1, "dijimos": 80.0, "paso": 100.0}
    assert m["peores"][0]["url"] == "u2"
    texto = mc.informe_md(m, "20/10/2026")
    assert "Las 5 peores" in texto and "| a | binary:log | 2 |" in texto


def test_programa_completo_con_metaculus_simulado(tmp_path, monkeypatch):
    for nombre in ("HISTORICO", "RESUELTAS", "SALIDA_JSON", "SALIDA_MD"):
        monkeypatch.setattr(mc, nombre, tmp_path / getattr(mc, nombre).name)
    descargas = tmp_path / "descargas" / "artefacto1"
    descargas.mkdir(parents=True)
    fila = _fila(
        "https://www.metaculus.com/questions/777/",
        "binary",
        0.7,
        [{"modelo": "a", "valor": 0.7}],
        horas=24 * 30,
    )
    fila["cuando_utc"] = (datetime.now(UTC) - timedelta(days=3)).isoformat()
    (descargas / "pronosticos_2026-10.jsonl").write_text(json.dumps(fila) + "\n", encoding="utf-8")
    pedidas = []
    monkeypatch.setattr(
        mc,
        "pedir_post",
        lambda pid, token: (
            pedidas.append(pid)
            or {
                "question": {
                    "id": 1,
                    "status": "resolved",
                    "resolution": "yes",
                    "my_forecasts": {"score_data": {"spot_peer_score": 8.0}},
                }
            }
        ),
    )
    monkeypatch.setattr(mc.time, "sleep", lambda s: None)
    assert mc.main(["--descargas", str(tmp_path / "descargas")]) == 0
    assert pedidas == [777]
    assert (
        json.loads((tmp_path / "marcador.json").read_text(encoding="utf-8"))["spot_peer_suma"]
        == 8.0
    )
    # segunda vez: ya resuelta en caché, no se vuelve a pedir
    assert mc.main(["--descargas", str(tmp_path / "descargas")]) == 0
    assert pedidas == [777]


def test_el_registro_guarda_valor_exacto_para_el_marcador(monkeypatch, llms, tmp_path):
    import main
    from tests.conftest import MetaculusFalso, preguntas_ejemplo

    monkeypatch.setenv("METACULUS_TOKEN", "t")
    main.ejecutar("test_questions", cliente=MetaculusFalso(preguntas_ejemplo()), llms=llms)
    [f] = list((tmp_path / "registro").glob("*.jsonl"))
    lineas = [json.loads(linea) for linea in f.read_text(encoding="utf-8").splitlines()]
    binaria, opciones, numerica = lineas
    assert binaria["valor"] == pytest.approx(0.72)
    assert set(opciones["valor"]) == {"Rojo", "Verde", "Azul"}
    assert isinstance(numerica["valor"], dict) and len(numerica["valor"]) >= 3
    assert "id_post" in binaria and "id_pregunta" in binaria
