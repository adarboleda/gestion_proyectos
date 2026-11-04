"""Etapa 1 segundo a segundo con el modelo guardado por 005, y verificación del modelo (research.md §3).

En cada segundo τ = 5…299 el clasificador ve solo la ventana de 30 s hasta τ (la misma que en
`construir_muestras` de 005); la familia se confirma con la regla sostenida de 005 (≥ 0,80 en τ − 1 y τ).
"""
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np

from clasificador_etapa1.config import FAMILIAS, TAU_MIN_S, UMBRAL
from clasificador_etapa1.evaluacion import confirmadas
from preparacion_pwr3l.config import CONJUNTOS, VARIABLES_ENTRADA
from preparacion_pwr3l.descubrimiento import Corrida


class ErrorModelo(Exception):
    """El modelo guardado no existe o no corresponde al reparto sin fuga actual."""


@dataclass(eq=False)
class LineaTiempo:
    corrida: str
    conjunto: str
    tau: np.ndarray  # (n,) int: 5…299
    probabilidades: np.ndarray  # (n, 3): NORM, LOCA, TRANS
    confirmada: List[str]  # familia confirmada en cada τ, o «» si ninguna


def verificar_modelo(ruta, reparto) -> Dict:
    """Configuración del modelo si sus corridas coinciden, conjunto por conjunto, con el reparto."""
    ruta = Path(ruta)
    if not (ruta / "modelo.json").is_file() or not (ruta / "modelo.pt").is_file():
        raise ErrorModelo(f"ERROR: el modelo de Etapa 1 no existe en {ruta} (ejecute entrenar-etapa1 primero).")
    configuracion = json.loads((ruta / "modelo.json").read_text(encoding="utf-8"))
    guardadas = configuracion.get("corridas", {})
    for conjunto in CONJUNTOS:
        actuales = sorted(c.id for c in reparto.corridas[conjunto])
        if sorted(guardadas.get(conjunto, [])) != actuales:
            raise ErrorModelo(
                f"ERROR: el modelo de {ruta} no corresponde al reparto actual (conjunto {conjunto}); "
                "use la misma semilla y los mismos datos con los que se entrenó."
            )
    return configuracion


def familias_confirmadas(probabilidades: np.ndarray, umbral: float = UMBRAL) -> List[str]:
    """Familia confirmada en cada fila (≥ umbral en esa fila y en la anterior), o «»."""
    conf = confirmadas(np.asarray(probabilidades), umbral)
    return [FAMILIAS[int(np.argmax(fila))] if fila.any() else "" for fila in conf]


def reproducir(clasificador, corridas: List[Corrida], conjunto: str) -> Dict[str, LineaTiempo]:
    """Probabilidades y confirmación de cada τ de cada corrida, solo con datos hasta τ."""
    from clasificador_etapa1.entrenamiento import predecir
    from clasificador_etapa1.muestras import ventanas

    variables = len(VARIABLES_ENTRADA)
    lineas = {}
    for corrida in corridas:
        serie = np.asarray(corrida.serie[:, :variables], dtype=np.float64)
        escalada = ((serie - clasificador.media) / clasificador.escala).astype(np.float32)
        tau = np.arange(TAU_MIN_S, len(escalada), dtype=np.int64)
        probabilidades = predecir(clasificador.modelo, ventanas(escalada, tau))
        lineas[corrida.id] = LineaTiempo(
            corrida.id, conjunto, tau, probabilidades, familias_confirmadas(probabilidades, clasificador.umbral)
        )
    return lineas
