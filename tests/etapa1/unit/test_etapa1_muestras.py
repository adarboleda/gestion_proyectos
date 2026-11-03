"""Pruebas de las muestras: ventana causal de 30 s por segundo y etiquetas (005)."""
import math

import numpy as np
import pytest

from clasificador_etapa1.muestras import construir_muestras


def series_de(corridas):
    return {c.id: c.serie[:, :26].astype(np.float32) for c in corridas}


def una(sinteticas, rid):
    return next(c for c in sinteticas.corridas if c.id == rid)


def test_una_muestra_por_segundo_desde_5_en_validacion_y_prueba(sinteticas):
    c = una(sinteticas, "R200")
    m = construir_muestras([c], series_de([c]), sinteticas.inicios, entrenamiento=False)
    assert list(m.tau) == list(range(5, 300))
    assert m.x.shape == (295, 30, 26) and m.x.dtype == np.float32
    assert m.y.dtype == np.int64 and m.tau.dtype == np.int64 and m.k.dtype == np.float64
    assert set(m.corrida) == {"R200"}


def test_ventana_son_las_filas_hasta_tau_y_se_rellena_con_la_fila_0(sinteticas):
    c = una(sinteticas, "R31")
    series = series_de([c])
    m = construir_muestras([c], series, sinteticas.inicios, entrenamiento=False)
    i = list(m.tau).index(100)
    np.testing.assert_array_equal(m.x[i], series["R31"][71:101])
    j = list(m.tau).index(5)
    esperado = np.vstack([np.repeat(series["R31"][:1], 24, axis=0), series["R31"][:6]])
    np.testing.assert_array_equal(m.x[j], esperado)


def test_ninguna_fila_posterior_a_tau(sinteticas):
    c = una(sinteticas, "R201")
    series = series_de([c])
    series["R201"][200:] = 999.0  # si se usaran filas futuras aparecería este valor
    m = construir_muestras([c], series, sinteticas.inicios, entrenamiento=False)
    assert not np.any(m.x[m.tau < 200] == 999.0)


def test_etiquetas_y_k_segun_el_inicio(sinteticas):
    c = una(sinteticas, "R21")  # ATWS -> TRANS (2)
    inicio = int(sinteticas.inicios["R21"])
    m = construir_muestras([c], series_de([c]), sinteticas.inicios, entrenamiento=False)
    assert set(m.y[m.tau < inicio]) <= {0}
    assert set(m.y[m.tau >= inicio]) == {2}
    np.testing.assert_array_equal(m.k, m.tau - inicio)


def test_inicio_fraccionario_se_redondea_hacia_arriba(sinteticas):
    c = una(sinteticas, "R200")  # LOCA -> 1
    inicios = dict(sinteticas.inicios, R200=24.5)
    m = construir_muestras([c], series_de([c]), inicios, entrenamiento=False)
    assert m.y[list(m.tau).index(24)] == 0
    assert m.y[list(m.tau).index(25)] == 1
    assert m.k[list(m.tau).index(25)] == 0.0


def test_norm_siempre_norm_y_k_nan(sinteticas):
    c = una(sinteticas, "R32")
    m = construir_muestras([c], series_de([c]), sinteticas.inicios, entrenamiento=False)
    assert set(m.y) == {0}
    assert all(math.isnan(v) for v in m.k)


def test_entrenamiento_solo_tramo_previo_y_primeros_60_s(sinteticas):
    norm, evento = una(sinteticas, "R33"), una(sinteticas, "R202")
    inicio = int(sinteticas.inicios["R202"])
    m = construir_muestras([norm, evento], series_de([norm, evento]), sinteticas.inicios, entrenamiento=True)
    assert (m.corrida == "R33").sum() == 295
    de_evento = m.corrida == "R202"
    k = m.k[de_evento]
    assert np.all((k < 0) | (k <= 60))
    assert k.max() == 60
    assert (m.tau[de_evento] < inicio).sum() == max(inicio - 5, 0)


def test_familias_por_clase(sinteticas):
    ids = {"R34": 0, "R200": 1, "R201": 1, "R22": 2, "R60": 2}
    corridas = [una(sinteticas, r) for r in ids]
    m = construir_muestras(corridas, series_de(corridas), sinteticas.inicios, entrenamiento=False)
    for rid, familia in ids.items():
        etiquetas = set(m.y[(m.corrida == rid) & (m.tau >= 299)])
        assert etiquetas == {familia}, rid


def test_corrida_de_evento_sin_inicio_detiene(sinteticas):
    c = una(sinteticas, "R200")
    inicios = dict(sinteticas.inicios)
    del inicios["R200"]
    with pytest.raises(ValueError, match="R200"):
        construir_muestras([c], series_de([c]), inicios, entrenamiento=False)
