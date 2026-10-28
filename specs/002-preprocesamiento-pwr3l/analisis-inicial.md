# Informe de análisis de especificación (inicial)

**Funcionalidad**: `002-preprocesamiento-pwr3l` (KAN-18)

**Fecha**: 2026-10-28

**Alcance**: `spec.md`, `plan.md` (con `research.md`, `data-model.md` y `contracts/`) y `tasks.md`, contrastados con la constitución v2.0.0 antes de `/speckit-implement`. Análisis de solo lectura: este informe no modificó ningún archivo. Las correcciones se aplicaron después en un commit aparte (ver «Resolución»).

## Hallazgos

| ID | Categoría | Severidad | Ubicación | Resumen | Recomendación |
|----|-----------|-----------|-----------|---------|---------------|
| U1 | Subespecificación | MEDIUM | contracts/cli.md (causa «no hay corridas de la clase»); spec FR-014; tasks T006, T025 | El contrato lista una causa de error que no está en la spec ni en las tareas. No se dice qué pasa si una clase de entrenamiento no tiene ninguna corrida en el origen, ni si todas sus corridas son cortas. | Clase sin ninguna corrida descubierta → error (el origen está incompleto). Clase con corridas pero todas cortas → sigue, con la fila en cero y advertencias. Añadirlo a FR-014, T006 y T025. |
| U2 | Subespecificación | MEDIUM | research §7; tasks T006, T031 | La tabla fija de gemelas es la fuente, pero si el `config.json` de una corrida automática declara otra gemela (o una que la tabla no tiene) nada lo detecta salvo la prueba con datos reales. Una pareja nueva añadida al dataset quedaría sin agrupar y podría repartirse entre dos conjuntos (principio II). | En el descubrimiento, comparar `gemelo_de` de cada `config.json` con la tabla y detenerse con un error si no coinciden. Añadir el caso a FR-014 y T006. |
| A1 | Ambigüedad | MEDIUM | spec FR-007 («reparto cercano a 70 % / 15 % / 15 %»); tasks T013 | «Cercano» no tiene medida. T013 fija ±1 grupo solo para grupos de tamaño 1; con el grupo de 2000 cm² (8 corridas) no hay criterio. | Precisar en FR-007 la regla (grupos completos al conjunto con mayor déficit, por familia; research §8) y en T013 la medida: cada conjunto queda a menos del tamaño del grupo más grande de su meta. |
| C1 | Hueco de cobertura | LOW | spec FR-016 (salida separada de NPPAD); tasks T015 | Ninguna prueba comprueba que los valores por defecto apuntan a `data_processed_pwr3l` y a `PWR 3L`, y no a la salida o al origen de 001. | Añadir a T015 la comprobación de los valores por defecto. |
| C2 | Hueco de cobertura | LOW | spec Edge Cases (re-ejecución sin restos); tasks T015 | Se prueba que dos ejecuciones dan lo mismo, pero no que una salida previa con un archivo ajeno lo conserve y que los artefactos viejos se reemplacen. | Añadir ese caso a T015 (la función `publicar` ya se probó en 001; aquí se prueba su uso). |
| D1 | Riesgo de datos | LOW | spec Assumptions; research §7 | Varias corridas NORM repiten el mismo rechazo de carga en distinta condición inicial (p. ej. R35 y R33, 10 %). No son «emparejadas» en el sentido del principio II (no hay un mismo escenario con y sin accidente), pero se parecen y pueden caer en conjuntos distintos. | Declararlo en las limitaciones del reporte. |
| I1 | Inconsistencia | LOW | plan.md, Technical Context | Dice pandas 3.0; el entorno instalado tiene pandas 3.1.0 y scikit-learn 1.9.1. | Corregir las versiones. |
| T1 | Terminología | LOW | spec («corrida») frente a la entrada y Jira («simulaciones») | Dos nombres para lo mismo. | Anotar una vez en la spec que corrida = simulación. |

## Cobertura de requisitos

| Requisito | ¿Tarea? | Tareas | Notas |
|---|---|---|---|
| FR-001 descubrir y leer sin modificar | Sí | T006, T007, T009, T010, T015, T031 | |
| FR-002 clase por carpeta, etiquetas 0–4 | Sí | T006, T008, T009, T015 | |
| FR-003 OOD sin muestras y listadas | Sí | T006, T015, T025, T031 | |
| FR-004 descartadas documentadas | Sí | T006, T008, T025, T031 | |
| FR-005 una muestra de 300 pasos | Sí | T007, T010, T015, T019 | |
| FR-006 cortas excluidas con aviso | Sí | T007, T010, T025, T031 | |
| FR-007 cada corrida en un conjunto | Sí | T013, T017, T015 | Véase A1 |
| FR-008 emparejadas juntas | Sí | T012, T016, T015, T031 | Véase U2 |
| FR-009 26 entradas medibles, sin WLR | Sí | T008, T019, T015 | |
| FR-010 escalado solo con train | Sí | T014, T018, T015 | |
| FR-011 márgenes sin escalar | Sí | T022, T023 | |
| FR-012 reporte | Sí | T025, T026, T027 | |
| FR-013 advertencias visibles | Sí | T025, T027 | |
| FR-014 archivo defectuoso detiene | Sí | T006, T007, T010, T015 | Véase U1 |
| FR-015 reproducibilidad | Sí | T013, T015 | |
| FR-016 un comando, salida propia | Parcial | T020, T032, T033 | Véase C1 |
| SC-001 a SC-008 | Sí | SC-001: T013, T015; SC-002: T012, T015, T031; SC-003: T014, T015; SC-004: T022; SC-005: T025, T026, T031; SC-006: T015; SC-007: T015, T031; SC-008: T033 | |

## Alineación con la constitución

Sin conflictos. Principio II: la partición por grupos y el escalador de entrenamiento están en la spec, el plan y las tareas (U2 refuerza la detección de parejas). Principio III: corridas cortas excluidas sin rellenar, exclusiones y limitaciones en el reporte. Principio IV: paquete, comando y salida propios; origen de solo lectura con prueba de hash. Flujo: pruebas antes de implementar en cada historia.

## Tareas sin requisito

Ninguna: T001–T004 (setup), T011/T021/T024/T030/T034 (ejecutar pruebas) y T032/T033 (documentación y quickstart) dan soporte a FR-016 y al flujo de la constitución.

## Métricas

- Requisitos funcionales: 16 · Criterios de éxito: 8 · Tareas: 34
- Cobertura (requisitos con al menos una tarea): 100 % (FR-016 parcial)
- Ambigüedades: 1 · Duplicaciones: 0 · Subespecificaciones: 2
- Hallazgos críticos: **0** · altos: 0 · medios: 3 · bajos: 5

## Siguientes acciones

Sin hallazgos críticos ni altos: se puede implementar. Se recomienda resolver antes U1, U2 y A1 (medios) y, de paso, los bajos.

## Resolución

El responsable delegó en el agente la ejecución completa de la iteración, así que el agente aplicó las ocho recomendaciones **antes** de implementar, en un commit propio (`docs(002): correcciones del análisis`), para que quede separado del informe y del código:

| Hallazgo | Cambio |
|---|---|
| U1 | FR-014 añade «una clase de entrenamiento sin ninguna corrida en el origen»; FR-013 y el caso límite cubren la clase con todas sus corridas cortas; T006 y T025 los prueban. |
| U2 | FR-014 añade «la gemela declarada en `config.json` no coincide con la tabla»; research §7 y T006/T009 lo incorporan. |
| A1 | FR-007 describe la regla de reparto; T013 fija la medida (desvío menor que el grupo más grande). |
| C1, C2 | T015 comprueba los valores por defecto y la re-ejecución sobre una salida previa con un archivo ajeno. |
| D1 | Nueva limitación en la spec (Assumptions) y en el reporte (T027). |
| I1 | plan.md: pandas 3.1, scikit-learn 1.9. |
| T1 | Nota de terminología en la spec. |
