# Implementation Plan: Evaluación del diagnóstico: matriz de confusión, abstenciones y validación cruzada

**Branch**: `011-evaluacion-diagnostico` | **Fecha**: 2026-11-04 | **Spec**: [spec.md](spec.md)

---

## 1. Technical Context & Approach

El objetivo es construir el subsistema de evaluación rigurosa del diagnóstico para reactores PWR (PWR 3L), reportando juntas:
- La **exactitud global con abstención** (contando `UNCERTAIN` como no acierto).
- La **tasa de abstención** ($\text{conf} < 0.80$).
- Los **errores con confianza alta** ($\hat{y} \ne y \land \text{conf} \ge 0.80$).
- La **matriz de confusión rectangular $3 \times 4$** con la columna `UNCERTAIN`.
- Los **intervalos de confianza del 95 %** para todas las proporciones mediante el método de Wilson.
- La **validación cruzada de 5 particiones agrupadas** (*Group K-Fold*), reportando media, desviación estándar e intervalos de confianza.
- El comando de consola `evaluar-diagnostico`.

### Constitution Check (Constitución v2.0.0)

| Principio | Estado | Justificación |
|---|---|---|
| I. Sin dependencias externas pesadas innecesarias | CUMPLE | Usa `numpy`, `scikit-learn` y la librería estándar (`math`, `json`, `argparse`). |
| II. Cero fuga de datos (*data leakage*) | CUMPLE | En k-fold CV los grupos pareados (LOCA/LOCAC de misma severidad y gemelos ATWS) van íntegros a un solo fold; ningún dato de evaluación se ve en entrenamiento. |
| III. Causalidad estricta | CUMPLE | La inferencia y evaluación operan segundo a segundo con la ventana histórica de 30 s sin mirar al futuro. |
| IV. Separación estricta de dominios de planta | CUMPLE | Opera sobre el dominio PWR 3L (26 variables de entrada, un dato por segundo). |
| V. Honestidad y transparencia en limitaciones | CUMPLE | Criterio conservador: las abstenciones no se ocultan ni se suman como aciertos, sino que reducen la exactitud global si el modelo no está seguro. |
| VI. Trazabilidad y reproducibilidad con Spec Kit | CUMPLE | Ciclo SDD completo con sesiones de métricas y commits convencionales. |

---

## 2. Architecture & File Structure

```
src/evaluacion_diagnostico/
├── __init__.py
├── __main__.py
├── config.py                 # Familias (NORM, LOCA, TRANS), umbral 0.80, k=5, semilla 42, aviso
├── metricas.py               # Exactitud con abstención, tasa abstención, errores alta conf, Wilson 95%, matriz 3x4
├── validacion_cruzada.py     # Group K-Fold de 5 particiones sin fuga, entrenamiento/evaluación por fold y agregación
├── reporte.py                # Generación de estructuras JSON y reporte formateado en texto
└── cli.py                    # Línea de órdenes `evaluar-diagnostico` con publicación atómica

tests/evaluacion_diagnostico/
├── conftest.py
├── test_metricas.py          # Pruebas unitarias de Wilson, matriz 3x4 y métricas conjuntas
├── test_validacion_cruzada.py# Pruebas de partición por grupos sin fuga y agregación de folds
└── test_cli.py               # Pruebas de integración del CLI `evaluar-diagnostico`
```

---

## 3. Plan de Fases de Tareas (TDD)

1. **Fase 1: Setup y Pruebas Unitarias Iniciales (TDD Red)**:
   - Configurar `pyproject.toml` con el script `evaluar-diagnostico = "evaluacion_diagnostico.cli:main"`.
   - Crear `tests/evaluacion_diagnostico/conftest.py` y pruebas unitarias en `test_metricas.py` para intervalos de Wilson y métricas conjuntas con abstención.
2. **Fase 2: US1 & US2 - Métricas Conjuntas, Matriz con Abstención e Intervalos de Confianza**:
   - Implementar `src/evaluacion_diagnostico/metricas.py`:
     * `intervalo_wilson(k, n, confianza=0.95) -> (inferior, superior)`
     * `matriz_confusion_con_abstencion(y_true, y_pred, is_uncertain, num_clases=3) -> np.ndarray (3, 4)`
     * `metricas_conjuntas(y_true, probabilidades, umbral=0.80) -> Dict`
3. **Fase 3: US3 - Validación Cruzada Agrupada (Group K-Fold)**:
   - Implementar `src/evaluacion_diagnostico/validacion_cruzada.py`:
     * Generación de folds agrupados sin solape de severidades ni gemelos ATWS.
     * Entrenamiento y evaluación por fold.
     * Consolidación estadística: medias, desviaciones estándar e intervalos de confianza.
4. **Fase 4: US4 - Reporte Estructurado y CLI**:
   - Implementar `src/evaluacion_diagnostico/reporte.py`: formato JSON y texto estructurado con secciones de validación, prueba y validación cruzada.
   - Implementar `src/evaluacion_diagnostico/cli.py`: comando `evaluar-diagnostico` y publicación atómica de `evaluacion_diagnostico.json` y `evaluacion_diagnostico.txt`.
5. **Fase 5: Verificación Integral, Polish y Convergencia**:
   - Ejecución de la suite completa y verificación de cero regresiones globales.
