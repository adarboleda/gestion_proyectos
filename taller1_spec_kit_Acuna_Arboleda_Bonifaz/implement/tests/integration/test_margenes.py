"""Márgenes térmicos conservados aparte, sin escalar y alineados con las variables de planta (FR-008)."""
import numpy as np
import pytest

from preparacion_datos.cli import main
from preparacion_datos.lectura import descubrir_simulaciones
from preparacion_datos.particion import repartir

CONJUNTOS = ("train", "val", "test")


@pytest.fixture(scope="module")
def corrida(_origen_base, tmp_path_factory):
    """Ejecuta una vez la preparación completa sobre el dataset sintético."""
    trabajo = tmp_path_factory.mktemp("trabajo_margenes")
    salida = trabajo / "salida"
    with pytest.MonkeyPatch.context() as mp:
        mp.chdir(trabajo)  # `../IA-Nuclear/...` no existe desde aquí
        assert main(["--origen", str(_origen_base), "--salida", str(salida)]) == 0
    particion = repartir(descubrir_simulaciones(_origen_base), 42)
    return salida, particion, _origen_base


def test_forma_tipo_y_orden_de_filas(corrida):
    salida, _, _ = corrida
    for c in CONJUNTOS:
        margenes = np.load(salida / f"margins_{c}.npy")
        x, y = np.load(salida / f"X_{c}.npy"), np.load(salida / f"y_{c}.npy")
        assert margenes.shape == (len(y), 150, 7)
        assert margenes.dtype == np.float64
        assert x.shape[0] == margenes.shape[0]


def test_valores_identicos_a_los_del_csv_de_origen(corrida, ayudas):
    salida, particion, origen = corrida
    for c in CONJUNTOS:
        margenes = np.load(salida / f"margins_{c}.npy")
        for fila, simulacion in enumerate(particion[c]):
            esperado = ayudas.leer_independiente(origen / simulacion.archivo, ayudas.VARIABLES_MARGEN)
            np.testing.assert_array_equal(margenes[fila], esperado, err_msg=simulacion.archivo)


def test_los_margenes_no_estan_escalados(corrida):
    salida, _, _ = corrida
    for nombre in ("scaler_mean.npy", "scaler_std.npy"):
        assert np.load(salida / nombre).shape == (12,)
    margenes = np.load(salida / "margins_train.npy").reshape(-1, 7)
    # Una variable escalada tendría media ~0; los márgenes conservan sus unidades originales.
    assert np.abs(margenes.mean(axis=0)).min() > 1.0


def test_alineacion_paso_a_paso_con_las_variables_de_planta(corrida, ayudas):
    salida, particion, origen = corrida
    media, escala = np.load(salida / "scaler_mean.npy"), np.load(salida / "scaler_std.npy")
    for c in CONJUNTOS:
        x = np.load(salida / f"X_{c}.npy")
        margenes = np.load(salida / f"margins_{c}.npy")
        for fila, simulacion in enumerate(particion[c]):
            archivo = origen / simulacion.archivo
            planta = ayudas.leer_independiente(archivo, ayudas.VARIABLES_PLANTA)
            # X está en float32: la reconstrucción coincide hasta su resolución (1e-5).
            np.testing.assert_allclose(x[fila] * escala + media, planta, rtol=1e-5, atol=1e-5)
            np.testing.assert_array_equal(
                margenes[fila], ayudas.leer_independiente(archivo, ayudas.VARIABLES_MARGEN)
            )
