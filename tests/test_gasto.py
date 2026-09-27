"""En qué se va el dinero (orden 26, 27/09/2026): coste por parte en el registro y resumen semanal
frente a la línea de ritmo. Con modelos simulados que «cuestan» cifras conocidas."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import pytest
from forecasting_tools import MonetaryCostManager

import main
from bot import config as cfg
from bot import gasto
from bot import marcador as mc
from tests.conftest import MetaculusFalso, ModeloFalso, preguntas_ejemplo

AHORA = datetime(2026, 10, 12, 6, 30, tzinfo=UTC)


class ModeloQueCuesta(ModeloFalso):
    """Como el falso, pero cada llamada «cuesta» lo que diría la librería: 0,01 $ la búsqueda y
    0,10 $ cada pasada de pronóstico."""

    async def invoke(self, prompt):  # type: ignore[override]
        texto = await super().invoke(prompt)
        coste = 0.01 if texto.startswith("Noticias") else 0.10
        MonetaryCostManager.increase_current_usage_in_parent_managers(coste)
        return texto


def test_el_registro_guarda_el_coste_de_cada_parte(monkeypatch, tmp_path):
    modelo = ModeloQueCuesta()
    llms = {"default": modelo, "summarizer": modelo, "researcher": modelo, "parser": modelo}
    monkeypatch.setenv("METACULUS_TOKEN", "t")
    main.ejecutar("test_questions", cliente=MetaculusFalso(preguntas_ejemplo()[:1]), llms=llms)
    [f] = list((tmp_path / "registro").glob("pronosticos_*.jsonl"))
    [fila] = [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines()]
    pasadas = cfg.cargar_params()["pronostico"]["pasadas_por_pregunta"]
    assert fila["coste_partes"] == {
        "busqueda": pytest.approx(0.01),
        "pronostico falso/modelo": pytest.approx(0.10 * pasadas),
    }
    # las partes suman lo mismo que el total de la pregunta (no se cuenta nada dos veces)
    assert sum(fila["coste_partes"].values()) == pytest.approx(fila["coste_usd"])


def _consulta(dias_atras: float, gastado: float) -> dict:
    return {
        "cuando_utc": (AHORA - timedelta(days=dias_atras)).isoformat(),
        "consulta": "openrouter_clave",
        "respuesta": {
            "data": {"usage": 0, "byok_usage": gastado, "limit": 100, "limit_remaining": 0}
        },
    }


def _pregunta(dias_atras: float, partes: dict) -> dict:
    return {
        "cuando_utc": (AHORA - timedelta(days=dias_atras)).isoformat(),
        "url": "u",
        "coste_usd": sum(partes.values()),
        "coste_partes": partes,
    }


def test_resumen_compara_la_clave_con_la_libreria_y_con_la_linea():
    partes = {"busqueda": 0.0, "pronostico a": 0.08, "pronostico b": 0.10}
    filas = [_consulta(6, 10.0), _consulta(0.1, 16.0)]
    filas += [_pregunta(d, partes) for d in (5, 4, 3, 2, 1, 0.5, 0.2, 0.3, 0.4, 0.6)]
    filas += [_consulta(20, 1.0), _pregunta(20, partes)]  # fuera de la semana: no cuentan
    filas.append({"cuando_utc": AHORA.isoformat(), "consulta": "otra"})  # ruido
    r = gasto.resumen(filas, cfg.cargar_params(), AHORA)
    assert r["preguntas"] == 10
    assert r["libreria_total"] == pytest.approx(1.8)
    assert r["por_parte_por_pregunta"]["pronostico b"] == pytest.approx(0.10)
    c = r["clave"]
    assert c["gastado_en_el_periodo"] == pytest.approx(6.0)
    assert c["sin_medir_por_la_libreria"] == pytest.approx(4.2)  # ≈ la búsqueda «:online»
    assert c["gastado_total"] == pytest.approx(16.0)
    # 12/10: 25 % de colchón + 14/100 días del resto ≈ 35 $ permitidos
    assert 30 < c["linea_de_ritmo"] < 40 and c["sobre_la_linea"] < 0
    # quedan 100 - 16 - 3 de reserva = 81 $; a 6 $ por semana, 13,5 semanas
    assert c["semanas_que_quedan"] == pytest.approx(13.5)
    texto = "\n".join(gasto.informe_md(r))
    assert "En qué se va el dinero" in texto and "por debajo" in texto
    assert "Sin medir por la librería" in texto and "pronostico b" in texto


def test_resumen_sin_consultas_de_la_clave():
    r = gasto.resumen([_pregunta(1, {"busqueda": 0.0})], cfg.cargar_params(), AHORA)
    assert r["clave"] == {"consultas": 0}
    assert "ninguna" in "\n".join(gasto.informe_md(r))


def test_consulta_con_otra_forma_se_ignora():
    mala = _consulta(1, 5.0)
    del mala["respuesta"]["data"]["byok_usage"]
    assert gasto.resumen([mala], cfg.cargar_params(), AHORA)["clave"] == {"consultas": 0}


def test_el_marcador_lleva_el_resumen_del_gasto(tmp_path, monkeypatch):
    for nombre in ("HISTORICO", "RESUELTAS", "SALIDA_JSON", "SALIDA_MD"):
        monkeypatch.setattr(mc, nombre, tmp_path / getattr(mc, nombre).name)
    descargas = tmp_path / "descargas" / "a1"
    descargas.mkdir(parents=True)
    ahora = datetime.now(UTC)
    filas = [
        {**_consulta(0, 0), "cuando_utc": (ahora - timedelta(days=2)).isoformat()},
        {**_consulta(0, 3), "cuando_utc": (ahora - timedelta(hours=1)).isoformat()},
    ]
    (descargas / "presupuesto_2026-10.jsonl").write_text(
        "".join(json.dumps(f) + "\n" for f in filas), encoding="utf-8"
    )
    assert mc.main(["--descargas", str(tmp_path / "descargas")]) == 0
    md = (tmp_path / "MARCADOR.md").read_text(encoding="utf-8")
    assert "En qué se va el dinero" in md and "Gastado en el periodo (clave) | 3.0 $" in md
    datos = json.loads((tmp_path / "marcador.json").read_text(encoding="utf-8"))
    assert datos["gasto"]["clave"]["gastado_en_el_periodo"] == pytest.approx(3.0)
