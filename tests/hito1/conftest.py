"""Resultados sintéticos con la forma real de los archivos de 005, 006, 008, 009 y 011."""
import copy
import json
from pathlib import Path

import pytest

ETAPA1 = {
    "aviso": "Clasificador consultivo: las salidas son recomendaciones; el operador decide.",
    "conjunto_prueba": {"corridas": ["R01", "R44"], "corridas_por_familia": {"NORM": 3, "LOCA": 5, "TRANS": 5}, "muestras": 3835},
    "global": {"matriz": [[1163, 0, 30], [14, 1285, 0], [0, 92, 1251]], "f1_macro": 0.9651,
               "por_familia": {"NORM": {"precision": 0.9881, "exhaustividad": 0.9749, "f1": 0.9815, "soporte": 1193},
                               "LOCA": {"precision": 0.9332, "exhaustividad": 0.9892, "f1": 0.9604, "soporte": 1299},
                               "TRANS": {"precision": 0.9766, "exhaustividad": 0.9315, "f1": 0.9535, "soporte": 1343}}},
    "primeros_30s": {"f1_macro": 0.9483},
    "falsas_alarmas": {"corridas_norm": {"instantes": 9, "episodios": 3, "corridas": ["R33", "R36", "R40"]},
                       "tramos_previos": {"instantes": 0, "episodios": 0, "corridas": []}},
    "metas": {"SC-001": {"valor": "2 de 2 en ≤ 10 s", "cumple": True, "meta": "LOCA ≥ 50 cm² confirmada en ≤ 10 s en el 100 %"},
              "SC-002": {"valor": "3 falsas alarmas en corridas NORM", "cumple": False, "meta": "0 falsas alarmas en corridas NORM"},
              "SC-003": {"valor": "F1 macro = 0.948", "cumple": True, "meta": "F1 macro de los primeros 30 s ≥ 0.80"}},
    "entrenamiento": {"mejor_epoca": 7, "epocas_ejecutadas": 13, "f1_validacion": 0.99001, "semilla": 42},
    "reparto": {"train": {"corridas": 63, "muestras": 8449}, "val": {"corridas": 15, "muestras": 4425},
                "test": {"corridas": 13, "muestras": 3835}},
}

REGLA_RESUMEN = {
    "version_formato": 1,
    "por_conjunto": {
        "train": {"atws_detectados": 12, "atws_omitidos": 0, "falsas_alarmas": 0, "rechazos_correctos": 51, "total": 63},
        "val": {"atws_detectados": 3, "atws_omitidos": 0, "falsas_alarmas": 1, "rechazos_correctos": 11, "total": 15},
        "test": {"atws_detectados": 3, "atws_omitidos": 0, "falsas_alarmas": 0, "rechazos_correctos": 10, "total": 13},
    },
    "errores": [{"id": "R54", "conjunto": "val", "tipo": "falsa_alarma", "pwnt_decision_pct": 57.3}],
    "tiempos": {"train": {"detectados": 12, "min_s": 2.0, "max_s": 2.5, "cumplen_meta": 12},
                "val": {"detectados": 3, "min_s": 2.0, "max_s": 2.5, "cumplen_meta": 3},
                "test": {"detectados": 3, "min_s": 2.0, "max_s": 2.5, "cumplen_meta": 3}},
    "advertencias": ["R54 (val): tipo de señal «turbine trip» no visto en entrenamiento; se usó el mayor retardo (2.5 s)."],
    "limitaciones": ["Pocas corridas."],
    "aviso": "Recomendación para el operador: la regla no actúa sobre la planta.",
}
REGLA = {"version_formato": 1, "calibrada_con": "train", "umbral_pwnt_pct": 19.291046, "espera_s": 2.0,
         "margen": {"minimo_atws_pct": 32.909252, "maximo_no_atws_pct": 5.67284, "solape": False}}

TIEMPOS = {
    "aviso": "Resultados consultivos.",
    "configuracion": {"semilla": 42, "meta_diagnostico_s": 10.0, "meta_atws_s": 3.0},
    "corridas": [
        {"corrida": "R44", "conjunto": "test", "clase": "LOCA", "familia": "LOCA", "area": 100,
         "falla": {"t": 50.0, "fuente": "programado", "incierta": False}, "tiempo_diagnostico_s": 4.0,
         "atws": {"recomendacion": "sin ATWS", "es_atws": False, "tiempo_desde_demanda_s": None, "falsa_alarma": False}},
        {"corrida": "R29", "conjunto": "test", "clase": "ATWS", "familia": "TRANS", "area": None,
         "falla": {"t": 2.0, "fuente": "registro", "incierta": False}, "tiempo_diagnostico_s": 4.0,
         "atws": {"recomendacion": "posible ATWS", "es_atws": True, "tiempo_desde_demanda_s": 2.0, "falsa_alarma": False}},
        {"corrida": "R68", "conjunto": "val", "clase": "NORM", "familia": "NORM", "area": None, "falla": None,
         "tiempo_diagnostico_s": None, "atws": {"recomendacion": "sin ATWS", "es_atws": False}},
    ],
    "metas": {"diagnostico_10s": {"dentro": 10, "total": 10, "valor": "10 de 10 (100 %)", "cumple": True,
                                  "meta": "familia del evento confirmada en ≤ 10 s desde la falla en el 100 % de las corridas de evento de prueba no inciertas"},
              "atws_3s": {"dentro": 6, "total": 6, "valor": "6 de 6 (100 %)", "cumple": True,
                          "meta": "ATWS reconocido en ≤ 3 s desde la demanda de disparo en el 100 % de los ATWS de validación y prueba"}},
    "falsas_alarmas": {"val": {"etapa1": {"corridas_norm": {"episodios": 1, "corridas": ["R68"]}}, "regla": {"recomendaciones": 1, "corridas": ["R54"]}},
                       "test": {"etapa1": {"corridas_norm": {"episodios": 3, "corridas": ["R33", "R36", "R40"]}}, "regla": {"recomendaciones": 0, "corridas": []}}},
}

ETAPA2 = {
    "aviso": "Clasificador consultivo de Etapa 2.",
    "global": {"muestras": 1299, "matriz": [[0, 0, 250], [0, 0, 1049]], "f1_macro": 0.0, "abstenciones": 1299,
               "cobertura": 0.0, "exactitud_decisiones": 0.0, "errores_confianza": 0},
    "corridas": [{"corrida": "R44", "clase": "LOCA", "area": 100, "confirmada": "UNCERTAIN", "correcta": False, "tiempo_s": None}],
    "metas": {"SC-001_sin_errores_confianza_30s": {"errores_confianza": 0, "exactitud_decisiones": 0.0, "cobertura": 0.0, "cumple": True},
              "SC-002_loca_50cm2_en_10s": {"confirmadas_en_10s": 0, "total": 2, "cumple": False}},
    "reparto": {"train": {"corridas": 25}, "val": {"corridas": 6}, "test": {"corridas": 5}},
}


def _conjunto(n, aciertos, abst, errores, matriz):
    return {"n_muestras": n, "aciertos_con_confianza": aciertos, "exactitud_con_abstencion": round(aciertos / n, 4),
            "exactitud_con_abstencion_ci": [0.94, 0.96], "abstenciones": abst, "tasa_abstencion": round(abst / n, 4),
            "tasa_abstencion_ci": [0.016, 0.025], "errores_alta_confianza": errores,
            "tasa_errores_alta_confianza": round(errores / n, 4), "tasa_errores_alta_confianza_ci": [0.025, 0.036],
            "exactitud_decididas": 0.9691, "exactitud_decididas_ci": [0.963, 0.974], "exactitud_estandar": 0.9645,
            "matriz_confusion_3x4": matriz, "col_class_names": ["NORM", "LOCA", "TRANS", "UNCERTAIN"],
            "row_class_names": ["NORM", "LOCA", "TRANS"], "lista_errores_alta_confianza": []}


DIAGNOSTICO = {
    "aviso": "Recomendación consultiva: el operador valida y decide.",
    "umbral_abstencion": 0.8,
    "nivel_confianza_intervalos": 0.95,
    "prueba": _conjunto(3835, 3642, 77, 116, [[1107, 0, 12, 74], [12, 1285, 0, 2], [0, 92, 1250, 1]]),
    "validacion": _conjunto(4425, 4317, 71, 37, [[1500, 0, 5, 60], [10, 1400, 0, 5], [0, 22, 1417, 6]]),
    "validacion_cruzada": {"k_folds": 5, "semilla": 42, "epocas_por_fold": 5, "folds": [{}] * 5, "resumen": {
        "exactitud_con_abstencion": {"media": 0.6594, "std": 0.3761, "ci_95": [0.1924, 1.0]},
        "tasa_abstencion": {"media": 0.3281, "std": 0.3884, "ci_95": [0.0, 0.8104]},
        "tasa_errores_alta_confianza": {"media": 0.0125, "std": 0.0194, "ci_95": [0.0, 0.0366]},
        "exactitud_decididas": {"media": 0.9873, "std": 0.0197, "ci_95": [0.9629, 1.0]},
        "exactitud_estandar": {"media": 0.9563, "std": 0.0364, "ci_95": [0.9111, 1.0]}}},
}

ARCHIVOS = {
    "etapa1": ("modelos/etapa1", {"reporte.json": ETAPA1}),
    "regla": ("resultados_regla_atws", {"resumen.json": REGLA_RESUMEN, "regla.json": REGLA}),
    "tiempos": ("resultados_tiempo_deteccion", {"tiempos.json": TIEMPOS}),
    "etapa2": ("modelos/etapa2", {"reporte.json": ETAPA2}),
    "diagnostico": ("resultados_evaluacion_diagnostico", {"evaluacion_diagnostico.json": DIAGNOSTICO}),
}


def escribir_resultados(raiz: Path) -> dict:
    rutas = {}
    for clave, (carpeta, archivos) in ARCHIVOS.items():
        destino = raiz / carpeta
        destino.mkdir(parents=True, exist_ok=True)
        for nombre, contenido in archivos.items():
            (destino / nombre).write_text(json.dumps(contenido, ensure_ascii=False, indent=2), encoding="utf-8")
        rutas[clave] = destino
    return rutas


@pytest.fixture
def resultados(tmp_path):
    """Rutas de las cinco fuentes sintéticas en un directorio propio de cada prueba."""
    return escribir_resultados(tmp_path / "proyecto")


@pytest.fixture
def datos():
    """Contenido de las fuentes en memoria (copias independientes)."""
    return {
        "etapa1": {"reporte": copy.deepcopy(ETAPA1)},
        "regla": {"resumen": copy.deepcopy(REGLA_RESUMEN), "regla": copy.deepcopy(REGLA)},
        "tiempos": {"tiempos": copy.deepcopy(TIEMPOS)},
        "etapa2": {"reporte": copy.deepcopy(ETAPA2)},
        "diagnostico": {"evaluacion": copy.deepcopy(DIAGNOSTICO)},
    }
