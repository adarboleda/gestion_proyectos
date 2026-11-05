# Data Model: Evaluación del diagnóstico

## 1. Estructura de `evaluacion_diagnostico.json`

```json
{
  "aviso": "Recomendación consultiva: el operador valida y decide; el sistema no actúa sobre la planta.",
  "umbral_abstencion": 0.80,
  "nivel_confianza_intervalos": 0.95,
  "clases": ["NORM", "LOCA", "TRANS"],
  "col_clases": ["NORM", "LOCA", "TRANS", "UNCERTAIN"],
  "validacion": {
    "n_muestras": 1500,
    "aciertos_con_confianza": 1450,
    "exactitud_con_abstencion": 0.9667,
    "exactitud_con_abstencion_ci": [0.956, 0.975],
    "abstenciones": 50,
    "tasa_abstencion": 0.0333,
    "tasa_abstencion_ci": [0.025, 0.044],
    "errores_alta_confianza": 0,
    "tasa_errores_alta_confianza": 0.0,
    "tasa_errores_alta_confianza_ci": [0.0, 0.0025],
    "exactitud_decididas": 1.0,
    "exactitud_estandar": 0.98,
    "matriz_confusion_3x4": [
      [300, 0, 0, 0],
      [0, 600, 0, 30],
      [0, 0, 550, 20]
    ],
    "lista_errores_alta_confianza": []
  },
  "prueba": {
    "n_muestras": 1200,
    "aciertos_con_confianza": 1150,
    "exactitud_con_abstencion": 0.9583,
    "exactitud_con_abstencion_ci": [0.945, 0.968],
    "abstenciones": 45,
    "tasa_abstencion": 0.0375,
    "tasa_abstencion_ci": [0.028, 0.050],
    "errores_alta_confianza": 5,
    "tasa_errores_alta_confianza": 0.0042,
    "tasa_errores_alta_confianza_ci": [0.0018, 0.0097],
    "exactitud_decididas": 0.9957,
    "exactitud_estandar": 0.975,
    "matriz_confusion_3x4": [
      [250, 0, 0, 0],
      [0, 500, 0, 25],
      [0, 5, 400, 20]
    ],
    "lista_errores_alta_confianza": [
      {
        "indice": 142,
        "clase_real": "TRANS",
        "clase_predicha": "LOCA",
        "confianza": 0.842
      }
    ]
  },
  "validacion_cruzada": {
    "k_folds": 5,
    "semilla": 42,
    "folds": [
      {
        "fold": 1,
        "n_muestras": 550,
        "exactitud_con_abstencion": 0.965,
        "tasa_abstencion": 0.035,
        "tasa_errores_alta_confianza": 0.0
      }
    ],
    "resumen": {
      "exactitud_con_abstencion": {
        "media": 0.962,
        "std": 0.008,
        "ci_95": [0.952, 0.972]
      },
      "tasa_abstencion": {
        "media": 0.036,
        "std": 0.006,
        "ci_95": [0.028, 0.044]
      },
      "tasa_errores_alta_confianza": {
        "media": 0.002,
        "std": 0.002,
        "ci_95": [0.0, 0.005]
      }
    }
  }
}
```
