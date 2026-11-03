# Informe de análisis de especificación (inicial)

**Funcionalidad**: `005-clasificador-etapa1`

**Fecha**: 2026-11-03

**Alcance**: `spec.md`, `plan.md` y `tasks.md` contrastados con la constitución v2.0.0, antes de `/speckit-implement`. Análisis de solo lectura; las correcciones aprobadas se aplican en un commit aparte.

## Hallazgos

| ID | Categoría | Severidad | Ubicación | Resumen | Recomendación |
|----|-----------|-----------|-----------|---------|---------------|
| U1 | Subespecificación | MEDIUM | spec FR-005, FR-009; research §3, §6 | k = τ − inicio solo es entero si el inicio lo es: con un inicio fraccionario ninguna muestra tendría k = h. Tampoco se dice si τ = inicio cuenta como evento cuando el inicio cae a mitad de segundo. | Redondear el inicio hacia arriba al segundo entero (`ceil`) antes de etiquetar y calcular k; probarlo en T006. |
| U2 | Subespecificación | LOW | spec SC-001; research §6; T019(g) | Si el conjunto de prueba no tuviera LOCA de 50 cm² o más, SC-001 no sería evaluable. | Informar la meta como «sin datos»; añadirlo a T019(g). |
| C1 | Hueco de cobertura | LOW | spec FR-015 | Ninguna prueba comprueba que el origen no cambia. | En T029, hash del origen antes y después. |
| C2 | Hueco de cobertura | LOW | contracts/cli.md (código 3); T013 | El código 3 (sin PyTorch) no tiene prueba. | Añadir a T013 la simulación de la falta de PyTorch. |
| A1 | Ambigüedad | LOW | spec SC-005; research §5 | El alcance de «mismas métricas» no está acotado (versión de PyTorch, hilos). | Misma máquina, misma versión de PyTorch y mismos hilos; registrar la versión en `modelo.json`. |
| T1 | Terminología | LOW | spec frente a plan y data-model | «Transitorio con disparo» y la etiqueta `TRANS` no se relacionan en la spec. | Presentar la etiqueta en Key Entities. |

## Cobertura de requisitos

| Requisito | ¿Tarea? | Tareas | Notas |
|---|---|---|---|
| FR-001 tres familias | Sí | T004, T008, T012 | |
| FR-002 reparto 004 + verificación | Sí | T006, T013, T017 | |
| FR-003 26 variables escaladas solo con entrenamiento | Sí | T013, T017 | |
| FR-004 ventana de 30 s | Sí | T006, T010 | |
| FR-005 etiqueta según el inicio | Sí | T006, T010 | Véase U1 |
| FR-006 pesos de clase | Sí | T012, T016 | |
| FR-007 determinismo | Sí | T012, T013, T031 | Véase A1 |
| FR-008 parada por validación | Sí | T012, T016 | |
| FR-009 métricas y horizontes | Sí | T019, T022 | Véase U1 |
| FR-010 tiempo de confirmación | Sí | T019, T022 | |
| FR-011 falsas alarmas | Sí | T019, T022 | |
| FR-012 artefactos | Sí | T013, T017, T020, T023 | |
| FR-013 clasificación consultiva | Sí | T025, T027 | |
| FR-014 evento sin inicio | Sí | T005, T013 | |
| FR-015 sin modificar origen ni usar NPPAD | Parcial | — | Véase C1 |
| SC-001 a SC-007 | Sí | SC-001–003: T019, T031; SC-004: T020; SC-005: T012, T013, T031; SC-006: T031; SC-007: T006, T013 | |

## Alineación con la constitución

Sin conflictos. I: salida consultiva con aviso. II: reparto de 004 verificado, escalado solo con entrenamiento, ventana causal, prueba reservada. III: definiciones exactas y metas informadas aunque no se cumplan. IV: solo PWR 3L. V: familias LOCA y transitorio con disparo; OOD fuera.

## Métricas

- Requisitos: 22 (15 FR, 7 SC). Tareas: 32.
- Cobertura: 100 %; FR-015 parcial.
- Ambigüedades: 1. Duplicaciones: 0. Críticos: 0 (1 MEDIUM, 5 LOW).

## Decisión

Sin problemas CRITICAL. El responsable aprobó de forma explícita aplicar los 6 hallazgos antes de implementar.
