"""Pruebas de la verificación de fuga del reparto NPPAD de 001 (004, historia 3)."""
import pytest

from preparacion_datos.lectura import cargar_simulaciones
from preparacion_datos.particion import repartir
from preparacion_datos.verificacion import ErrorFuga, verificar_particion


@pytest.fixture
def particion(origen_sintetico):
    return repartir(cargar_simulaciones(origen_sintetico), 42)


def buscar(particion, archivo):
    for conjunto, lista in particion.items():
        for simulacion in lista:
            if simulacion.archivo == archivo:
                return conjunto, simulacion
    raise AssertionError(archivo)


def otro(conjunto):
    return {"train": "test", "val": "train", "test": "train"}[conjunto]


def test_la_particion_de_001_no_tiene_fuga(particion):
    verificar_particion(particion)


def test_simulacion_en_dos_conjuntos(particion):
    conjunto, simulacion = buscar(particion, "LOCA/7.csv")
    particion[otro(conjunto)].append(simulacion)
    with pytest.raises(ErrorFuga) as error:
        verificar_particion(particion)
    pares = sorted([conjunto, otro(conjunto)], key=("train", "val", "test").index)
    assert f"la simulación LOCA/7.csv está en {pares[0]} y en {pares[1]}" in error.value.violaciones


def test_severidad_partida_entre_loca_y_locac(particion):
    conjunto, locac = buscar(particion, "LOCAC/37.csv")
    particion[conjunto].remove(locac)
    particion[otro(conjunto)].append(locac)
    with pytest.raises(ErrorFuga) as error:
        verificar_particion(particion)
    linea = next(v for v in error.value.violaciones if v.startswith("la severidad 37 está partida"))
    assert f"LOCA/37.csv ({conjunto})" in linea and f"LOCAC/37.csv ({otro(conjunto)})" in linea


def test_varias_violaciones_juntas(particion):
    for archivo in ("LOCA/7.csv", "LOCAC/12.csv"):
        conjunto, simulacion = buscar(particion, archivo)
        particion[otro(conjunto)].append(simulacion)
    with pytest.raises(ErrorFuga) as error:
        verificar_particion(particion)
    assert len(error.value.violaciones) >= 2
    assert str(error.value).startswith("FUGA DE DATOS: ")
