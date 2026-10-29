"""Verificación de que la partición NPPAD no tiene fuga de datos (funcionalidad 004)."""
from typing import Dict, List

from preparacion_datos.config import CONJUNTOS
from preparacion_datos.lectura import Simulacion

CLASES_PAREADAS = ("LOCA", "LOCAC")


class ErrorFuga(Exception):
    """Partición con fuga de datos: lista todas las violaciones encontradas."""

    def __init__(self, violaciones: List[str]):
        self.violaciones = list(violaciones)
        detalle = "\n".join(f"- {v}" for v in self.violaciones)
        super().__init__(f"FUGA DE DATOS: {len(self.violaciones)} violación(es)\n{detalle}")


def _ordenados(conjuntos) -> List[str]:
    return sorted(set(conjuntos), key=CONJUNTOS.index)


def verificar_particion(particion: Dict[str, List[Simulacion]]) -> None:
    """Comprueba que cada simulación esté en un solo conjunto y que la LOCA y la LOCAC de igual
    severidad compartan conjunto. Lanza ``ErrorFuga`` con todas las violaciones."""
    conjuntos_de: Dict[str, List[str]] = {}
    simulacion_de: Dict[str, Simulacion] = {}
    for conjunto in CONJUNTOS:
        for simulacion in particion.get(conjunto, []):
            conjuntos_de.setdefault(simulacion.archivo, []).append(conjunto)
            simulacion_de.setdefault(simulacion.archivo, simulacion)
    violaciones: List[str] = []
    for archivo in sorted(conjuntos_de):
        if len(set(conjuntos_de[archivo])) > 1:
            violaciones.append(f"la simulación {archivo} está en " + " y en ".join(_ordenados(conjuntos_de[archivo])))
    por_severidad: Dict[int, List[str]] = {}
    for archivo, simulacion in simulacion_de.items():
        if simulacion.clase in CLASES_PAREADAS and simulacion.severidad is not None:
            por_severidad.setdefault(simulacion.severidad, []).append(archivo)
    for severidad in sorted(por_severidad):
        archivos = sorted(por_severidad[severidad])
        if len({c for a in archivos for c in conjuntos_de[a]}) > 1:
            detalle = ", ".join(f"{a} ({'/'.join(_ordenados(conjuntos_de[a]))})" for a in archivos)
            violaciones.append(f"la severidad {severidad} está partida: {detalle}")
    if violaciones:
        raise ErrorFuga(violaciones)
