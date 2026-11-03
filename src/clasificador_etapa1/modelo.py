"""Bi-LSTM de la Etapa 1: familia del evento a partir de una ventana de 30 s."""
import torch
from torch import nn

from clasificador_etapa1.config import FAMILIAS


class BiLSTMEtapa1(nn.Module):
    """LSTM bidireccional pequeña (pocos datos: 63 corridas de entrenamiento).

    Resume la ventana con el último estado hacia delante, el último estado hacia atrás y la media
    temporal de las salidas. Devuelve logits (la entropía cruzada aplica el softmax).
    La ventana solo contiene datos hasta el instante actual, así que la dirección hacia atrás no ve
    el futuro de la planta.
    """

    def __init__(self, entradas: int, unidades: int = 32, capas: int = 1, dropout: float = 0.3,
                 clases: int = len(FAMILIAS)):
        super().__init__()
        self.lstm = nn.LSTM(entradas, unidades, num_layers=capas, batch_first=True, bidirectional=True)
        self.dropout = nn.Dropout(dropout)
        self.salida = nn.Linear(unidades * 2 * 2, clases)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        salidas, (h, _) = self.lstm(x)
        ultimo = torch.cat([h[-2], h[-1]], dim=1)  # último estado hacia delante y hacia atrás
        media = salidas.mean(dim=1)
        return self.salida(self.dropout(torch.cat([ultimo, media], dim=1)))
