"""Reparto de los grupos de corridas PWR 3L en entrenamiento, validación y prueba sin partir grupos."""
from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np

from preparacion_pwr3l.config import CLASES, CONJUNTOS, PROPORCIONES, SEMILLA
from preparacion_pwr3l.descubrimiento import Corrida, clave_orden
from preparacion_pwr3l.grupos import ORDEN_FAMILIAS, Grupo


@dataclass(eq=False)
class Reparto:
    semilla: int
    grupos: List[Grupo]
    conjunto_de_grupo: Dict[str, str]  # clave de grupo -> conjunto
    conjunto_de_corrida: Dict[str, str]  # id de corrida -> conjunto
    corridas: Dict[str, List[Corrida]]  # conjunto -> corridas ordenadas con clave_orden
    conteos: Dict[str, Dict[str, int]]  # clase -> conjunto -> corridas (las 5 clases, ceros incluidos)
    metas: Dict[str, Dict[str, float]] = field(default_factory=dict)  # familia -> conjunto -> meta
    asignadas: Dict[str, Dict[str, int]] = field(default_factory=dict)  # familia -> conjunto -> corridas


def metas(n: int) -> Dict[str, float]:
    """Metas de corridas por conjunto para una familia de `n` corridas: 70/15/15, sin redondear."""
    return {conjunto: PROPORCIONES[conjunto] * n for conjunto in CONJUNTOS}


def _repartir_familia(grupos: List[Grupo], generador: np.random.Generator):
    """Asigna cada grupo al conjunto con mayor déficit, de mayor a menor tamaño (empates sorteados)."""
    sorteo = generador.permutation(len(grupos))
    orden = sorted(range(len(grupos)), key=lambda i: (-grupos[i].tamano, int(sorteo[i])))
    meta = metas(sum(g.tamano for g in grupos))
    asignadas = {conjunto: 0 for conjunto in CONJUNTOS}
    destino = {}
    for i in orden:
        # Mayor déficit; ante empate, el primero de CONJUNTOS (train -> val -> test)
        conjunto = max(CONJUNTOS, key=lambda c: (meta[c] - asignadas[c], -CONJUNTOS.index(c)))
        destino[grupos[i].clave] = conjunto
        asignadas[conjunto] += grupos[i].tamano
    return destino, meta, asignadas


def repartir(grupos: List[Grupo], semilla: int = SEMILLA) -> Reparto:
    """Reparte los grupos completos por familia hacia 70/15/15.

    Determinista: el resultado depende solo de los grupos y de la semilla, no del orden de la lista.
    """
    claves = [g.clave for g in grupos]
    if len(set(claves)) != len(claves):
        raise ValueError("Hay grupos con la misma clave.")
    generador = np.random.default_rng(semilla)
    conjunto_de_grupo: Dict[str, str] = {}
    metas_familia: Dict[str, Dict[str, float]] = {}
    asignadas_familia: Dict[str, Dict[str, int]] = {}
    for familia in ORDEN_FAMILIAS:
        de_familia = sorted((g for g in grupos if g.familia == familia), key=lambda g: g.clave)
        destino, meta, asignadas = _repartir_familia(de_familia, generador)
        conjunto_de_grupo.update(destino)
        metas_familia[familia] = meta
        asignadas_familia[familia] = asignadas
    ordenados = sorted(grupos, key=lambda g: (ORDEN_FAMILIAS.index(g.familia), g.clave))
    conjunto_de_corrida = {c.id: conjunto_de_grupo[g.clave] for g in ordenados for c in g.corridas}
    corridas = {
        conjunto: sorted(
            (c for g in ordenados if conjunto_de_grupo[g.clave] == conjunto for c in g.corridas), key=clave_orden
        )
        for conjunto in CONJUNTOS
    }
    conteos = {clase: {conjunto: 0 for conjunto in CONJUNTOS} for clase in CLASES}
    for conjunto, lista in corridas.items():
        for corrida in lista:
            conteos[corrida.clase][conjunto] += 1
    return Reparto(
        semilla=semilla,
        grupos=ordenados,
        conjunto_de_grupo=conjunto_de_grupo,
        conjunto_de_corrida=conjunto_de_corrida,
        corridas=corridas,
        conteos=conteos,
        metas=metas_familia,
        asignadas=asignadas_familia,
    )
