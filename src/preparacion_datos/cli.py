"""Línea de órdenes: prepara los conjuntos de entrenamiento, validación y prueba de NPPAD."""
import argparse
import sys
from pathlib import Path
from typing import List, Optional

from preparacion_datos.config import (
    CONJUNTOS,
    ORIGEN_POR_DEFECTO,
    REFERENCIA_POR_DEFECTO,
    SALIDA_POR_DEFECTO,
    SEMILLA,
)
from preparacion_datos.escalado import ajustar_escalador, aplicar
from preparacion_datos.lectura import ErrorDatos, cargar_simulaciones
from preparacion_datos.particion import repartir
from preparacion_datos.reporte import comparar_referencia, construir_resumen, contar_muestras, formatear_reporte
from preparacion_datos.salida import construir_conjunto, construir_metadata, publicar, serializar_metadata
from preparacion_datos.verificacion import ErrorFuga, verificar_particion


def _crear_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="preparar-datos",
        description="Prepara los datos de simulación NPPAD sin fuga de información.",
    )
    parser.add_argument("--origen", default=ORIGEN_POR_DEFECTO, help="carpeta Operation_csv_data (solo lectura)")
    parser.add_argument("--salida", default=SALIDA_POR_DEFECTO, help="carpeta donde se publican los artefactos")
    parser.add_argument("--semilla", type=int, default=SEMILLA, help="semilla del reparto por severidad")
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument(
        "--referencia",
        default=REFERENCIA_POR_DEFECTO,
        help="metadata.json del proyecto previo para comparar los conteos de LOCA y LOCAC",
    )
    grupo.add_argument("--sin-referencia", action="store_true", help="omite la comparación con la referencia")
    return parser


def _tolerar_consolas_limitadas() -> None:
    """Evita que un carácter no representable en la consola interrumpa la salida."""
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def main(argv: Optional[List[str]] = None) -> int:
    _tolerar_consolas_limitadas()
    argumentos = _crear_parser().parse_args(argv)
    try:
        simulaciones = cargar_simulaciones(argumentos.origen)
        paso_medido = simulaciones[0].paso_segundos
        particion = repartir(simulaciones, argumentos.semilla)
        verificar_particion(particion)
        crudos = {conjunto: construir_conjunto(particion[conjunto]) for conjunto in CONJUNTOS}
        escalador = ajustar_escalador(crudos["train"][0])
        archivos = {}
        for conjunto in CONJUNTOS:
            x, margenes, y = crudos[conjunto]
            archivos[f"X_{conjunto}.npy"] = aplicar(escalador, x)
            archivos[f"y_{conjunto}.npy"] = y
            archivos[f"margins_{conjunto}.npy"] = margenes
        archivos["scaler_mean.npy"] = escalador.media
        archivos["scaler_std.npy"] = escalador.escala
        ruta_referencia = None if argumentos.sin_referencia else Path(argumentos.referencia)
        referencia = comparar_referencia(ruta_referencia, contar_muestras(particion))
        resumen = construir_resumen(
            argumentos.origen,
            argumentos.semilla,
            particion,
            escalador,
            referencia,
            paso_segundos=paso_medido,
        )
        archivos["metadata.json"] = serializar_metadata(construir_metadata(resumen))
        publicar(argumentos.salida, archivos)
    except (ErrorDatos, ErrorFuga) as error:
        print(error, file=sys.stderr)
        return 1
    except OSError as error:
        print(f"ERROR: no se pudo escribir en {argumentos.salida}: {error}", file=sys.stderr)
        return 1
    print(formatear_reporte(resumen, sorted(archivos)), end="")
    return 2 if referencia["estado"] == "DIFIERE" else 0
