"""Pruebas del escalador PWR 3L ajustado solo con entrenamiento (26 entradas, 300 pasos)."""
import numpy as np
import pytest

from preparacion_pwr3l.config import PASOS, VARIABLES_ENTRADA, VARIABLES_MARGEN
from preparacion_pwr3l.escalado import Escalador, ajustar_escalador, aplicar

TOLERANCIA = 1e-4


def datos(n: int, semilla: int, desplazamiento: float = 0.0) -> np.ndarray:
    rng = np.random.default_rng(semilla)
    n_vars = len(VARIABLES_ENTRADA)
    base = rng.normal(
        loc=np.arange(n_vars) * 5.0,
        scale=np.arange(1, n_vars + 1) * 0.5,
        size=(n, PASOS, n_vars),
    )
    return base + desplazamiento


def test_ninguna_variable_de_margen_entra_en_el_escalado():
    assert len(VARIABLES_ENTRADA) == 26
    assert set(VARIABLES_ENTRADA).isdisjoint(VARIABLES_MARGEN)


def test_parametros_son_los_de_las_filas_de_entrenamiento_aplanadas():
    x_train = datos(15, 1)
    escalador = ajustar_escalador(x_train)
    assert isinstance(escalador, Escalador)
    filas = x_train.reshape(-1, 26)
    np.testing.assert_allclose(escalador.media, filas.mean(axis=0), rtol=1e-12)
    np.testing.assert_allclose(escalador.escala, filas.std(axis=0), rtol=1e-12)
    assert escalador.filas_ajuste == 15 * 300


def test_entrenamiento_escalado_tiene_media_0_y_desviacion_1():
    x_train = datos(15, 2)
    escalado = aplicar(ajustar_escalador(x_train), x_train)
    filas = escalado.reshape(-1, 26).astype(np.float64)
    assert np.all(np.abs(filas.mean(axis=0)) < TOLERANCIA)
    assert np.all(np.abs(filas.std(axis=0) - 1.0) < TOLERANCIA)


def test_cambiar_validacion_o_prueba_no_altera_los_parametros():
    x_train = datos(15, 3)
    escalador = ajustar_escalador(x_train)
    media, escala = escalador.media.copy(), escalador.escala.copy()
    aplicar(escalador, datos(4, 10, desplazamiento=1e5))
    aplicar(escalador, datos(4, 11, desplazamiento=-1e5))
    np.testing.assert_array_equal(escalador.media, media)
    np.testing.assert_array_equal(escalador.escala, escala)
    repetido = ajustar_escalador(x_train.copy())
    np.testing.assert_array_equal(repetido.media, media)
    np.testing.assert_array_equal(repetido.escala, escala)


def test_validacion_y_prueba_se_transforman_con_parametros_de_entrenamiento():
    x_train, x_val = datos(15, 4), datos(4, 5)
    escalador = ajustar_escalador(x_train)
    esperado = ((x_val - escalador.media) / escalador.escala).astype(np.float32)
    np.testing.assert_array_equal(aplicar(escalador, x_val), esperado)


def test_variable_sin_varianza_queda_con_escala_1_e_informada_sin_nan_ni_inf():
    x_train = datos(10, 6)
    x_train[:, :, 3] = 42.0
    x_train[:, :, 25] = -3.5
    escalador = ajustar_escalador(x_train)
    assert escalador.escala[3] == 1.0 and escalador.escala[25] == 1.0
    assert escalador.variables_sin_varianza == [VARIABLES_ENTRADA[3], VARIABLES_ENTRADA[25]]
    escalado = aplicar(escalador, x_train)
    assert np.all(np.isfinite(escalado))
    assert np.all(escalado[:, :, 3] == 0.0) and np.all(escalado[:, :, 25] == 0.0)


def test_formas_tipos_y_conjunto_vacio():
    x_train = datos(8, 7)
    escalador = ajustar_escalador(x_train)
    assert escalador.media.shape == (26,) and escalador.media.dtype == np.float64
    assert escalador.escala.shape == (26,) and escalador.escala.dtype == np.float64
    escalado = aplicar(escalador, x_train)
    assert escalado.shape == (8, 300, 26) and escalado.dtype == np.float32
    vacio = aplicar(escalador, np.empty((0, 300, 26), dtype=np.float64))
    assert vacio.shape == (0, 300, 26) and vacio.dtype == np.float32


@pytest.mark.parametrize(
    "forma",
    [
        (0, 300, 26),
        (5, 300),
        (5, 299, 26),
        (5, 300, 33),
    ],
)
def test_ajustar_escalador_rechaza_entrenamiento_vacio_o_forma_invalida(forma):
    with pytest.raises(ValueError):
        ajustar_escalador(np.zeros(forma, dtype=np.float64))


@pytest.mark.parametrize(
    "forma",
    [
        (5, 300),
        (5, 299, 26),
        (5, 300, 33),
    ],
)
def test_aplicar_rechaza_forma_invalida(forma):
    escalador = ajustar_escalador(datos(5, 8))
    with pytest.raises(ValueError):
        aplicar(escalador, np.zeros(forma, dtype=np.float64))
