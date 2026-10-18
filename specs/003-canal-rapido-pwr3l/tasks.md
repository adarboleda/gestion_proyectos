# Tasks: Canal rápido de detección a 1 s con PWR 3L

**Input**: Design documents from `/specs/003-canal-rapido-pwr3l/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Sí; la especificación pide 17 pruebas automáticas (`test_pwr3l.py`).

**Estado**: Implementada y validada. Abiertas: límites declarados.

**Rutas**: relativas a `IA-Nuclear/NuclearPowerPlantAccidentData/pipeline/` salvo que se indique otra cosa.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [x] T001 Instalar `openpyxl` (los `.xls` son `.xlsx`) y verificar lectura con `pd.read_excel(engine="openpyxl")` en `preprocess_pwr3l.py`
- [x] T002 Documentar el plan de dataset y las correcciones previas a entrenar en `../../docs/PLAN_DATASET_PWR3L_DETECCION_RAPIDA.md`

## Phase 2: Foundational

- [x] T003 Cargar las 106 corridas, calcular inicio real, disparo requerido y gemelos en `pwr3l_rapid_detector.py`
- [x] T004 Normalizar relativo al estado inicial y usar solo datos causales en `preprocess_pwr3l.py`
- [x] T005 Aplicar ruido fijo por instrumento (FR-011) en `pwr3l_rapid_detector.py`
- [x] T006 Crear las particiones de validación cruzada por grupos (ATWS con su gemelo) en `pwr3l_rapid_detector.py`

## Phase 3: User Story 1 - Corridas de simulación confiables (Priority: P1) 🎯 MVP

**Goal**: 106 corridas validadas, 20 por clase.
**Independent Test**: `validar_corridas.py` marca cada corrida; `test_pwr3l` comprueba 20 por clase.

- [x] T007 [US1] Plan de corridas con 79 filas en `../pctran_auto/plan_corridas_pwr3l.csv`
- [x] T008 [US1] Automatizar PCTRAN (escribir la falla en la base, ×16, fin de la demo) en `../pctran_auto/ejecutar_lote.py`, `pctran_gui.py` y `pctran_db.py`
- [x] T009 [US1] Validar cada corrida (inicio real, contaminación, IC válida) en `../pctran_auto/validar_corridas.py`
- [x] T010 [US1] Generar las 5 corridas manuales R59–R63 con `../pctran_auto/preparar_manual.py`
- [x] T011 [US1] Excluir R07 (contaminada) y marcar R20, R64–R66, R107, R108 como fuera de distribución

## Phase 4: User Story 2 - Detección temprana de LOCA/LOCAC (Priority: P1)

**Goal**: ≤ 10 s en 100 % y ≤ 3 s en ≥ 10 cm².
**Independent Test**: `validate_pwr3l_acceptance.py` → `acceptance.json`.

- [x] T012 [US2] Clasificador HistGradientBoosting de 5 clases con 26 variables medibles y confirmación de 2 s en `pwr3l_rapid_detector.py`
- [x] T013 [US2] Comparar con Random Forest, GRU causal y regresión logística y ejecutar ablaciones en `evaluate_pwr3l.py` y `train_temporal_pwr3l.py`
- [x] T014 [US2] Evaluación por corrida, tres realizaciones, peor caso en `validate_pwr3l_acceptance.py`

## Phase 5: User Story 3 - ATWS frente a disparo normal (Priority: P1)

**Goal**: Compuerta 20/20 sin falsos positivos.
**Independent Test**: pruebas de integración `test_gate_*` en `test_pwr3l.py`.

- [x] T015 [US3] Compuerta ATWS (`atws_gate_series`, margen 1.5 s, PWNT > 20 %) en `pwr3l_rapid_detector.py`
- [x] T016 [US3] Clases TRANS y TRIP_OK con 20 gemelos en `preprocess_pwr3l.py`
- [x] T017 [US3] Tabla de ATWS por iniciador con mínimo físico en `validate_pwr3l_acceptance.py`

## Phase 6: User Story 4 - Sin falsas alarmas y INCIERTO ante lo desconocido (Priority: P1)

**Goal**: 0 falsas alarmas; 6/6 OOD → INCIERTO.
**Independent Test**: pruebas de integración de novedad en `test_pwr3l.py`.

- [x] T018 [US4] `NoveltyMonitor` con radiación, asimetría de GV, PORV y presión de contención en `pwr3l_rapid_detector.py`
- [x] T019 [US4] Fusión con prioridad novedad → compuerta → desacuerdo → clase en `fusion_pwr3l.py`

## Phase 7: User Story 5 - Rama caliente o fría (Priority: P2)

**Goal**: ≥ 90 % en roturas ≥ 50 cm².
**Independent Test**: `prueba_rama_caliente_fria_pwr3l.py` y `BranchClassifier`.

- [x] T020 [US5] `BranchClassifier` con la excursión de PWR/PWNT enclavada en `pwr3l_rapid_detector.py`

## Phase 8: User Story 6 - Margen térmico en PWR 3L (Priority: P2)

**Goal**: R² > 0.95.
**Independent Test**: `pwr3l_output/thermal/`.

- [x] T021 [US6] Reentrenar la FNN-SELU sin `WLR` a 1 s en `thermal_pwr3l.py`
- [x] T022 [US6] Documentar el fallo de transferencia del modelo de NPPAD en `transfer_fase3_pwr3l.py`

## Phase 9: User Story 7 - Demostrar que el tiempo bajó (Priority: P3)

**Goal**: Comparación antes / control / ahora.
**Independent Test**: pestaña "Mejora de tiempos" y prueba de resultados.

- [x] T023 [US7] `slow_style_detection` (control con la regla de la Fase 2) en `pwr3l_rapid_detector.py`
- [x] T024 [US7] Consola con pestañas Cumplimiento, En vivo, Mejora de tiempos, Conexión con las fases y Caso a caso en `build_demo_pwr3l_fase4.py` y `demo_operador_pwr3l_fase4.template.html`

## Phase 10: Polish & Cross-Cutting

- [x] T025 [P] Escribir las 17 pruebas en `test_pwr3l.py`
- [x] T026 [P] Redactar resultados y límites en `../../RESULTADOS_IMPLEMENTACION_PWR3L.md` y los resúmenes ES/EN en `../../docs/RESUMEN_PWR3L.md` y `RESUMEN_PWR3L_EN.md`
- [x] T027 [P] Importancia por permutación en `explain_pwr3l.py`

## Phase 11: Límites declarados (abiertos)

- [ ] T040 [P] Justificar con bibliografía los σ de ruido de sensores (hoy supuestos) y añadir las referencias a `../../RESULTADOS_IMPLEMENTACION_PWR3L.md` §6
- [ ] T041 [P] Probar los monitores de novedad con eventos desconocidos distintos de los 6 de diseño (por ejemplo, otros iniciadores disponibles en PCTRAN) en `validate_pwr3l_acceptance.py`
- [ ] T042 Mejorar la rama caliente/fría en LOCA + pérdida de red (R78) y en R15/R16 con ruido, en `BranchClassifier` de `pwr3l_rapid_detector.py`
- [ ] T043 [P] Mejorar o declarar el límite de roturas de 2–5 cm² (4–6 s; sin rama) con variables lentas de inventario
- [ ] T044 Resolver con el responsable de las simulaciones las preguntas 5, 6 y 7 de `../../docs/PLAN_DATASET_PWR3L_DETECCION_RAPIDA.md` §9 (HPI/LPI en 0 de R17 y R18; qué pasó en R07; licencia completa de PCTRAN)

## Dependencies & Execution Order

- Setup → Foundational → US1 → {US2, US3, US4} → US5 → US6 → US7 → Polish.
- US2, US3 y US4 comparten `pwr3l_rapid_detector.py`; se desarrollaron en orden pero se prueban por separado.
- T040–T044 son independientes entre sí.

## Implementation Strategy

- **MVP**: US1 + US2 (corridas + detección de LOCA).
- **Incremento**: ATWS (US3) y abstención (US4) cierran las metas de seguridad; US5–US7 aportan caracterización, térmico y evidencia.
- **Siguiente paso**: T040 (defensa del ruido supuesto) y T041 (robustez de la novedad).
