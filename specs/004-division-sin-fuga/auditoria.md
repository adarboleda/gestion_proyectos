# Auditoría de la funcionalidad 004-division-sin-fuga

**Fecha**: 2026-10-28

**Rama**: `004-division-sin-fuga`

**Fuentes**: [analisis-inicial.md](analisis-inicial.md) (`/speckit-analyze`), una pasada de `/speckit-converge`, el código, las pruebas y los registros de `speckit-metricas`.

## 1. Resumen

- El análisis inicial (antes de implementar) encontró **7 hallazgos**: 0 críticos, 1 MEDIUM y 6 LOW, con cobertura del 100 % de los requisitos (FR-014 parcial).
- El responsable **aprobó de forma explícita** aplicar U1, C1, C2, C3 y T1 antes de implementar; D1 e I1 quedaron sin cambio, como recomendaba el informe. Las correcciones se aplicaron en un commit aparte (`a149615`).
- `/speckit-converge` dio **«converged»** en la primera pasada: 0 hallazgos y `tasks.md` sin cambios.
- Estado final: **25 de 25 tareas completadas**, **44 pruebas nuevas** y la suite completa con los datasets reales en **210 pasadas y 1 omitida**.
- Con el dataset real de PWR 3L, la verificación no encuentra fuga y el reparto queda en **63 / 15 / 13** corridas.

## 2. Cobertura de requisitos (estado final)

| Requisito | Tareas | Pruebas que lo verifican |
|---|---|---|
| FR-001 solo usables | T004, T012, T021 | `test_pwr3l_grupos` (excluidas fuera), `test_pwr3l_verificacion` (excluida dentro), `test_pwr3l_particion_real` |
| FR-002 grupos por área | T004, T006 | `test_pwr3l_grupos` (misma área, repeticiones, áreas distintas) |
| FR-003 gemelas | T004, T006 | `test_pwr3l_grupos` (pareja completa, pareja corta, orden natural) |
| FR-004 grupos individuales | T004, T006 | `test_pwr3l_grupos` (NORM) |
| FR-005 una corrida en un grupo | T004, T006 | `test_pwr3l_grupos` (exactamente un grupo, claves) |
| FR-006 grupo completo en un conjunto | T008, T010 | `test_pwr3l_particion` |
| FR-007 familias, 70/15/15, mayor primero | T008, T010 | `test_pwr3l_particion` (metas, grupo mayor a entrenamiento) |
| FR-008 cota del desvío | T008, T021 | `test_pwr3l_particion` (200 repartos aleatorios), `test_pwr3l_particion_real` |
| FR-009 reproducible e independiente del orden | T004, T008, T021 | `test_pwr3l_grupos`, `test_pwr3l_particion`, `test_pwr3l_particion_real` |
| FR-010 semilla 42 | T008 | `test_pwr3l_particion` |
| FR-011 verificación a–e | T012, T016, T018 | `test_pwr3l_verificacion` (11 pruebas, una por regla, y `repartir` nunca devuelve fuga) |
| FR-012 conteos y listas | T008 | `test_pwr3l_particion` (5 clases × 3 conjuntos, orden) |
| FR-013 errores de entrada | T004 | `test_pwr3l_grupos` (LOCA sin área, sin usables) |
| FR-014 no modificar | T004, T008 | `test_pwr3l_grupos`, `test_pwr3l_particion` (añadidas por C3) |
| FR-015 verificación NPPAD | T013, T014, T017, T019, T022 | `test_verificacion`, `test_cli::test_particion_con_fuga_detiene_sin_publicar`, `test_verificacion_real` |
| SC-001 0 violaciones con datos reales | T021 | `test_pwr3l_particion_real` |
| SC-002 desvío acotado | T008, T021 | `test_pwr3l_particion`, `test_pwr3l_particion_real` |
| SC-003 reproducible | T008, T021 | `test_pwr3l_particion`, `test_pwr3l_particion_real` |
| SC-004 detecta el 100 % de las fugas introducidas | T012 | `test_pwr3l_verificacion` |
| SC-005 excluidas fuera | T021 | `test_pwr3l_particion_real` |
| SC-006 familias en los tres conjuntos | T021 | `test_pwr3l_particion_real` |
| SC-007 NPPAD sin fuga | T022 | `test_verificacion_real` |

Pruebas nuevas por archivo (44): `test_pwr3l_grupos` 13, `test_pwr3l_particion` 12, `test_pwr3l_verificacion` 11, `test_verificacion` (NPPAD) 4, `test_cli` +1, `test_pwr3l_particion_real` 2 y `test_verificacion_real` 1.

## 3. Hallazgos del análisis inicial y su resolución

| ID | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| U1 | MEDIUM | `repartir` solo conoce corridas usables, así que la regla (e) no puede fallar dentro de él. | **Aplicado con aprobación.** El contrato exige que quien construye la salida llame a `verificar_reparto` con todas las corridas; la prueba real lo hace con las 109. |
| C1 | LOW | Sin medida del objetivo de rendimiento. | **Aplicado.** La prueba real mide el tiempo: 0,0015 s para agrupar, repartir y verificar (objetivo: menos de 1 s). |
| C2 | LOW | Sin pruebas de familia con menos de 3 grupos ni de clase sin usables. | **Aplicado.** Dos pruebas en `test_pwr3l_particion`. |
| C3 | LOW | Sin prueba de que no se modifican las corridas. | **Aplicado.** Una prueba en `test_pwr3l_grupos` y otra en `test_pwr3l_particion`. |
| T1 | LOW | «Severidad» con dos significados. | **Aplicado.** Frase de terminología en los supuestos de la spec. |
| D1 | LOW | SC-002 repite FR-008. | **Aceptado, sin cambio.** |
| I1 | LOW | `specs/002…/tasks.md` sigue mostrando T012, T013, T016 y T017 sin marcar. | **Aceptado, sin cambio**: 002 pertenece a KAN-18; queda anotado en `ENTREGABLES-004.md`. |

## 4. Resultado de `/speckit-converge`

Una pasada, después de implementar T001–T025: **converged**, 0 hallazgos (missing 0, partial 0, contradicts 0, unrequested 0). Se comprobaron 15 FR, 7 SC, 15 escenarios de aceptación, 8 casos límite, 7 decisiones del plan y los 5 principios de la constitución. `tasks.md` no se modificó.

## 5. Estado final de las tareas

| Fase | Tareas | Estado | Commits |
|---|---|---|---|
| Phase 1: Setup | T001–T002 | 2/2 | `30e1b77` |
| Phase 2: Foundational | T003 | 1/1 | `30e1b77` |
| Phase 3: US1 (MVP) | T004–T007 | 4/4 | `30e1b77`, `9dc7d57` |
| Phase 4: US2 | T008–T011 | 4/4 | `3eb8f37`, `6f116e4` |
| Phase 5: US3 | T012–T020 | 9/9 | `70befcc`, `53069a5`, `6adaec5` |
| Phase 6: Polish | T021–T025 | 5/5 | `6ae9389`, `dcf28d0` |
| **Total** | **25** | **25/25** | |

## 6. Observaciones de proceso

- **Trailer `Causa:` ausente en un commit.** `53069a5` reescribió 2 líneas de `particion.py` (de `return Reparto(…)` a `reparto = Reparto(…)`, para verificar antes de devolver, tarea T018) sin el trailer que exige la constitución. Las métricas cuentan 1 línea eliminada «sin clasificar»; su causa real es `requisito` (T018 estaba planificada). No se reescribió el historial.
- **Las respuestas de `/speckit-clarify` y la aprobación de las correcciones las dio el responsable**, con preguntas explícitas durante la sesión (a diferencia de 001, donde se aplicaron sin aprobación).
- **La prueba real NPPAD de 001** (`tests/integration/test_dataset_real.py`) sigue buscando el dataset en `../IA-Nuclear` y se omite en esta máquina. Las pruebas nuevas usan `IANUCLEAR_DATOS`. La validación NPPAD real se hizo con `test_verificacion_real.py` y ejecutando `preparar-datos` a mano (código 0, `COINCIDE`).
- **Las horas** son el mínimo por sesión que registra la extensión (0,25 h), no un cronómetro: el reloj marca unos 27 minutos de trabajo del agente entre la primera y la última sesión (21:48–22:15). La exploración previa del dataset y del proyecto de referencia no está registrada.

## 7. Pendientes

- **KAN-18 (002)** debe usar `formar_grupos`, `repartir` y `verificar_reparto(corridas, reparto)` con todas las corridas al construir `X_*`, `y_*`, `margins_*`, el reporte y `metadata.json`.
- **Limitación heredada (D1 de 002)**: las corridas NORM parecidas entre sí no se agrupan; podrían repartirse entre conjuntos aunque representen escenarios casi iguales.
