"""Armado de los arreglos de cada conjunto y del contenido de metadata.json."""
import json
from typing import List, Tuple

import numpy as np

from preparacion_pwr3l.config import PASOS, VARIABLES_ENTRADA, VARIABLES_MARGEN
from preparacion_pwr3l.config import CLASES, PASO_SEGUNDOS, PROPORCIONES
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


def construir_metadata(resumen) -> dict:
    """Contenido de metadata.json (contracts/salidas.md)."""
    return {
        "version_formato": 1,
        "planta": "PWR 3L",
        "origen": resumen.origen,
        "semilla": resumen.semilla,
        "proporciones": dict(PROPORCIONES),
        "pasos_por_muestra": PASOS,
        "paso_segundos": PASO_SEGUNDOS,
        "clases": dict(CLASES),
        "variables_entrada": list(VARIABLES_ENTRADA),
        "variables_margen": list(VARIABLES_MARGEN),
        "corridas_encontradas": {clase: dict(v) for clase, v in resumen.corridas_encontradas.items()},
        "conteos_muestras": {clase: dict(v) for clase, v in resumen.conteos_muestras.items()},
        "totales": dict(resumen.totales),
        "corridas": {conjunto: list(ids) for conjunto, ids in resumen.corridas.items()},
        "grupos": {conjunto: {k: list(v) for k, v in g.items()} for conjunto, g in resumen.grupos.items()},
        "excluidas": [dict(e) for e in resumen.excluidas],
        "escalador": {
            "ajustado_con": "train",
            "filas_ajuste": resumen.filas_ajuste,
            "variables_sin_varianza": list(resumen.variables_sin_varianza),
        },
        "advertencias": list(resumen.advertencias),
        "limitaciones": list(resumen.limitaciones),
    }


def serializar_metadata(metadata: dict) -> str:
    return json.dumps(metadata, indent=2, ensure_ascii=False) + "\n"
