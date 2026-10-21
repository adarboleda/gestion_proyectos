"""Escalado de las variables de planta, ajustado solo con entrenamiento."""
from dataclasses import dataclass
from typing import List

import numpy as np
from sklearn.preprocessing import StandardScaler

from preparacion_datos.config import VARIABLES_PLANTA


@dataclass(eq=False)
class Escalador:
    scaler: StandardScaler
    media: np.ndarray  # (12,) float64
    escala: np.ndarray  # (12,) float64; vale 1.0 para una variable sin varianza
    variables_sin_varianza: List[str]
    filas_ajuste: int


def ajustar_escalador(x_train: np.ndarray) -> Escalador:
    """Ajusta un StandardScaler con las filas de entrenamiento aplanadas (N·150, 12)."""
    filas = x_train.reshape(-1, x_train.shape[-1]).astype(np.float64, copy=False)
    scaler = StandardScaler().fit(filas)
    sin_varianza = [
        VARIABLES_PLANTA[i] for i in np.flatnonzero(np.ptp(filas, axis=0) == 0)
    ]
    return Escalador(
        scaler=scaler,
        media=np.asarray(scaler.mean_, dtype=np.float64),
        escala=np.asarray(scaler.scale_, dtype=np.float64),
        variables_sin_varianza=sin_varianza,
        filas_ajuste=filas.shape[0],
    )


def aplicar(escalador: Escalador, x: np.ndarray) -> np.ndarray:
    """Escala `x` (N, 150, 12) con los parámetros de entrenamiento, sin reajustar; devuelve float32."""
    forma = x.shape
    filas = x.reshape(-1, forma[-1]).astype(np.float64)
    return escalador.scaler.transform(filas).reshape(forma).astype(np.float32)
