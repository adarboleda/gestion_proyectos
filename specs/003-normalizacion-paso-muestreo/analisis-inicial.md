# Informe de análisis de especificación (inicial)

**Funcionalidad**: `003-normalizacion-paso-muestreo`

**Fecha**: 2026-10-28

**Alcance**: `spec.md`, `plan.md` (con `research.md`, `data-model.md` y `contracts/`) y `tasks.md`, contrastados con la constitución v2.0.0 antes de `/speckit-implement`.

## Hallazgos

| ID | Categoría | Severidad | Ubicación | Resumen | Recomendación |
|----|-----------|-----------|-----------|---------|---------------|
| I1 | Inconsistencia | LOW | spec.md SC-005; contracts/salidas.md; tasks.md T018 | SC-005 menciona que solo se actualizan las pruebas del mensaje de tiempo de 002, pero FR-007 exige añadir `duracion_muestra_segundos` a `metadata.json` de NPPAD, lo que requiere añadir esa clave a `CLAVES_METADATA` en `tests/integration/test_cli_reporte.py` (ya previsto en T018). | Aclarar en SC-005 que también se actualiza el conjunto de claves esperadas de `metadata.json` en `test_cli_reporte.py` por el nuevo campo de FR-007. |
| U1 | Subespecificación | LOW | research.md §4; data-model.md §4; tasks.md T017, T019 | En `tests/unit/test_reporte.py` las instancias de `Simulacion` se crean en memoria sin pasar por `leer_simulacion`, por lo que `paso_segundos` vale `None` si no se fija. | Especificar en T017 y T019 que `construir_resumen` toma el `paso_segundos` común de las simulaciones (o un parámetro explícito) y que el helper `construir()` de `test_reporte.py` inicializa `paso_segundos=10`. |
| C1 | Hueco de cobertura | LOW | spec.md FR-001, SC-002; tasks.md T006, T008 | FR-001 y SC-002 exigen que no exista una constante `PASO_SEGUNDOS` en la configuración de ninguna de las dos plantas, pero T006 y T008 no incluyen una aserción explícita `not hasattr(config, "PASO_SEGUNDOS")`. | Añadir la comprobación `not hasattr(config, "PASO_SEGUNDOS")` en T006 (`test_lectura.py`) y T008 (`test_pwr3l_lectura.py`). |

## Cobertura de requisitos

| Requisito | ¿Tarea? | Tareas | Notas |
|---|---|---|---|
| FR-001 calcular paso desde TIME sin constante fija | Sí | T001, T002, T006, T008, T009, T010 | Véase C1 |
| FR-002 error si TIME no avanza o cambia de paso (>1e-6) | Sí | T006, T008, T009, T010 | |
| FR-003 error si archivo tiene < 2 filas | Sí | T006, T008, T009, T010 | |
| FR-004 comprobar paso común en todo el dataset | Sí | T006, T008, T009, T010 | |
| FR-005 no escribir artefactos ante error de TIME | Sí | T007, T009 | |
| FR-006 conservar inicio en 0 s en PWR 3L | Sí | T008, T010 | |
| FR-007 publicar paso y duración en NPPAD | Sí | T017, T018, T019, T021 | Véase U1 |
| FR-008 paso en Corrida y paso común en PWR 3L | Sí | T005, T008, T010, T021 | |
| FR-009 normalizar solo con entrenamiento | Sí | T012, T013, T014, T015 | |
| FR-010 variables sin varianza con escala 1 e informadas | Sí | T012, T013, T014, T015 | |
| FR-011 error si train vacío o forma inválida | Sí | T012, T013, T014, T015 | |
| FR-012 márgenes térmicos fuera de la normalización | Sí | T012, T013, T014, T015 | |
| FR-013 paquetes separados para NPPAD y PWR 3L | Sí | T009, T010, T014, T015 | |
| FR-014 determinismo entre ejecuciones | Sí | T013, T021, T022 | |
| SC-001 a SC-006 | Sí | SC-001: T006–T010; SC-002: T006, T008, T018, T021; SC-003: T012, T013; SC-004: T012, T013; SC-005: T003, T008, T018, T022; SC-006: T021, T022 | Véase I1 |

## Alineación con la constitución

Sin conflictos con la constitución v2.0.0:
- **Principio II (Cero fuga de datos)**: el escalador se ajusta exclusivamente con `X_train` en ambas plantas.
- **Principio III (Honestidad y reproducibilidad)**: el paso se mide de `TIME` en el archivo completo sin asumir valores; cualquier anomalía detiene la ejecución.
- **Principio IV (Procedencia de datos)**: NPPAD y PWR 3L mantienen sus módulos separados y el origen se abre en solo lectura.

## Tareas sin requisito

Ninguna: T003 corrige el redondeo de la prueba de `.xls` de 002 (SC-005) y T011, T016, T020 y T022 ejecutan las verificaciones de cada fase.

## Métricas

- Requisitos funcionales: 14 · Criterios de éxito: 6 · Tareas: 22 (48 puntos de tarea)
- Cobertura (requisitos con al menos una tarea): 100 %
- Ambigüedades: 0 · Duplicaciones: 0 · Subespecificaciones: 1
- Hallazgos críticos: **0** · altos: 0 · medios: 0 · bajos: 3

## Siguientes acciones

Sin hallazgos críticos, altos ni medios. Se aplican las tres mejoras bajas (I1, U1, C1) en un commit separado antes de iniciar `/speckit-implement`.
