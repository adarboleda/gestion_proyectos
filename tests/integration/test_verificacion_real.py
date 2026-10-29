"""Verificación de fuga del reparto NPPAD de 001 con el dataset real (se omite si no está)."""
import pytest

from datos_reales import ruta_nppad
from preparacion_datos.lectura import cargar_simulaciones
from preparacion_datos.particion import repartir
from preparacion_datos.verificacion import verificar_particion

ORIGEN = ruta_nppad()

pytestmark = pytest.mark.skipif(not ORIGEN.is_dir(), reason="dataset NPPAD no disponible")


def test_el_reparto_real_de_001_no_tiene_fuga():
    particion = repartir(cargar_simulaciones(ORIGEN), 42)
    verificar_particion(particion)

    conjunto_de = {}
    for conjunto, lista in particion.items():
        for simulacion in lista:
            assert simulacion.archivo not in conjunto_de
            conjunto_de[simulacion.archivo] = conjunto
    por_severidad = {}
    for conjunto, lista in particion.items():
        for simulacion in lista:
            if simulacion.clase in ("LOCA", "LOCAC"):
                por_severidad.setdefault(simulacion.severidad, set()).add(conjunto)
    assert por_severidad
    assert all(len(conjuntos) == 1 for conjuntos in por_severidad.values())
