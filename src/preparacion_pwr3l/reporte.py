"""Resumen de la preparación y reporte impreso (contracts/cli.md)."""
from dataclasses import dataclass, field
from typing import Dict, List

from preparacion_pwr3l.config import (
    CLASE_OOD,
    CLASES,
    CONJUNTOS,
    DESCARTADAS,
    PASOS,
    VARIABLES_ENTRADA,
    VARIABLES_MARGEN,
)
from preparacion_pwr3l.descubrimiento import Corrida

NOMBRES_CONJUNTO = {"train": "entrenamiento", "val": "validación", "test": "prueba"}
ESTADOS = ("usable", "corta", "descartada", "ood")
SECCIONES = (
    "1. Origen y configuración",
    "2. Corridas encontradas",
    "3. Muestras por clase y conjunto",
    "4. Grupos y corridas por conjunto",
    "5. Corridas sin muestra",
    "6. Escalador",
    "7. Advertencias",
    "8. Limitaciones conocidas",
    "9. Artefactos escritos",
)
DETALLE_OOD = "evento fuera de distribución (no es clase de entrenamiento)"

LIMITACIONES = [
    "Pocas corridas por clase (unas 20): validación y prueba tienen solo unas 3 muestras por clase, así que "
    "las métricas posteriores tendrán mucha incertidumbre.",
    "Una etiqueta por muestra: en las corridas de accidente los segundos previos al evento son operación normal "
    "y llevan la etiqueta de la corrida.",
    "LOCA y LOCAC de igual área van juntas: el grupo de 2000 cm² reúne varias corridas y desequilibra el "
    "reparto de esa familia.",
    "Varias corridas NORM repiten el mismo rechazo de carga con otra condición inicial y no se agrupan; "
    "pueden inflar algo las métricas de NORM.",
    "Datos de un único simulador (PCTran) y una única planta (PWR 3L, 2705 MWt), sin ruido de sensores; "
    "no se mezclan con NPPAD ni hay datos de planta real.",
    "Las corridas OOD no se preparan: quedan para probar la detección de novedades en otra funcionalidad.",
]


@dataclass
class Resumen:
    origen: str
    semilla: int
    corridas_encontradas: Dict[str, Dict[str, int]]
    conteos_muestras: Dict[str, Dict[str, int]]
    totales: Dict[str, int]
    corridas: Dict[str, List[str]]  # conjunto -> ids, en el orden de las filas
    grupos: Dict[str, Dict[str, List[str]]]  # conjunto -> clave de grupo -> ids
    excluidas: List[Dict[str, str]]
    filas_ajuste: int
    variables_sin_varianza: List[str]
    advertencias: List[str]
    limitaciones: List[str] = field(default_factory=lambda: list(LIMITACIONES))


def _detalle(corrida: Corrida) -> str:
    if corrida.estado == "descartada":
        return DESCARTADAS.get(corrida.id, "descartada por el equipo")
    if corrida.estado == "ood":
        return DETALLE_OOD
    return f"tiene {corrida.filas} filas; se necesitan {PASOS}"


def generar_advertencias(conteos: Dict[str, Dict[str, int]], corridas: List[Corrida]) -> List[str]:
    advertencias = [
        f"{c.id} ({c.clase}) sin muestra: {c.archivo} tiene {c.filas} filas; se necesitan {PASOS}."
        for c in corridas
        if c.estado == "corta"
    ]
    for clase, por_conjunto in conteos.items():
        if sum(por_conjunto.values()) == 0:
            advertencias.append(f"{clase}: ninguna corrida usable; la clase no tiene muestras.")
            continue
        for conjunto in CONJUNTOS:
            if por_conjunto[conjunto] == 0:
                advertencias.append(f"{clase}: sin muestras de {NOMBRES_CONJUNTO[conjunto]}.")
    return advertencias


def construir_resumen(origen, semilla, corridas, grupos, conjunto_de, particion, escalador) -> Resumen:
    encontradas = {clase: {e: 0 for e in ESTADOS} for clase in list(CLASES) + [CLASE_OOD]}
    for corrida in corridas:
        encontradas[corrida.clase][corrida.estado] += 1
    conteos = {clase: {conjunto: 0 for conjunto in CONJUNTOS} for clase in CLASES}
    for conjunto in CONJUNTOS:
        for corrida in particion[conjunto]:
            conteos[corrida.clase][conjunto] += 1
    por_conjunto = {conjunto: {} for conjunto in CONJUNTOS}
    for grupo in grupos:
        por_conjunto[conjunto_de[grupo.clave]][grupo.clave] = [c.id for c in grupo.corridas]
    excluidas = [
        {"id": c.id, "clase": c.clase, "archivo": c.archivo, "motivo": c.estado, "detalle": _detalle(c)}
        for c in corridas
        if c.estado in ("corta", "descartada", "ood")
    ]
    return Resumen(
        origen=str(origen),
        semilla=semilla,
        corridas_encontradas=encontradas,
        conteos_muestras=conteos,
        totales={conjunto: len(particion[conjunto]) for conjunto in CONJUNTOS},
        corridas={conjunto: [c.id for c in particion[conjunto]] for conjunto in CONJUNTOS},
        grupos=por_conjunto,
        excluidas=excluidas,
        filas_ajuste=escalador.filas_ajuste,
        variables_sin_varianza=list(escalador.variables_sin_varianza),
        advertencias=generar_advertencias(conteos, corridas),
    )


def _titulo(numero: int) -> str:
    return f"\n== {SECCIONES[numero - 1]} =="


def _tabla_encontradas(resumen: Resumen) -> List[str]:
    lineas = [f"{'Clase':<9}" + "".join(f"{e:>12}" for e in ESTADOS) + f"{'Total':>8}"]
    for clase, por_estado in resumen.corridas_encontradas.items():
        lineas.append(f"{clase:<9}" + "".join(f"{por_estado[e]:>12}" for e in ESTADOS) + f"{sum(por_estado.values()):>8}")
    total = sum(sum(v.values()) for v in resumen.corridas_encontradas.values())
    lineas.append(f"Total de corridas encontradas: {total}")
    return lineas


def _tabla_muestras(resumen: Resumen) -> List[str]:
    lineas = [f"{'Clase':<9}" + "".join(f"{c:>8}" for c in CONJUNTOS) + f"{'Total':>8}"]
    for clase, por_conjunto in resumen.conteos_muestras.items():
        celdas = [f"{por_conjunto[c]}{'*' if por_conjunto[c] == 0 else ''}" for c in CONJUNTOS]
        lineas.append(f"{clase:<9}" + "".join(f"{x:>8}" for x in celdas) + f"{sum(por_conjunto.values()):>8}")
    lineas.append(
        f"{'Total':<9}" + "".join(f"{resumen.totales[c]:>8}" for c in CONJUNTOS) + f"{sum(resumen.totales.values()):>8}"
    )
    if any(v == 0 for por in resumen.conteos_muestras.values() for v in por.values()):
        lineas.append("* sin muestras: ver las advertencias.")
    return lineas


def _grupos(resumen: Resumen) -> List[str]:
    lineas = []
    for conjunto in CONJUNTOS:
        grupos = resumen.grupos[conjunto]
        lineas.append(f"{conjunto} ({resumen.totales[conjunto]} corridas, {len(grupos)} grupos)")
        sueltas = []
        for clave, ids in grupos.items():
            if len(ids) == 1 and clave == ids[0]:
                sueltas.append(ids[0])
            else:
                lineas.append(f"  {clave}: {' '.join(ids)}")
        if sueltas:
            lineas.append(f"  sin pareja: {' '.join(sueltas)}")
    return lineas


def formatear_reporte(resumen: Resumen, artefactos: List[str]) -> str:
    lineas = ["REPORTE DE PREPARACIÓN DE DATOS PWR 3L"]
    lineas += [_titulo(1), f"Origen: {resumen.origen}"]
    lineas.append(
        f"Semilla: {resumen.semilla} | Reparto 70/15/15 por grupos de corridas | {PASOS} pasos de 1 s | "
        f"{len(VARIABLES_ENTRADA)} entradas, {len(VARIABLES_MARGEN)} márgenes"
    )
    lineas += [_titulo(2)] + _tabla_encontradas(resumen)
    lineas += [_titulo(3)] + _tabla_muestras(resumen)
    lineas += [_titulo(4)] + _grupos(resumen)
    lineas += [_titulo(5)]
    lineas += [f"- {e['id']} ({e['clase']}, {e['motivo']}): {e['archivo']} — {e['detalle']}" for e in resumen.excluidas]
    lineas += [] if resumen.excluidas else ["Ninguna."]
    lineas += [_titulo(6), f"Ajustado solo con entrenamiento ({resumen.filas_ajuste} filas)."]
    lineas.append(
        "Variables sin varianza: "
        + (", ".join(resumen.variables_sin_varianza) if resumen.variables_sin_varianza else "ninguna")
    )
    lineas += [_titulo(7)] + ([f"- {a}" for a in resumen.advertencias] or ["Ninguna."])
    lineas += [_titulo(8)] + [f"- {limitacion}" for limitacion in resumen.limitaciones]
    lineas += [_titulo(9)] + [f"- {nombre}" for nombre in artefactos]
    return "\n".join(lineas) + "\n"
