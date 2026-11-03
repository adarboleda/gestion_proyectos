"""Armado de los arreglos de cada conjunto y del contenido de metadata.json."""
from typing import List, Tuple

import numpy as np

from preparacion_pwr3l.config import PASOS, VARIABLES_ENTRADA, VARIABLES_MARGEN
from preparacion_pwr3l.descubrimiento import Corrida

N_ENTRADAS = len(VARIABLES_ENTRADA)


def construir_conjunto(corridas: List[Corrida]) -> Tuple[np.ndarray, np.ndarray]:
    """Entradas sin escalar (N, 300, 26) float64 y etiquetas (N,) int64, en el orden recibido."""
    x = np.empty((len(corridas), PASOS, N_ENTRADAS), dtype=np.float64)
    y = np.empty(len(corridas), dtype=np.int64)
    for i, corrida in enumerate(corridas):
        x[i] = corrida.serie[:, :N_ENTRADAS]
        y[i] = corrida.etiqueta
    return x, y


def construir_margenes(corridas: List[Corrida]) -> np.ndarray:
    """Márgenes térmicos (N, 300, 7) float64 en sus unidades originales, sin ninguna transformación."""
    margenes = np.empty((len(corridas), PASOS, len(VARIABLES_MARGEN)), dtype=np.float64)
    for i, corrida in enumerate(corridas):
        margenes[i] = corrida.serie[:, N_ENTRADAS:]
    return margenes
