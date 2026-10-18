# Tasks: Informe técnico final y documentación consolidada

**Input**: Design documents from `/specs/006-informe-final/`

**Prerequisites**: plan.md, spec.md, research.md; feature 005 cerrada (23 oct)

**Tests**: Verificación automática de cifras (`build_tabla_cumplimiento.py`) y lectura por una persona ajena al código.

**Plazo**: 24 oct – 4 nov 2026.

**Rutas**: relativas a `IA-Nuclear/` salvo que se indique otra cosa.

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [ ] T001 Crear `docs/informe/` con los archivos de capítulo vacíos listados en `plan.md`
- [ ] T002 [P] Acordar con la universidad el formato final (PDF/DOCX), la plantilla y el límite de páginas

## Phase 2: Foundational

- [ ] T003 Congelar resultados: ejecutar `python -m unittest test_pwr3l test_fase5 -v` y guardar la fecha y la versión (commit) en `docs/informe/00_resumen.md`
- [ ] T004 Crear `NuclearPowerPlantAccidentData/pipeline/build_tabla_cumplimiento.py` que lea `fase2_output/metrics_fase2.json`, `fase3_output/metrics_fase3.json`, `pwr3l_output/acceptance/acceptance.json`, `fase4_output/metrics_fase4.json` y `fase5_output/shadow_summary.json` y escriba `docs/informe/06_cumplimiento_metas.md` y `docs/informe/cifras.json`

## Phase 3: User Story 1 - Informe técnico final auditable (Priority: P1) 🎯 MVP

**Goal**: Informe completo y entendible sin leer código.
**Independent Test**: lectura por una persona ajena.

- [ ] T005 [US1] Redactar introducción, alcance y arquitectura de dos canales en `docs/informe/01_introduccion_alcance.md`
- [ ] T006 [P] [US1] Redactar la revisión de literatura desde `docs/RSL.docx` y `Articulos/` en `docs/informe/02_revision_literatura.md`
- [ ] T007 [P] [US1] Redactar datos y por qué no se mezclan NPPAD y PWR 3L en `docs/informe/03_datos_dos_plantas.md`
- [ ] T008 [US1] Redactar la metodología (Fases 1–5, normalización relativa, definición del tiempo de detección y mínimo físico de ATWS, ablación de `WLR`, ruido de sensores) en `docs/informe/04_metodologia.md`
- [ ] T009 [US1] Redactar resultados por fase y por canal con figuras (matriz de confusión, curvas DNBR/PCT, línea de tiempo del canal rápido) en `docs/informe/05_resultados.md`
- [ ] T010 [US1] Escribir el anexo de reproducción con comandos y tiempos aproximados en `docs/informe/anexo_reproduccion.md`

## Phase 4: User Story 2 - Metas del plan frente a resultados (Priority: P1)

**Goal**: Tabla de cumplimiento completa y honesta.
**Independent Test**: cada meta tiene fila, definición, resultado, estado y fuente.

- [ ] T011 [US2] Ejecutar `build_tabla_cumplimiento.py` y revisar que cada meta del plan tenga fila (precisión, tiempo, falsos negativos, DNBR/PCT, EOP/XAI, compuertas, sombra)
- [ ] T012 [US2] Escribir la causa y la mitigación de cada meta parcial, no cumplida o no alcanzable en `docs/informe/06_cumplimiento_metas.md`
- [ ] T013 [US2] Incluir la comparación antes / control / ahora con la advertencia de lo que no demuestra en `docs/informe/05_resultados.md`
- [ ] T014 [US2] Reunir las limitaciones de las features 001–005 en `docs/informe/07_limitaciones.md`
- [ ] T015 [US2] Escribir conclusiones y trabajo futuro (incluida la licencia completa de PCTRAN, transitorio común a ambas plantas y validación con otro código) en `docs/informe/08_conclusiones_trabajo_futuro.md`

## Phase 5: User Story 3 - Documentos corregidos y consistentes (Priority: P2)

**Goal**: 4 de 4 correcciones hechas.
**Independent Test**: buscar cada error en los documentos.

- [ ] T016 [P] [US3] Corregir "ventanas de 150 pasos (Δt = 0.05 s)" a Δt = 10 s (NPPAD) y 1 s (PWR 3L) en `docs/planning/plan-de-trabajo1.0.md` (Fase 2)
- [ ] T017 [P] [US3] Definir el tiempo de detección y asignar la meta < 3 s al canal rápido en `docs/planning/plan-de-trabajo1.0.md` (Fase 2)
- [ ] T018 [P] [US3] Corregir "Modelo de planta AP1000" en `docs/Metodologías y preguntas de aclaración.docx` y en `docs/Methodologies and clarification questions.docx` (NPPAD no es AP1000; es un modelo PCTRAN PWR)
- [ ] T019 [P] [US3] Reemplazar el ejemplo de XAI con "Incremento en caudal WLR" por una variable medible (`PRB`) en `docs/planning/plan-de-trabajo1.0.md` (Fase 4) (coordinar con T032 de la feature 004)
- [ ] T020 [US3] Actualizar los números desactualizados en `docs/PLAN_DATASET_PWR3L_DETECCION_RAPIDA.md` (por ejemplo "12 pruebas" → 17) y en `docs/RESUMEN_PWR3L.md` si difieren de `RESULTADOS_IMPLEMENTACION_PWR3L.md`

## Phase 6: User Story 4 - Material de defensa (Priority: P3)

**Goal**: Resumen y presentación coherentes con el informe, ES y EN.
**Independent Test**: 0 cifras distintas.

- [ ] T021 [US4] Redactar el resumen ejecutivo en español y su versión en inglés en `docs/informe/00_resumen.md`
- [ ] T022 [P] [US4] Actualizar la presentación en `docs/avances-presentacion-v3.pptx` (o crear la versión final) con las cifras de `cifras.json`
- [ ] T023 [P] [US4] Escribir la guía breve de consolas (casos `#vivo:R13`, `#vivo:R49`, `#vivo:R56`, `#vivo:R64`, `#mejora`) en `docs/informe/anexo_reproduccion.md`

## Phase 7: Polish & Cross-Cutting

- [ ] T024 Verificar que 0 cifras del informe, resumen y presentación carezcan de entrada en `docs/informe/cifras.json`
- [ ] T025 Pedir una lectura a una persona ajena al código y registrar las preguntas que no pudo responder con el informe
- [ ] T026 Exportar el documento final al formato acordado (T002) y guardarlo en `docs/informe/`
- [ ] T027 Resolver la justificación bibliográfica del ruido de sensores (tarea T040 de la feature 003) antes de cerrar el capítulo 4

## Dependencies & Execution Order

- Feature 005 cerrada → T003 → T004 → T011.
- T005–T010 (US1) pueden empezar en paralelo con T004 salvo T009, que necesita los resultados congelados.
- US2 depende de T004 y de T009.
- US3 es independiente del resto y puede hacerse antes del 24 oct.
- US4 depende de US1 y US2.

## Implementation Strategy

- **MVP**: US1 + US2 (informe con tabla de cumplimiento) antes del 4 de noviembre.
- **Adelantable**: US3 (correcciones de documentos) no depende de la Fase 5; puede hacerse esta semana.
- **Riesgo**: si la feature 005 no cierra, el informe declara lo no hecho como límite; no se reformulan las metas.
