"""Pruebas de lectura y validación de las simulaciones (FR-001, FR-002, FR-012)."""
import numpy as np
import pytest

from preparacion_datos.lectura import ErrorDatos, descubrir_simulaciones, leer_simulacion


def test_descubre_las_cuatro_clases_con_sus_etiquetas(origen_sintetico):
    simulaciones = descubrir_simulaciones(origen_sintetico)
    por_clase = {}
    for s in simulaciones:
        por_clase.setdefault((s.clase, s.etiqueta), []).append(s)
    assert {k: len(v) for k, v in por_clase.items()} == {
        ("NORM", 0): 1,
        ("LOCA", 1): 100,
        ("LOCAC", 2): 100,
        ("ATWS", 3): 1,
    }


def test_severidad_numerica_del_nombre_y_orden_numerico(origen_sintetico):
    loca = [s for s in descubrir_simulaciones(origen_sintetico) if s.clase == "LOCA"]
    assert [s.severidad for s in loca] == list(range(1, 101))
    assert loca[6].archivo == "LOCA/7.csv"
    normal = [s for s in descubrir_simulaciones(origen_sintetico) if s.clase == "NORM"][0]
    assert normal.severidad is None


def test_serie_de_forma_150_x_19_con_las_primeras_150_filas(origen_sintetico, ayudas):
    sim = leer_simulacion(origen_sintetico, "LOCA", "7.csv")
    assert sim.serie.shape == (150, 19)
    esperado = ayudas.leer_independiente(origen_sintetico / "LOCA" / "7.csv", ayudas.VARIABLES)
    np.testing.assert_array_equal(sim.serie, esperado)


def test_defectos_fuera_de_las_primeras_150_filas_no_detienen(origen_sintetico, ayudas):
    ayudas.poner_valor(origen_sintetico / "LOCA" / "7.csv", "P", 155, "")
    sim = leer_simulacion(origen_sintetico, "LOCA", "7.csv")
    assert sim.serie.shape == (150, 19)


@pytest.mark.parametrize(
    "defecto, causa",
    [
        ("columna", "falta la variable"),
        ("texto", "valor no numérico"),
        ("vacio", "valor faltante"),
        ("infinito", "valor no finito"),
        ("corto", "menos de 150 pasos (tiene 149)"),
    ],
)
def test_archivo_defectuoso_lanza_error_con_archivo_y_causa(origen_sintetico, ayudas, defecto, causa):
    ruta = origen_sintetico / "LOCAC" / "12.csv"
    if defecto == "columna":
        ayudas.quitar_columna(ruta, "TSAT")
    elif defecto == "texto":
        ayudas.poner_valor(ruta, "TSAT", 20, "abc")
    elif defecto == "vacio":
        ayudas.poner_valor(ruta, "TSAT", 20, "")
    elif defecto == "infinito":
        ayudas.poner_valor(ruta, "TSAT", 20, "inf")
    else:
        ayudas.truncar(ruta, 149)
    with pytest.raises(ErrorDatos) as info:
        leer_simulacion(origen_sintetico, "LOCAC", "12.csv")
    mensaje = str(info.value)
    assert mensaje.startswith("ERROR: LOCAC/12.csv: ")
    assert causa in mensaje
    if defecto != "corto":
        assert "[variable TSAT]" in mensaje


def test_carpeta_de_clase_inexistente(origen_sintetico):
    import shutil

    shutil.rmtree(origen_sintetico / "ATWS")
    with pytest.raises(ErrorDatos) as info:
        descubrir_simulaciones(origen_sintetico)
    assert "no existe la carpeta de clase" in str(info.value)
    assert "ATWS" in str(info.value)
