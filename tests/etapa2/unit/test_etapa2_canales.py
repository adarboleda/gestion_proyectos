"""Pruebas unitarias de los canales de desviación pico causal de PWR y PWNT (009)."""
import numpy as np
import pytest

from clasificador_etapa2.canales import canales_corrida, desviacion_pico, leer_pwr
from preparacion_pwr3l.config import PASOS, VARIABLES
from preparacion_pwr3l.descubrimiento import Corrida, ErrorDatos
from tests.etapa2.conftest import COL, escribir_csv_corrida


def test_desviacion_pico_resta_valor_inicial_y_olvida_tras_15s():
    x = np.full(40, 100.0)
    # Pulso constante de +6 en t = 5, 6, 7 → media móvil de 3 s alcanza +6 en t = 7
    x[5:8] = 106.0
    d = desviacion_pico(x)
    assert d.shape == (40,)
    assert np.isclose(d[0], 0.0)
    assert np.isclose(d[4], 0.0)
    assert np.isclose(d[5], 2.0)   # MM3(5) = (100+100+106)/3 = 102 → +2
    assert np.isclose(d[6], 4.0)   # MM3(6) = (100+106+106)/3 = 104 → +4
    assert np.isclose(d[7], 6.0)   # MM3(7) = (106+106+106)/3 = 106 → +6
    # El máximo de +6 en t=7 permanece dentro de la ventana [τ-14, τ] hasta τ = 21
    assert np.isclose(d[21], 6.0)
    # En τ = 22 la ventana es [8, 22]: en t=8 MM3(8)=(106+106+100)/3=104 → +4; en τ = 24 ya es 0
    assert np.isclose(d[22], 4.0)
    assert np.isclose(d[24], 0.0)


def test_desviacion_pico_es_estrictamente_causal():
    rng = np.random.default_rng(7)
    x1 = 100.0 + rng.standard_normal(60)
    x2 = x1.copy()
    tau = 25
    x2[tau + 1:] += 50.0  # alteración futura grande después de τ
    d1 = desviacion_pico(x1)
    d2 = desviacion_pico(x2)
    np.testing.assert_allclose(d1[: tau + 1], d2[: tau + 1], atol=1e-12)


def test_desviacion_pico_rechaza_serie_vacia_o_no_1d():
    with pytest.raises(ValueError):
        desviacion_pico(np.array([]))
    with pytest.raises(ValueError):
        desviacion_pico(np.ones((10, 2)))


def test_leer_pwr_y_canales_corrida_desde_archivo(tmp_path):
    serie = np.full((PASOS, len(VARIABLES)), 50.0)
    serie[:, COL["PWNT"]] = 100.0
    serie[10:20, COL["PWNT"]] = 103.0
    pwr = np.full(PASOS, 100.0)
    pwr[10:20] = 101.5
    relativo = "auto/R41_LOCA/plotdata.csv"
    escribir_csv_corrida(tmp_path / relativo, serie, pwr=pwr)

    corrida = Corrida("R41", "LOCA", "auto", relativo, area=50, estado="usable", filas=PASOS, paso_segundos=1, serie=serie)
    leido = leer_pwr(tmp_path, corrida)
    assert leido.shape == (PASOS,)
    np.testing.assert_allclose(leido, pwr)

    canales = canales_corrida(tmp_path, corrida)
    assert canales.shape == (PASOS, 2)
    np.testing.assert_allclose(canales[:, 0], desviacion_pico(pwr))
    np.testing.assert_allclose(canales[:, 1], desviacion_pico(serie[:, COL["PWNT"]]))


def test_leer_pwr_falla_si_falta_columna_o_no_es_numerica(tmp_path):
    serie = np.ones((PASOS, len(VARIABLES)))
    rel_sin = "auto/R41_LOCA/plotdata.csv"
    escribir_csv_corrida(tmp_path / rel_sin, serie, incluir_pwr=False)
    corrida_sin = Corrida("R41", "LOCA", "auto", rel_sin, area=50, estado="usable", filas=PASOS, paso_segundos=1, serie=serie)
    with pytest.raises(ErrorDatos, match="PWR"):
        leer_pwr(tmp_path, corrida_sin)

    rel_mal = "auto/R42_LOCA/plotdata.csv"
    pwr_mal = [100.0] * PASOS
    pwr_mal[12] = "NO_NUMERICO"
    escribir_csv_corrida(tmp_path / rel_mal, serie, pwr=pwr_mal)
    corrida_mal = Corrida("R42", "LOCA", "auto", rel_mal, area=50, estado="usable", filas=PASOS, paso_segundos=1, serie=serie)
    with pytest.raises(ErrorDatos, match="PWR"):
        leer_pwr(tmp_path, corrida_mal)

