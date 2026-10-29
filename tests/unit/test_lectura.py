"""Pruebas de lectura, validación de las simulaciones y verificación del paso de muestreo desde TIME."""
import numpy as np
import pytest

from preparacion_datos import config
from preparacion_datos.lectura import ErrorDatos, cargar_simulaciones, descubrir_simulaciones, leer_simulacion


def test_config_no_asume_paso_segundos_fijo():
    assert not hasattr(config, "PASO_SEGUNDOS")
    assert config.VARIABLE_TIEMPO == "TIME"


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


def test_serie_de_forma_150_x_19_con_las_primeras_150_filas_y_paso_medido(origen_sintetico, ayudas):
    sim = leer_simulacion(origen_sintetico, "LOCA", "7.csv")
    assert sim.serie.shape == (150, 19)
    assert sim.paso_segundos == 10
    esperado = ayudas.leer_independiente(origen_sintetico / "LOCA" / "7.csv", ayudas.VARIABLES)
    np.testing.assert_array_equal(sim.serie, esperado)


def test_paso_constante_distinto_de_10_y_ruido_de_redondeo_dentro_de_tolerancia(origen_sintetico, ayudas):
    ruta = origen_sintetico / "LOCA" / "7.csv"
    for fila in range(160):
        ruido = 1e-8 if fila % 2 == 0 else -1e-8
        ayudas.poner_valor(ruta, "TIME", fila, f"{100.0 + fila * 5.0 + ruido:.10f}")
    sim = leer_simulacion(origen_sintetico, "LOCA", "7.csv")
    assert sim.paso_segundos == 5


@pytest.mark.parametrize(
    "valor, causa",
    [("", "valor faltante"), ("abc", "valor no numérico"), ("inf", "valor no finito")],
)
def test_defectos_en_cualquier_fila_del_archivo_detienen(origen_sintetico, ayudas, valor, causa):
    # FR-012: el archivo se valida completo, también las filas posteriores a los 150 pasos usados.
    ayudas.poner_valor(origen_sintetico / "LOCA" / "7.csv", "P", 155, valor)
    with pytest.raises(ErrorDatos) as info:
        leer_simulacion(origen_sintetico, "LOCA", "7.csv")
    assert str(info.value).startswith("ERROR: LOCA/7.csv: ")
    assert causa in str(info.value) and "[variable P]" in str(info.value)


def test_un_archivo_valido_mas_largo_solo_aporta_sus_primeros_150_pasos(origen_sintetico, ayudas):
    sim = leer_simulacion(origen_sintetico, "LOCA", "7.csv")  # el archivo sintético tiene 160 filas
    esperado = ayudas.leer_independiente(origen_sintetico / "LOCA" / "7.csv", ayudas.VARIABLES, filas=160)
    assert sim.serie.shape == (150, 19)
    np.testing.assert_array_equal(sim.serie, esperado[:150])


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


@pytest.mark.parametrize(
    "defecto, causa",
    [
        ("sin_time", "falta la variable"),
        ("time_vacio", "valor faltante"),
        ("time_texto", "valor no numérico"),
        ("time_inf", "valor no finito"),
        ("una_fila", "menos de 2 filas para calcular el paso de muestreo"),
        ("repetido", "el tiempo no avanza en la fila de datos 6"),
        ("retroceso", "el tiempo no avanza en la fila de datos 6"),
        ("salto_temprano", "paso de muestreo no constante en la fila de datos 6 (esperado 10 s, encontrado 15 s)"),
        ("salto_tardio", "paso de muestreo no constante en la fila de datos 156 (esperado 10 s, encontrado 12 s)"),
    ],
)
def test_defectos_en_time_detienen_con_archivo_causa_y_variable_time(origen_sintetico, ayudas, defecto, causa):
    ruta = origen_sintetico / "LOCA" / "7.csv"
    if defecto == "sin_time":
        ayudas.quitar_columna(ruta, "TIME")
    elif defecto == "time_vacio":
        ayudas.poner_valor(ruta, "TIME", 4, "")
    elif defecto == "time_texto":
        ayudas.poner_valor(ruta, "TIME", 4, "no_es_tiempo")
    elif defecto == "time_inf":
        ayudas.poner_valor(ruta, "TIME", 4, "inf")
    elif defecto == "una_fila":
        ayudas.truncar(ruta, 1)
    elif defecto == "repetido":
        ayudas.poner_valor(ruta, "TIME", 5, "40.0")
    elif defecto == "retroceso":
        ayudas.poner_valor(ruta, "TIME", 5, "35.0")
    elif defecto == "salto_temprano":
        ayudas.poner_valor(ruta, "TIME", 5, "55.0")
    elif defecto == "salto_tardio":
        ayudas.poner_valor(ruta, "TIME", 155, "1552.0")
    with pytest.raises(ErrorDatos) as info:
        leer_simulacion(origen_sintetico, "LOCA", "7.csv")
    assert info.value.archivo == "LOCA/7.csv"
    assert info.value.variable == "TIME"
    assert causa in info.value.causa


def test_cargar_simulaciones_detiene_si_un_archivo_tiene_paso_distinto_al_resto(origen_sintetico, ayudas):
    ruta = origen_sintetico / "LOCAC" / "3.csv"
    for fila in range(160):
        ayudas.poner_valor(ruta, "TIME", fila, f"{fila * 5.0}")
    with pytest.raises(ErrorDatos) as info:
        cargar_simulaciones(origen_sintetico)
    assert info.value.archivo == "LOCAC/3.csv"
    assert info.value.variable == "TIME"
    assert "paso de muestreo (5 s) distinto al del resto del dataset (10 s en Normal/1.csv)" in info.value.causa


def test_carpeta_de_clase_inexistente(origen_sintetico):
    import shutil

    shutil.rmtree(origen_sintetico / "ATWS")
    with pytest.raises(ErrorDatos) as info:
        descubrir_simulaciones(origen_sintetico)
    assert "no existe la carpeta de clase" in str(info.value)
    assert "ATWS" in str(info.value)


def test_normal_y_atws_pueden_tener_cualquier_nombre_de_archivo(origen_sintetico):
    (origen_sintetico / "Normal" / "1.csv").rename(origen_sintetico / "Normal" / "base_normal.csv")
    (origen_sintetico / "ATWS" / "1.csv").rename(origen_sintetico / "ATWS" / "atws.csv")
    simulaciones = descubrir_simulaciones(origen_sintetico)
    normal = [s for s in simulaciones if s.clase == "NORM"]
    atws = [s for s in simulaciones if s.clase == "ATWS"]
    assert [(s.archivo, s.severidad) for s in normal] == [("Normal/base_normal.csv", None)]
    assert [(s.archivo, s.severidad) for s in atws] == [("ATWS/atws.csv", None)]
    assert leer_simulacion(origen_sintetico, "Normal", "base_normal.csv").serie.shape == (150, 19)


def test_loca_y_locac_siguen_exigiendo_nombre_numerico(origen_sintetico):
    (origen_sintetico / "LOCA" / "7.csv").rename(origen_sintetico / "LOCA" / "siete.csv")
    with pytest.raises(ErrorDatos) as info:
        descubrir_simulaciones(origen_sintetico)
    assert "LOCA/siete.csv" in str(info.value)
    assert "severidad" in str(info.value)
