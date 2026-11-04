# Análisis inicial (`/speckit-analyze`) — 008 Tiempo de detección desde la falla

Fecha: 2026-11-04. Artefactos revisados: `spec.md`, `plan.md`, `tasks.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md` y la constitución v2.0.0. Este informe se guarda tal como salió, antes de aplicar correcciones.

## Hallazgos

| ID | Categoría | Severidad | Ubicación | Resumen | Recomendación |
|----|-----------|-----------|-----------|---------|---------------|
| I1 | Inconsistencia | ALTA | spec.md FR-008, FR-014, SC-003; research.md §6; tasks.md T011(e) | La meta de ATWS se define sobre conjuntos distintos. FR-008 dice que es «sobre las corridas de prueba»; SC-003, research §6 y T011(e) dicen «validación y prueba». La constitución (III) exige enunciar cada meta sobre un conjunto exacto. | Unificar así: la meta de 3 s se mide sobre validación + prueba, porque la regla de 006 se calibra solo con entrenamiento y no usó validación. Informar aparte la cifra solo de prueba. Ajustar FR-008 y FR-014. |
| I2 | Inconsistencia / Constitución III | ALTA | spec.md FR-003; research.md §6; data-model.md; tasks.md T011(e) | FR-003 excluye las corridas inciertas de todas las metas. Pero el tiempo de ATWS se mide desde la demanda (FR-006), que no depende del instante de la falla. Excluirlas quitaría R47 (ATWS de validación) de la meta de 3 s sin un motivo válido. Además, no se define cómo se cuentan las falsas alarmas en las inciertas. | Limitar la exclusión de las inciertas a la meta de diagnóstico, que es la que depende de t_falla. En la meta de ATWS, contar todos los ATWS, con `tiempo_atws_falla_s` vacío en las inciertas. En las falsas alarmas, la regla cuenta en todas las corridas; la Etapa 1 «antes de la falla» no se cuenta en las inciertas y se informa aparte. |
| U1 | Subespecificación | MEDIA | spec.md FR-001; data-model.md; tasks.md T005 | Research §1 y la medición real buscan la línea del iniciador solo en ATWS y TRIP_OK. FR-001 y data-model no lo dicen. Ninguna prueba asegura que una LOCA cuyo registro tenga una consecuencia que coincida con un patrón (por ejemplo, `Turbine Trip Control Change: True` después del scram) siga usando el instante programado. | Escribir en FR-001 y data-model que la búsqueda en el registro se hace solo en ATWS y TRIP_OK. Añadir a T005 el caso «LOCA con línea de disparo de turbina → programado». |
| U2 | Subespecificación | MEDIA | spec.md Edge Cases, FR-005, FR-010; tasks.md T011 | Si tras la falla se confirma primero una familia equivocada y después la correcta (o nunca la correcta), no está definido qué pasa. Esa confusión no es falsa alarma (FR-009) y no se informa en ningún lado. | Mantener que el tiempo es el de la primera confirmación de la familia correcta. Añadir a cada corrida el campo «primera familia confirmada tras la falla» y contar las confusiones en el resumen. Cubrirlo en T011. |
| U3 | Subespecificación | BAJA | research.md §5; tasks.md T011(c) | Una confirmación con τ − 1 < t_falla ≤ τ no cuenta ni como detección ni como falsa alarma. Es correcto, pero no está escrito. | Anotarlo en research §5. |
| C1 | Cobertura | BAJA | spec.md FR-015 | No se usa NPPAD por diseño (solo se lee `--origen` de PWR 3L), pero no hay una prueba explícita. La parte «no modificar el origen» sí está cubierta por el hash de T023. | Aceptable; basta con el diseño. |

## Cobertura

| Requisito | ¿Tiene tarea? | Tareas | Notas |
|-----------|---------------|--------|-------|
| FR-001 | Sí | T005, T007 | Ver U1 |
| FR-002 | Sí | T005, T007 | |
| FR-003 | Sí | T005, T007, T011 | Ver I2 |
| FR-004 | Sí | T009, T014 | |
| FR-005 | Sí | T009, T011, T016 | Ver U2 |
| FR-006 | Sí | T010, T015 | |
| FR-007 | Sí | T009, T012, T014 | |
| FR-008 | Sí | T011, T016 | Ver I1 |
| FR-009 | Sí | T010, T011, T016 | |
| FR-010 | Sí | T012, T016, T017 | |
| FR-011 | Sí | T019, T021 | |
| FR-012 | Sí | T019, T021 | |
| FR-013 | Sí | T012, T017, T025 | |
| FR-014 | Sí | T011, T016 | Ver I1 |
| FR-015 | Sí | T023 | Ver C1 |
| SC-001 | Sí | T005, T023 | |
| SC-002 | Sí | T011, T025 | |
| SC-003 | Sí | T011, T025 | |
| SC-004 | Sí | T011, T025 | |
| SC-005 | Sí | T012, T025 | |
| SC-006 | Sí | T025 | |
| SC-007 | Sí | T009, T010 | |

**Alineación con la constitución**: I2 afecta al principio III (honestidad: no se excluyen corridas de una meta sin un motivo válido). No hay violaciones de los principios I, II, IV ni V.

**Tareas sin requisito**: ninguna (T001–T004 son de preparación; T024 corresponde a la documentación).

## Métricas

- Requisitos: 22 (15 FR + 7 SC).
- Tareas: 26.
- Cobertura: 100 % (22/22).
- Ambigüedades: 0. Duplicaciones: 0.
- Hallazgos: 2 ALTA, 2 MEDIA, 2 BAJA. Críticos: 0.

## Siguientes pasos

No hay críticos, pero conviene corregir I1 e I2 antes de `/speckit-implement`, porque cambian la definición de las metas y las pruebas de T011. U1 y U2 se pueden corregir a la vez con poco costo.
