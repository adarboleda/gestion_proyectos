"""Muestras de evento para el clasificador de Etapa 2 (rama caliente o fría) de PWR 3L (009)."""
from typing import Dict, List, Optional

import numpy as np

from clasificador_etapa1.muestras import Muestras, inicio_entero, ventanas
from clasificador_etapa2.config import (
    CANALES,
    CLASES,
    ETIQUETA,
    HORIZONTE_ENTRENAMIENTO_S,
    VENTANA_S,
)
from preparacion_pwr3l.descubrimiento import Corrida


def es_rama(corrida: Corrida) -> bool:
    """Devuelve True si `corrida` es usable y pertenece a LOCA (caliente) o LOCAC (fría)."""
    return corrida.estado == "usable" and corrida.clase in CLASES


def construir_muestras(
    corridas: List[Corrida],
    series: Dict[str, np.ndarray],
    inicios: Dict[str, Optional[float]],
    entrenamiento: bool,
) -> Muestras:
    """Forma una muestra por cada segundo τ ≥ ceil(inicio) de cada corrida LOCA/LOCAC.

    En cada segundo τ, la ventana contiene los últimos 30 s de los 2 canales hasta τ (rellenados
    con la fila 0 al comenzar). En entrenamiento se conservan los primeros 60 s del evento
    (0 ≤ k ≤ 60); en validación y evaluación se conservan todos los instantes del evento (k ≥ 0).
    """
    partes_x, partes_y, partes_tau, partes_k, partes_id = [], [], [], [], []
    for corrida in corridas:
        if not es_rama(corrida):
            continue
        inicio_raw = inicios.get(corrida.id)
        if inicio_raw is None:
            raise ValueError(f"La corrida {corrida.id} ({corrida.clase}) no tiene instante de inicio del evento.")
        inicio = inicio_entero(inicio_raw)
        serie = np.asarray(series[corrida.id], dtype=np.float32)
        if serie.ndim != 2 or serie.shape[1] != len(CANALES):
            raise ValueError(
                f"La corrida {corrida.id} tiene canales de forma {serie.shape}; se esperaba (T, {len(CANALES)})."
            )
        taus = np.arange(max(0, inicio), len(serie), dtype=np.int64)
        k = (taus - inicio).astype(np.float64)
        if entrenamiento:
            conservar = k <= HORIZONTE_ENTRENAMIENTO_S
            taus, k = taus[conservar], k[conservar]
        if len(taus) == 0:
            continue
        y = np.full(len(taus), ETIQUETA[corrida.clase], dtype=np.int64)
        partes_x.append(ventanas(serie, taus).astype(np.float32))
        partes_y.append(y)
        partes_tau.append(taus)
        partes_k.append(k)
        partes_id.append(np.array([corrida.id] * len(taus), dtype=object))
    if not partes_y:
        return Muestras(
            np.empty((0, VENTANA_S, len(CANALES)), dtype=np.float32),
            np.empty(0, dtype=np.int64),
            np.empty(0, dtype=np.int64),
            np.empty(0, dtype=np.float64),
            np.empty(0, dtype=object),
        )
    return Muestras(
        np.concatenate(partes_x),
        np.concatenate(partes_y),
        np.concatenate(partes_tau),
        np.concatenate(partes_k),
        np.concatenate(partes_id),
    )

