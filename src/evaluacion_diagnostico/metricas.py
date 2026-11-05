"""Cálculo de métricas conjuntas con abstención, matriz rectangular e intervalos de Wilson."""
import math
from typing import Dict, List, Optional, Tuple

import numpy as np

from evaluacion_diagnostico.config import COL_FAMILIAS, FAMILIAS, UMBRAL_DEFAULT

Z_95 = 1.959963984540054  # cuantil normal estándar para nivel de confianza del 95 %


def _redondear(valor: Optional[float], decimales: int = 4) -> Optional[float]:
    return None if valor is None else round(float(valor), decimales)


def intervalo_wilson(
    k: int, n: int, nivel_confianza: float = 0.95
) -> Tuple[Optional[float], Optional[float]]:
    """Calcula el intervalo de confianza de Wilson (score interval) para una proporción binomial k/n.

    Garantiza límites asintóticos estrictamente acotados en [0, 1] sin sufrir el colapso a ancho 0
    que afecta al intervalo asintótico estándar de Wald ante proporciones 0 o 1.
    """
    if n <= 0:
        return None, None
    if k < 0 or k > n:
        raise ValueError(f"k ({k}) no puede ser menor a 0 ni mayor a n ({n}).")

    z = Z_95 if abs(nivel_confianza - 0.95) < 1e-4 else math.sqrt(2) * math.erfinv(nivel_confianza)
    p_hat = float(k) / float(n)
    z2 = z * z
    denominador = 1.0 + (z2 / float(n))
    centro_ajustado = (p_hat + (z2 / (2.0 * float(n)))) / denominador
    error_estandar = (z / denominador) * math.sqrt(
        (p_hat * (1.0 - p_hat) / float(n)) + (z2 / (4.0 * float(n) * float(n)))
    )

    lim_inf = max(0.0, centro_ajustado - error_estandar)
    lim_sup = min(1.0, centro_ajustado + error_estandar)
    return _redondear(lim_inf), _redondear(lim_sup)


def matriz_confusion_con_abstencion(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    is_uncertain: np.ndarray,
    num_clases: int = len(FAMILIAS),
) -> np.ndarray:
    """Construye la matriz de confusión rectangular K x (K+1).

    Filas: clases verdaderas (0 .. K-1)
    Columnas: clases predichas con confianza (0 .. K-1) más la columna UNCERTAIN (índice K).
    """
    y_true = np.asarray(y_true, dtype=np.int64)
    y_pred = np.asarray(y_pred, dtype=np.int64)
    is_uncertain = np.asarray(is_uncertain, dtype=bool)

    cm = np.zeros((num_clases, num_clases + 1), dtype=np.int64)
    col_uncertain = num_clases

    for yt, yp, unc in zip(y_true, y_pred, is_uncertain):
        if 0 <= yt < num_clases:
            if unc:
                cm[yt, col_uncertain] += 1
            elif 0 <= yp < num_clases:
                cm[yt, yp] += 1
    return cm


def metricas_conjuntas(
    y_true: np.ndarray,
    probabilidades: np.ndarray,
    umbral: float = UMBRAL_DEFAULT,
    class_names: Optional[List[str]] = None,
) -> Dict:
    """Calcula el reporte conjunto de exactitud con abstención, tasa de abstención,

    errores de alta confianza, matriz 3x4 e intervalos de confianza de Wilson al 95 %.
    """
    y_true = np.asarray(y_true, dtype=np.int64)
    probs = np.asarray(probabilidades, dtype=np.float64)
    if probs.ndim != 2:
        raise ValueError("probabilidades debe tener 2 dimensiones (N, K).")
    n_muestras = len(y_true)
    if len(probs) != n_muestras:
        raise ValueError(f"Discrepancia de longitud entre y_true ({n_muestras}) y probabilidades ({len(probs)}).")

    nombres = list(class_names) if class_names is not None else list(FAMILIAS)
    num_clases = len(nombres)

    if n_muestras == 0:
        return {
            "n_muestras": 0,
            "aciertos_con_confianza": 0,
            "exactitud_con_abstencion": None,
            "exactitud_con_abstencion_ci": [None, None],
            "abstenciones": 0,
            "tasa_abstencion": None,
            "tasa_abstencion_ci": [None, None],
            "errores_alta_confianza": 0,
            "tasa_errores_alta_confianza": None,
            "tasa_errores_alta_confianza_ci": [None, None],
            "exactitud_decididas": None,
            "exactitud_decididas_ci": [None, None],
            "exactitud_estandar": None,
            "matriz_confusion_3x4": np.zeros((num_clases, num_clases + 1), dtype=int).tolist(),
            "lista_errores_alta_confianza": [],
        }

    pred_idx = probs.argmax(axis=1)
    max_conf = probs.max(axis=1)
    is_uncertain = max_conf < umbral

    mask_acierto = (pred_idx == y_true) & (~is_uncertain)
    mask_abstencion = is_uncertain
    mask_error_alta = (pred_idx != y_true) & (~is_uncertain)

    n_aciertos = int(mask_acierto.sum())
    n_abstenciones = int(mask_abstencion.sum())
    n_errores_alta = int(mask_error_alta.sum())
    n_decididas = n_aciertos + n_errores_alta

    acc_abst = float(n_aciertos) / float(n_muestras)
    tasa_abst = float(n_abstenciones) / float(n_muestras)
    tasa_err_alta = float(n_errores_alta) / float(n_muestras)
    acc_decididas = (float(n_aciertos) / float(n_decididas)) if n_decididas > 0 else None
    acc_estandar = float((pred_idx == y_true).mean())

    cm = matriz_confusion_con_abstencion(y_true, pred_idx, is_uncertain, num_clases)

    # Detalle de errores con alta confianza
    lista_errores = []
    indices_err = np.flatnonzero(mask_error_alta)
    for idx in indices_err:
        yt = int(y_true[idx])
        yp = int(pred_idx[idx])
        lista_errores.append(
            {
                "indice": int(idx),
                "clase_real": nombres[yt] if yt < num_clases else str(yt),
                "clase_predicha": nombres[yp] if yp < num_clases else str(yp),
                "confianza": _redondear(float(max_conf[idx])),
            }
        )

    return {
        "n_muestras": n_muestras,
        "aciertos_con_confianza": n_aciertos,
        "exactitud_con_abstencion": _redondear(acc_abst),
        "exactitud_con_abstencion_ci": list(intervalo_wilson(n_aciertos, n_muestras)),
        "abstenciones": n_abstenciones,
        "tasa_abstencion": _redondear(tasa_abst),
        "tasa_abstencion_ci": list(intervalo_wilson(n_abstenciones, n_muestras)),
        "errores_alta_confianza": n_errores_alta,
        "tasa_errores_alta_confianza": _redondear(tasa_err_alta),
        "tasa_errores_alta_confianza_ci": list(intervalo_wilson(n_errores_alta, n_muestras)),
        "exactitud_decididas": _redondear(acc_decididas),
        "exactitud_decididas_ci": list(intervalo_wilson(n_aciertos, n_decididas)) if n_decididas > 0 else [None, None],
        "exactitud_estandar": _redondear(acc_estandar),
        "matriz_confusion_3x4": cm.tolist(),
        "col_class_names": nombres + ["UNCERTAIN"],
        "row_class_names": nombres,
        "lista_errores_alta_confianza": lista_errores,
    }
