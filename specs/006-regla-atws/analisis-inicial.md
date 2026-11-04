# Informe de análisis de especificación (inicial)

**Funcionalidad**: `006-regla-atws` (KAN-22) · **Fecha**: 2026-11-04

**Alcance**: `spec.md`, `plan.md` (con `research.md`, `data-model.md` y `contracts/`) y `tasks.md`, contrastados con la constitución v2.0.0 antes de implementar. Análisis de solo lectura; las correcciones van en un commit aparte.

## Hallazgos

| ID | Categoría | Severidad | Ubicación | Resumen | Recomendación |
|----|-----------|-----------|-----------|---------|---------------|
| U1 | Subespecificación | MEDIUM | spec FR-005, research §4 | No se dice qué pasa con un ATWS de entrenamiento **sin demanda** (ni señal ni alto flujo): no tiene flujo en la decisión y no entra en `min(ATWS)`. Si existiera, la regla lo omitiría sin que la calibración lo note. | Calibrar solo con corridas con demanda; contar todo ATWS sin demanda como omisión (también en entrenamiento) y advertirlo en el reporte. Añadirlo a T009 y T014. |
| U2 | Subespecificación | MEDIUM | spec Assumptions; research §1 | En los ATWS el simulador puede no registrar la señal real (R91 no registra «Scram High Prz Level», que sí aparece en su gemela R99). La demanda puede llegar tarde y el tiempo de detección quedar mal medido, sin que se informe. | Declararlo como limitación en el reporte. Informar el tiempo desde la señal que sí se registró, no desde una supuesta. |
| I1 | Inconsistencia | LOW | spec US2 (texto y escenario 1) | Dice «reparto de 002»; desde la renumeración, el reparto es el de 004 (FR-001). | Cambiar a 004. |
| C1 | Cobertura | LOW | SC-006; T010, T014 | El aviso consultivo se prueba en el reporte y en `resumen.json`, pero no en `regla.json`, que también lo lleva según el contrato. | Añadirlo a T010. |
| A1 | Ambigüedad | LOW | research §3 | «Flujo relativo» divide por `PWNT[0]`; no se dice qué pasa si `PWNT[0]` ≤ 0 (no ocurre en el dataset, pero sí podría en datos sintéticos). | Detener con un error que nombre la corrida si `PWNT[0]` ≤ 0. Añadirlo a T009. |

## Cobertura de requisitos

| Requisito | Tareas |
|---|---|
| FR-001 corridas de 002, reparto de 004 | T012, T010, T018 |
| FR-002 señal de disparo | T005, T007, T018 (R97) |
| FR-003 retardo por tipo | T009, T011, T018 (turbina 5 s) |
| FR-004 decisión a 2 s | T009, T011 |
| FR-005 umbral con entrenamiento | T009, T010, T011 |
| FR-006 evaluación por conjunto | T010, T014, T015 |
| FR-007 tiempos y meta | T009, T014, T015 |
| FR-008 recomendación consultiva | T010, T014 |
| FR-009 registro faltante o ilegible | T005, T010 |
| FR-010 reproducible, un comando | T010, T020 |
| SC-001…SC-006 | T010, T014, T018 |

## Constitución

Sin conflictos. Principio I: salida marcada como recomendación. Principio II: calibración solo con entrenamiento (T010 lo comprueba alterando validación y prueba). Principio III: omisiones, falsas alarmas y limitaciones (U2) en el reporte.

## Métricas

- 10 FR · 6 SC · 21 tareas · cobertura 100 %
- Hallazgos: **0 críticos**, 0 altos, 2 medios y 3 bajos

## Resolución

Las cinco recomendaciones se aplican antes de implementar, en el commit `docs(006): correcciones del análisis`. Las aplica el agente por delegación del responsable.
