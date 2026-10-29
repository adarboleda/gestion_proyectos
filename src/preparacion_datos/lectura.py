"""Descubrimiento, lectura y validación de las simulaciones de NPPAD (solo lectura)."""
import math
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

import numpy as np
import pandas as pd

from preparacion_datos.config import (
    CLASES_POR_CARPETA,
    CLASES_SIN_SEVERIDAD,
    PASOS,
    VARIABLE_TIEMPO,
    VARIABLES,
)

COLUMNAS = [VARIABLE_TIEMPO] + VARIABLES
TOLERANCIA_RELATIVA_PASO = 1e-6


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
    paso_segundos: Optional[Union[int, float]] = None


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


def _normalizar_paso(paso: float) -> Union[int, float]:
    entero = round(paso)
    if abs(paso - entero) <= TOLERANCIA_RELATIVA_PASO * max(1.0, abs(paso)):
        return int(entero)
    return float(paso)


def _medir_paso_tiempo(tiempo: np.ndarray, relativo: str) -> Union[int, float]:
    """Calcula y verifica que el paso de muestreo sea positivo y constante en todo el archivo."""
    if len(tiempo) < 2:
        raise ErrorDatos(relativo, "menos de 2 filas para calcular el paso de muestreo", VARIABLE_TIEMPO)
    diferencias = np.diff(tiempo)
    no_avanza = np.flatnonzero(diferencias <= 0)
    if no_avanza.size:
        i = int(no_avanza[0])
        paso_malo = _normalizar_paso(float(diferencias[i]))
        raise ErrorDatos(
            relativo,
            f"el tiempo no avanza en la fila de datos {i + 2} (paso {paso_malo:g} s)",
            VARIABLE_TIEMPO,
        )
    paso_base = float(diferencias[0])
    desviados = np.flatnonzero(np.abs(diferencias - paso_base) > TOLERANCIA_RELATIVA_PASO * paso_base)
    if desviados.size:
        i = int(desviados[0])
        esperado = _normalizar_paso(paso_base)
        encontrado = _normalizar_paso(float(diferencias[i]))
        raise ErrorDatos(
            relativo,
            f"paso de muestreo no constante en la fila de datos {i + 2} "
            f"(esperado {esperado:g} s, encontrado {encontrado:g} s)",
            VARIABLE_TIEMPO,
        )
    return _normalizar_paso(paso_base)


def leer_simulacion(origen, carpeta: str, nombre: str) -> Simulacion:
    """Valida el archivo completo, mide el paso desde TIME y devuelve los primeros 150 pasos.

    Los valores se convierten con ``float()`` de Python (conversión exacta del texto). Cualquier
    defecto en cualquier fila del archivo (variable ausente, valor no numérico, faltante o no
    finito, paso de muestreo no constante o menos de 150 pasos) lanza ``ErrorDatos``; solo los
    primeros 150 pasos entran en la muestra.
    """
    origen = Path(origen)
    relativo = f"{carpeta}/{nombre}"
    ruta = origen / carpeta / nombre
    clase, etiqueta = CLASES_POR_CARPETA[carpeta]
    try:
        cabecera = pd.read_csv(ruta, nrows=0).columns
        for variable in COLUMNAS:
            if variable not in cabecera:
                raise ErrorDatos(relativo, "falta la variable", variable)
        datos = pd.read_csv(ruta, usecols=COLUMNAS, dtype=str, keep_default_na=False, na_filter=False)
    except FileNotFoundError:
        raise ErrorDatos(relativo, "el archivo no existe") from None
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as error:
        raise ErrorDatos(relativo, f"archivo ilegible ({error.__class__.__name__})") from None
    tiempo = _convertir_columna(datos[VARIABLE_TIEMPO].tolist(), relativo, VARIABLE_TIEMPO)
    columnas = {
        variable: _convertir_columna(datos[variable].tolist(), relativo, variable)
        for variable in VARIABLES
    }
    paso = _medir_paso_tiempo(tiempo, relativo)
    if len(datos) < PASOS:
        raise ErrorDatos(relativo, f"menos de {PASOS} pasos (tiene {len(datos)})")
    serie = np.column_stack([columnas[variable] for variable in VARIABLES])[:PASOS]
    severidad = None if clase in CLASES_SIN_SEVERIDAD else int(Path(nombre).stem)
    return Simulacion(clase, etiqueta, severidad, relativo, serie, paso)


def cargar_simulaciones(origen) -> List[Simulacion]:
    """Lee y valida todas las simulaciones y verifica que compartan el mismo paso de muestreo."""
    simulaciones: List[Simulacion] = []
    referencia: Optional[Simulacion] = None
    for descubierta in descubrir_simulaciones(origen):
        leida = leer_simulacion(origen, *Path(descubierta.archivo).parts)
        if referencia is None:
            referencia = leida
        elif abs(float(leida.paso_segundos) - float(referencia.paso_segundos)) > (
            TOLERANCIA_RELATIVA_PASO * float(referencia.paso_segundos)
        ):
            raise ErrorDatos(
                leida.archivo,
                f"paso de muestreo ({leida.paso_segundos:g} s) distinto al del resto del dataset "
                f"({referencia.paso_segundos:g} s en {referencia.archivo})",
                VARIABLE_TIEMPO,
            )
        simulaciones.append(leida)
    return simulaciones
