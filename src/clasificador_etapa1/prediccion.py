"""Clasificación consultiva de una secuencia nueva con el modelo de Etapa 1 guardado."""
import json
from pathlib import Path
from typing import Dict

import numpy as np
import torch

from clasificador_etapa1.config import AVISO, TAU_MIN_S
from clasificador_etapa1.modelo import BiLSTMEtapa1
from clasificador_etapa1.muestras import ventanas


class Clasificador:
    """Modelo guardado más todo lo necesario para usarlo: familias, escalador, ventana y umbral."""

    def __init__(self, modelo: BiLSTMEtapa1, configuracion: Dict):
        self.modelo = modelo
        self.configuracion = configuracion
        self.familias = configuracion["familias"]
        self.media = np.asarray(configuracion["escalador"]["media"], dtype=np.float64)
        self.escala = np.asarray(configuracion["escalador"]["escala"], dtype=np.float64)
        self.umbral = configuracion["umbral"]

    def clasificar(self, serie) -> Dict:
        """`serie`: (T, 26) sin escalar, filas hasta el instante actual, T ≥ 5.

        Devuelve las probabilidades de cada familia y la recomendada, o «INCIERTO» si ninguna
        alcanza el umbral. Es una recomendación consultiva.
        """
        serie = np.asarray(serie, dtype=np.float64)
        variables = len(self.configuracion["variables"])
        if serie.ndim != 2 or serie.shape[1] != variables:
            raise ValueError(f"Se esperaba una serie de forma (T, {variables}), pero se recibió {serie.shape}.")
        if serie.shape[0] < TAU_MIN_S:
            raise ValueError(f"Se necesitan al menos {TAU_MIN_S} filas (segundos) de datos; hay {serie.shape[0]}.")
        escalada = ((serie - self.media) / self.escala).astype(np.float32)
        x = ventanas(escalada, np.array([len(escalada) - 1]))
        self.modelo.eval()
        with torch.no_grad():
            probabilidades = torch.softmax(self.modelo(torch.from_numpy(x)), dim=1).numpy()[0]
        mejor = int(np.argmax(probabilidades))
        return {
            "probabilidades": {f: float(p) for f, p in zip(self.familias, probabilidades)},
            "recomendacion": self.familias[mejor] if probabilidades[mejor] >= self.umbral else "INCIERTO",
            "aviso": AVISO,
        }


def cargar(ruta) -> Clasificador:
    """Carga `modelo.pt` y `modelo.json` publicados por `entrenar-etapa1`."""
    ruta = Path(ruta)
    configuracion = json.loads((ruta / "modelo.json").read_text(encoding="utf-8"))
    hp = configuracion["hiperparametros"]
    modelo = BiLSTMEtapa1(entradas=len(configuracion["variables"]), unidades=hp["unidades"],
                          capas=hp["capas"], dropout=hp["dropout"], clases=len(configuracion["familias"]))
    modelo.load_state_dict(torch.load(ruta / "modelo.pt", weights_only=True))
    modelo.eval()
    return Clasificador(modelo, configuracion)
