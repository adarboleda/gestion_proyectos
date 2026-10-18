# Tasks: Compuertas deterministas, rechazo de la IA y modo sombra

**Input**: Design documents from `/specs/005-compuertas-modo-sombra/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/shadow-log.md; features 001–004

**Tests**: Sí; se pide `test_fase5.py` (compuertas con la IA forzada, rechazo < 1 s, fusión, cobertura del log).

**Plazo**: Fase 5 del plan = 10–23 oct 2026. Hoy: 18 oct. La redacción (feature 006) arranca el 24 oct.

**Rutas**: relativas a `IA-Nuclear/NuclearPowerPlantAccidentData/pipeline/` salvo que se indique otra cosa.

## Format: `[ID] [P?] [Story] Description`

## Phase 0: Bloqueantes de decisión

- [x] T000 Resolver Q1 (DNBR relativo), respaldo de Q2 (setpoints de la planta + E-0) y Q3 (referencia automática + revisión ciega) y registrarlos en la sección *Clarifications* de `specs/005-compuertas-modo-sombra/spec.md` (hecho 2026-10-18)
- [ ] T000b Llevar a la experta: (a) la tabla de DNBR por clase de T006b con el 1.3 literal como referencia, para que confirme el porcentaje; (b) la pregunta del límite de PCT (valor y escala; PCTRAN no es temperatura real de vaina: parte de ~550 °C y no pasa de 606 °C); (c) la muestra de ~10 corridas para su anotación a ciegas. Registrar sus respuestas en `specs/005-compuertas-modo-sombra/spec.md`

## Phase 1: Setup

- [ ] T001 Crear `fase5_output/` (en `../../fase5_output/`) y `README_FASE5.md` con la estructura de fase
- [ ] T002 [P] Crear `test_fase5.py` con la estructura de casos vacía (compuertas, rechazo, fusión, log)

## Phase 2: Foundational

- [ ] T003 Extraer `atws_gate_series` y su regla a `safety_gates.py` como API determinista sin importar modelos (la lógica actual vive en `pwr3l_rapid_detector.py`; mantener compatibilidad)
- [ ] T004 [P] Implementar el cálculo de divergencia KL con histogramas contra la distribución de entrenamiento en `reject_fallback.py`
- [ ] T005 [P] Definir `RegistroDeSombra` y su escritura JSON Lines según `contracts/shadow-log.md` en `shadow_mode.py`

## Phase 3: User Story 1 - Compuertas que mandan sobre la IA (Priority: P1) 🎯 MVP

**Goal**: Alerta prioritaria aunque la IA diga otra cosa.
**Independent Test**: `test_fase5.py` con la IA forzada a NORM.

- [x] T006 [US1] Compuerta ATWS ya implementada y validada (20/20, 0 falsos positivos) en `pwr3l_rapid_detector.py` y `fusion_pwr3l.py`
- [ ] T006b [US1] Construir la tabla de DNBR por clase (NORM, LOCA, LOCAC, ATWS, TRIP_OK; mínimo, caída máxima porcentual desde el DNBR nominal de la IC, y cuántas corridas cruzarían 1.3 literal) en `dnbr_by_class.py`; verificar el dato "peor ATWS de PWR 3L cae 28 % (2.29 → 1.65)"
- [ ] T007 [US1] Compuerta de DNBR relativa (porcentaje configurable; solo si el reactor no ha disparado, es decir, no en TRIP_OK; no activar con estimación no fiable de ATWS) en `safety_gates.py`; el valor por defecto sale de T006b y lo confirma la experta (T000b)
- [ ] T008 [US1] Compuerta de PCT con umbral configurable en `safety_gates.py`; reportar contra 900 °C (informativo) y 1204 °C (referencia 10 CFR 50.46); el valor y la escala definitivos dependen de T000b
- [ ] T009 [US1] Evitar activaciones espurias en ATWS (la FNN estima DNBR −11.31) con el caveat térmico existente en `safety_gates.py` y `eop_mapper.py`
- [ ] T010 [US1] Prueba: con la salida de la IA forzada a NORM, cada condición de compuerta emite alerta prioritaria en `test_fase5.py`

## Phase 4: User Story 2 - Rechazo de la IA y respaldo < 1 s (Priority: P1)

**Goal**: Rechazo y respaldo en menos de 1 s.
**Independent Test**: inyección de baja confianza y deriva en `test_fase5.py`.

- [ ] T011 [US2] Rechazo por confianza < 0.80 con `EventoDeRechazo` y respaldo activo en `reject_fallback.py`
- [ ] T012 [US2] Rechazo por KL > 0.1 sobre ventanas deslizantes en `reject_fallback.py`
- [ ] T013 [US2] Integrar los monitores de novedad del canal rápido como motivo `novedad` en `reject_fallback.py` y `fusion_pwr3l.py`
- [ ] T014 [US2] Respaldo `setpoints_planta`: setpoints automáticos de la guía (132.2 bar disparo por presión baja, 118.1 bar HPI, 1.30 bar contención, nivel bajo de GV 17 %, 43.27 bar acumuladores, 11.36 bar RHR) + mapeo a E-0 + compuerta ATWS + monitores de novedad, sin importar ningún modelo, en `reject_fallback.py`
- [ ] T015 [US2] Prueba: medir `t_conmutacion` < 1 s sobre inyecciones en `test_fase5.py`

## Phase 5: User Story 3 - Fusión de los dos canales (Priority: P2)

**Goal**: Alarma temprana, confirmación y desacuerdo.
**Independent Test**: tres casos en `test_fase5.py`.

- [ ] T016 [P] [US3] Implementar `fusion_channels.py` con alarma temprana, confirmación al coincidir e INCIERTO con ambos diagnósticos al discrepar
- [ ] T017 [P] [US3] Manejar canal ausente sin bloquear en `fusion_channels.py`
- [ ] T018 [US3] Pruebas de coincidencia, desacuerdo y canal ausente en `test_fase5.py`
- [ ] T019 [US3] (opcional) Probar el canal lento sobre PWR 3L con 1 dato de cada 10 y normalización relativa y reportar el resultado tal como salga en `README_FASE5.md`

## Phase 6: User Story 4 - Modo sombra con registros auditables (Priority: P2)

**Goal**: Log completo de todas las corridas.
**Independent Test**: cobertura del log = 100 %.

- [ ] T020 [US4] Ejecutor de sombra para PWR 3L (106 corridas a 1 s con prefijos `[0, t)`) en `shadow_mode.py`
- [ ] T021 [US4] Ejecutor de sombra para NPPAD (corridas de prueba a 10 s) en `shadow_mode.py`
- [ ] T022 [US4] Referencia automática (procedimiento por clase y tiempos de referencia de R03, R09 y R28 de `../../docs/Thresholds_EOP_Timeline_simplified.pdf`), comparación del detector contra esos tiempos y cálculo de acuerdo por clase en `shadow_mode.py`
- [ ] T022b [US4] Preparar la muestra de ~10 corridas para la anotación ciega de la experta (sin diagnóstico ni etiqueta visibles; incluir LOCA grande y pequeño, LOCAC, ATWS de distintos iniciadores, TRIP_OK, NORM y un evento desconocido) y cargar sus respuestas como `referencia_fuente = revision_ciega` en `shadow_mode.py`
- [ ] T023 [US4] Escribir `shadow_log_*.jsonl` y `shadow_summary.json` en `../../fase5_output/`
- [ ] T024 [US4] Mostrar el log y el estado de respaldo en la consola en `build_demo_pwr3l_fase4.py` y `demo_operador_pwr3l_fase4.template.html`
- [ ] T025 [US4] Prueba de cobertura del log (una línea por decisión, `advisory_only = true`) en `test_fase5.py`

## Phase 7: User Story 5 - Eventos fuera de distribución (Priority: P3)

**Goal**: INCIERTO o respaldo ante lo desconocido.
**Independent Test**: fracción reportada por canal.

- [x] T026 [US5] PWR 3L: 6/6 eventos fuera de distribución → INCIERTO, 0/100 falsas novedades (ya medido) en `validate_pwr3l_acceptance.py`
- [ ] T027 [US5] Canal lento: evaluar las 14 categorías de NPPAD no entrenadas (FLB, LACP, LLB, LOF, LR, MD, RI, RW, SGATR, SGBTR, SLBIC, SLBOC, SP, TT) y reportar la fracción INCIERTO o respaldo en `shadow_mode.py`
- [ ] T028 [US5] Si la fracción del canal lento es baja, añadir el rechazo por KL como respaldo y repetir en `reject_fallback.py`

## Phase 8: Polish & Cross-Cutting

- [ ] T029 [P] Documentar en `README_FASE5.md` el alcance real, los límites (fusión sin transitorio común, referencia de expertos, brecha del DNBR) y cómo regenerar
- [ ] T030 [P] Actualizar `../../RESULTADOS_IMPLEMENTACION_PWR3L.md` §4 (Fase 5) con el estado nuevo
- [ ] T031 Ejecutar `python -m unittest test_pwr3l test_fase5 -v` y confirmar que las 17 pruebas previas siguen pasando
- [ ] T032 Pasar el resumen de sombra a la feature 006 (tabla de cumplimiento del informe)

## Dependencies & Execution Order

- Las decisiones de diseño ya están tomadas (T000). **T000b** (respuestas de la experta) solo afina valores: el porcentaje de DNBR (T007), el límite de PCT (T008) y la muestra ciega (T022b). Todo el código puede avanzar con umbrales configurables.
- T006b alimenta T007 y T000b: hacerla primero, hoy.
- Foundational (T003–T005) → US1 y US2 en paralelo → US3 → US4 → US5 → Polish.
- T016/T017 son paralelas (archivo distinto de T018).
- US4 necesita US1–US3 para que el log tenga compuertas, rechazo y fusión.

## Implementation Strategy

- **MVP (para el 23 oct)**: T006b, T000b (enviar), T003, T007–T010, T011–T015 y T020/T023/T025 (PWR 3L): compuertas, rechazo y sombra sobre las 106 corridas con log auditable.
- **Incremento**: fusión (US3), sombra de NPPAD y OOD del canal lento (T021, T027, T028).
- **Si el tiempo no alcanza**: declarar como límite lo no hecho en `README_FASE5.md` y en el informe, antes de maquillarlo.
