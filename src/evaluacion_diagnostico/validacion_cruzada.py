"""Validación cruzada agrupada (Group K-Fold) sin fuga de información."""
import math
import random
from typing import Dict, List, Optional, Tuple

import numpy as np

from evaluacion_diagnostico.config import K_FOLDS_DEFAULT, SEMILLA_DEFAULT, UMBRAL_DEFAULT
from evaluacion_diagnostico.metricas import metricas_conjuntas
from preparacion_pwr3l.config import VARIABLES_ENTRADA
from preparacion_pwr3l.descubrimiento import Corrida
from preparacion_pwr3l.escalado import ajustar_escalador, aplicar


def _redondear(valor: Optional[float], decimales: int = 4) -> Optional[float]:
    return None if valor is None else round(float(valor), decimales)


def obtener_clave_grupo(c: Corrida) -> str:
    """Identifica el grupo de no-fuga al que pertenece la corrida."""
    if hasattr(c, "grupo") and c.grupo:
        return str(c.grupo)
    if getattr(c, "area", None) is not None:
        return f"AREA-{c.area}"
    if getattr(c, "gemela", None):
        pareja = sorted([c.id, c.gemela])
        return f"GEMELAS-{pareja[0]}-{pareja[1]}"
    return c.id


def particionar_kfold_por_grupos(
    corridas: List[Corrida], k: int = K_FOLDS_DEFAULT, semilla: int = SEMILLA_DEFAULT
) -> List[Tuple[List[Corrida], List[Corrida]]]:
    """Divide las corridas en k particiones disjuntas por grupo (Group K-Fold).

    Garantiza que todas las corridas pertenecientes al mismo grupo (pares de rotura LOCA/LOCAC
    o pares de transitorios ATWS/TRIP_OK) permanezcan en el mismo fold, evitando cualquier
    fuga de información (Principio II de la Constitución).
    """
    if k <= 1:
        raise ValueError(f"k ({k}) debe ser mayor a 1.")

    por_grupo: Dict[str, List[Corrida]] = {}
    for c in corridas:
        clave = obtener_clave_grupo(c)
        por_grupo.setdefault(clave, []).append(c)

    grupos_unicos = sorted(por_grupo.keys())
    if len(grupos_unicos) < k:
        raise ValueError(f"Número de grupos únicos ({len(grupos_unicos)}) menor que k ({k}).")

    rng = random.Random(semilla)
    shuffled_grupos = list(grupos_unicos)
    rng.shuffle(shuffled_grupos)

    # Distribuir grupos en k folds equilibrando el conteo de corridas
    folds_grupos: List[List[str]] = [[] for _ in range(k)]
    conteos_corridas = [0] * k

    for g in shuffled_grupos:
        min_idx = int(np.argmin(conteos_corridas))
        folds_grupos[min_idx].append(g)
        conteos_corridas[min_idx] += len(por_grupo[g])

    particiones: List[Tuple[List[Corrida], List[Corrida]]] = []
    todos_los_grupos = set(grupos_unicos)

    for i in range(k):
        test_g = set(folds_grupos[i])
        train_g = todos_los_grupos - test_g

        train_corridas = [c for g in sorted(train_g) for c in por_grupo[g]]
        test_corridas = [c for g in sorted(test_g) for c in por_grupo[g]]
        particiones.append((train_corridas, test_corridas))

    return particiones


def agregar_metricas_folds(resultados_folds: List[Dict]) -> Dict:
    """Calcula la media, desviación estándar e intervalo de confianza al 95 % entre los folds."""
    k = len(resultados_folds)
    if k == 0:
        return {}

    metricas_claves = [
        "exactitud_con_abstencion",
        "tasa_abstencion",
        "tasa_errores_alta_confianza",
        "exactitud_decididas",
        "exactitud_estandar",
    ]

    resumen = {}
    t_val = 2.7764 if k == 5 else (2.262 if k == 10 else 1.96)

    for clave in metricas_claves:
        valores = [
            float(r[clave])
            for r in resultados_folds
            if r.get(clave) is not None
        ]
        if not valores:
            resumen[clave] = {"media": None, "std": None, "ci_95": [None, None]}
            continue

        media = float(np.mean(valores))
        std = float(np.std(valores, ddof=1)) if len(valores) > 1 else 0.0
        error_estandar = (std / math.sqrt(len(valores))) if len(valores) > 1 else 0.0
        ci_inf = max(0.0, media - t_val * error_estandar)
        ci_sup = min(1.0, media + t_val * error_estandar)

        resumen[clave] = {
            "media": _redondear(media),
            "std": _redondear(std),
            "ci_95": [_redondear(ci_inf), _redondear(ci_sup)],
        }

    return resumen


def ejecutar_kfold(
    corridas: List[Corrida],
    inicios: Dict[str, Optional[float]],
    k: int = K_FOLDS_DEFAULT,
    semilla: int = SEMILLA_DEFAULT,
    umbral: float = UMBRAL_DEFAULT,
    epocas: int = 5,
) -> Dict:
    """Ejecuta la validación cruzada completa de k folds entrenando y evaluando con cero fuga."""
    import torch
    from clasificador_etapa1.config import HIPERPARAMETROS
    from clasificador_etapa1.entrenamiento import entrenar, predecir
    from clasificador_etapa1.muestras import construir_muestras

    particiones = particionar_kfold_por_grupos(corridas, k=k, semilla=semilla)
    resultados_folds: List[Dict] = []

    for fold_idx, (train_corridas, test_corridas) in enumerate(particiones, start=1):
        x_train_raw = np.stack([c.serie[:, : len(VARIABLES_ENTRADA)] for c in train_corridas])
        escalador_fold = ajustar_escalador(x_train_raw)

        series_train = {c.id: aplicar(escalador_fold, c.serie[None, :, : len(VARIABLES_ENTRADA)])[0] for c in train_corridas}
        series_test = {c.id: aplicar(escalador_fold, c.serie[None, :, : len(VARIABLES_ENTRADA)])[0] for c in test_corridas}

        m_train = construir_muestras(train_corridas, series_train, inicios, entrenamiento=True)
        m_test = construir_muestras(test_corridas, series_test, inicios, entrenamiento=False)

        hp_fold = dict(HIPERPARAMETROS, epocas=epocas)
        semilla_fold = semilla + fold_idx * 100
        res_entrenamiento = entrenar(m_train, m_test, hp_fold, semilla=semilla_fold)

        probs_test = predecir(res_entrenamiento.modelo, m_test.x)
        metricas_fold = metricas_conjuntas(m_test.y, probs_test, umbral=umbral)

        metricas_fold["fold"] = fold_idx
        metricas_fold["corridas_test"] = [c.id for c in test_corridas]
        metricas_fold["n_corridas_test"] = len(test_corridas)
        resultados_folds.append(metricas_fold)

    resumen = agregar_metricas_folds(resultados_folds)
    return {
        "k_folds": k,
        "semilla": semilla,
        "umbral": umbral,
        "epocas_por_fold": epocas,
        "folds": resultados_folds,
        "resumen": resumen,
    }
