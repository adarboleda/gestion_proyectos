"""Muestras del clasificador: en cada segundo τ, los últimos 30 s hasta τ con su familia."""
import math
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np

from clasificador_etapa1.config import ETIQUETA, FAMILIA_DE_CLASE, HORIZONTE_ENTRENAMIENTO_S, TAU_MIN_S, VENTANA_S
from preparacion_pwr3l.descubrimiento import Corrida


@dataclass(eq=False)
class Muestras:
    x: np.ndarray  # (n, 30, 26) float32
    y: np.ndarray  # (n,) int64
    tau: np.ndarray  # (n,) int64
    k: np.ndarray  # (n,) float64; τ − inicio, nan en NORM
    corrida: np.ndarray  # (n,) ids

    def __len__(self) -> int:
        return len(self.y)


def ventanas(serie: np.ndarray, taus: np.ndarray) -> np.ndarray:
    """Filas [τ − 29, τ] de `serie` para cada τ; las que faltan al inicio repiten la fila 0."""
    relleno = np.vstack([np.repeat(serie[:1], VENTANA_S - 1, axis=0), serie])
    indices = taus[:, None] + np.arange(VENTANA_S)[None, :]  # en `relleno`, la fila τ está en τ + 29
    return relleno[indices]


def inicio_entero(inicio: Optional[float]) -> Optional[int]:
    """El inicio se redondea hacia arriba al segundo entero (τ es entero)."""
    return None if inicio is None else int(math.ceil(inicio))


def construir_muestras(
    corridas: List[Corrida],
    series: Dict[str, np.ndarray],
    inicios: Dict[str, Optional[float]],
    entrenamiento: bool,
) -> Muestras:
    """Una muestra por segundo τ = 5…299 de cada corrida.

    Etiqueta: NORM antes del inicio del evento (o siempre, en corridas NORM) y la familia de la
    corrida desde el inicio. En entrenamiento solo se conservan las corridas NORM completas, el tramo
    previo al evento y los primeros 60 s de cada evento.
    """
    partes_x, partes_y, partes_tau, partes_k, partes_id = [], [], [], [], []
    for corrida in corridas:
        familia = FAMILIA_DE_CLASE[corrida.clase]
        if familia != "NORM" and inicios.get(corrida.id) is None:
            raise ValueError(f"La corrida {corrida.id} ({corrida.clase}) no tiene instante de inicio del evento.")
        serie = np.asarray(series[corrida.id], dtype=np.float32)
        taus = np.arange(TAU_MIN_S, len(serie), dtype=np.int64)
        if familia == "NORM":
            k = np.full(len(taus), np.nan)
            y = np.zeros(len(taus), dtype=np.int64)
        else:
            inicio = inicio_entero(inicios[corrida.id])
            k = (taus - inicio).astype(np.float64)
            y = np.where(taus < inicio, ETIQUETA["NORM"], ETIQUETA[familia]).astype(np.int64)
            if entrenamiento:
                conservar = k <= HORIZONTE_ENTRENAMIENTO_S
                taus, k, y = taus[conservar], k[conservar], y[conservar]
        partes_x.append(ventanas(serie, taus).astype(np.float32))
        partes_y.append(y)
        partes_tau.append(taus)
        partes_k.append(k)
        partes_id.append(np.array([corrida.id] * len(taus), dtype=object))
    if not partes_y:
        return Muestras(
            np.empty((0, VENTANA_S, 0), dtype=np.float32), np.empty(0, dtype=np.int64),
            np.empty(0, dtype=np.int64), np.empty(0), np.empty(0, dtype=object),
        )
    return Muestras(
        np.concatenate(partes_x), np.concatenate(partes_y), np.concatenate(partes_tau),
        np.concatenate(partes_k), np.concatenate(partes_id),
    )
