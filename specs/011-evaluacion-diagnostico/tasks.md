# Tasks: Evaluación del diagnóstico: matriz de confusión, abstenciones y validación cruzada

**Input**: Design documents from `specs/011-evaluacion-diagnostico/`  
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/cli.md`  
**Tests**: `tests/evaluacion_diagnostico/test_metricas.py`, `tests/evaluacion_diagnostico/test_validacion_cruzada.py`, `tests/evaluacion_diagnostico/test_evaluacion_cli.py`  
**Estado**: Completado

---

## Phase 1: Setup

- [x] T001 Modificar `pyproject.toml` agregando script `evaluar-diagnostico = "evaluacion_diagnostico.cli:main"` y crear `src/evaluacion_diagnostico/__init__.py`, `__main__.py` y `config.py`
- [x] T002 Crear `tests/evaluacion_diagnostico/conftest.py` con fixtures de corridas sintéticas, probabilidades y etiquetas

---

## Phase 2: User Story 1 & 2 - Métricas Conjuntas, Matriz con Abstención e Intervalos de Confianza

- [x] T003 [P] [US1] [US2] Crear `tests/evaluacion_diagnostico/test_metricas.py` con pruebas para intervalo de Wilson, matriz rectangular 3x4 y cálculo conjunto de exactitud, abstención y errores alta confianza
- [x] T004 [US1] [US2] Implementar `src/evaluacion_diagnostico/metricas.py`: `intervalo_wilson(k, n)`, `matriz_confusion_con_abstencion(y_true, y_pred, unc)` y `metricas_conjuntas(y_true, probs, umbral)`

---

## Phase 3: User Story 3 - Validación Cruzada Agrupada (Group K-Fold)

- [x] T005 [P] [US3] Crear `tests/evaluacion_diagnostico/test_validacion_cruzada.py` probando generación de 5 folds sin fuga y agregación estadística (media, std, IC)
- [x] T006 [US3] Implementar `src/evaluacion_diagnostico/validacion_cruzada.py`: partición agrupada sin fuga de severidad ni gemelos ATWS, ejecución por fold y agregación

---

## Phase 4: User Story 4 - Reporte Estructurado y CLI

- [x] T007 [P] [US4] Crear `tests/evaluacion_diagnostico/test_evaluacion_cli.py` probando serialización de reporte JSON, texto y códigos de salida de `evaluar-diagnostico`
- [x] T008 [US4] Implementar `src/evaluacion_diagnostico/reporte.py`: consolidación de validación, prueba y CV en `formatear_reporte_texto` y `construir_reporte_json`
- [x] T009 [US4] Implementar `src/evaluacion_diagnostico/cli.py`: parser de argumentos, pipeline de evaluación, publicación atómica y códigos de salida 0/1/3

---

## Phase 5: Polish, Integración y Documentación

- [x] T010 Integrar en `clasificador_etapa1/cli.py` la inclusión opcional de métricas conjuntas de validación en el reporte de entrenamiento sin romper compatibilidad
- [x] T011 Actualizar `README.md` documentando el comando `evaluar-diagnostico` y las métricas conjuntas de evaluación
- [x] T012 Ejecutar la suite completa de pruebas unitarias e integración y verificar 0 regresiones en el repositorio global
