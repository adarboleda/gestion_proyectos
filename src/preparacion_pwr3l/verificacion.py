"""Verificación independiente de que un reparto PWR 3L no tiene fuga de datos.

Las reglas se comprueban con los atributos de cada corrida (estado, área y gemela), no con los
grupos, de modo que también detectan un error al agrupar.
"""
from typing import Dict, List

from preparacion_pwr3l.config import CLASES, CLASES_CON_AREA, CONJUNTOS
from preparacion_pwr3l.descubrimiento import Corrida, clave_id


class ErrorFuga(Exception):
    """Reparto con fuga de datos: lista todas las violaciones encontradas."""

    def __init__(self, violaciones: List[str]):
        self.violaciones = list(violaciones)
        detalle = "\n".join(f"- {v}" for v in self.violaciones)
        super().__init__(f"FUGA DE DATOS: {len(self.violaciones)} violación(es)\n{detalle}")


def _ordenados(conjuntos) -> List[str]:
    return sorted(set(conjuntos), key=CONJUNTOS.index)


def _usable(corrida: Corrida) -> bool:
    return corrida.estado == "usable" and corrida.clase in CLASES


def verificar_reparto(corridas: List[Corrida], reparto) -> None:
    """Comprueba el reparto contra todas las corridas (incluidas las excluidas).

    Reglas: (a) cada corrida usable en exactamente un conjunto; (b) ningún grupo partido; (c) todas
    las LOCA/LOCAC de una misma área en el mismo conjunto; (d) cada pareja de gemelas usables en el
    mismo conjunto; (e) ninguna corrida corta, descartada u OOD en un conjunto. Lanza ``ErrorFuga``.
    """
    conjuntos_de: Dict[str, List[str]] = {}
    objeto: Dict[str, Corrida] = {c.id: c for c in corridas}
    for conjunto in CONJUNTOS:
        for corrida in reparto.corridas.get(conjunto, []):
            conjuntos_de.setdefault(corrida.id, []).append(conjunto)
            objeto.setdefault(corrida.id, corrida)
    violaciones: List[str] = []

    for rid in sorted(conjuntos_de, key=clave_id):
        corrida = objeto[rid]
        if not _usable(corrida):
            for conjunto in _ordenados(conjuntos_de[rid]):
                violaciones.append(f"la corrida {rid} ({corrida.estado}) está en {conjunto}")
        elif len(set(conjuntos_de[rid])) > 1:
            violaciones.append(f"la corrida {rid} está en " + " y en ".join(_ordenados(conjuntos_de[rid])))

    usables = sorted((c for c in objeto.values() if _usable(c)), key=lambda c: clave_id(c.id))
    for corrida in usables:
        if corrida.id not in conjuntos_de:
            violaciones.append(f"la corrida usable {corrida.id} no está en ningún conjunto")

    def describir(corrida: Corrida) -> str:
        return f"{corrida.id} ({'/'.join(_ordenados(conjuntos_de[corrida.id]))})"

    por_area: Dict[int, List[Corrida]] = {}
    for corrida in usables:
        if corrida.clase in CLASES_CON_AREA and corrida.area is not None and corrida.id in conjuntos_de:
            por_area.setdefault(corrida.area, []).append(corrida)
    for area in sorted(por_area):
        miembros = por_area[area]
        if len({c for m in miembros for c in conjuntos_de[m.id]}) > 1:
            violaciones.append(f"el área de {area} cm² está partida: " + ", ".join(describir(m) for m in miembros))

    vistas = set()
    for corrida in usables:
        gemela = objeto.get(corrida.gemela) if corrida.gemela else None
        if gemela is None or not _usable(gemela) or frozenset((corrida.id, gemela.id)) in vistas:
            continue
        vistas.add(frozenset((corrida.id, gemela.id)))
        if corrida.id in conjuntos_de and gemela.id in conjuntos_de:
            if len(set(conjuntos_de[corrida.id]) | set(conjuntos_de[gemela.id])) > 1:
                a, b = sorted((corrida, gemela), key=lambda c: clave_id(c.id))
                violaciones.append(f"las gemelas {describir(a)} y {describir(b)} están en conjuntos distintos")

    for grupo in getattr(reparto, "grupos", []):
        presentes = {c for m in grupo.corridas for c in conjuntos_de.get(m.id, [])}
        if len(presentes) > 1:
            violaciones.append(f"el grupo {grupo.clave} está partido entre " + " y ".join(_ordenados(presentes)))

    if violaciones:
        raise ErrorFuga(violaciones)
