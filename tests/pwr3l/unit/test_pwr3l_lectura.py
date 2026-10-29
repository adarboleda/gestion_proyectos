"""Lectura, validación del archivo completo y medición del paso de muestreo en PWR 3L."""
import csv

import numpy as np
import openpyxl
import pandas as pd
import pytest

from preparacion_pwr3l import config
from preparacion_pwr3l.config import PASOS, VARIABLES, VARIABLES_ENTRADA, VARIABLES_MARGEN
from preparacion_pwr3l.descubrimiento import ErrorDatos, descubrir_corridas
from preparacion_pwr3l.lectura import cargar_corridas, leer_corrida, obtener_paso_comun


@pytest.fixture(scope="module")
def cargadas(arbol_pwr3l):
    return {c.id: c for c in cargar_corridas(arbol_pwr3l)}


def _corrida(origen, rid):
    return next(c for c in descubrir_corridas(origen) if c.id == rid)


def test_variables_requeridas_y_sin_paso_fijo_en_config():
    assert len(VARIABLES_ENTRADA) == 26 and len(VARIABLES_MARGEN) == 7
    assert VARIABLES == VARIABLES_ENTRADA + VARIABLES_MARGEN
    assert "WLR" not in VARIABLES and "PWR" not in VARIABLES
    assert PASOS == 300
    assert not hasattr(config, "PASO_SEGUNDOS")


def test_csv_serie_de_300_pasos_con_los_valores_del_texto_y_paso_medido(arbol_pwr3l, cargadas):
    corrida = cargadas["R31"]
    assert corrida.estado == "usable" and corrida.filas == 301 and corrida.paso_segundos == 1
    assert corrida.serie.shape == (300, 33) and corrida.serie.dtype == np.float64
    with open(arbol_pwr3l / corrida.archivo, newline="", encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    esperado = np.array([[float(fila[v]) for v in VARIABLES] for fila in filas[:300]])
    assert np.array_equal(corrida.serie, esperado)


def test_libro_xlsx_con_extension_xls(arbol_pwr3l, cargadas):
    corrida = cargadas["R01"]
    assert corrida.archivo.endswith(".xls") and corrida.estado == "usable" and corrida.paso_segundos == 1
    assert corrida.serie.shape == (300, 33)
    with open(arbol_pwr3l / corrida.archivo, "rb") as archivo:
        libro = openpyxl.load_workbook(archivo, data_only=True, read_only=True)
        filas = list(libro.active.iter_rows(values_only=True))
        libro.close()
    cabecera = [str(c).strip() for c in filas[0]]
    indices = [cabecera.index(v) for v in VARIABLES]
    esperado = np.array([[float(fila[i]) for i in indices] for fila in filas[1:301]], dtype=np.float64)
    assert np.array_equal(corrida.serie, esperado)


def test_corrida_de_exactamente_300_filas_es_usable(cargadas):
    assert cargadas["R76"].filas == 300 and cargadas["R76"].estado == "usable" and cargadas["R76"].paso_segundos == 1


def test_corrida_corta_se_marca_sin_serie_pero_con_paso_medido(cargadas):
    corta = cargadas["R55"]
    assert corta.estado == "corta" and corta.filas == 295 and corta.serie is None and corta.paso_segundos == 1


def test_descartadas_y_ood_no_se_leen(cargadas):
    for rid in ("R07", "R27", "R20", "R64"):
        assert cargadas[rid].filas is None and cargadas[rid].serie is None and cargadas[rid].paso_segundos is None
    assert cargadas["R07"].estado == "descartada" and cargadas["R20"].estado == "ood"


def test_todas_las_demas_quedan_usables_y_paso_comun_es_1(cargadas):
    estados = {c.estado for rid, c in cargadas.items() if rid not in {"R07", "R27", "R20", "R64", "R55"}}
    assert estados == {"usable"}
    assert obtener_paso_comun(list(cargadas.values())) == 1


def test_paso_constante_distinto_de_1_y_redondeo_dentro_de_tolerancia(copia_pwr3l):
    corrida = _corrida(copia_pwr3l, "R33")
    ruta = copia_pwr3l / corrida.archivo
    tabla = pd.read_csv(ruta, dtype=str, keep_default_na=False)
    tabla["TIME"] = [f"{i * 2.0 + (1e-8 if i % 2 else 0.0):.10f}" for i in range(len(tabla))]
    tabla.to_csv(ruta, index=False)
    leida = leer_corrida(copia_pwr3l, corrida)
    assert leida.paso_segundos == 2


@pytest.mark.parametrize(
    "modo, variable, causa",
    [
        ("quitar", "DNBR", "falta la variable"),
        ("quitar", "RM1", "falta la variable"),
        ("texto", "P", "valor no numérico"),
        ("vacio", "TPCT", "valor faltante"),
        ("inf", "WFWA", "valor no finito"),
    ],
)
def test_archivo_defectuoso_detiene_con_archivo_causa_y_variable(copia_pwr3l, ayudantes, modo, variable, causa):
    corrida = _corrida(copia_pwr3l, "R33")
    ayudantes.corromper_csv(copia_pwr3l / corrida.archivo, modo, variable)
    with pytest.raises(ErrorDatos) as info:
        leer_corrida(copia_pwr3l, corrida)
    assert info.value.archivo == "auto/R33_NORM/plotdata.csv"
    assert info.value.causa == causa and info.value.variable == variable
    assert str(info.value).startswith("ERROR: auto/R33_NORM/plotdata.csv: ")


def test_defecto_despues_de_la_fila_300_tambien_detiene(copia_pwr3l, ayudantes):
    corrida = _corrida(copia_pwr3l, "R33")
    ayudantes.corromper_csv(copia_pwr3l / corrida.archivo, "texto", "P", fila=300)
    with pytest.raises(ErrorDatos, match="valor no numérico"):
        leer_corrida(copia_pwr3l, corrida)


def test_defecto_en_una_corrida_corta_detiene(copia_pwr3l, ayudantes):
    corrida = _corrida(copia_pwr3l, "R55")
    ayudantes.corromper_csv(copia_pwr3l / corrida.archivo, "vacio", "P")
    with pytest.raises(ErrorDatos, match="valor faltante"):
        leer_corrida(copia_pwr3l, corrida)


@pytest.mark.parametrize(
    "fila, esperado",
    [
        (0, "el tiempo debe iniciar en 0 s (inicia en 1 s)"),
        (7, "paso de muestreo no constante en la fila de datos 8 (esperado 1 s, encontrado 2 s)"),
        (300, "paso de muestreo no constante en la fila de datos 301 (esperado 1 s, encontrado 2 s)"),
    ],
)
def test_tiempo_que_no_inicia_en_0_o_cambia_de_paso(copia_pwr3l, ayudantes, fila, esperado):
    corrida = _corrida(copia_pwr3l, "R33")
    ayudantes.corromper_csv(copia_pwr3l / corrida.archivo, "salto", fila=fila)
    with pytest.raises(ErrorDatos) as info:
        leer_corrida(copia_pwr3l, corrida)
    assert esperado in info.value.causa
    assert info.value.variable == "TIME"


@pytest.mark.parametrize(
    "valor, esperado",
    [
        ("4", "el tiempo no avanza en la fila de datos 6 (paso 0 s)"),
        ("2", "el tiempo no avanza en la fila de datos 6 (paso -2 s)"),
    ],
)
def test_tiempo_repetido_o_que_retrocede_detiene(copia_pwr3l, valor, esperado):
    corrida = _corrida(copia_pwr3l, "R33")
    ruta = copia_pwr3l / corrida.archivo
    tabla = pd.read_csv(ruta, dtype=str, keep_default_na=False)
    tabla.loc[5, "TIME"] = valor
    tabla.to_csv(ruta, index=False)
    with pytest.raises(ErrorDatos) as info:
        leer_corrida(copia_pwr3l, corrida)
    assert esperado in info.value.causa
    assert info.value.variable == "TIME"


def test_archivo_con_una_sola_fila_detiene(copia_pwr3l):
    corrida = _corrida(copia_pwr3l, "R33")
    ruta = copia_pwr3l / corrida.archivo
    tabla = pd.read_csv(ruta, dtype=str, keep_default_na=False).iloc[:1]
    tabla.to_csv(ruta, index=False)
    with pytest.raises(ErrorDatos) as info:
        leer_corrida(copia_pwr3l, corrida)
    assert "menos de 2 filas para calcular el paso de muestreo" in info.value.causa
    assert info.value.variable == "TIME"


def test_paso_discordante_entre_corridas_detiene_en_cargar_corridas(copia_pwr3l):
    corrida = _corrida(copia_pwr3l, "R33")
    ruta = copia_pwr3l / corrida.archivo
    tabla = pd.read_csv(ruta, dtype=str, keep_default_na=False)
    tabla["TIME"] = [str(i * 2) for i in range(len(tabla))]
    tabla.to_csv(ruta, index=False)
    with pytest.raises(ErrorDatos) as info:
        cargar_corridas(copia_pwr3l)
    assert info.value.archivo == "auto/R33_NORM/plotdata.csv"
    assert info.value.variable == "TIME"
    assert "paso de muestreo (2 s) distinto al del resto del dataset (1 s en NORM/R01_NORM/R01_plotdata_NORM.xls)" in info.value.causa


def test_xlsx_con_celda_vacia(copia_pwr3l, ayudantes):
    corrida = _corrida(copia_pwr3l, "R09")
    tabla = ayudantes.datos_corrida(3).astype(object)
    tabla.loc[10, "SCMA"] = None
    ayudantes.escribir_tabla(copia_pwr3l / corrida.archivo, tabla, "xlsx")
    with pytest.raises(ErrorDatos) as info:
        leer_corrida(copia_pwr3l, corrida)
    assert info.value.causa == "valor faltante" and info.value.variable == "SCMA"


def test_archivo_ilegible(copia_pwr3l):
    corrida = _corrida(copia_pwr3l, "R09")
    (copia_pwr3l / corrida.archivo).write_bytes(b"esto no es un libro de Excel")
    with pytest.raises(ErrorDatos, match="archivo ilegible"):
        leer_corrida(copia_pwr3l, corrida)


def test_cargar_se_detiene_en_el_primer_defecto(copia_pwr3l, ayudantes):
    ayudantes.corromper_csv(copia_pwr3l / "auto" / "R44_LOCA" / "plotdata.csv", "quitar", "TSAT")
    with pytest.raises(ErrorDatos, match="R44_LOCA"):
        cargar_corridas(copia_pwr3l)
