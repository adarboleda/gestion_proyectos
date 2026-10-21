# Auditoría de la funcionalidad 001-preparacion-datos

**Fecha**: 2026-10-20

**Rama**: `001-preparacion-datos`

**Fuentes**: [analisis-inicial.md](analisis-inicial.md) (`/speckit-analyze`), dos pasadas de `/speckit-converge`, el código y las pruebas del repositorio. No se ejecutó un segundo `/speckit-analyze`; la verificación posterior a la implementación la hicieron las dos pasadas de converge.

## 1. Resumen

- El análisis inicial (antes de implementar) encontró **9 hallazgos**: 0 críticos, 3 MEDIUM y 6 LOW, con cobertura del 100 % de los requisitos (FR-009 parcial).
- Durante la implementación se aplicaron **sin aprobación explícita** las correcciones U1, I1, C1, C2 y A1 (más I2 y U2, ver §4). Nadie respondió a la oferta de remediación del análisis; la implementación siguió adelante y resolvió esos puntos sobre la marcha. **I1 y C1 se resolvieron de forma distinta a la propuesta** (ver §4.1).
- La primera pasada de `/speckit-converge` encontró **5 hallazgos** (1 MEDIUM, 4 LOW) y anexó **5 tareas** (T035–T039), que se implementaron. La segunda pasada dio **«converged»** con 0 hallazgos y sin tocar `tasks.md`.
- Estado final: **39 de 39 tareas completadas**, **79 pruebas verdes** (incluida una con el dataset NPPAD real), y 11 commits de esta funcionalidad sobre la base del proyecto (el árbol de trabajo estaba limpio antes de crear este documento).
- Quedan **2 hallazgos aceptados sin cambio** (C3 e I3) y algunas diferencias menores de redacción (§8).

## 2. Cobertura de requisitos (estado final)

| Requisito | Tareas | Pruebas que lo verifican |
|---|---|---|
| FR-001 leer sin modificar el origen | T008, T012, T032 | `test_lectura` (descubrimiento), `test_cli::test_los_csv_de_origen_no_cambian`, `test_dataset_real` |
| FR-002 una muestra de 150 pasos por simulación | T008, T016 | `test_lectura` (serie 150×19), `test_cli` (formas y tipos), `test_cli_reporte` (metadata) |
| FR-003 simulaciones completas, sin repetirse | T010, T014 | `test_particion::test_ninguna_simulacion_aparece_en_mas_de_un_conjunto` |
| FR-004 LOCA/LOCAC de igual severidad juntas | T010, T014 | `test_particion` (emparejamiento y severidad en una sola clase) |
| FR-005 12 variables de planta | T007, T016 | `test_cli` (forma `(N,150,12)`), `test_margenes` (alineación) |
| FR-006 escalado solo con entrenamiento | T011, T015 | `test_escalado` (parámetros de entrenamiento, invariancia ante validación/prueba) |
| FR-007 Normal y ATWS completas a entrenamiento | T010, T012, T014 | `test_particion`, `test_cli::test_normal_y_atws_aparecen_solo_en_entrenamiento` |
| FR-008 márgenes sin escalar y alineados | T019, T021 | `test_margenes` (4 pruebas, comparación exacta con el CSV) |
| FR-009 reporte con conteos, simulaciones y limitaciones | T023, T026–T028 | `test_reporte`, `test_cli_reporte` |
| FR-010 advertencias de clases con una simulación y celdas en cero | T023, T026 | `test_reporte` (advertencias, `0*`) |
| FR-011 reproducibilidad | T012 | `test_cli::test_dos_ejecuciones_producen_archivos_identicos`, `test_particion` (semilla) |
| FR-012 archivo defectuoso detiene sin escribir | T006, T008, T012, T039 | `test_lectura` (defectos en cualquier fila), `test_cli` (defectuoso, salida previa intacta), `test_salida` |
| FR-013 una ejecución documentada | T017, T031, T037 | `test_cli::test_python_m…`, README y quickstart |
| SC-001 0 simulaciones en dos conjuntos | T010, T012 | `test_particion`, validación 2 del quickstart |
| SC-002 parámetros de escala solo de entrenamiento | T011 | `test_escalado`, validación 3 del quickstart |
| SC-003 márgenes idénticos al CSV | T019 | `test_margenes`, validación 4 |
| SC-004 suma de conteos = total; 4 clases × 3 conjuntos | T023 | `test_reporte` |
| SC-005 100 % de clases de una simulación y celdas en cero con advertencia | T023, T026 | `test_reporte` |
| SC-006 ejecuciones idénticas | T012 | `test_cli` |
| SC-007 origen sin cambios | T012, T030 | `test_cli`, `test_dataset_real` |
| SC-008 una ejecución sin pasos manuales | T017, T031 | README, quickstart, `test_dataset_real` |

Pruebas por archivo (79 en total): `test_lectura` 15, `test_particion` 12, `test_escalado` 6, `test_reporte` 11, `test_salida` 11, `test_cli` 13, `test_cli_reporte` 6, `test_margenes` 4, `test_dataset_real` 1.

Resultado con el dataset real: 142 muestras de entrenamiento (70 LOCA, 70 LOCAC, 1 Normal, 1 ATWS), 30 de validación y 30 de prueba; la comparación con la referencia del proyecto previo da `COINCIDE` para LOCA y LOCAC; los 202 archivos pasan la validación completa.

## 3. Hallazgos del análisis inicial y su resolución

| ID | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| U1 | MEDIUM | Publicación sobre una salida existente: el reemplazo de la carpeta completa no es posible si no está vacía y destruiría archivos ajenos. | **Aplicado en la implementación sin aprobación.** `publicar` reemplaza solo los artefactos publicados, archivo por archivo, sin tocar otros. Prueba: `test_cli::test_salida_previa_se_reemplaza_sin_tocar_archivos_ajenos`. `research.md` §8 se reescribió. Esta solución dejó abierta la brecha de «todos o ninguno», cerrada después por converge (F1 → T035). |
| I1 | MEDIUM | SC-003 exige igualdad exacta; el lector de pandas puede diferir 1 ulp de `float()`. | **Aplicado sin aprobación y de forma distinta a la propuesta** (ver §4.1). |
| C1 | MEDIUM | FR-009 pide la lista de simulaciones por conjunto, ausente del reporte impreso. | **Aplicado sin aprobación y de forma distinta a la propuesta** (ver §4.1). |
| C2 | LOW | Faltaba probar que las variables sin varianza se informan en el reporte y en `metadata.json`. | **Aplicado sin aprobación.** Prueba `test_reporte::test_variables_sin_varianza_se_informan_en_reporte_y_metadata`. El texto de T023 en `tasks.md` no se editó. |
| A1 | LOW | «Cercana a 0/1» y «tolerancia de float32» sin valores. | **Aplicado sin aprobación.** Las pruebas usan tolerancia absoluta de 1e-5 para media y desviación, y `rtol=1e-5` con `atol=1e-5` en la reconstrucción. Con `rtol` solo la prueba de alineación falló en un valor casi cero (diferencia de 1e-7), por lo que se añadió `atol`. El texto de T011, T019 y del quickstart conserva «cercana a». |
| C3 | LOW | La comparación con la referencia no tiene FR/SC en la spec. | **Aceptado, sin cambio.** La comparación está implementada porque la pide el plan; la spec no se modificó. |
| I2 | LOW | El árbol de pruebas del plan omitía tres archivos de pruebas. | **Aplicado sin aprobación** (no figuraba entre los cinco listados): `plan.md` actualizado. Después se añadió `test_salida.py` y el árbol no se volvió a actualizar (§8). |
| I3 | LOW | Normal / NORM / operación normal para el mismo concepto. | **Aceptado, sin cambio.** La spec no se modificó; el mapeo carpeta → clase → etiqueta está en `config.py` y `data-model.md`. |
| U2 | LOW | Alcance de la fixture del dataset sintético. | **Aplicado sin aprobación** (tampoco figuraba entre los cinco): `conftest.py` crea el dataset una vez por sesión y entrega una copia por prueba. |

## 4. Decisiones tomadas sin aprobación explícita

La oferta de remediación del análisis («¿quieres que proponga las ediciones para U1, I1 y C1?») no tuvo respuesta; la siguiente orden fue `/speckit-implement`, y las correcciones se aplicaron dentro de esa implementación. Esto es lo que se decidió sin consultar:

- **U1, I1, C1, C2 y A1**, como se describe en §3.
- **I2 y U2**, también aplicados.
- **C1 y los textos del plan:** además de cambiar el código se reescribió `contracts/cli.md` y se cambió «7 secciones» por «8 secciones» en T024 y T026.
- **U1 y `research.md`:** se reescribió §8 y se añadió §12.
- **T039:** la tarea ofrecía dos caminos (validar el archivo completo, o aclarar la spec). Se eligió validar el archivo completo, sin consultar, y se actualizaron `research.md` §4 y `data-model.md`.
- **T038:** la tarea ofrecía justificar o eliminar la tolerancia de consola. Se eligió conservarla y justificarla.

### 4.1 I1 y C1: qué se propuso y qué se hizo

**I1.** Propuesta: fijar `float_precision="round_trip"` en la lectura de pandas (T008) y que la prueba de márgenes (T019b) compare contra una lectura con `csv` y `float()`.
Aplicado: la lectura no usa el parámetro de pandas; lee todo como texto (`dtype=str`) y convierte cada valor con `float()` de Python, de modo que la conversión es la misma que la de la lectura independiente de la prueba. La prueba sí compara contra `csv` + `float()`, como se proponía. El resultado es una igualdad exacta en los 202 archivos reales.

**C1.** Propuesta: dos alternativas excluyentes, «añadir la lista al reporte impreso» o «precisar en FR-009 que `metadata.json` es la forma persistente del reporte», dejando la decisión al usuario.
Aplicado: se eligió la primera, añadiendo la sección «Simulaciones por conjunto» (el reporte pasó de 7 a 8 secciones, con las simulaciones agrupadas por clase), y se extendió más allá de lo propuesto al reescribir `contracts/cli.md` y los textos de T024 y T026. La spec no se modificó. La lista sigue también en `metadata.json`.

## 5. Hallazgos de `/speckit-converge`

**Primera pasada** (después de implementar T001–T034):

| ID | Tipo | Sev. | Hallazgo | Tarea | Commit |
|---|---|---|---|---|---|
| F1 | partial | MEDIUM | `publicar` mueve archivo por archivo: un fallo a mitad dejaba la salida mezclada, contra el contrato «todos juntos o ninguno». | T035 | `96ca897` |
| F2 | unrequested | LOW | La lectura exigía nombre numérico también a Normal y ATWS. | T036 | `ec7ae0c` |
| F3 | partial | LOW | `python -m preparacion_datos` sin prueba automática. | T037 | `1620545` |
| F4 | unrequested | LOW | `_tolerar_consolas_limitadas` sin justificación ni prueba. | T038 | `eaf0627` |
| F5 | partial | LOW | FR-012 pide detener ante valores defectuosos en el archivo; solo se validaban las primeras 150 filas. | T039 | `23e6580` |

**Segunda pasada** (después de T035–T039): **converged**, 0 hallazgos; `tasks.md` quedó sin cambios.

## 6. Cómo se resolvió cada tarea de convergencia

- **T035:** `publicar` respalda los archivos que va a reemplazar y, si algo falla, restaura los previos, quita los nuevos y elimina la carpeta si la había creado. 11 pruebas en `test_salida.py` fuerzan el fallo en cada movimiento posible. Commit con `Causa: defecto`.
- **T036:** solo LOCA y LOCAC requieren nombre numérico; Normal y ATWS se ordenan por nombre. Commit con `Causa: defecto`.
- **T037:** prueba con `subprocess` de `python -m preparacion_datos`.
- **T038:** se conservó la tolerancia de consola, se documentó en `research.md` §12 y se probó con una salida ASCII.
- **T039:** se validan todas las filas de las 19 variables y solo los primeros 150 pasos entran en la muestra; la spec no cambió. Commit con `Causa: defecto`.

## 7. Estado final de las tareas

| Fase | Tareas | Estado | Commit principal |
|---|---|---|---|
| Phase 1: Setup | T001–T004 | 4/4 completadas | `1b67f1e` |
| Phase 2: Foundational | T005–T009 | 5/5 completadas | `1b67f1e` |
| Phase 3: US1 (MVP) | T010–T018 | 9/9 completadas | `c20d17a`, `5ef3383` |
| Phase 4: US2 | T019–T022 | 4/4 completadas | `5ef3383` |
| Phase 5: US3 | T023–T029 | 7/7 completadas | `5ef3383` |
| Phase 6: Polish | T030–T034 | 5/5 completadas | `5ef3383`, `4fee101` |
| Phase 7: Convergence | T035–T039 | 5/5 completadas | `96ca897` … `23e6580` |
| **Total** | **39** | **39/39** | |

## 8. Pendientes y aceptados

- **C3 e I3** quedan aceptados sin cambio en la spec (§3).
- **Redacción residual de las tareas y el quickstart.** T011, T019 y la validación 3 del quickstart siguen diciendo «cercana a 0/1» (A1). T016 conserva la frase «lo reemplaza al final», anterior al diseño de `publicar` por archivo. T023 no menciona la prueba de variables sin varianza (C2).
- **Documentos no actualizados.** `plan.md` no lista `tests/unit/test_salida.py`. `contracts/cli.md` enumera menos causas de error que las que produce el código (por ejemplo «archivo ilegible», «nombre sin severidad»).
- **Métricas.** La línea base de puntos de tarea es 82 PTS; las 5 tareas de convergencia no se han registrado en `puntos-tarea.csv`. La sesión de métricas de implementación sigue abierta.
- **Rendimiento.** La ejecución completa con el dataset real tarda unos 12 s y la suite unos 2 min 30 s; el plan no fija un objetivo cuantitativo.
