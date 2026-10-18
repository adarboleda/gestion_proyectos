# Tasks: Estimación del margen térmico (FNN-SELU)

**Input**: Design documents from `/specs/002-margen-termico-fnn/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md; feature 001 completa

**Tests**: Bloque "Verificación rápida" de `README_FASE3.md` §10.

**Estado**: Implementada (iteración 2). Abiertas: mejoras de las limitaciones.

**Rutas**: relativas a `IA-Nuclear/NuclearPowerPlantAccidentData/pipeline/` salvo que se indique otra cosa.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [x] T001 Crear `model_fase3.py` con la FNN-SELU de 7 capas (60→256→256→128→128→64→64→2), AlphaDropout 0.1 e inicialización LeCun normal

## Phase 2: Foundational

- [x] T002 Reutilizar la partición de severidades de la Fase 2 en `severity_paired_margins_fase3.py` (caché en `../../fase3_output/severity_paired_margins/`)
- [x] T003 Calcular el contexto causal (media, máx., mín., desv. hasta `t`) en `dataset_fase3.py` (`_compute_causal_window_stats`)
- [x] T004 Normalizar objetivos con escalador solo de train y guardar `scaler_targets_mean.npy` / `_std.npy` en `../../fase3_output/`

## Phase 3: User Story 1 - Curvas DNBR(t) y PCT(t) causales (Priority: P1) 🎯 MVP

**Goal**: R² > 0.90 en prueba.
**Independent Test**: `evaluate_fase3.py` → `metrics_fase3.json`.

- [x] T005 [US1] Entrenar con Adam (lr 1e-3, wd 1e-4, batch 32, paciencia 60) en `train_fase3.py`
- [x] T006 [US1] Selección de checkpoint por `val_mse` en `train_fase3.py`
- [x] T007 [US1] Evaluar MAE, RMSE, R², sesgo y zona crítica en `evaluate_fase3.py`
- [x] T008 [US1] Medir latencia de inferencia (< 10 ms) en `evaluate_fase3.py`

## Phase 4: User Story 2 - Estimaciones físicamente plausibles (Priority: P2)

**Goal**: Violaciones del piso < 30 %.
**Independent Test**: campo `pinn_violation_rate_dnbr` de `metrics_fase3.json`.

- [x] T009 [US2] Definir `DNBR_PHYSICAL_FLOOR = 2.0` única en `dataset_fase3.py` e importarla en `train_fase3.py` y `evaluate_fase3.py`
- [x] T010 [US2] Activar `λ_pinn = 0.1` en `train_fase3.py` y documentar la prueba con `λ = 0.5` (descartada) en `README_FASE3.md` §8.2

## Phase 5: User Story 3 - Reporte honesto por clase (Priority: P2)

**Goal**: Desglose por clase y caso ATWS declarado.
**Independent Test**: `metrics_fase3.json` → `test.by_class`.

- [x] T011 [US3] Desglose por clase LOCA/LOCAC/ATWS en `evaluate_fase3.py`
- [x] T012 [US3] Ponderar el régimen plano (`FLAT_REGIME_WEIGHT_BETA = 5.0`) solo en entrenamiento en `dataset_fase3.py` y `train_fase3.py`
- [x] T013 [US3] Archivar la iteración 1 en `../../fase3_output_v1_archive/`
- [x] T014 [US3] Documentar la falla de ATWS y los 3 valores de β probados en `README_FASE3.md` §6.5

## Phase 6: Mejoras pendientes

- [ ] T030 [P] Resolver ATWS: (a) buscar más datos ATWS de NPPAD no usados, (b) verificar si los 16 ATWS disponibles son el mismo escenario benigno, (c) objetivo o arquitectura específicos del régimen "sin cambio" en `train_fase3.py` / `model_fase3.py`
- [ ] T031 [P] Expresar los umbrales de éxito (MAE, sesgo) como porcentaje del rango real en `README_FASE3.md` §7.1 y en `evaluate_fase3.py`
- [ ] T032 [P] Reducir las violaciones residuales del piso en las severidades extremas de LOCA/LOCAC (21.17 %) en `train_fase3.py`
- [ ] T033 Decidido en la clarificación de la feature 005: no se usa el 1.3 literal; la compuerta de DNBR es un umbral relativo sobre el DNBR nominal de la condición inicial (ver *Clarifications* de `specs/005-compuertas-modo-sombra/spec.md`). Documentar en `README_FASE3.md` que el piso 2.0 es solo de entrenamiento y no la compuerta
- [ ] T034 [P] Añadir explicabilidad de la FNN (qué variables mueven DNBR/PCT) en `xai_shap_fase4.py` (hoy SHAP solo explica la Bi-LSTM)

## Dependencies & Execution Order

- Foundational bloquea US1; US2 y US3 modifican `train_fase3.py` y se aplicaron en ese orden.
- T030–T034 son independientes salvo T033, que espera la clarificación de la feature 005.

## Implementation Strategy

- **MVP**: US1 (curvas causales) — entregado.
- **Siguiente paso**: T033 destraba la compuerta de DNBR de la feature 005; T030 es la mejora técnica de mayor valor.
