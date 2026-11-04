"""Escalado de los 2 canales y entrenamiento determinista de la Bi-LSTM de Etapa 2 (009)."""
import copy
from dataclasses import dataclass, field
from typing import Dict, List

import numpy as np
import torch
from sklearn.metrics import f1_score
from sklearn.preprocessing import StandardScaler
from torch import nn

from clasificador_etapa1.entrenamiento import fijar_semilla
from clasificador_etapa1.modelo import BiLSTMEtapa1
from clasificador_etapa1.muestras import Muestras
from clasificador_etapa2.config import CANALES, CLASES
from preparacion_pwr3l.config import PASOS

ETIQUETAS = list(range(len(CLASES)))


@dataclass(eq=False)
class EscaladorCanales:
    scaler: StandardScaler
    media: np.ndarray  # (2,) float64
    escala: np.ndarray  # (2,) float64
    canales_sin_varianza: List[str]
    filas_ajuste: int


@dataclass(eq=False)
class ResultadoEntrenamiento:
    modelo: BiLSTMEtapa1
    historial: List[Dict[str, float]]
    mejor_epoca: int
    pesos: np.ndarray
    corridas_entrenamiento: List[str] = field(default_factory=list)


def _validar_forma_canales(x: np.ndarray, exigir_no_vacio: bool) -> None:
    esperada = (PASOS, len(CANALES))
    if not isinstance(x, np.ndarray) or x.ndim != 3 or x.shape[1:] != esperada:
        raise ValueError(
            f"Se esperaba un arreglo 3D de forma (N, {esperada[0]}, {esperada[1]}), "
            f"pero se recibió {getattr(x, 'shape', type(x))}."
        )
    if exigir_no_vacio and x.shape[0] < 1:
        raise ValueError("El conjunto de entrenamiento está vacío: se necesita al menos una corrida.")


def ajustar_escalador_canales(x_train: np.ndarray) -> EscaladorCanales:
    """Ajusta un StandardScaler sobre las filas (N·300, 2) de los canales de entrenamiento."""
    _validar_forma_canales(x_train, exigir_no_vacio=True)
    filas = x_train.reshape(-1, x_train.shape[-1]).astype(np.float64, copy=False)
    scaler = StandardScaler().fit(filas)
    sin_varianza = [CANALES[i] for i in np.flatnonzero(np.ptp(filas, axis=0) == 0)]
    return EscaladorCanales(
        scaler=scaler,
        media=np.asarray(scaler.mean_, dtype=np.float64),
        escala=np.asarray(scaler.scale_, dtype=np.float64),
        canales_sin_varianza=sin_varianza,
        filas_ajuste=int(filas.shape[0]),
    )


def escalar_canales(escalador: EscaladorCanales, x: np.ndarray) -> np.ndarray:
    """Escala `x` (N, 300, 2) con el escalador de entrenamiento, sin reajustar; devuelve float32."""
    _validar_forma_canales(x, exigir_no_vacio=False)
    forma = x.shape
    if forma[0] == 0:
        return np.empty(forma, dtype=np.float32)
    filas = x.reshape(-1, forma[-1]).astype(np.float64)
    return escalador.scaler.transform(filas).reshape(forma).astype(np.float32)


def pesos_clase(y: np.ndarray, clases: int = len(CLASES)) -> np.ndarray:
    """Peso de cada rama inverso a su frecuencia: N / (2 · n_c)."""
    conteos = np.bincount(np.asarray(y, dtype=np.int64), minlength=clases).astype(np.float64)
    return len(y) / (clases * np.maximum(conteos, 1.0))


def predecir(modelo: nn.Module, x: np.ndarray, lote: int = 1024) -> np.ndarray:
    """Probabilidades (n, 2) de LOCA y LOCAC."""
    modelo.eval()
    partes = []
    with torch.no_grad():
        for inicio in range(0, len(x), lote):
            logits = modelo(torch.from_numpy(np.ascontiguousarray(x[inicio:inicio + lote])))
            partes.append(torch.softmax(logits, dim=1).numpy())
    return np.concatenate(partes) if partes else np.empty((0, len(CLASES)), dtype=np.float32)


def f1_macro(y: np.ndarray, probabilidades: np.ndarray) -> float:
    if len(y) == 0:
        return 0.0
    return float(f1_score(y, probabilidades.argmax(axis=1), average="macro", labels=ETIQUETAS, zero_division=0))


def entrenar(train: Muestras, val: Muestras, hiperparametros: Dict, semilla: int) -> ResultadoEntrenamiento:
    """Entrena la Bi-LSTM con entropía cruzada ponderada y parada por F1 macro en validación."""
    conteos = np.bincount(np.asarray(train.y, dtype=np.int64), minlength=len(CLASES))
    for indice, nombre in enumerate(CLASES):
        if conteos[indice] == 0:
            raise ValueError(f"El conjunto de entrenamiento no tiene muestras de la rama {nombre}.")

    fijar_semilla(semilla)
    modelo = BiLSTMEtapa1(
        entradas=train.x.shape[-1],
        unidades=hiperparametros["unidades"],
        capas=hiperparametros["capas"],
        dropout=hiperparametros["dropout"],
        clases=len(CLASES),
    )
    pesos = pesos_clase(train.y)
    perdida_fn = nn.CrossEntropyLoss(weight=torch.tensor(pesos, dtype=torch.float32))
    optimizador = torch.optim.Adam(
        modelo.parameters(),
        lr=hiperparametros["lr"],
        weight_decay=hiperparametros["weight_decay"],
    )
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

