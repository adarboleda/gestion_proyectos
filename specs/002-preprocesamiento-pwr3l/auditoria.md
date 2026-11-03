# Auditoría de la funcionalidad `002-preprocesamiento-pwr3l` (KAN-18)

**Fecha**: 2026-11-03 · **Rama**: `002-preprocesamiento-pwr3l` · **Constitución**: v2.0.0

Reúne el análisis previo a la implementación (`/speckit-analyze`, ver [analisis-inicial.md](analisis-inicial.md)) y las pasadas de `/speckit-converge` posteriores.

## 1. Resumen

| Momento | Resultado |
|---|---|
| `/speckit-analyze` (antes de implementar) | 8 hallazgos: 0 críticos, 3 medios, 5 bajos; cobertura 100 %; sin conflictos con la constitución |
| Correcciones del análisis | Las 8 aplicadas antes de programar, en un commit propio (`73c553e`) |
| `/speckit-converge`, 1.ª pasada | 4 hallazgos → tareas T035–T038, implementadas (`d45af77`) |
| `/speckit-converge`, 2.ª pasada | **converged**: 0 hallazgos, `tasks.md` sin cambios |
| Tareas | 38/38 |
| Pruebas de 002 | 102, todas verdes (incluye la carpeta real) |

## 2. Cobertura de requisitos

| Requisito | Tareas | Pruebas (archivo: casos) |
|---|---|---|
| FR-001 descubrir y leer sin modificar | T006, T007, T009, T010, T015, T031 | descubrimiento: carpetas manuales y auto; lectura: CSV y xlsx; cli y real: hash del origen sin cambios |
| FR-002 clase por carpeta, etiquetas 0–4 | T006, T008, T009 | descubrimiento: clase por carpeta y sufijo, etiquetas |
| FR-003 OOD sin muestras y listadas | T006, T025, T031 | descubrimiento, reporte, cli, real (6 OOD) |
| FR-004 descartadas documentadas | T006, T008, T025, T031 | descubrimiento (R07, R27 con dos archivos), reporte (motivo), real (R07, R27, R28) |
| FR-005 una muestra de 300 pasos | T007, T010, T019 | lectura (filas 0–299, 300 filas exactas), cli (forma (N, 300, 26)) |
| FR-006 cortas excluidas con aviso | T007, T010, T025, T031 | lectura (295 filas), reporte (advertencia con archivo y filas), real (9 cortas) |
| FR-007 cada corrida en un conjunto, ≈ 70/15/15 | T013, T017 | particion: grupos de tamaño 1, cota del grupo más grande, por familia, semilla |
| FR-008 emparejadas juntas | T012, T016, T015, T031 | grupos (gemelas, áreas, gemela corta), cli y real (restricciones de grupo) |
| FR-009 26 entradas medibles, sin WLR | T008, T019 | lectura (`WLR`, `PWR` fuera), cli (26 columnas) |
| FR-010 escalado solo con train | T014, T018, T015 | escalado (5 casos), cli (media = filas de train) |
| FR-011 márgenes sin escalar | T022, T023 | margenes: CSV y xlsx idénticos al archivo, forma, fuera del escalador |
| FR-012 reporte | T025–T027 | reporte (9 secciones, grupos, exclusiones, limitaciones), cli (metadata.json) |
| FR-013 advertencias visibles | T025, T027 | reporte (cortas, celdas en cero, clase sin usables) |
| FR-014 defectos detienen | T006, T007, T010, T037, T038 | descubrimiento (10 causas), lectura (variable, texto, vacío, inf, tiempo, xlsx, ilegible, defecto tras la fila 300), cli (código 1 sin salida; sin usables) |
| FR-015 reproducible | T013, T015 | particion (semilla, orden de entrada), cli (byte a byte) |
| FR-016 un comando, salida propia | T020, T032, T033 | cli (`python -m`, valores por defecto), quickstart con la carpeta real |
| SC-001…SC-008 | — | SC-001/002: cli y real; SC-003: escalado y cli; SC-004: margenes; SC-005: reporte y real (109 = 91 + 9 + 3 + 6); SC-006: cli; SC-007: cli y real; SC-008: quickstart |

## 3. Hallazgos de converge

| ID | Tipo | Hallazgo | Tarea | Resolución |
|---|---|---|---|---|
| G1 | partial | `data-model.md` decía que solo R27 guarda la carpeta como `archivo`; el código lo hace con todas las descartadas y OOD | T035 | Documento corregido |
| G2 | partial | El contrato de la CLI no nombraba dos causas que el código produce (`el archivo no existe`, `no hay corridas usables`) | T036 | Contrato corregido |
| G3 | partial | La rama de `config.json` ilegible no tenía prueba | T037 | Prueba añadida |
| G4 | unrequested | La rama «no hay corridas usables» de `cli.py` no tenía prueba | T038 | Prueba añadida |

## 4. Decisiones sin aprobación explícita

- Las tres respuestas de `/speckit-clarify` (cortas excluidas, igual severidad = área, OOD solo listadas) las eligió el agente con la opción recomendada, por delegación. Están anotadas en la spec.
- Las 8 correcciones del análisis se aplicaron sin una aprobación aparte, pero en un commit propio y documentado (a diferencia de 001, donde se aplicaron dentro de la implementación).

## 5. Incidencias durante la implementación

- Una prueba de lectura de xlsx comparaba con el generador del árbol sintético en lugar de con el archivo: openpyxl guarda 16 cifras significativas (diferencia ~6e-14). Se corrigió la prueba, no el código (`bf3dcad`, `Causa: defecto`).
- La implementación se detuvo una vez en la fase 2 a pedido del responsable y se retomó después; no hubo cambios de alcance.

## 6. Pendientes y aceptados

- La tabla de gemelas y la lista de descartadas son fijas en `config.py`; una corrida nueva con gemela declarada distinta detiene la preparación (control U2), pero una gemela nueva sin `gemelo_de` en `config.json` (como las manuales) debe añadirse a mano a la tabla.
- La señal de demanda de disparo y el etiquetado paso a paso no son parte de esta funcionalidad (los usan KAN-22 y KAN-23).
