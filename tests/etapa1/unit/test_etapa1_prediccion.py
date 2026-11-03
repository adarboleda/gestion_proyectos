"""Pruebas de la clasificación consultiva con el modelo guardado (005, historia 3)."""
import json

import numpy as np
import pytest

torch = pytest.importorskip("torch")

import clasificador_etapa1.cli as cli  # noqa: E402
from clasificador_etapa1.config import AVISO  # noqa: E402
from clasificador_etapa1.muestras import ventanas  # noqa: E402
from clasificador_etapa1.prediccion import cargar  # noqa: E402


@pytest.fixture
def modelo_publicado(sinteticas, monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "cargar_corridas", lambda origen: sinteticas.corridas)
    monkeypatch.setattr(cli, "inicios_evento", lambda origen, corridas: dict(sinteticas.inicios))
    salida = tmp_path / "etapa1"
    assert cli.main(["--origen", "x", "--salida", str(salida), "--epocas", "6"]) == 0
    return salida, {c.id: c for c in sinteticas.corridas}


def test_devuelve_probabilidades_recomendacion_y_aviso(modelo_publicado):
    salida, por_id = modelo_publicado
    resultado = cargar(salida).clasificar(por_id["R200"].serie[:120, :26])
    assert set(resultado["probabilidades"]) == {"NORM", "LOCA", "TRANS"}
    assert sum(resultado["probabilidades"].values()) == pytest.approx(1.0, abs=1e-6)
    assert resultado["recomendacion"] in {"NORM", "LOCA", "TRANS", "INCIERTO"}
    assert resultado["aviso"] == AVISO


def test_recomienda_la_mas_probable_si_supera_el_umbral(modelo_publicado):
    salida, por_id = modelo_publicado
    resultado = cargar(salida).clasificar(por_id["R31"].serie[:200, :26])
    mejor = max(resultado["probabilidades"], key=resultado["probabilidades"].get)
    esperado = mejor if resultado["probabilidades"][mejor] >= 0.80 else "INCIERTO"
    assert resultado["recomendacion"] == esperado


def test_incierto_si_ninguna_alcanza_el_umbral(modelo_publicado, monkeypatch):
    salida, por_id = modelo_publicado
    clasificador = cargar(salida)
    monkeypatch.setattr(clasificador.modelo, "forward", lambda x: torch.zeros(x.shape[0], 3))
    resultado = clasificador.clasificar(por_id["R200"].serie[:120, :26])
    assert resultado["recomendacion"] == "INCIERTO"
    assert resultado["probabilidades"]["NORM"] == pytest.approx(1 / 3)


def test_coincide_con_escalar_y_pasar_la_ventana_al_modelo(modelo_publicado):
    salida, por_id = modelo_publicado
    clasificador = cargar(salida)
    configuracion = json.loads((salida / "modelo.json").read_text(encoding="utf-8"))
    serie = por_id["R21"].serie[:90, :26]
    escalada = ((serie - np.array(configuracion["escalador"]["media"])) / np.array(configuracion["escalador"]["escala"])).astype(np.float32)
    x = ventanas(escalada, np.array([len(serie) - 1]))
    with torch.no_grad():
        esperado = torch.softmax(clasificador.modelo(torch.from_numpy(x)), dim=1).numpy()[0]
    obtenido = clasificador.clasificar(serie)["probabilidades"]
    np.testing.assert_allclose([obtenido[f] for f in ("NORM", "LOCA", "TRANS")], esperado, rtol=1e-5, atol=1e-6)


@pytest.mark.parametrize("forma", [(10, 25), (4, 26), (26,)])
def test_serie_invalida(modelo_publicado, forma):
    salida, _ = modelo_publicado
    with pytest.raises(ValueError):
        cargar(salida).clasificar(np.zeros(forma))
