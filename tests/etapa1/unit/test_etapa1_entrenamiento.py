"""Pruebas del modelo y del entrenamiento de la Etapa 1 (005, historia 1)."""
import numpy as np
import pytest

torch = pytest.importorskip("torch")

from clasificador_etapa1.config import HIPERPARAMETROS  # noqa: E402
from clasificador_etapa1.entrenamiento import entrenar, pesos_clase, predecir  # noqa: E402
from clasificador_etapa1.modelo import BiLSTMEtapa1  # noqa: E402
from clasificador_etapa1.muestras import construir_muestras  # noqa: E402
from preparacion_pwr3l.grupos import formar_grupos  # noqa: E402
from preparacion_pwr3l.particion import repartir  # noqa: E402

RAPIDO = dict(HIPERPARAMETROS, epocas=8, paciencia=3)


def preparar(sinteticas):
    reparto = repartir(formar_grupos(sinteticas.corridas))
    series = {c.id: c.serie[:, :26].astype(np.float32) for c in sinteticas.corridas}
    m = {
        conjunto: construir_muestras(reparto.corridas[conjunto], series, sinteticas.inicios, conjunto == "train")
        for conjunto in ("train", "val", "test")
    }
    return reparto, m


def test_pesos_de_clase_inversos_a_la_frecuencia():
    y = np.array([0] * 80 + [1] * 15 + [2] * 5)
    pesos = pesos_clase(y)
    np.testing.assert_allclose(pesos, [100 / (3 * 80), 100 / (3 * 15), 100 / (3 * 5)])
    assert pesos[2] > pesos[1] > pesos[0]


def test_la_red_devuelve_tres_salidas_que_suman_1_con_softmax():
    red = BiLSTMEtapa1(entradas=26)
    salida = red(torch.zeros(4, 30, 26))
    assert salida.shape == (4, 3)
    np.testing.assert_allclose(torch.softmax(salida, dim=1).sum(dim=1).detach().numpy(), 1.0, rtol=1e-6)


def test_aprende_las_tres_familias_sinteticas(sinteticas):
    _, m = preparar(sinteticas)
    resultado = entrenar(m["train"], m["val"], RAPIDO, semilla=42)
    assert max(h["f1_val"] for h in resultado.historial) > 0.9


def test_misma_semilla_mismo_modelo_e_historial(sinteticas):
    _, m = preparar(sinteticas)
    a = entrenar(m["train"], m["val"], dict(RAPIDO, epocas=3), semilla=7)
    b = entrenar(m["train"], m["val"], dict(RAPIDO, epocas=3), semilla=7)
    assert a.historial == b.historial
    for (nombre, pa), (_, pb) in zip(a.modelo.state_dict().items(), b.modelo.state_dict().items()):
        assert torch.equal(pa, pb), nombre


def test_devuelve_la_mejor_epoca_y_respeta_la_paciencia(sinteticas):
    _, m = preparar(sinteticas)
    resultado = entrenar(m["train"], m["val"], dict(RAPIDO, epocas=30, paciencia=2), semilla=1)
    f1 = [h["f1_val"] for h in resultado.historial]
    assert resultado.mejor_epoca == int(np.argmax(f1)) + 1
    assert len(f1) - resultado.mejor_epoca <= 2
    # el modelo devuelto es el de la mejor época: su F1 de validación coincide
    from sklearn.metrics import f1_score
    pred = predecir(resultado.modelo, m["val"].x).argmax(axis=1)
    assert f1_score(m["val"].y, pred, average="macro", labels=[0, 1, 2], zero_division=0) == pytest.approx(max(f1))


def test_no_usa_las_corridas_de_prueba(sinteticas):
    reparto, m = preparar(sinteticas)
    prueba = {c.id for c in reparto.corridas["test"]}
    assert not prueba & set(m["train"].corrida) and not prueba & set(m["val"].corrida)
    resultado = entrenar(m["train"], m["val"], dict(RAPIDO, epocas=1), semilla=0)
    assert set(resultado.corridas_entrenamiento) == set(m["train"].corrida)
