"""Lectura, validación del archivo completo y medición del paso de muestreo de cada corrida PWR 3L."""
import math
from pathlib import Path
from typing import List, Optional, Union

import numpy as np
import pandas as pd

from preparacion_pwr3l.config import PASOS, VARIABLE_TIEMPO, VARIABLES
from preparacion_pwr3l.descubrimiento import Corrida, ErrorDatos, descubrir_corridas

COLUMNAS = [VARIABLE_TIEMPO] + VARIABLES
TOLERANCIA_RELATIVA_PASO = 1e-6


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


def _normalizar_paso(paso: float) -> Union[int, float]:
    entero = round(paso)
    if abs(paso - entero) <= TOLERANCIA_RELATIVA_PASO * max(1.0, abs(paso)):
        return int(entero)
    return float(paso)


def _medir_paso_tiempo(tiempo: np.ndarray, relativo: str) -> Union[int, float]:
    """Comprueba inicio en 0 s y que el paso de muestreo sea positivo y constante en todo el archivo."""
    if len(tiempo) < 2:
        raise ErrorDatos(relativo, "menos de 2 filas para calcular el paso de muestreo", VARIABLE_TIEMPO)
    if tiempo[0] != 0.0:
        inicio = _normalizar_paso(float(tiempo[0]))
        raise ErrorDatos(
            relativo,
            f"el tiempo debe iniciar en 0 s (inicia en {inicio:g} s)",
            VARIABLE_TIEMPO,
        )
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


def leer_corrida(origen, corrida: Corrida) -> Corrida:
    """Valida el archivo completo de `corrida` y fija `filas`, `paso_segundos`, `estado` y `serie`.

    Cualquier defecto en cualquier fila lanza ``ErrorDatos``. Sin defectos, una corrida con menos
    de 300 filas queda como «corta» (sin serie, no se rellena nada, pero con su paso medido); si no,
    la serie son las filas 0 a 299 de las 26 entradas y los 7 márgenes.
    """
    relativo = corrida.archivo
    tabla = _leer_tabla(Path(origen) / relativo, relativo)
    columnas = {v: _convertir_columna(tabla[v].tolist(), relativo, v) for v in COLUMNAS}
    tiempo = columnas[VARIABLE_TIEMPO]
    corrida.paso_segundos = _medir_paso_tiempo(tiempo, relativo)
    corrida.filas = len(tiempo)
    if corrida.filas < PASOS:
        corrida.estado = "corta"
        corrida.serie = None
        return corrida
    corrida.estado = "usable"
    corrida.serie = np.column_stack([columnas[v] for v in VARIABLES])[:PASOS]
    return corrida


def obtener_paso_comun(corridas: List[Corrida]) -> Union[int, float]:
    """Verifica que todas las corridas leídas compartan el mismo paso de muestreo y lo devuelve."""
    referencia: Optional[Corrida] = None
    for corrida in corridas:
        if corrida.paso_segundos is None:
            continue
        if referencia is None:
            referencia = corrida
        elif abs(float(corrida.paso_segundos) - float(referencia.paso_segundos)) > (
            TOLERANCIA_RELATIVA_PASO * float(referencia.paso_segundos)
        ):
            raise ErrorDatos(
                corrida.archivo,
                f"paso de muestreo ({corrida.paso_segundos:g} s) distinto al del resto del dataset "
                f"({referencia.paso_segundos:g} s en {referencia.archivo})",
                VARIABLE_TIEMPO,
            )
    if referencia is None:
        raise ValueError("No hay corridas leídas con paso de muestreo medido.")
    return referencia.paso_segundos


def cargar_corridas(origen) -> List[Corrida]:
    """Descubre todas las corridas, lee las de las cinco clases y verifica que tengan el mismo paso."""
    corridas = descubrir_corridas(origen)
    for corrida in corridas:
        if corrida.estado == "pendiente":
            leer_corrida(origen, corrida)
    obtener_paso_comun(corridas)
    return corridas
