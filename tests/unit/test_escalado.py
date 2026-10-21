"""Pruebas del escalador ajustado solo con entrenamiento (FR-005, FR-006)."""
import numpy as np

from preparacion_datos.config import VARIABLES_PLANTA
from preparacion_datos.escalado import ajustar_escalador, aplicar

TOLERANCIA = 1e-5


def datos(n, semilla, desplazamiento=0.0):
    rng = np.random.default_rng(semilla)
    base = rng.normal(loc=np.arange(12) * 10.0, scale=np.arange(1, 13), size=(n, 150, 12))
    return base + desplazamiento


def test_parametros_son_los_de_las_filas_de_entrenamiento():
    x_train = datos(20, 1)
    escalador = ajustar_escalador(x_train)
    filas = x_train.reshape(-1, 12)
    np.testing.assert_allclose(escalador.media, filas.mean(axis=0), rtol=1e-12)
    np.testing.assert_allclose(escalador.escala, filas.std(axis=0), rtol=1e-12)
    assert escalador.filas_ajuste == 20 * 150


def test_cambiar_validacion_y_prueba_no_altera_los_parametros():
    x_train = datos(20, 1)
    escalador = ajustar_escalador(x_train)
    media, escala = escalador.media.copy(), escalador.escala.copy()
    aplicar(escalador, datos(5, 2, desplazamiento=1e6))
    aplicar(escalador, datos(5, 3, desplazamiento=-1e6))
    np.testing.assert_array_equal(escalador.media, media)
    np.testing.assert_array_equal(escalador.escala, escala)
    # El ajuste solo recibe entrenamiento: con los mismos datos de entrenamiento da lo mismo.
    otro = ajustar_escalador(x_train.copy())
    np.testing.assert_array_equal(otro.media, media)
    np.testing.assert_array_equal(otro.escala, escala)


def test_entrenamiento_escalado_tiene_media_0_y_desviacion_1():
    x_train = datos(20, 1)
    escalado = aplicar(ajustar_escalador(x_train), x_train)
    filas = escalado.reshape(-1, 12).astype(np.float64)
    assert np.all(np.abs(filas.mean(axis=0)) < TOLERANCIA)
    assert np.all(np.abs(filas.std(axis=0) - 1.0) < TOLERANCIA)


def test_validacion_y_prueba_usan_los_parametros_de_entrenamiento():
    x_train, x_val = datos(20, 1), datos(5, 2)
    escalador = ajustar_escalador(x_train)
    esperado = ((x_val - escalador.media) / escalador.escala).astype(np.float32)
    np.testing.assert_array_equal(aplicar(escalador, x_val), esperado)


def test_variable_sin_varianza_queda_con_escala_1_y_se_informa():
    x_train = datos(20, 1)
    x_train[:, :, 4] = 7.5
    escalador = ajustar_escalador(x_train)
    assert escalador.escala[4] == 1.0
    assert escalador.variables_sin_varianza == [VARIABLES_PLANTA[4]]
    escalado = aplicar(escalador, x_train)
    assert np.all(np.isfinite(escalado))
    assert np.all(escalado[:, :, 4] == 0.0)


def test_formas_y_tipos():
    x_train = datos(20, 1)
    escalador = ajustar_escalador(x_train)
    assert escalador.media.shape == (12,) and escalador.media.dtype == np.float64
    assert escalador.escala.shape == (12,) and escalador.escala.dtype == np.float64
    escalado = aplicar(escalador, x_train)
    assert escalado.shape == (20, 150, 12)
    assert escalado.dtype == np.float32
    assert escalador.variables_sin_varianza == []
