"""Lectura y validación del archivo completo de cada corrida PWR 3L (CSV o libro xlsx)."""
import math
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from preparacion_pwr3l.config import PASOS, VARIABLE_TIEMPO, VARIABLES
from preparacion_pwr3l.descubrimiento import Corrida, ErrorDatos, descubrir_corridas

COLUMNAS = [VARIABLE_TIEMPO] + VARIABLES


def _leer_tabla(ruta: Path, relativo: str) -> pd.DataFrame:
    """Lee todas las filas de las columnas requeridas sin convertir nada en silencio.

    CSV: como texto, para convertir cada valor con ``float()`` (valor exacto del texto).
    `.xls`/`.xlsx`: los `.xls` de PCTran son libros xlsx, así que se fuerza openpyxl; las celdas
    se leen como objetos (números, texto o vacías).
    """
    try:
        if ruta.suffix.lower() == ".csv":
            tabla = pd.read_csv(ruta, dtype=str, keep_default_na=False, na_filter=False)
        else:
            tabla = pd.read_excel(ruta, engine="openpyxl", dtype=object)
    except FileNotFoundError:
        raise ErrorDatos(relativo, "el archivo no existe") from None
    except Exception as error:  # formato roto: pandas y openpyxl lanzan tipos variados
        raise ErrorDatos(relativo, f"archivo ilegible ({error.__class__.__name__})") from None
    tabla.columns = [str(columna).strip() for columna in tabla.columns]
    for variable in COLUMNAS:
        if variable not in tabla.columns:
            raise ErrorDatos(relativo, "falta la variable", variable)
    return tabla


def _convertir_columna(valores, relativo: str, variable: str) -> np.ndarray:
    resultado = np.empty(len(valores), dtype=np.float64)
    for i, valor in enumerate(valores):
        if valor is None:
            raise ErrorDatos(relativo, "valor faltante", variable)
        if isinstance(valor, str):
            if valor.strip() == "":
                raise ErrorDatos(relativo, "valor faltante", variable)
            try:
                numero = float(valor)
            except ValueError:
                raise ErrorDatos(relativo, "valor no numérico", variable) from None
        elif isinstance(valor, (bool, np.bool_)):
            raise ErrorDatos(relativo, "valor no numérico", variable)
        else:
            try:
                numero = float(valor)
            except (TypeError, ValueError):
                raise ErrorDatos(relativo, "valor no numérico", variable) from None
        if math.isnan(numero):
            raise ErrorDatos(relativo, "valor faltante", variable)
        if math.isinf(numero):
            raise ErrorDatos(relativo, "valor no finito", variable)
        resultado[i] = numero
    return resultado


def leer_corrida(origen, corrida: Corrida) -> Corrida:
    """Valida el archivo completo de `corrida` y fija `filas`, `estado` y `serie`.

    Cualquier defecto en cualquier fila lanza ``ErrorDatos``. Sin defectos, una corrida con menos
    de 300 filas queda como «corta» (sin serie, no se rellena nada); si no, la serie son las filas
    0 a 299 de las 26 entradas y los 7 márgenes.
    """
    relativo = corrida.archivo
    tabla = _leer_tabla(Path(origen) / relativo, relativo)
    columnas = {v: _convertir_columna(tabla[v].tolist(), relativo, v) for v in COLUMNAS}
    tiempo = columnas[VARIABLE_TIEMPO]
    distintos = np.flatnonzero(tiempo != np.arange(len(tiempo)))
    if distintos.size:
        raise ErrorDatos(
            relativo, f"el tiempo no avanza de 1 s en 1 s desde 0 (fila de datos {distintos[0] + 1})", VARIABLE_TIEMPO
        )
    corrida.filas = len(tiempo)
    if corrida.filas < PASOS:
        corrida.estado = "corta"
        corrida.serie = None
        return corrida
    corrida.estado = "usable"
    corrida.serie = np.column_stack([columnas[v] for v in VARIABLES])[:PASOS]
    return corrida


def cargar_corridas(origen) -> List[Corrida]:
    """Descubre todas las corridas y lee las de las cinco clases; se detiene en el primer defecto."""
    corridas = descubrir_corridas(origen)
    for corrida in corridas:
        if corrida.estado == "pendiente":
            leer_corrida(origen, corrida)
    return corridas
