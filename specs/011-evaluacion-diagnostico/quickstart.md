# Quickstart: Evaluación del diagnóstico

Guía rápida para evaluar el clasificador de diagnóstico reportando juntas la exactitud con abstención, la tasa de abstención, los errores con confianza alta, los intervalos de confianza y la validación cruzada.

---

## 1. Ejecución desde Consola

```powershell
.venv\Scripts\evaluar-diagnostico.exe --origen "C:\Users\Administrador\Desktop\Nuecleare\IA-Nuclear\PWR 3L" --salida resultados_evaluacion
```

O como módulo de Python:
```bash
python -m evaluacion_diagnostico --origen "..." --salida resultados_evaluacion
```

---

## 2. Uso Programático desde Python

```python
import numpy as np
from evaluacion_diagnostico.metricas import metricas_conjuntas, intervalo_wilson

# y_true: array (N,) con 0: NORM, 1: LOCA, 2: TRANS
# probs: array (N, 3) con probabilidades softmax
y_true = np.array([0, 1, 2, 1])
probs = np.array([
    [0.95, 0.03, 0.02], # acierto alta conf
    [0.10, 0.70, 0.20], # abstencion (<0.80)
    [0.05, 0.05, 0.90], # acierto alta conf
    [0.85, 0.10, 0.05], # error alta conf (predijo NORM con 0.85, era LOCA)
])

res = metricas_conjuntas(y_true, probs, umbral=0.80)
print("Exactitud con abstención:", res["exactitud_con_abstencion"], res["exactitud_con_abstencion_ci"])
print("Tasa de abstención:", res["tasa_abstencion"], res["tasa_abstencion_ci"])
print("Errores de alta confianza:", res["errores_alta_confianza"], res["tasa_errores_alta_confianza_ci"])
print("Matriz 3x4:\n", np.array(res["matriz_confusion_3x4"]))
```
