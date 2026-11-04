"""Pruebas unitarias de escalado de canales y entrenamiento de la Bi-LSTM de Etapa 2 (009)."""
import numpy as np
import pytest

torch = pytest.importorskip("torch")

from clasificador_etapa2.canales import desviacion_pico  # noqa: E402
from clasificador_etapa2.config import HIPERPARAMETROS  # noqa: E402
from clasificador_etapa2.entrenamiento import (  # noqa: E402
    ajustar_escalador_canales,
    entrenar,
    escalar_canales,
    pesos_clase,
    predecir,
)
from clasificador_etapa2.muestras import construir_muestras, es_rama  # noqa: E402
from preparacion_pwr3l.grupos import formar_grupos  # noqa: E402
from preparacion_pwr3l.particion import repartir  # noqa: E402
from tests.etapa2.conftest import COL  # noqa: E402


def _preparar_conjuntos(sinteticas):
    reparto = repartir(formar_grupos(sinteticas.corridas), semilla=42)
    brutos = {}
    for c in sinteticas.corridas:
        if es_rama(c):
            d_pwr = desviacion_pico(sinteticas.pwr[c.id])
            d_pwnt = desviacion_pico(c.serie[:, COL["PWNT"]])
            brutos[c.id] = np.column_stack([d_pwr, d_pwnt])
    ramas_train = [c for c in reparto.corridas["train"] if es_rama(c)]
    x_train = np.stack([brutos[c.id] for c in ramas_train])
    escalador = ajustar_escalador_canales(x_train)
    escalados = {cid: escalar_canales(escalador, arr[None, ...])[0] for cid, arr in brutos.items()}
    muestras = {
        conj: construir_muestras(reparto.corridas[conj], escalados, sinteticas.inicios, conj == "train")
        for conj in ("train", "val", "test")
    }
    return reparto, brutos, escalador, muestras


def test_escalador_se_ajusta_solo_con_entrenamiento(sinteticas):
    reparto, brutos, escalador1, _ = _preparar_conjuntos(sinteticas)
    # Alterar drásticamente val y test no cambia el escalador
    for conj in ("val", "test"):
        for c in reparto.corridas[conj]:
            if es_rama(c):
                brutos[c.id] = brutos[c.id] * 1000.0 + 500.0
    ramas_train = [c for c in reparto.corridas["train"] if es_rama(c)]
    escalador2 = ajustar_escalador_canales(np.stack([brutos[c.id] for c in ramas_train]))
    np.testing.assert_allclose(escalador1.media, escalador2.media)
    np.testing.assert_allclose(escalador1.escala, escalador2.escala)


def test_pesos_clase_inversos_a_frecuencia():
    y = np.array([0, 0, 0, 1], dtype=np.int64)
    pesos = pesos_clase(y)
    np.testing.assert_allclose(pesos, [4.0 / 6.0, 4.0 / 2.0])


def test_entrenamiento_aprende_y_es_determinista(sinteticas):
    _, _, _, muestras = _preparar_conjuntos(sinteticas)
    hp = dict(HIPERPARAMETROS, epocas=6)
    r1 = entrenar(muestras["train"], muestras["val"], hp, semilla=42)
    r2 = entrenar(muestras["train"], muestras["val"], hp, semilla=42)

    assert r1.historial == r2.historial
    assert r1.mejor_epoca == r2.mejor_epoca
    assert max(h["f1_val"] for h in r1.historial) >= 0.90

    probs1 = predecir(r1.modelo, muestras["test"].x)
    probs2 = predecir(r2.modelo, muestras["test"].x)
    np.testing.assert_allclose(probs1, probs2)
    np.testing.assert_allclose(probs1.sum(axis=1), 1.0, atol=1e-5)


def test_entrenar_falla_si_falta_una_rama_en_entrenamiento(sinteticas):
    _, _, _, muestras = _preparar_conjuntos(sinteticas)
    solo_loca = muestras["train"]
    solo_loca.y = np.zeros_like(solo_loca.y)
    with pytest.raises(ValueError, match="LOCAC"):
        entrenar(solo_loca, muestras["val"], dict(HIPERPARAMETROS, epocas=2), semilla=42)

