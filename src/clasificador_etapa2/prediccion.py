"""Clasificación consultiva en cascada con el modelo guardado de Etapa 2 (009)."""
import json
from pathlib import Path
from typing import Dict

import numpy as np
import torch

from clasificador_etapa1.modelo import BiLSTMEtapa1
from clasificador_etapa1.muestras import ventanas
from clasificador_etapa2.canales import desviacion_pico
from clasificador_etapa2.config import AVISO, FAMILIA_ACTIVADORA, INCIERTO, NO_APLICA


class Clasificador:
    """Modelo de Etapa 2 guardado con sus canales, escalador, clases y umbral."""

    def __init__(self, modelo: BiLSTMEtapa1, configuracion: Dict):
        self.modelo = modelo
        self.configuracion = configuracion
        self.clases = configuracion["clases"]
        self.canales = configuracion["canales"]
        self.media = np.asarray(configuracion["escalador"]["media"], dtype=np.float64)
        self.escala = np.asarray(configuracion["escalador"]["escala"], dtype=np.float64)
        self.umbral = float(configuracion["umbral"])

    def clasificar(self, serie, familia_etapa1: str = FAMILIA_ACTIVADORA) -> Dict:
        """Clasifica una serie (T, 2) de `[PWR, PWNT]` sin escalar desde t = 0.

        Si `familia_etapa1 != "LOCA"`, devuelve `NO_APLICA` sin ejecutar el modelo.
        Si la mayor probabilidad es menor que el umbral (0,80), devuelve `UNCERTAIN`.
        Toda salida incluye el aviso de recomendación consultiva.
        """
        arr = np.asarray(serie, dtype=np.float64)
        esperadas = len(self.canales)
        if arr.ndim != 2 or arr.shape[1] != esperadas or arr.shape[0] < 1:
            raise ValueError(
                f"Se esperaba una serie no vacía de forma (T, {esperadas}), pero se recibió {arr.shape}."
            )
        if familia_etapa1 != FAMILIA_ACTIVADORA:
            return {
                "probabilidades": None,
                "recomendacion": NO_APLICA,
                "aviso": AVISO,
            }
        canales = np.column_stack([desviacion_pico(arr[:, i]) for i in range(esperadas)])
        escalada = ((canales - self.media) / self.escala).astype(np.float32)
        x = ventanas(escalada, np.array([len(escalada) - 1], dtype=np.int64))
        self.modelo.eval()
        with torch.no_grad():
            probabilidades = torch.softmax(self.modelo(torch.from_numpy(x)), dim=1).numpy()[0]
        mejor = int(np.argmax(probabilidades))
        recomendacion = self.clases[mejor] if float(probabilidades[mejor]) >= self.umbral else INCIERTO
        return {
            "probabilidades": {c: float(p) for c, p in zip(self.clases, probabilidades)},
            "recomendacion": recomendacion,
            "aviso": AVISO,
        }


def cargar(ruta) -> Clasificador:
    """Carga `modelo.pt` y `modelo.json` publicados por `entrenar-etapa2`."""
    ruta = Path(ruta)
    configuracion = json.loads((ruta / "modelo.json").read_text(encoding="utf-8"))
    hp = configuracion["hiperparametros"]
    modelo = BiLSTMEtapa1(
        entradas=len(configuracion["canales"]),
        unidades=hp["unidades"],
        capas=hp["capas"],
        dropout=hp["dropout"],
        clases=len(configuracion["clases"]),
    )
    modelo.load_state_dict(torch.load(ruta / "modelo.pt", weights_only=True))
    modelo.eval()
    return Clasificador(modelo, configuracion)

