"""Pruebas unitarias de la construcción de muestras de evento para la Etapa 2 (009)."""
import math

import numpy as np
import pytest

from clasificador_etapa2.config import HORIZONTE_ENTRENAMIENTO_S, VENTANA_S
from clasificador_etapa2.muestras import construir_muestras, es_rama


def test_es_rama_filtra_solo_loca_y_locac_usables(sinteticas):
    clases = {c.clase for c in sinteticas.corridas if es_rama(c)}
    assert clases == {"LOCA", "LOCAC"}


def test_construir_muestras_entrenamiento_recorta_a_60s_y_evaluacion_usa_todo(sinteticas):
    ramas = [c for c in sinteticas.corridas if es_rama(c)][:4]
    canales = {c.id: np.ones((300, 2), dtype=np.float32) * (i + 1) for i, c in enumerate(ramas)}
    inicios = {c.id: 20.2 for c in ramas}  # ceil(20.2) = 21

    m_train = construir_muestras(ramas, canales, inicios, entrenamiento=True)
    m_eval = construir_muestras(ramas, canales, inicios, entrenamiento=False)

    # En entrenamiento: k = 0..60 (61 muestras por corrida)
    assert len(m_train) == 4 * (HORIZONTE_ENTRENAMIENTO_S + 1)
    assert m_train.x.shape == (len(m_train), VENTANA_S, 2)
    assert m_train.k.min() == 0.0 and m_train.k.max() == float(HORIZONTE_ENTRENAMIENTO_S)
    assert m_train.tau.min() == math.ceil(20.2)

    # En evaluación: τ = 21..299 (279 muestras por corrida)
    assert len(m_eval) == 4 * (300 - 21)
    assert m_eval.k.min() == 0.0 and m_eval.k.max() == float(299 - 21)
    assert set(m_eval.y.tolist()) == {0, 1}


def test_construir_muestras_ignora_otras_clases_y_falla_sin_inicio(sinteticas):
    canales = {c.id: np.zeros((300, 2), dtype=np.float32) for c in sinteticas.corridas}
    m = construir_muestras(sinteticas.corridas, canales, sinteticas.inicios, entrenamiento=True)
    ids_ramas = {c.id for c in sinteticas.corridas if c.clase in ("LOCA", "LOCAC")}
    assert set(m.corrida.tolist()) == ids_ramas

    una_loca = next(c for c in sinteticas.corridas if c.clase == "LOCA")
    inicios_mal = dict(sinteticas.inicios, **{una_loca.id: None})
    with pytest.raises(ValueError, match=una_loca.id):
        construir_muestras([una_loca], canales, inicios_mal, entrenamiento=True)

