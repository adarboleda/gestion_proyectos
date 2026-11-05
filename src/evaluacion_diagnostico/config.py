"""Constantes para la evaluación del diagnóstico con abstención y validación cruzada."""

FAMILIAS = ("NORM", "LOCA", "TRANS")
ETIQUETAS = list(range(len(FAMILIAS)))
COL_FAMILIAS = ("NORM", "LOCA", "TRANS", "UNCERTAIN")

UMBRAL_DEFAULT = 0.80
K_FOLDS_DEFAULT = 5
SEMILLA_DEFAULT = 42

SALIDA_POR_DEFECTO = "resultados_evaluacion_diagnostico"
ARTEFACTOS = ("evaluacion_diagnostico.json", "evaluacion_diagnostico.txt")

AVISO = "Recomendación consultiva: el operador valida y decide; el sistema no actúa sobre la planta."
