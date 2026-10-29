"""Reporte de la preparación: conteos, advertencias, limitaciones y comparación con la referencia."""
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union

from preparacion_datos.config import CLASES, CLASES_POR_CARPETA, CONJUNTOS, PASOS

NOMBRES_CONJUNTO = {"train": "entrenamiento", "val": "validación", "test": "prueba"}
CLASES_COMPARADAS = ("LOCA", "LOCAC")  # Normal y ATWS no son comparables con la referencia

LIMITACIONES = [
    "Normal y ATWS provienen de una sola simulación cada una y no tienen muestras de validación ni de "
    "prueba: no habrá métricas sobre datos no vistos para esas clases.",
    "Hay una muestra por simulación (primeros 150 pasos): las clases quedan muy desbalanceadas "
    "(1 / unas 100 / unas 100 / 1).",
    "Los datos provienen de un único simulador (PCTRAN) y de una única configuración de planta; "
    "no hay datos de planta real.",
]


@dataclass
class Resumen:
    origen: str
    semilla: int
    paso_segundos: Union[int, float]
    duracion_muestra_segundos: Union[int, float]
    conteos_archivos: Dict[str, int]
    conteos_muestras: Dict[str, Dict[str, int]]
    totales: Dict[str, int]
    simulaciones: Dict[str, List[str]]  # conjunto -> archivos, en el orden de las filas
    filas_ajuste: int
    variables_sin_varianza: List[str]
    advertencias: List[str]
    limitaciones: List[str] = field(default_factory=lambda: list(LIMITACIONES))
    referencia: Dict[str, object] = field(default_factory=dict)


def contar_muestras(particion) -> Dict[str, Dict[str, int]]:
    """Muestras por clase y conjunto; todas las clases aparecen, incluso con cero."""
    conteos = {clase: {conjunto: 0 for conjunto in CONJUNTOS} for clase in CLASES}
    for conjunto in CONJUNTOS:
        for simulacion in particion[conjunto]:
            conteos[simulacion.clase][conjunto] += 1
    return conteos


def generar_advertencias(conteos: Dict[str, Dict[str, int]]) -> List[str]:
    advertencias = []
    for clase, por_conjunto in conteos.items():
        total = sum(por_conjunto.values())
        if total == 1:
            advertencias.append(
                f"{clase} tiene una sola simulación: asignada completa a entrenamiento; "
                "no tiene muestras de validación ni de prueba."
            )
    for clase, por_conjunto in conteos.items():
        if sum(por_conjunto.values()) == 1:
            continue
        for conjunto in CONJUNTOS:
            if por_conjunto[conjunto] == 0:
                advertencias.append(f"{clase}: sin muestras de {NOMBRES_CONJUNTO[conjunto]}.")
    return advertencias


def comparar_referencia(ruta: Optional[Path], conteos: Dict[str, Dict[str, int]]) -> Dict[str, object]:
    """Compara solo los conteos de LOCA y LOCAC con `sample_counts` de la referencia."""
    if ruta is None:
        return {"archivo": None, "estado": "OMITIDA", "diferencias": []}
    ruta = Path(ruta)
    resultado = {"archivo": str(ruta), "estado": "NO DISPONIBLE", "diferencias": []}
    try:
        referencia = json.loads(ruta.read_text(encoding="utf-8"))["sample_counts"]
        diferencias = []
        for clase in CLASES_COMPARADAS:
            for conjunto in CONJUNTOS:
                esperado = int(referencia[clase][conjunto])
                if esperado != conteos[clase][conjunto]:
                    diferencias.append(
                        {
                            "clase": clase,
                            "conjunto": conjunto,
                            "obtenido": conteos[clase][conjunto],
                            "referencia": esperado,
                        }
                    )
    except (OSError, ValueError, KeyError, TypeError):
        return resultado
    resultado["estado"] = "DIFIERE" if diferencias else "COINCIDE"
    resultado["diferencias"] = diferencias
    return resultado


def _obtener_paso_particion(particion) -> Union[int, float]:
    for conjunto in CONJUNTOS:
        for simulacion in particion[conjunto]:
            if simulacion.paso_segundos is not None:
                return simulacion.paso_segundos
    raise ValueError("No se encontró paso_segundos medido en las simulaciones de la partición.")


def construir_resumen(
    origen,
    semilla,
    particion,
    escalador,
    referencia: Optional[dict],
    paso_segundos: Optional[Union[int, float]] = None,
) -> Resumen:
    conteos = contar_muestras(particion)
    paso = paso_segundos if paso_segundos is not None else _obtener_paso_particion(particion)
    duracion = PASOS * paso
    if isinstance(duracion, float) and duracion.is_integer():
        duracion = int(duracion)
    return Resumen(
        origen=str(origen),
        semilla=semilla,
        paso_segundos=paso,
        duracion_muestra_segundos=duracion,
        conteos_archivos={clase: sum(por_conjunto.values()) for clase, por_conjunto in conteos.items()},
        conteos_muestras=conteos,
        totales={conjunto: len(particion[conjunto]) for conjunto in CONJUNTOS},
        simulaciones={conjunto: [s.archivo for s in particion[conjunto]] for conjunto in CONJUNTOS},
        filas_ajuste=escalador.filas_ajuste,
        variables_sin_varianza=list(escalador.variables_sin_varianza),
        advertencias=generar_advertencias(conteos),
        referencia=referencia
        if referencia is not None
        else {"archivo": None, "estado": "OMITIDA", "diferencias": []},
    )


def _titulo(texto: str) -> str:
    return f"\n== {texto} =="


def _tabla(resumen: Resumen) -> List[str]:
    lineas = [f"{'Clase':<8}{'train':>8}{'val':>8}{'test':>8}{'Total':>8}"]
    for clase, por_conjunto in resumen.conteos_muestras.items():
        celdas = [f"{por_conjunto[c]}{'*' if por_conjunto[c] == 0 else ''}" for c in CONJUNTOS]
        lineas.append(f"{clase:<8}" + "".join(f"{celda:>8}" for celda in celdas) + f"{sum(por_conjunto.values()):>8}")
    totales = [str(resumen.totales[c]) for c in CONJUNTOS]
    lineas.append(f"{'Total':<8}" + "".join(f"{t:>8}" for t in totales) + f"{sum(resumen.totales.values()):>8}")
    if any(v == 0 for por_conjunto in resumen.conteos_muestras.values() for v in por_conjunto.values()):
        lineas.append("* sin muestras: ver las advertencias.")
    return lineas


def _numeros_por_clase(archivos: List[str]) -> Dict[str, List[str]]:
    clase_de = {carpeta: clase for carpeta, (clase, _) in CLASES_POR_CARPETA.items()}
    agrupado: Dict[str, List[str]] = {}
    for archivo in archivos:
        carpeta, nombre = archivo.split("/")
        agrupado.setdefault(clase_de[carpeta], []).append(Path(nombre).stem)
    return agrupado


def formatear_reporte(resumen: Resumen, artefactos: List[str]) -> str:
    lineas = ["REPORTE DE PREPARACIÓN DE DATOS NPPAD"]
    lineas += [_titulo("1. Origen y configuración")]
    lineas += [
        f"Origen: {resumen.origen}",
        f"Semilla: {resumen.semilla} | Reparto 70/15/15 por simulación completa | "
        f"{PASOS} pasos por muestra (paso medido de TIME: {resumen.paso_segundos:g} s, "
        f"duración: {resumen.duracion_muestra_segundos:g} s)",
    ]
    lineas += [_titulo("2. Muestras por clase y conjunto")] + _tabla(resumen)
    lineas += [_titulo("3. Simulaciones por conjunto")]
    for conjunto in CONJUNTOS:
        lineas.append(f"{conjunto} ({len(resumen.simulaciones[conjunto])})")
        for clase, numeros in _numeros_por_clase(resumen.simulaciones[conjunto]).items():
            lineas.append(f"  {clase}: {' '.join(numeros)}")
    lineas += [_titulo("4. Escalador")]
    lineas.append(f"Ajustado solo con entrenamiento ({resumen.filas_ajuste} filas).")
    lineas.append(
        "Variables sin varianza: "
        + (", ".join(resumen.variables_sin_varianza) if resumen.variables_sin_varianza else "ninguna")
    )
    lineas += [_titulo("5. Advertencias")]
    lineas += [f"- {a}" for a in resumen.advertencias] or ["Ninguna."]
    lineas += [_titulo("6. Limitaciones conocidas")]
    lineas += [f"- {limitacion}" for limitacion in resumen.limitaciones]
    lineas += [_titulo("7. Comparación con la referencia")]
    lineas.append(f"Estado: {resumen.referencia['estado']} (solo LOCA y LOCAC)")
    if resumen.referencia.get("archivo"):
        lineas.append(f"Archivo: {resumen.referencia['archivo']}")
    for d in resumen.referencia.get("diferencias", []):
        lineas.append(f"  {d['clase']}/{d['conjunto']}: obtenido {d['obtenido']}, referencia {d['referencia']}")
    lineas += [_titulo("8. Artefactos escritos")]
    lineas += [f"- {nombre}" for nombre in artefactos]
    return "\n".join(lineas) + "\n"
