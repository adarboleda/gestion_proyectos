"""Lectura y validación del archivo completo de cada corrida (CSV y libros xlsx)."""
import csv

import numpy as np
import pytest

from preparacion_pwr3l.config import PASOS, VARIABLES, VARIABLES_ENTRADA, VARIABLES_MARGEN
from preparacion_pwr3l.descubrimiento import ErrorDatos, descubrir_corridas
from preparacion_pwr3l.lectura import cargar_corridas, leer_corrida


@pytest.fixture(scope="module")
def cargadas(arbol_pwr3l):
    return {c.id: c for c in cargar_corridas(arbol_pwr3l)}


def _corrida(origen, rid):
    return next(c for c in descubrir_corridas(origen) if c.id == rid)


def test_variables_requeridas():
    assert len(VARIABLES_ENTRADA) == 26 and len(VARIABLES_MARGEN) == 7
    assert VARIABLES == VARIABLES_ENTRADA + VARIABLES_MARGEN
    assert "WLR" not in VARIABLES and "PWR" not in VARIABLES
    assert PASOS == 300


def test_csv_serie_de_300_pasos_con_los_valores_del_texto(arbol_pwr3l, cargadas):
    corrida = cargadas["R31"]
    assert corrida.estado == "usable" and corrida.filas == 301
    assert corrida.serie.shape == (300, 33) and corrida.serie.dtype == np.float64
    with open(arbol_pwr3l / corrida.archivo, newline="", encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    esperado = np.array([[float(fila[v]) for v in VARIABLES] for fila in filas[:300]])
    assert np.array_equal(corrida.serie, esperado)


def test_libro_xlsx_con_extension_xls(arbol_pwr3l, cargadas, ayudantes):
    corrida = cargadas["R01"]
    assert corrida.archivo.endswith(".xls") and corrida.estado == "usable"
    assert corrida.serie.shape == (300, 33)
    tabla = ayudantes.datos_corrida(1)
    assert np.array_equal(corrida.serie, tabla[VARIABLES].to_numpy()[:300])


def test_corrida_de_exactamente_300_filas_es_usable(cargadas):
    assert cargadas["R76"].filas == 300 and cargadas["R76"].estado == "usable"


def test_corrida_corta_se_marca_sin_serie(cargadas):
    corta = cargadas["R55"]
    assert corta.estado == "corta" and corta.filas == 295 and corta.serie is None


def test_descartadas_y_ood_no_se_leen(cargadas):
    for rid in ("R07", "R27", "R20", "R64"):
        assert cargadas[rid].filas is None and cargadas[rid].serie is None
    assert cargadas["R07"].estado == "descartada" and cargadas["R20"].estado == "ood"


def test_todas_las_demas_quedan_usables(cargadas):
    estados = {c.estado for rid, c in cargadas.items() if rid not in {"R07", "R27", "R20", "R64", "R55"}}
    assert estados == {"usable"}


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


@pytest.mark.parametrize("fila", [0, 7, 300])
def test_tiempo_que_no_avanza_de_1_s_desde_0(copia_pwr3l, ayudantes, fila):
    corrida = _corrida(copia_pwr3l, "R33")
    ayudantes.corromper_csv(copia_pwr3l / corrida.archivo, "salto", fila=fila)
    with pytest.raises(ErrorDatos) as info:
        leer_corrida(copia_pwr3l, corrida)
    assert "el tiempo no avanza de 1 s en 1 s desde 0" in info.value.causa
    assert info.value.variable == "TIME"


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
