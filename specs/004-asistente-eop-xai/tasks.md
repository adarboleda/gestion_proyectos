# Tasks: Asistente EOP y explicabilidad

**Input**: Design documents from `/specs/004-asistente-eop-xai/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md; features 001, 002 y 003

**Tests**: Bloque de "Verificación rápida" (`README_FASE4.md` §10) y pruebas de consola/fusión de `test_pwr3l.py`.

**Estado**: Implementada. Abiertas: mejoras declaradas.

**Rutas**: relativas a `IA-Nuclear/NuclearPowerPlantAccidentData/pipeline/` salvo que se indique otra cosa.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [x] T001 Instalar `shap` y confirmar que corre sobre la Bi-LSTM

## Phase 2: Foundational

- [x] T002 Implementar `EOPMapper`, `EOP_DEFINITIONS` y `EOP_TREE` (lógica determinista) en `eop_mapper.py`
- [x] T003 Ampliar `eop_mapper.py` con TRANS y TRIP_OK y alinear el mapeo con `../../docs/Thresholds_EOP_Timeline_simplified.pdf`

## Phase 3: User Story 1 - Procedimiento recomendado (Priority: P1) 🎯 MVP

**Goal**: Recomendación coherente para las 33 muestras.
**Independent Test**: `evaluate_fase4.py` → `../../fase4_output/metrics_fase4.json`.

- [x] T004 [US1] Alertas térmicas informativas (DNBR 2.5, PCT 900 °C) en `eop_mapper.py`
- [x] T005 [US1] Caveat térmico de ATWS en `eop_mapper.py`
- [x] T006 [US1] Orquestar la recomendación sobre test y val en `evaluate_fase4.py`
- [x] T007 [US1] Conectar el mapeo con la fusión del canal rápido en `fusion_pwr3l.py`

## Phase 4: User Story 2 - Explicación de sensores (Priority: P1)

**Goal**: Explicaciones físicamente coherentes.
**Independent Test**: `../../fase4_output/xai_explanations.json`.

- [x] T008 [US2] SHAP `GradientExplainer` con fallback por oclusión en `xai_shap_fase4.py`
- [x] T009 [US2] Narrativa con valores físicos y regla de "estable" en `xai_shap_fase4.py`
- [x] T010 [US2] Selección determinista de las 8 muestras representativas en `evaluate_fase4.py`
- [x] T011 [US2] Importancia por permutación del canal rápido en `explain_pwr3l.py`
- [x] T012 [US2] Línea "Por qué" (ATWS, LOCA/LOCAC, INCIERTO, TRIP_OK) en `build_demo_pwr3l_fase4.py`

## Phase 5: User Story 3 - Contrafáctico (Priority: P2)

**Goal**: Contrafácticos honestos.
**Independent Test**: campo contrafáctico de `xai_explanations.json`.

- [x] T013 [US3] Interpolación hacia el perfil medio de la segunda clase más probable en `xai_counterfactual.py`
- [x] T014 [US3] Reportar "no encontrado" cuando 1–2 variables no bastan en `xai_counterfactual.py`

## Phase 6: User Story 4 - Consola del operador (Priority: P2)

**Goal**: Dos consolas con reproducción causal y ES/EN.
**Independent Test**: abrir los HTML; pruebas `test_console_*` de `test_pwr3l.py`.

- [x] T015 [US4] Consola del canal lento con reproducción causal en `demo_operador_fase4.html`
- [x] T016 [US4] Consola del canal rápido (5 pestañas) en `demo_operador_pwr3l_fase4.template.html` y `build_demo_pwr3l_fase4.py`
- [x] T017 [US4] Botón ES/EN con clave compartida `idss_lang` en ambas consolas
- [x] T018 [US4] Pruebas de consola (en vivo, ES/EN, "Por qué", consola generada con resultados vigentes) en `test_pwr3l.py`

## Phase 7: Polish & Mejoras pendientes

- [ ] T030 [P] Calcular la alerta de margen térmico solo sobre la porción posterior al disparo para que no se dispare en el 100 % de LOCA/LOCAC, en `eop_mapper.py`
- [ ] T031 [P] Explicabilidad de la FNN-SELU (variables que mueven DNBR/PCT) en `xai_shap_fase4.py`
- [ ] T032 [P] Reemplazar el ejemplo de XAI con `WLR` por una variable medible (presión de contención `PRB`) en `../../docs/planning/plan-de-trabajo1.0.md` y en las narrativas de `xai_shap_fase4.py` (coordinar con la feature 006)
- [ ] T033 Decidir si se añade el árbol de enfriamiento del núcleo (FR-C.1/C.2/C.3) o se mantiene fuera de alcance, y documentarlo en `README_FASE4.md`
- [ ] T034 [P] Documentar en `README_FASE4.md` §5 que el canal rápido usa permutación en vez de SHAP y por qué (decisión D9 de `research.md`)

## Dependencies & Execution Order

- Foundational (EOP) → US1 → US2 → US3 → US4.
- US4 depende de las salidas de US1–US3 y de la feature 003.
- T030–T034 son independientes; T032 se coordina con la feature 006.

## Implementation Strategy

- **MVP**: US1 + US2 — entregado.
- **Siguiente paso**: T030 (la alerta que se dispara siempre resta credibilidad) y T032 (corrección de un ejemplo con variable no medible).
