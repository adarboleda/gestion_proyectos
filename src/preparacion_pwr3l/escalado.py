"""Escalado de las 26 variables de entrada de PWR 3L, ajustado solo con entrenamiento."""
from dataclasses import dataclass
from typing import List

import numpy as np
from sklearn.preprocessing import StandardScaler

from preparacion_pwr3l.config import PASOS, VARIABLES_ENTRADA


@dataclass(eq=False)
class Escalador:
    scaler: StandardScaler
    media: np.ndarray  # (26,) float64
    escala: np.ndarray  # (26,) float64; vale 1.0 para una variable sin varianza
    variables_sin_varianza: List[str]
    filas_ajuste: int


def _validar_forma(x: np.ndarray, exigir_no_vacio: bool) -> None:
    esperada = (PASOS, len(VARIABLES_ENTRADA))
    if not isinstance(x, np.ndarray) or x.ndim != 3 or x.shape[1:] != esperada:
        raise ValueError(
            f"Se esperaba un arreglo 3D de forma (N, {esperada[0]}, {esperada[1]}), "
            f"pero se recibió {getattr(x, 'shape', type(x))}."
        )
    if exigir_no_vacio and x.shape[0] < 1:
        raise ValueError("El conjunto de entrenamiento está vacío: se necesita al menos una muestra.")


def ajustar_escalador(x_train: np.ndarray) -> Escalador:
    """Ajusta un StandardScaler con las filas de entrenamiento aplanadas (N·300, 26)."""
    _validar_forma(x_train, exigir_no_vacio=True)
    filas = x_train.reshape(-1, x_train.shape[-1]).astype(np.float64, copy=False)
    scaler = StandardScaler().fit(filas)
    sin_varianza = [
        VARIABLES_ENTRADA[i] for i in np.flatnonzero(np.ptp(filas, axis=0) == 0)
    ]
    return Escalador(
        scaler=scaler,
        media=np.asarray(scaler.mean_, dtype=np.float64),
        escala=np.asarray(scaler.scale_, dtype=np.float64),
        variables_sin_varianza=sin_varianza,
        filas_ajuste=filas.shape[0],
    )


def aplicar(escalador: Escalador, x: np.ndarray) -> np.ndarray:
    """Escala `x` (N, 300, 26) con los parámetros de entrenamiento, sin reajustar; devuelve float32."""
    _validar_forma(x, exigir_no_vacio=False)
    forma = x.shape
    if forma[0] == 0:
        return np.empty(forma, dtype=np.float32)
    filas = x.reshape(-1, forma[-1]).astype(np.float64)
    return escalador.scaler.transform(filas).reshape(forma).astype(np.float32)
