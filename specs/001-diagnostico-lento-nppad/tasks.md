# Tasks: Diagnóstico de accidentes sobre NPPAD (canal lento)

**Input**: Design documents from `/specs/001-diagnostico-lento-nppad/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Las comprobaciones son los scripts de "verificación rápida" de los README de fase (no hay suite unittest para esta feature).

**Estado**: Implementada (Fases 1–2). Las tareas marcadas `[x]` ya existen en `IA-Nuclear`; las abiertas son mejoras declaradas en las limitaciones.

**Rutas**: relativas a `IA-Nuclear/NuclearPowerPlantAccidentData/pipeline/` salvo que se indique otra cosa.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [x] T001 Instalar dependencias listadas en `../requirements.txt` (`torch`, `scikit-learn`, `pandas`, `matplotlib`) y usar semilla 42 en todos los scripts
- [x] T002 Corregir el mapeo de carpetas (`Normal` en vez de `NORM`; separar LOCA y LOCAC) en `preprocess_fase1.py`

## Phase 2: Foundational

- [x] T003 Seleccionar 12 sensores de entrada y 7 variables de margen térmico en `preprocess_fase1.py`
- [x] T004 Implementar `StandardScaler` solo con train y guardar `scaler_mean.npy` / `scaler_std.npy` en `../../data_processed/`
- [x] T005 Escribir `metadata.json` con `known_limitations` en `../../data_processed/metadata.json`

## Phase 3: User Story 1 - Datos de NPPAD listos y sin fuga (Priority: P1) 🎯 MVP

**Goal**: Conjuntos train/val/test sin fuga con márgenes alineados.
**Independent Test**: bloque "Verificación rápida" de `README_FASE1.md` §9.

- [x] T006 [US1] Group-split 70/15/15 por archivo completo para LOCA y LOCAC en `preprocess_fase1.py`
- [x] T007 [US1] Ventaneo con bloques disjuntos para NORM y ATWS (`stride_single_file=10`) en `preprocess_fase1.py`
- [x] T008 [US1] Imprimir conteos por clase×conjunto y advertir de conjuntos vacíos en `preprocess_fase1.py`
- [x] T009 [US1] Documentar resultados y limitaciones en `README_FASE1.md`

## Phase 4: User Story 2 - Diagnóstico NORM / LOCA / ATWS con abstención (Priority: P1)

**Goal**: Etapa 1 con 100 % en test y abstención al 0.80.
**Independent Test**: `evaluate_fase2.py` → matriz 4×5 sin errores.

- [x] T010 [P] [US2] Dataset PyTorch y pesos de clase por etapa en `dataset_fase2.py`
- [x] T011 [P] [US2] Clase `BiLSTMAccidentClassifier` (pooling `last_and_mean` / `attention`) en `model_fase2.py`
- [x] T012 [US2] Entrenar Etapa 1 (hidden 32, lr 1e-3) en `train_fase2.py`
- [x] T013 [US2] Criterio de checkpoint: F1 mayor o igual con `val_loss` menor en `train_fase2.py`
- [x] T014 [US2] Evaluación con matriz 4×5, ROC y falsos negativos en `evaluate_fase2.py`
- [x] T015 [US2] Archivar la iteración 1 plana en `../../fase2_output/baseline_flat_4class_archive/`

## Phase 5: User Story 3 - Rama caliente/fría (Priority: P2)

**Goal**: Etapa 2 con ≥ 95 % en k-fold.
**Independent Test**: `kfold_stage2.py` → 99.0 % ± 2.0 %.

- [x] T016 [US3] Partición pareada por severidad en `severity_paired_data.py`
- [x] T017 [US3] Canal de desviación pico causal de `PWR`/`PWNT` con escalador propio en `severity_paired_data.py`
- [x] T018 [US3] Entrenar Etapa 2 (hidden 48, atención, lr 3e-3) en `train_fase2.py`
- [x] T019 [US3] Validación cruzada de 5 particiones en `kfold_stage2.py`
- [x] T020 [US3] Confirmación independiente con regresión logística sobre el pico de `PWR` (99.0 % ± 2.0 %)

## Phase 6: User Story 4 - Tiempo de confirmación honesto (Priority: P3)

**Goal**: Latencia causal y de inferencia reportadas.
**Independent Test**: `causal_latency_fase2.py` → `../../fase2_output/latency_fase2.json`.

- [x] T021 [US4] Detección causal sostenida (`sustain_count = 3`) en `causal_latency_fase2.py`
- [x] T022 [US4] Medir latencia de inferencia (p95 < 10 ms) en `causal_latency_fase2.py`
- [x] T023 [US4] Documentar que la meta de 3 s es inalcanzable a 10 s y derivarla al canal rápido en `README_FASE2.md` §7

## Phase 7: Mejoras pendientes (limitaciones declaradas)

- [ ] T040 Ablación sin `WLR`: reentrenar Etapas 1 y 2 sin esa entrada en `../../fase2_output_sinWLR/` y comparar con las métricas actuales (declarar la caída si la hay)
- [ ] T041 [P] Revisar si la Etapa 1 mejora con el mismo criterio de checkpoint por confianza (limitación 7 de `README_FASE2.md`) en `train_fase2.py`
- [ ] T042 [P] Reportar el tiempo de la Fase 2 como "tiempo de confirmación" y no "tiempo de detección" en `README_FASE2.md` y en la consola `demo_operador_fase4.html`
- [ ] T043 [P] Mitigar el diagnóstico ATWS confiado en los primeros ~450–550 s de un LOCA (más NORM de entrenamiento o regla de confirmación más exigente) en `train_fase2.py` / `causal_latency_fase2.py`
- [ ] T044 Validar la señal de sobrepotencia (hot/cold) con otro código (RELAP5/TRACE) o con datos de entrenador de operadores, si hay acceso (hipótesis física no confirmada)

## Dependencies & Execution Order

- Fase 2 (Foundational) bloquea las historias.
- US1 → US2 → US3 → US4 (cada una consume la salida de la anterior).
- T040–T044 son independientes entre sí; T040 es la de mayor valor para la defensa.

## Implementation Strategy

- **MVP**: US1 + US2 (datos + Etapa 1) — ya entregado.
- **Entrega incremental**: US3 y US4 agregaron la rama y la latencia sin romper lo anterior.
- **Siguiente paso**: T040 (ablación sin `WLR`).
