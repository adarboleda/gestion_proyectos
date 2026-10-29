"""Reparto de las simulaciones completas entre entrenamiento, validación y prueba."""
from typing import Dict, List, Tuple

import numpy as np

from preparacion_datos.config import (
    CLASES_SIN_SEVERIDAD,
    CONJUNTOS,
    PROPORCION_TRAIN,
    PROPORCION_VAL,
)
from preparacion_datos.lectura import Simulacion


def tamanos(n: int) -> Tuple[int, int, int]:
    """Tamaños de train, val y test para `n` severidades.

    n_train = round(0.70·n), n_val = round(0.15·n), n_test = n − n_train − n_val.
    """
    n_train = int(round(PROPORCION_TRAIN * n))
    n_val = int(round(PROPORCION_VAL * n))
    return n_train, n_val, n - n_train - n_val


def _clave_orden(simulacion: Simulacion):
    return (simulacion.etiqueta, simulacion.severidad or 0, simulacion.archivo)


def repartir(simulaciones: List[Simulacion], semilla: int) -> Dict[str, List[Simulacion]]:
    """Asigna cada simulación completa a exactamente un conjunto.

    Las severidades (unión de LOCA y LOCAC, ordenadas numéricamente) se reparten una sola vez con
    la semilla dada, de modo que la simulación de LOCA y la de LOCAC de igual severidad caen en el
    mismo conjunto. Las clases sin severidad (Normal y ATWS, una sola simulación) van completas a
    entrenamiento. El resultado no depende del orden de entrada.
    """
    severidades = sorted({s.severidad for s in simulaciones if s.clase not in CLASES_SIN_SEVERIDAD})
    n_train, n_val, _ = tamanos(len(severidades))
    orden = np.random.default_rng(semilla).permutation(len(severidades))
    conjunto_de = {}
    for posicion, indice in enumerate(orden):
        if posicion < n_train:
            conjunto_de[severidades[indice]] = "train"
        elif posicion < n_train + n_val:
            conjunto_de[severidades[indice]] = "val"
        else:
            conjunto_de[severidades[indice]] = "test"
    particion = {conjunto: [] for conjunto in CONJUNTOS}
    for simulacion in simulaciones:
        if simulacion.clase in CLASES_SIN_SEVERIDAD:
            particion["train"].append(simulacion)
        else:
            particion[conjunto_de[simulacion.severidad]].append(simulacion)
    for conjunto in CONJUNTOS:
        particion[conjunto].sort(key=_clave_orden)
    return particion
