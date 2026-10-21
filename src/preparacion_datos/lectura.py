"""Descubrimiento, lectura y validación de las simulaciones de NPPAD (solo lectura)."""
import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd

from preparacion_datos.config import CLASES_POR_CARPETA, CLASES_SIN_SEVERIDAD, PASOS, VARIABLES


class ErrorDatos(Exception):
    """Archivo de origen defectuoso: nombra el archivo y la causa."""

    def __init__(self, archivo: str, causa: str, variable: Optional[str] = None):
        self.archivo = archivo
        self.causa = causa
        self.variable = variable
        mensaje = f"ERROR: {archivo}: {causa}"
        if variable:
            mensaje += f" [variable {variable}]"
        super().__init__(mensaje)


@dataclass(eq=False)
class Simulacion:
    clase: str
    etiqueta: int
    severidad: Optional[int]
    archivo: str  # ruta relativa al origen, p. ej. "LOCA/7.csv"
    serie: Optional[np.ndarray] = None  # (150, 19) float64: 12 de planta + 7 de margen


def _clave_archivo(ruta: Path, relativo: str) -> int:
    if not ruta.stem.isdigit():
        raise ErrorDatos(relativo, "el nombre del archivo no es un número de severidad")
    return int(ruta.stem)


def descubrir_simulaciones(origen) -> List[Simulacion]:
    """Lista las simulaciones de las cuatro clases, sin leer su contenido.

    Orden: por clase (NORM, LOCA, LOCAC, ATWS) y luego por severidad numérica.
    """
    origen = Path(origen)
    if not origen.is_dir():
        raise ErrorDatos(str(origen), "no existe la carpeta de origen")
    simulaciones: List[Simulacion] = []
    for carpeta, (clase, etiqueta) in CLASES_POR_CARPETA.items():
        directorio = origen / carpeta
        if not directorio.is_dir():
            raise ErrorDatos(carpeta, "no existe la carpeta de clase")
        if clase in CLASES_SIN_SEVERIDAD:
            archivos = sorted(directorio.glob("*.csv"), key=lambda r: r.name)
        else:
            archivos = sorted(
                directorio.glob("*.csv"), key=lambda r: _clave_archivo(r, f"{carpeta}/{r.name}")
            )
        if not archivos:
            raise ErrorDatos(carpeta, "la carpeta de clase no contiene simulaciones (.csv)")
        for ruta in archivos:
            severidad = None if clase in CLASES_SIN_SEVERIDAD else int(ruta.stem)
            simulaciones.append(Simulacion(clase, etiqueta, severidad, f"{carpeta}/{ruta.name}"))
    return simulaciones


def _convertir_columna(valores, relativo: str, variable: str) -> np.ndarray:
    resultado = np.empty(len(valores), dtype=np.float64)
    for i, texto in enumerate(valores):
        if texto.strip() == "":
            raise ErrorDatos(relativo, "valor faltante", variable)
        try:
            numero = float(texto)
        except ValueError:
            raise ErrorDatos(relativo, "valor no numérico", variable) from None
        if math.isnan(numero):
            raise ErrorDatos(relativo, "valor faltante", variable)
        if math.isinf(numero):
            raise ErrorDatos(relativo, "valor no finito", variable)
        resultado[i] = numero
    return resultado


def leer_simulacion(origen, carpeta: str, nombre: str) -> Simulacion:
    """Lee los primeros 150 pasos de las 19 variables requeridas de un archivo.

    Los valores se convierten con ``float()`` de Python (conversión exacta del texto). Cualquier
    defecto en esas filas lanza ``ErrorDatos``; el resto del archivo no se valida porque no se usa.
    """
    origen = Path(origen)
    relativo = f"{carpeta}/{nombre}"
    ruta = origen / carpeta / nombre
    clase, etiqueta = CLASES_POR_CARPETA[carpeta]
    try:
        cabecera = pd.read_csv(ruta, nrows=0).columns
        for variable in VARIABLES:
            if variable not in cabecera:
                raise ErrorDatos(relativo, "falta la variable", variable)
        datos = pd.read_csv(
            ruta, usecols=VARIABLES, nrows=PASOS, dtype=str, keep_default_na=False, na_filter=False
        )
    except FileNotFoundError:
        raise ErrorDatos(relativo, "el archivo no existe") from None
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as error:
        raise ErrorDatos(relativo, f"archivo ilegible ({error.__class__.__name__})") from None
    if len(datos) < PASOS:
        raise ErrorDatos(relativo, f"menos de {PASOS} pasos (tiene {len(datos)})")
    serie = np.column_stack(
        [_convertir_columna(datos[variable].tolist(), relativo, variable) for variable in VARIABLES]
    )
    severidad = None if clase in CLASES_SIN_SEVERIDAD else int(Path(nombre).stem)
    return Simulacion(clase, etiqueta, severidad, relativo, serie)


def cargar_simulaciones(origen) -> List[Simulacion]:
    """Lee y valida todas las simulaciones; se detiene en el primer archivo defectuoso."""
    return [
        leer_simulacion(origen, *Path(s.archivo).parts) for s in descubrir_simulaciones(origen)
    ]
