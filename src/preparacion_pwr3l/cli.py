"""Línea de órdenes: prepara los conjuntos PWR 3L de 300 s y cinco clases."""
import argparse
import sys
from typing import List, Optional

from preparacion_datos.salida import publicar
from preparacion_pwr3l.config import CONJUNTOS, ORIGEN_POR_DEFECTO, SALIDA_POR_DEFECTO, SEMILLA
from preparacion_pwr3l.descubrimiento import ErrorDatos
from preparacion_pwr3l.escalado import ajustar_escalador, aplicar
from preparacion_pwr3l.grupos import formar_grupos
from preparacion_pwr3l.lectura import cargar_corridas
from preparacion_pwr3l.particion import repartir
from preparacion_pwr3l.salida import construir_conjunto
from preparacion_pwr3l.salida import construir_margenes
from preparacion_pwr3l.reporte import construir_resumen, formatear_reporte
from preparacion_pwr3l.salida import construir_metadata, serializar_metadata


def _crear_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="preparar-pwr3l",
        description="Prepara los datos PWR 3L (300 pasos de 1 s, cinco clases) sin fuga de información.",
    )
    parser.add_argument("--origen", default=ORIGEN_POR_DEFECTO, help="carpeta PWR 3L (solo lectura)")
    parser.add_argument("--salida", default=SALIDA_POR_DEFECTO, help="carpeta donde se publican los artefactos")
    parser.add_argument("--semilla", type=int, default=SEMILLA, help="semilla del reparto de grupos")
    return parser


def _tolerar_consolas_limitadas() -> None:
    """Evita que un carácter no representable en la consola interrumpa la salida (research §12)."""
    for flujo in (sys.stdout, sys.stderr):
        try:
            flujo.reconfigure(errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def main(argv: Optional[List[str]] = None) -> int:
    _tolerar_consolas_limitadas()
    argumentos = _crear_parser().parse_args(argv)
    try:
        corridas = cargar_corridas(argumentos.origen)
        usables = [c for c in corridas if c.estado == "usable"]
        if not usables:
            raise ErrorDatos(str(argumentos.origen), "no hay corridas usables")
        grupos = formar_grupos(usables)
        conjunto_de, particion = repartir(grupos, argumentos.semilla)
        crudos = {conjunto: construir_conjunto(particion[conjunto]) for conjunto in CONJUNTOS}
        escalador = ajustar_escalador(crudos["train"][0])
        archivos = {}
        for conjunto in CONJUNTOS:
            x, y = crudos[conjunto]
            archivos[f"X_{conjunto}.npy"] = aplicar(escalador, x)
            archivos[f"y_{conjunto}.npy"] = y
        archivos["scaler_mean.npy"] = escalador.media
        archivos["scaler_std.npy"] = escalador.escala
        for conjunto in CONJUNTOS:
            archivos[f"margins_{conjunto}.npy"] = construir_margenes(particion[conjunto])
        resumen = construir_resumen(
            argumentos.origen, argumentos.semilla, corridas, grupos, conjunto_de, particion, escalador
        )
        archivos["metadata.json"] = serializar_metadata(construir_metadata(resumen))
        publicar(argumentos.salida, archivos)
    except ErrorDatos as error:
        print(error, file=sys.stderr)
        return 1
    except OSError as error:
        print(f"ERROR: no se pudo escribir en {argumentos.salida}: {error}", file=sys.stderr)
        return 1
    print(formatear_reporte(resumen, sorted(archivos)), end="")
    return 0
