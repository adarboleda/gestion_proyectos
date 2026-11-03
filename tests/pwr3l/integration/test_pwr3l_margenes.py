"""Márgenes térmicos sin escalar, alineados paso a paso con las entradas (US2)."""
import csv

import numpy as np
import pytest

from preparacion_pwr3l.cli import main
from preparacion_pwr3l.config import CONJUNTOS, VARIABLES_ENTRADA, VARIABLES_MARGEN


@pytest.fixture(scope="module")
def salida(arbol_pwr3l, tmp_path_factory):
    destino = tmp_path_factory.mktemp("margenes") / "s"
    assert main(["--origen", str(arbol_pwr3l), "--salida", str(destino)]) == 0
    return destino


def _todas(salida):
    return np.concatenate([np.load(salida / f"margins_{c}.npy") for c in CONJUNTOS])


def test_forma_y_tipo(salida):
    for conjunto in CONJUNTOS:
        margenes = np.load(salida / f"margins_{conjunto}.npy")
        x = np.load(salida / f"X_{conjunto}.npy")
        assert margenes.dtype == np.float64 and margenes.shape == (len(x), 300, 7)


def _filas_identicas(salida, esperado):
    return sum(np.array_equal(m, esperado) for m in _todas(salida))


def test_csv_identico_al_archivo(arbol_pwr3l, salida):
    with open(arbol_pwr3l / "auto" / "R31_NORM" / "plotdata.csv", newline="", encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))[:300]
    esperado = np.array([[float(f[v]) for v in VARIABLES_MARGEN] for f in filas])
    assert _filas_identicas(salida, esperado) == 1


def test_xlsx_identico_al_archivo(arbol_pwr3l, salida, ayudantes):
    esperado = ayudantes.celdas_xlsx(arbol_pwr3l / "NORM" / "R01_NORM" / "R01_plotdata_NORM.xls", VARIABLES_MARGEN)[:300]
    assert _filas_identicas(salida, esperado) == 1


def test_margenes_fuera_de_las_entradas_y_del_escalador(salida):
    assert not set(VARIABLES_MARGEN) & set(VARIABLES_ENTRADA)
    assert np.load(salida / "scaler_mean.npy").shape == (26,)
    assert np.load(salida / "scaler_std.npy").shape == (26,)
