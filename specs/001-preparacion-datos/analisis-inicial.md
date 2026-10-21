# Informe de análisis de especificación (inicial)

**Funcionalidad**: `001-preparacion-datos`

**Fecha**: 2026-10-20

**Alcance**: `spec.md`, `plan.md` y `tasks.md` contrastados con la constitución v2.0.0, antes de `/speckit-implement`. Análisis de solo lectura: no se modificó ningún archivo.

## Hallazgos

| ID | Categoría | Severidad | Ubicación | Resumen | Recomendación |
|----|-----------|-----------|-----------|---------|---------------|
| U1 | Subespecificación | MEDIUM | research.md §8, tasks T016, T012(b), spec Edge Cases (re-ejecución) | "Escribir en un directorio temporal y reemplazar el destino" no funciona si `--salida` ya existe y tiene contenido: `os.replace` de un directorio sobre uno no vacío falla en Windows y en POSIX. La alternativa (borrar y recrear) destruiría archivos ajenos si alguien usa `--salida .`. Tampoco hay prueba de "no mezclar restos de ejecuciones anteriores". | Definir que se reemplazan solo los 12 artefactos conocidos, archivo por archivo, desde el directorio temporal, sin tocar otros archivos. Añadir a T012 una prueba con una salida previa que tenga un archivo ajeno y otro obsoleto, y corregir research §8 y T016. |
| I1 | Inconsistencia | MEDIUM | tasks T008 y T019(b); spec SC-003 | SC-003 exige coincidencia del 100 % de los valores de margen. El lector CSV de pandas por defecto puede diferir 1 ulp de `float()` de Python, así que T019(b) ("leído de forma independiente") podría fallar sin que haya ningún defecto real. | En T008 fijar `float_precision="round_trip"`, y que T019(b) compare contra una lectura con `csv` y `float()`. |
| C1 | Hueco de cobertura | MEDIUM | spec FR-009; contracts/cli.md (secciones del reporte); T023, T026 | FR-009 pide que el reporte incluya "la lista de simulaciones de cada conjunto", pero las 7 secciones del reporte impreso no la tienen: solo está en `metadata.json`. | O añadir la lista al reporte impreso, o precisar en FR-009 que `metadata.json` es la forma persistente del reporte. Añadir la comprobación a T023. |
| C2 | Hueco de cobertura | LOW | spec Edge Cases (desviación cero); T011(e), T023 | Se prueba que `variables_sin_varianza` se calcula (T011), pero ninguna tarea prueba que el reporte impreso y `metadata.json` la muestren (`cli.md` §3). | Añadir ese caso a T023. |
| C3 | Hueco de cobertura | LOW | spec (sin FR/SC); T023(e), T024(c), T026, T028 | La comparación con `../IA-Nuclear/data_processed/metadata.json` y el código de salida 2 vienen de la entrada del plan y no tienen requisito ni criterio en la spec. | Añadir un FR o una nota en Assumptions que lo recoja. No bloquea. |
| A1 | Ambigüedad | LOW | T011(c), T019(d), quickstart validación 3 | "Media cercana a 0, desviación cercana a 1" y "tolerancia de float32" no tienen valor numérico. | Fijar tolerancias, por ejemplo `abs(media) < 1e-5`, `abs(std − 1) < 1e-5` y `rtol 1e-5` en la reconstrucción. |
| I2 | Inconsistencia | LOW | plan.md (árbol de `tests/`) frente a tasks T019, T024, T030 | Las tareas crean `test_margenes.py`, `test_cli_reporte.py` y `test_dataset_real.py`, que el plan no lista. | Añadirlos al árbol del plan. |
| I3 | Terminología | LOW | spec ("operación normal") frente a plan, tasks y contracts ("Normal"/"NORM") | Un mismo concepto con tres nombres. | Anotar una vez en la spec: carpeta `Normal` = clase operación normal = etiqueta `NORM`. |
| U2 | Subespecificación | LOW | T005 | La fixture crea 202 CSV y el ayudante de corrupción los modifica. No se indica el alcance ni si cada prueba usa una copia. | Fixture de sesión de solo lectura, con copia por prueba para los casos defectuosos. |

## Cobertura de requisitos

| Requisito | ¿Tarea? | Tareas | Notas |
|---|---|---|---|
| FR-001 leer sin modificar | Sí | T008, T012(e), T032 | |
| FR-002 una muestra de 150 pasos | Sí | T008, T016, T012(a) | |
| FR-003 sin repetirse entre conjuntos | Sí | T010(a), T014 | |
| FR-004 LOCA/LOCAC igual severidad | Sí | T010(b), T014 | |
| FR-005 12 variables de planta | Sí | T007, T016 | |
| FR-006 escalado solo con entrenamiento | Sí | T011, T015, T017 | |
| FR-007 Normal y ATWS en entrenamiento | Sí | T010(d), T012(c), T014, T023(c) | |
| FR-008 márgenes sin escalar | Sí | T019, T021 | Véase I1 |
| FR-009 reporte | Parcial | T023, T026, T028 | Véase C1 |
| FR-010 advertencias visibles | Sí | T023(b,c), T026 | |
| FR-011 reproducibilidad | Sí | T012(d) | |
| FR-012 archivo defectuoso detiene | Sí | T006, T008, T012(b) | |
| FR-013 una ejecución documentada | Sí | T017, T031 | |
| SC-001 a SC-008 | Sí | SC-001: T010, T012; SC-002: T011; SC-003: T019; SC-004/005: T023; SC-006: T012(d); SC-007: T012(e), T030; SC-008: T031, T033 | |

## Alineación con la constitución

Sin conflictos.

- **Principio I**: no aplica, porque la funcionalidad no emite diagnósticos.
- **Principio II**: la partición es por simulación completa, el escalado se ajusta solo con entrenamiento y LOCA/LOCAC van emparejados.
- **Principio III**: hay semilla, un comando y un reporte con limitaciones.
- **Principio IV**: el origen se abre solo para lectura y se usa una sola planta.
- **Principio V**: solo se leen las cuatro carpetas.
- **Flujo de desarrollo**: pruebas primero, `src/`, `tests/`, español y commits `feat(001):` están cubiertos en las tareas.

## Tareas sin requisito directo (esperado)

- Las de infraestructura y ejecución de pruebas: T001–T004, T009, T013, T018, T020, T022, T025, T029, T034.
- T032, que apunta al principio IV.
- Las de comparación con la referencia (véase C3).

## Métricas

- **Requisitos**: 21 (13 FR y 8 SC).
- **Tareas**: 34.
- **Cobertura**: 100 % con al menos una tarea; FR-009 es parcial.
- **Ambigüedades**: 1.
- **Duplicaciones**: 0.
- **Problemas críticos**: 0 (3 MEDIUM, 6 LOW).

## Próximas acciones

No hay problemas CRITICAL, así que se puede pasar a `/speckit-implement`. Antes conviene resolver U1 e I1, porque cambian el diseño de `salida.py` y de la lectura. Con C1 hay que decidir primero si la lista va en el reporte impreso o si basta con `metadata.json`. El resto son ajustes de redacción que se pueden hacer a mano en `tasks.md`, `plan.md` y `spec.md`.
