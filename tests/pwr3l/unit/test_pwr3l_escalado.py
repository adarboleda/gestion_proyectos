"""Escalado de las 26 entradas, ajustado solo con entrenamiento."""
import numpy as np

from preparacion_pwr3l.config import VARIABLES_ENTRADA
from preparacion_pwr3l.escalado import ajustar_escalador, aplicar


def _datos(n, semilla):
    rng = np.random.default_rng(semilla)
    return rng.normal(loc=np.arange(26) * 10.0, scale=np.arange(1, 27), size=(n, 300, 26))


def test_parametros_iguales_a_los_de_las_filas_de_entrenamiento():
    x = _datos(5, 0)
    escalador = ajustar_escalador(x)
    filas = x.reshape(-1, 26)
    assert np.allclose(escalador.media, filas.mean(axis=0), rtol=1e-12, atol=0)
    assert np.allclose(escalador.escala, filas.std(axis=0), rtol=1e-12, atol=0)
    assert escalador.filas_ajuste == 5 * 300
    assert escalador.media.shape == (26,) and escalador.escala.shape == (26,)


def test_entrenamiento_escalado_queda_centrado():
    x = _datos(4, 1)
    escalado = aplicar(ajustar_escalador(x), x)
    filas = escalado.reshape(-1, 26).astype(np.float64)
    assert np.all(np.abs(filas.mean(axis=0)) < 1e-4)
    assert np.all(np.abs(filas.std(axis=0) - 1) < 1e-4)


def test_val_y_test_no_alteran_los_parametros():
    x = _datos(4, 2)
    escalador = ajustar_escalador(x)
    media = escalador.media.copy()
    aplicar(escalador, _datos(3, 3) * 50)
    assert np.array_equal(escalador.media, media)
    assert np.array_equal(ajustar_escalador(x).media, media)


def test_variable_sin_varianza_se_informa_sin_valores_invalidos():
    x = _datos(3, 4)
    x[:, :, 5] = 7.0
    escalador = ajustar_escalador(x)
    assert escalador.variables_sin_varianza == [VARIABLES_ENTRADA[5]]
    escalado = aplicar(escalador, x)
    assert np.all(np.isfinite(escalado)) and np.all(escalado[:, :, 5] == 0)


def test_salida_float32_con_la_misma_forma_incluso_vacia():
    escalador = ajustar_escalador(_datos(2, 5))
    assert aplicar(escalador, _datos(3, 6)).dtype == np.float32
    vacio = aplicar(escalador, np.empty((0, 300, 26)))
    assert vacio.shape == (0, 300, 26) and vacio.dtype == np.float32
