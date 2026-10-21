# Auditoría de especificación — `/speckit-analyze`

**Feature**: 005-compuertas-modo-sombra
**Fecha**: 2026-10-20
**Artefactos revisados**: `spec.md`, `plan.md`, `tasks.md`, `research.md`, `data-model.md`, `contracts/shadow-log.md`, `quickstart.md`, `checklists/requirements.md` y `.specify/memory/constitution.md` (v1.0.0)
**Modo**: solo lectura sobre las specs. Este archivo es el único agregado.
**Sesión de métricas**: fase `analizar`, herramienta `claude-code`, modelo `claude-sonnet-5-5`.

## Specification Analysis Report

| ID | Categoría | Severidad | Ubicación | Resumen | Recomendación |
|----|-----------|-----------|-----------|---------|---------------|
| I1 | Inconsistencia / Constitución IV | HIGH | `spec.md` L127 (FR-012) vs L116 (FR-002) | FR-012 exige compuertas "independientes del estado de los modelos", pero la compuerta de DNBR (FR-002) se alimenta con la estimación de la FNN-SELU. La lógica es determinista, pero su entrada es estadística. | Reformular FR-012 ("la lógica de la compuerta es determinista y no importa modelos; si la estimación de la FNN no está disponible o no es fiable, la compuerta se degrada a *no evaluable* y lo informa") y añadir una prueba en `tasks.md`. |
| A1 | Ambigüedad | HIGH | `spec.md` L34, L118 (FR-003) | Límite de PCT sin valor ni escala (`[NEEDS CLARIFICATION]`). Requisito no verificable y SC-001 depende de él. | Cerrar con T000b (experta). Mientras tanto, dejar el umbral configurable y marcar FR-003 como "provisional". |
| U1 | Subespecificación | MEDIUM | `spec.md` L116 (FR-002) | "Porcentaje configurable" sin valor por defecto ni rango; depende de T006b/T000b. | Fijar un valor provisional en el plan una vez exista la tabla de T006b. |
| C1 | Cobertura | MEDIUM | `spec.md` L127 (FR-012) | Ninguna tarea verifica la independencia de modelos (p. ej. que `safety_gates.py` y `reject_fallback.py` no importen PyTorch/scikit-learn). | Añadir a `tasks.md` una prueba de importaciones en `test_fase5.py`. |
| O1 | Orden de tareas | MEDIUM | `tasks.md` L18 (T000b) vs L37 (T006b) | T000b (Fase 0) usa la salida de T006b (Fase 3). Dependencia hacia adelante. | Mover T006b a Fase 1 o 2, o mover T000b después de ella. |
| T1 | Herramientas / Alcance | HIGH | `plan.md` (estructura de código), `tasks.md` L11 | El código nuevo va en el repositorio `IA-Nuclear`, pero Spec Kit y `speckit-metricas` están en `gestion_proyectos`. La extensión solo cuenta commits de su propio repositorio, así que las líneas de código de la iteración no se medirían. | Decidir dónde viven los módulos nuevos de la iteración (ver Next Actions). |
| K1 | Constitución (flujo) | MEDIUM | `constitution.md`, sección Flujo de Desarrollo | La extensión de métricas exige commits con ámbito `feat(005):` y trailer `Causa:`; la constitución solo dice "commits pequeños y descriptivos". | Enmendar la constitución a v1.1.0 con la convención de commits. |
| N1 | Inconsistencia de IDs | LOW | `spec.md` L117 (FR-002b), L146–148 (SC-008 entre SC-005 y SC-006) | Numeración irregular. | Renumerar (FR-003…, SC en orden). |
| N2 | Redundancia | LOW | `spec.md` L50 vs L121; `tasks.md` L51 | La lista de setpoints (132.2, 118.1, 1.30, 17 %…) está repetida en tres sitios. | Dejarla en una sola fuente (`research.md` D6) y referenciarla. |
| N3 | Estado mezclado | LOW | `spec.md` L32, L48, L81, L154–155 | Escenarios y supuestos incluyen estado de implementación ("ya implementada", "falta…"). Contamina una spec que debe decir qué y por qué. | Mantener el estado solo en `tasks.md`. |
| D1 | Desactualizado | LOW | `tasks.md` L9 ("Hoy: 18 oct"), `spec.md` L153 ("quedan 5 días hábiles") | Hoy es 20 oct; quedan 3 días hábiles hasta el 23 oct. | Actualizar y revisar el alcance del MVP. |
| U2 | Subespecificación | LOW | `tasks.md` L22 (T001) | No indica en qué carpeta va `README_FASE5.md`. | Indicar `pipeline/`. |
| R1 | Riesgo de plazo | MEDIUM | `tasks.md` L103 (MVP) | El MVP de 18 tareas en 3 días hábiles, con T000b dependiendo de la experta, es optimista. | Reducir el MVP (ver Next Actions). |

## Coverage Summary Table

| Requisito | ¿Tiene tarea? | Tareas | Notas |
|---|---|---|---|
| FR-001 compuerta ATWS | Sí | T003, T006 | T006 ya hecha; T003 la extrae a módulo |
| FR-002 compuerta DNBR relativa | Sí | T006b, T007, T010 | Depende de la experta para el valor |
| FR-002b no activar con estimación no fiable | Sí | T007, T009 | |
| FR-003 compuerta PCT | Sí | T008 | Bloqueada por A1 |
| FR-004 rechazo por confianza | Sí | T011, T015 | |
| FR-005 rechazo por KL | Sí | T004, T012 | |
| FR-006 respaldo < 1 s | Sí | T014, T015, T024 | |
| FR-007 fusión de canales | Sí | T016, T017, T018 | |
| FR-008 modo sombra con log | Sí | T005, T020, T021, T023, T025 | |
| FR-009 comparación con referencia | Sí | T022, T022b | |
| FR-010 OOD en ambos canales | Sí | T026, T027, T028 | |
| FR-011 declarar limitación de fusión | Sí | T029 | |
| FR-012 independencia de modelos | Parcial | T003, T014 | Sin prueba (C1) |
| SC-001…SC-008 | Sí | T010, T006, T015, T025, T022, T027, T018, T006b | |

## Constitution Alignment Issues

- **Principio IV**: tensión entre una compuerta "determinista" y su entrada estimada por IA (I1). No es una violación directa, pero hay que reformular.
- **Principio II**: T012 (KL) y T020/T021 (sombra) deben usar solo ventanas pasadas. El plan lo dice; añadir una prueba de causalidad.
- **Principios I, III, V, VI**: sin conflicto.

## Unmapped Tasks

T001, T002 (preparación), T019 (opcional, sin requisito propio), T030, T031 y T032 (transversales). Ninguna es problemática.

## Metrics

| Métrica | Valor |
|---|---|
| Requisitos totales (FR + SC) | 21 (13 FR + 8 SC) |
| Tareas totales | 36 (3 hechas, 33 abiertas) |
| Cobertura (requisitos con ≥ 1 tarea) | 100 % (21/21), 1 parcial |
| Ambigüedades | 2 (A1, U1) |
| Duplicaciones | 1 (N2) |
| Issues CRITICAL | 0 |
| Issues HIGH | 3 (I1, A1, T1) |

## Next Actions

No hay CRITICAL. Se puede avanzar, pero conviene resolver antes de `/speckit-implement`:

1. **T1 (decidir dónde va el código de la iteración).** Para que la medición de tiempo y de líneas refleje la implementación, opciones: (a) poner los módulos nuevos de la Fase 5 en `gestion_proyectos/src/fase5/` importando el pipeline de `IA-Nuclear`; (b) instalar la extensión también en `IA-Nuclear`. Recomendada: (a).
2. **I1**: reformular FR-012 y añadir la prueba de importaciones (C1).
3. **O1**: reordenar T006b.
4. **K1**: enmendar la constitución con la convención de commits.
5. **R1**: reducir el MVP a T001–T003, T006b, T007–T010 (historia 1) para el 23 oct.

Comandos sugeridos: edición manual de `spec.md` y `tasks.md` (I1, O1, N1), luego `/speckit-implement`.
