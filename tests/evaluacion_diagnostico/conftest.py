"""Fixtures y generadores de datos sintéticos para pruebas de evaluación diagnóstica."""
import numpy as np
import pytest

from preparacion_pwr3l.descubrimiento import Corrida


@pytest.fixture
def probabilidades_y_etiquetas_sinteticas():
    """Genera un conjunto sintético con casos claros de acierto, abstención y error con alta confianza."""
    # 0: NORM, 1: LOCA, 2: TRANS
    y_true = np.array([0, 0, 1, 1, 1, 2, 2, 2, 1, 0])
    probs = np.array([
        [0.90, 0.05, 0.05],  # 0 acierto alta conf (NORM)
        [0.85, 0.10, 0.05],  # 1 acierto alta conf (NORM)
        [0.05, 0.95, 0.00],  # 2 acierto alta conf (LOCA)
        [0.10, 0.82, 0.08],  # 3 acierto alta conf (LOCA)
        [0.30, 0.50, 0.20],  # 4 abstención (<0.80)
        [0.05, 0.05, 0.90],  # 5 acierto alta conf (TRANS)
        [0.10, 0.20, 0.70],  # 6 abstención (<0.80)
        [0.85, 0.05, 0.10],  # 7 error alta conf: predijo NORM con 0.85 pero era TRANS
        [0.92, 0.04, 0.04],  # 8 error alta conf: predijo NORM con 0.92 pero era LOCA
        [0.40, 0.30, 0.30],  # 9 abstención (<0.80)
    ], dtype=np.float64)
    # Total n = 10
    # Aciertos alta conf: 0, 1, 2, 3, 5 -> 5 (5/10 = 0.5)
    # Abstenciones: 4, 6, 9 -> 3 (3/10 = 0.3)
    # Errores alta conf: 7, 8 -> 2 (2/10 = 0.2)
    # Suma: 0.5 + 0.3 + 0.2 = 1.0
    return y_true, probs


@pytest.fixture
def corridas_sinteticas_pwr3l():
    """Genera corridas sintéticas con grupos pareados para validación cruzada."""
    corridas = []
    # 5 grupos pareados LOCA/LOCAC (severidades 10, 20, 30, 40, 50 cm2)
    for area in [10, 20, 30, 40, 50]:
        grupo = f"AREA-{area}"
        for clase in ("LOCA", "LOCAC"):
            cid = f"R_loca_{area}_{clase.lower()}"
            serie = np.zeros((300, 33), dtype=np.float64)
            c = Corrida(
                id=cid,
                clase=clase,
                origen="manual",
                archivo=f"sub/{cid}.csv",
                area=area,
                estado="usable",
                filas=300,
                serie=serie,
            )
            c.grupo = grupo
            corridas.append(c)

    # 5 corridas NORM
    for i in range(5):
        cid = f"R_norm_{i}"
        serie = np.zeros((300, 33), dtype=np.float64)
        c = Corrida(
            id=cid,
            clase="NORM",
            origen="manual",
            archivo=f"sub/{cid}.csv",
            estado="usable",
            filas=300,
            serie=serie,
        )
        c.grupo = f"NORM_{i}"
        corridas.append(c)

    # 5 pares de ATWS / TRIP_OK
    for i in range(5):
        grupo = f"GEMELAS-atws_{i}-trip_{i}"
        for clase in ("ATWS", "TRIP_OK"):
            cid = f"R_{clase.lower()}_{i}"
            gemela = f"R_{'trip_ok' if clase == 'ATWS' else 'atws'}_{i}"
            serie = np.zeros((300, 33), dtype=np.float64)
            c = Corrida(
                id=cid,
                clase=clase,
                origen="manual",
                archivo=f"sub/{cid}.csv",
                gemela=gemela,
                estado="usable",
                filas=300,
                serie=serie,
            )
            c.grupo = grupo
            corridas.append(c)

    # Total 25 corridas, 15 grupos disjuntos
    return corridas
