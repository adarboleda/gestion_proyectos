"""Entrenamiento determinista de la Bi-LSTM con pesos de clase y parada por validación."""
import copy
import random
from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np
import torch
from sklearn.metrics import f1_score
from torch import nn

from clasificador_etapa1.config import FAMILIAS
from clasificador_etapa1.modelo import BiLSTMEtapa1
from clasificador_etapa1.muestras import Muestras

ETIQUETAS = list(range(len(FAMILIAS)))


@dataclass(eq=False)
class ResultadoEntrenamiento:
    modelo: BiLSTMEtapa1
    historial: List[Dict[str, float]]
    mejor_epoca: int
    pesos: np.ndarray
    corridas_entrenamiento: List[str] = field(default_factory=list)


def pesos_clase(y: np.ndarray, clases: int = len(FAMILIAS)) -> np.ndarray:
    """Peso de cada familia inverso a su frecuencia: N / (clases · n_c)."""
    conteos = np.bincount(np.asarray(y, dtype=np.int64), minlength=clases).astype(np.float64)
    return len(y) / (clases * np.maximum(conteos, 1.0))


def fijar_semilla(semilla: int) -> None:
    random.seed(semilla)
    np.random.seed(semilla)
    torch.manual_seed(semilla)
    torch.use_deterministic_algorithms(True)


def predecir(modelo: nn.Module, x: np.ndarray, lote: int = 1024) -> np.ndarray:
    """Probabilidades (n, 3) de cada familia."""
    modelo.eval()
    partes = []
    with torch.no_grad():
        for inicio in range(0, len(x), lote):
            logits = modelo(torch.from_numpy(np.ascontiguousarray(x[inicio:inicio + lote])))
            partes.append(torch.softmax(logits, dim=1).numpy())
    return np.concatenate(partes) if partes else np.empty((0, len(FAMILIAS)), dtype=np.float32)


def f1_macro(y: np.ndarray, probabilidades: np.ndarray) -> float:
    return float(f1_score(y, probabilidades.argmax(axis=1), average="macro", labels=ETIQUETAS, zero_division=0))


def entrenar(train: Muestras, val: Muestras, hiperparametros: Dict, semilla: int) -> ResultadoEntrenamiento:
    """Entrena con entropía cruzada ponderada y se queda con la época de mejor F1 macro en validación."""
    fijar_semilla(semilla)
    modelo = BiLSTMEtapa1(
        entradas=train.x.shape[-1],
        unidades=hiperparametros["unidades"],
        capas=hiperparametros["capas"],
        dropout=hiperparametros["dropout"],
    )
    pesos = pesos_clase(train.y)
    perdida_fn = nn.CrossEntropyLoss(weight=torch.tensor(pesos, dtype=torch.float32))
    optimizador = torch.optim.Adam(modelo.parameters(), lr=hiperparametros["lr"],
                                   weight_decay=hiperparametros["weight_decay"])
    generador = torch.Generator().manual_seed(semilla)
    x = torch.from_numpy(train.x)
    y = torch.from_numpy(train.y)
    lote = hiperparametros["lote"]
    historial: List[Dict[str, float]] = []
    mejor_f1, mejor_epoca, mejor_estado, sin_mejora = -1.0, 0, None, 0
    for epoca in range(1, hiperparametros["epocas"] + 1):
        modelo.train()
        orden = torch.randperm(len(y), generator=generador)
        total = 0.0
        for inicio in range(0, len(y), lote):
            indices = orden[inicio:inicio + lote]
            optimizador.zero_grad()
            perdida = perdida_fn(modelo(x[indices]), y[indices])
            perdida.backward()
            optimizador.step()
            total += perdida.item() * len(indices)
        f1_val = f1_macro(val.y, predecir(modelo, val.x))
        historial.append({"epoca": epoca, "perdida": round(total / len(y), 6), "f1_val": round(f1_val, 6)})
        if f1_val > mejor_f1:
            mejor_f1, mejor_epoca, sin_mejora = f1_val, epoca, 0
            mejor_estado = copy.deepcopy(modelo.state_dict())
        else:
            sin_mejora += 1
            if sin_mejora >= hiperparametros["paciencia"]:
                break
    modelo.load_state_dict(mejor_estado)
    modelo.eval()
    return ResultadoEntrenamiento(modelo, historial, mejor_epoca, pesos, sorted(set(train.corrida)))
