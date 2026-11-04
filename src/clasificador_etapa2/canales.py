"""Canales de desviación pico causal de PWR y PWNT para la Etapa 2 de PWR 3L (009)."""
from pathlib import Path

import numpy as np
import pandas as pd

from clasificador_etapa2.config import MEDIA_MOVIL_S, VENTANA_PICO_S
from preparacion_pwr3l.config import PASOS, VARIABLES
from preparacion_pwr3l.descubrimiento import Corrida, ErrorDatos
from preparacion_pwr3l.lectura import _convertir_columna, _leer_tabla

INDICE_PWNT = VARIABLES.index("PWNT")


def desviacion_pico(x: np.ndarray, ventana: int = VENTANA_PICO_S, media_movil: int = MEDIA_MOVIL_S) -> np.ndarray:
    """Desviación pico causal: max en [τ − (ventana − 1), τ] de la media móvil de 3 s menos x[0]."""
    arr = np.asarray(x, dtype=np.float64)
    if arr.ndim != 1 or len(arr) < 1:
        raise ValueError(f"Se esperaba una serie 1D no vacía, pero se recibió {arr.shape}.")
    suavizada = pd.Series(arr).rolling(media_movil, min_periods=1).mean().to_numpy(dtype=np.float64)
    maximo_ventana = pd.Series(suavizada).rolling(ventana, min_periods=1).max().to_numpy(dtype=np.float64)
    return maximo_ventana - float(arr[0])


def leer_pwr(origen, corrida: Corrida) -> np.ndarray:
    """Lee y valida las primeras 300 filas de la columna `PWR` del archivo de `corrida`."""
    ruta = Path(origen) / corrida.archivo
    tabla = _leer_tabla(ruta, corrida.archivo)
    if "PWR" not in tabla.columns:
        raise ErrorDatos(corrida.archivo, "falta la variable", "PWR")
    columna = _convertir_columna(tabla["PWR"].tolist(), corrida.archivo, "PWR")
    if len(columna) < PASOS:
        raise ErrorDatos(corrida.archivo, f"menos de {PASOS} filas", "PWR")
    return columna[:PASOS]


def canales_corrida(origen, corrida: Corrida) -> np.ndarray:
    """Construye los 2 canales (300, 2) float64 de desviación pico de PWR y PWNT de `corrida`."""
    if corrida.serie is None or len(corrida.serie) < PASOS:
        raise ErrorDatos(corrida.archivo, "la corrida no tiene serie usable")
    pwr = leer_pwr(origen, corrida)
    pwnt = np.asarray(corrida.serie[:PASOS, INDICE_PWNT], dtype=np.float64)
    return np.column_stack([desviacion_pico(pwr), desviacion_pico(pwnt)])

