"""Reparto de grupos completos entre entrenamiento, validación y prueba (research.md §8)."""
from typing import Dict, List, Tuple

import numpy as np

from preparacion_pwr3l.config import CONJUNTOS, PROPORCIONES
from preparacion_pwr3l.descubrimiento import Corrida, clave_orden
from preparacion_pwr3l.grupos import Grupo


def repartir(grupos: List[Grupo], semilla: int) -> Tuple[Dict[str, str], Dict[str, List[Corrida]]]:
    """Asigna cada grupo completo a un conjunto; devuelve (conjunto por grupo, corridas por conjunto).

    Por familia: los grupos se ordenan por clave, se barajan con la semilla y se asignan uno a uno
    al conjunto con mayor déficit respecto de su meta (desempate train → val → test). Un grupo solo
    va a un conjunto con déficit positivo, así que ningún conjunto supera su meta en un grupo entero.
    """
    conjunto_de: Dict[str, str] = {}
    for familia in sorted({g.familia for g in grupos}):
        propios = sorted((g for g in grupos if g.familia == familia), key=lambda g: g.clave)
        total = sum(len(g.corridas) for g in propios)
        metas = {c: PROPORCIONES[c] * total for c in CONJUNTOS}
        asignadas = {c: 0 for c in CONJUNTOS}
        for indice in np.random.default_rng(semilla).permutation(len(propios)):
            grupo = propios[indice]
            destino = max(CONJUNTOS, key=lambda c: (metas[c] - asignadas[c], -CONJUNTOS.index(c)))
            conjunto_de[grupo.clave] = destino
            asignadas[destino] += len(grupo.corridas)
    particion: Dict[str, List[Corrida]] = {c: [] for c in CONJUNTOS}
    for grupo in grupos:
        particion[conjunto_de[grupo.clave]].extend(grupo.corridas)
    for conjunto in CONJUNTOS:
        particion[conjunto].sort(key=clave_orden)
    return conjunto_de, particion
