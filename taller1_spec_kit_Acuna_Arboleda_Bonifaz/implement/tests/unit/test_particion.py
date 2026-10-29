"""Pruebas de la partición por simulación completa (FR-003, FR-004, FR-007, FR-011)."""
import random

import pytest

from preparacion_datos.lectura import Simulacion
from preparacion_datos.particion import repartir, tamanos

CONJUNTOS = ("train", "val", "test")


def construir(n_loca=100, n_locac=100):
    simulaciones = [Simulacion("NORM", 0, None, "Normal/1.csv")]
    simulaciones += [Simulacion("LOCA", 1, n, f"LOCA/{n}.csv") for n in range(1, n_loca + 1)]
    simulaciones += [Simulacion("LOCAC", 2, n, f"LOCAC/{n}.csv") for n in range(1, n_locac + 1)]
    simulaciones.append(Simulacion("ATWS", 3, None, "ATWS/1.csv"))
    return simulaciones


def archivos(particion):
    return {c: [s.archivo for s in particion[c]] for c in CONJUNTOS}


def test_ninguna_simulacion_aparece_en_mas_de_un_conjunto():
    simulaciones = construir()
    particion = repartir(simulaciones, semilla=42)
    por_conjunto = archivos(particion)
    for i, a in enumerate(CONJUNTOS):
        for b in CONJUNTOS[i + 1:]:
            assert set(por_conjunto[a]).isdisjoint(por_conjunto[b])
    todos = [f for c in CONJUNTOS for f in por_conjunto[c]]
    assert len(todos) == len(set(todos)) == len(simulaciones)
    assert set(todos) == {s.archivo for s in simulaciones}


def test_loca_y_locac_de_igual_severidad_van_al_mismo_conjunto():
    particion = repartir(construir(), semilla=42)
    conjunto_de = {s.archivo: c for c in CONJUNTOS for s in particion[c]}
    for n in range(1, 101):
        assert conjunto_de[f"LOCA/{n}.csv"] == conjunto_de[f"LOCAC/{n}.csv"]


def test_conteos_70_15_15_por_clase_y_totales_142_30_30():
    particion = repartir(construir(), semilla=42)
    conteo = {c: {} for c in CONJUNTOS}
    for c in CONJUNTOS:
        for s in particion[c]:
            conteo[c][s.clase] = conteo[c].get(s.clase, 0) + 1
    assert conteo["train"] == {"NORM": 1, "LOCA": 70, "LOCAC": 70, "ATWS": 1}
    assert conteo["val"] == {"LOCA": 15, "LOCAC": 15}
    assert conteo["test"] == {"LOCA": 15, "LOCAC": 15}
    assert [len(particion[c]) for c in CONJUNTOS] == [142, 30, 30]


def test_normal_y_atws_aparecen_solo_en_entrenamiento():
    particion = repartir(construir(), semilla=42)
    for conjunto in ("val", "test"):
        assert all(s.clase not in ("NORM", "ATWS") for s in particion[conjunto])
    en_train = [s.clase for s in particion["train"]]
    assert en_train.count("NORM") == 1
    assert en_train.count("ATWS") == 1


def test_reparto_determinista_con_semilla_42_y_distinto_con_otra():
    a = archivos(repartir(construir(), semilla=42))
    b = archivos(repartir(construir(), semilla=42))
    c = archivos(repartir(construir(), semilla=7))
    assert a == b
    assert a != c


def test_no_depende_del_orden_de_entrada():
    simulaciones = construir()
    barajadas = list(simulaciones)
    random.Random(1).shuffle(barajadas)
    assert archivos(repartir(simulaciones, 42)) == archivos(repartir(barajadas, 42))


def test_cada_conjunto_se_ordena_por_clase_y_severidad():
    particion = repartir(construir(), semilla=42)
    for conjunto in CONJUNTOS:
        claves = [(s.etiqueta, s.severidad or 0) for s in particion[conjunto]]
        assert claves == sorted(claves)


def test_severidad_presente_en_una_sola_clase_se_asigna_sin_romper_la_regla():
    simulaciones = construir(n_loca=100, n_locac=90)
    particion = repartir(simulaciones, semilla=42)
    por_conjunto = archivos(particion)
    todos = [f for c in CONJUNTOS for f in por_conjunto[c]]
    assert len(todos) == len(set(todos)) == len(simulaciones)
    conjunto_de = {s.archivo: c for c in CONJUNTOS for s in particion[c]}
    for n in range(1, 91):
        assert conjunto_de[f"LOCA/{n}.csv"] == conjunto_de[f"LOCAC/{n}.csv"]


@pytest.mark.parametrize(
    "n, esperado",
    [(100, (70, 15, 15)), (20, (14, 3, 3)), (10, (7, 2, 1)), (7, (5, 1, 1))],
)
def test_tamanos_de_los_conjuntos(n, esperado):
    # n_train = round(0.70·n), n_val = round(0.15·n), n_test = n − n_train − n_val
    assert tamanos(n) == esperado
    assert sum(tamanos(n)) == n
