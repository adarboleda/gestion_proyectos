# Tasks: Preparación de datos NPPAD sin fuga de información

**Input**: Documentos de diseño en `/specs/001-preparacion-datos/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ (`cli.md`, `salidas.md`), quickstart.md

**Tests**: Solicitados de forma explícita: en cada historia de usuario las pruebas se escriben **antes** de la implementación y se comprueba que fallan (la constitución exige pruebas automáticas para todo comportamiento crítico).

**Organization**: Las tareas se agrupan por historia de usuario para poder implementar y probar cada una por separado.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede ejecutar en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: historia de usuario a la que pertenece (US1, US2, US3)
- Todas las rutas son relativas a la raíz del repositorio

## Path Conventions

- Proyecto único con diseño `src/`: código en `src/preparacion_datos/`, pruebas en `tests/unit/` y `tests/integration/`
- Salida generada en `data_processed/` (no se edita a mano)
- Commits con la forma `feat(001): descripción`; si un commit elimina o reescribe código, añadir el trailer `Causa: requisito|defecto|refactor`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialización del proyecto y estructura básica

- [X] T001 Crear `pyproject.toml` en la raíz: paquete `preparacion_datos` con diseño `src/`, `requires-python >= 3.11`, dependencias `pandas`, `numpy`, `scikit-learn`, extra `dev` con `pytest`, guion `preparar-datos = "preparacion_datos.cli:main"` y `[tool.pytest.ini_options] testpaths = ["tests"]`
- [X] T002 [P] Crear `src/preparacion_datos/__init__.py` (vacío con docstring en español) y `src/preparacion_datos/__main__.py` que llama a `preparacion_datos.cli.main()` y termina con su código de salida; crear las carpetas `tests/unit/` y `tests/integration/`
- [X] T003 [P] Añadir `data_processed/` al `.gitignore` de la raíz (artefacto regenerable; research.md decisión 11)
- [X] T004 Instalar con `pip install -e ".[dev]"` y comprobar que `pytest --collect-only` se ejecuta sin errores de importación del paquete

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Lectura y validación de las simulaciones, de las que dependen las tres historias

**CRITICAL**: Ninguna historia puede empezar hasta terminar esta fase

### Tests (escribir primero; deben fallar)

- [X] T005 Crear `tests/conftest.py` con una fixture `origen_sintetico` que construye en un directorio temporal las carpetas `Normal` (1 archivo), `LOCA` y `LOCAC` (100 archivos `1.csv`…`100.csv` cada una) y `ATWS` (1 archivo), con una columna `TIME` y las 19 variables requeridas (12 de planta + 7 de margen), 160 filas de valores numéricos deterministas y distintos por archivo; incluir helpers para corromper un archivo (quitar una columna, poner texto, dejar un valor vacío, poner `inf`, truncar a 149 filas) y para calcular el hash de todos los CSV
- [X] T006 Crear `tests/unit/test_lectura.py` (usa la fixture de T005) con pruebas de: descubrimiento de las 4 clases con etiquetas 0 = NORM, 1 = LOCA, 2 = LOCAC, 3 = ATWS y severidad numérica tomada del nombre del archivo (`7.csv` → 7, orden numérico y no alfabético); la serie leída tiene forma (150, 19) y solo contiene las primeras 150 filas; `ErrorDatos` con el archivo relativo y la causa en cada caso: variable ausente, valor no numérico, valor faltante, valor no finito, menos de 150 pasos (`tiene N`) y carpeta de clase inexistente; el mensaje tiene la forma `ERROR: <archivo>: <causa> [variable <nombre>]`

### Implementation

- [X] T007 Crear `src/preparacion_datos/config.py` con las constantes: correspondencia carpeta → clase → etiqueta (`Normal`→NORM→0, `LOCA`→1, `LOCAC`→2, `ATWS`→3), `VARIABLES_PLANTA` en el orden `P, TAVG, THA, TCA, WRCA, WRCB, LVPZ, LVCR, PWNT, PWR, WECS, WLR`, `VARIABLES_MARGEN` en el orden `DNBR, TPCT, SCMA, SCMB, TSAT, FRCL, FRZR`, `PASOS = 150`, `PASO_SEGUNDOS = 10`, proporciones 0.70 / 0.15 / 0.15, `SEMILLA = 42` y las rutas por defecto de `contracts/cli.md`
- [X] T008 Crear `src/preparacion_datos/lectura.py` con la excepción `ErrorDatos`, la dataclass `Simulacion` (clase, etiqueta, severidad o `None`, archivo relativo al origen, serie de forma (150, 19) float64 con las 12 variables de planta seguidas de las 7 de margen), `descubrir_simulaciones(origen)` y `leer_simulacion(...)`, que usa `pandas.read_csv(usecols=<19 variables>, nrows=150)` y lanza `ErrorDatos` con el formato de T006 ante cualquier defecto; el origen se abre solo para lectura (depende de T007)
- [X] T009 Ejecutar `pytest tests/unit/test_lectura.py` y comprobar que pasa

**Checkpoint**: la lectura y validación funcionan; se pueden empezar las historias de usuario

---

## Phase 3: User Story 1 - Conjuntos de entrenamiento, validación y prueba sin fuga (Priority: P1) MVP

**Goal**: obtener los conjuntos train/val/test con simulaciones completas sin repetirse entre conjuntos, las 12 variables de planta escaladas solo con entrenamiento y una muestra de los primeros 150 pasos por simulación.

**Independent Test**: ejecutar `preparar-datos` y comprobar que ninguna simulación aparece en dos conjuntos, que los parámetros de escala salen solo de entrenamiento y que un archivo defectuoso detiene la ejecución sin escribir nada.

### Tests for User Story 1 (escribir primero; deben fallar antes de implementar)

- [X] T010 [P] [US1] Crear `tests/unit/test_particion.py` con pruebas de: (a) **ninguna simulación aparece en más de un conjunto** y la unión de los tres conjuntos es el total; (b) la simulación de LOCA y la de LOCAC de igual severidad quedan en el mismo conjunto; (c) con 100 severidades se obtiene 70 / 15 / 15 por clase y totales 142 / 30 / 30 con Normal y ATWS; (d) **Normal y ATWS aparecen solo en entrenamiento**: ninguna está en `val` ni en `test` y cada una está exactamente una vez en `train`; (e) el reparto es determinista con la semilla 42, cambia con otra semilla y no depende del orden en que se listan los archivos; (f) una severidad presente en una sola clase se asigna sin romper la regla; (g) `n_train = round(0.70·n)`, `n_val = round(0.15·n)`, `n_test = n − n_train − n_val`
- [X] T011 [P] [US1] Crear `tests/unit/test_escalado.py` con pruebas de: (a) **el escalador se ajusta solo con entrenamiento**: `scaler_mean` y `scaler_std` son iguales a la media y desviación de las filas de entrenamiento aplanadas (N_train·150, 12); (b) cambiar por completo los datos de validación y prueba no altera ni un valor de los parámetros; (c) `X_train` escalado tiene media cercana a 0 y desviación cercana a 1 por variable; (d) validación y prueba se transforman con los parámetros de entrenamiento, sin recalcular; (e) una variable con desviación cero en entrenamiento queda con escala 1.0 y aparece en `variables_sin_varianza`; (f) formas y tipos: `X` (N, 150, 12) float32, parámetros (12,) float64
- [X] T012 [P] [US1] Crear `tests/integration/test_cli.py` con pruebas sobre `origen_sintetico` que ejecutan el comando con `--origen` y `--salida` en un directorio temporal: (a) código de salida 0 y escritura de `X_*.npy`, `y_*.npy`, `scaler_mean.npy` y `scaler_std.npy` con las formas y tipos de `contracts/salidas.md` (`y` int64, valores 0–3); (b) **un archivo defectuoso detiene la preparación con un error que nombra el archivo y la causa, sin escribir ningún conjunto**: caso parametrizado (columna ausente, texto, vacío, `inf`, 149 filas) con código de salida 1, el archivo y la causa en la salida de error, y la carpeta de salida sin crear; si la salida ya existía, queda byte a byte igual; (c) **Normal y ATWS aparecen solo en entrenamiento**: `y_val` y `y_test` no contienen 0 ni 3 y `y_train` contiene exactamente un 0 y un 3; (d) dos ejecuciones seguidas producen archivos idénticos; (e) el contenido de los CSV de origen no cambia (hash antes y después)
- [X] T013 [US1] Ejecutar `pytest tests/unit/test_particion.py tests/unit/test_escalado.py tests/integration/test_cli.py` y comprobar que T010–T012 **fallan** antes de seguir

### Implementation for User Story 1

- [X] T014 [P] [US1] Crear `src/preparacion_datos/particion.py` con `repartir(simulaciones, semilla)` que devuelve la asignación de cada simulación a `train`, `val` o `test`: reparte las severidades (unión de LOCA y LOCAC, ordenadas numéricamente) con `numpy.random.default_rng(semilla)` y la misma asignación para LOCA y LOCAC; `n_train = round(0.70·n)`, `n_val = round(0.15·n)`, `n_test = n − n_train − n_val`; la única simulación de Normal y la de ATWS van completas a `train`; ordena cada conjunto por etiqueta de clase y luego por severidad numérica (depende de T008)
- [X] T015 [P] [US1] Crear `src/preparacion_datos/escalado.py` con `ajustar_escalador(X_train)` que ajusta un `StandardScaler` con las filas aplanadas (N_train·150, 12) y devuelve media (`mean_`, (12,) float64), escala (`scale_`, (12,) float64; "vale 1.0 para una variable sin varianza en entrenamiento") y `variables_sin_varianza`, y `aplicar(escalador, X)` que devuelve "X (N, 150, 12) float32" sin reajustar
- [X] T016 [US1] Crear `src/preparacion_datos/salida.py` con `construir_conjunto(simulaciones)` (apila las 12 variables de planta de cada serie en un arreglo (N, 150, 12) y las etiquetas en un vector (N,) int64) y `publicar(salida, archivos)`, que escribe `X_*.npy`, `y_*.npy`, `scaler_mean.npy` y `scaler_std.npy` en un directorio temporal junto a la salida y lo reemplaza al final, de modo que un fallo previo deje la salida sin cambios (depende de T014 y T015)
- [X] T017 [US1] Crear `src/preparacion_datos/cli.py` con `main(argv=None)`: opciones `--origen`, `--salida` y `--semilla` (valores por defecto de `contracts/cli.md`); orquesta cargar todas las simulaciones → repartir → ajustar el escalador solo con `train` → transformar los tres conjuntos → publicar; ante `ErrorDatos` imprime el mensaje en la salida de error y devuelve 1 sin tocar la salida (depende de T008 y T014–T016)
- [X] T018 [US1] Ejecutar las pruebas de T010–T012 y comprobar que pasan

**Checkpoint**: la historia 1 funciona sola; es el MVP (conjuntos sin fuga y escalados)

---

## Phase 4: User Story 2 - Márgenes térmicos conservados aparte y sin escalar (Priority: P2)

**Goal**: guardar, alineadas paso a paso con las 12 variables de planta de cada muestra, las 7 variables de margen térmico en unidades originales.

**Independent Test**: comparar los `margins_*` de una muestra con las mismas filas del CSV de origen y comprobar que son idénticos y no pasaron por escalado.

### Tests for User Story 2 (escribir primero; deben fallar antes de implementar)

- [X] T019 [P] [US2] Crear `tests/integration/test_margenes.py` con pruebas sobre `origen_sintetico`: (a) `margins_train/val/test.npy` tienen forma (N, 150, 7) y tipo float64, con el mismo N y el mismo orden de filas que `X_*` e `y_*`; (b) para varias muestras de cada clase, los valores coinciden exactamente con los de `DNBR, TPCT, SCMA, SCMB, TSAT, FRCL, FRZR` en las primeras 150 filas del CSV leído de forma independiente; (c) no están escalados: no coinciden con `(valor − media) / desviación` y no existe ningún parámetro de escala para ellos (`scaler_mean.npy` y `scaler_std.npy` tienen 12 elementos); (d) alineación paso a paso: `X * scaler_std + scaler_mean` reproduce las 12 variables de planta de las mismas filas del CSV (con tolerancia de float32)
- [X] T020 [US2] Ejecutar `pytest tests/integration/test_margenes.py` y comprobar que T019 **falla** antes de implementar

### Implementation for User Story 2

- [X] T021 [US2] Ampliar `src/preparacion_datos/salida.py`: `construir_conjunto` devuelve también los márgenes "margins (150, 7) float64" tomados de las 7 últimas columnas de la serie sin ninguna transformación, y `publicar` escribe `margins_train.npy`, `margins_val.npy` y `margins_test.npy` en la misma publicación atómica; actualizar `src/preparacion_datos/cli.py` para pasarlos (depende de T016 y T017)
- [X] T022 [US2] Ejecutar `pytest tests/integration/test_margenes.py tests/integration/test_cli.py` y comprobar que pasan sin romper la historia 1

**Checkpoint**: las historias 1 y 2 funcionan por separado

---

## Phase 5: User Story 3 - Reporte de conteos y limitaciones (Priority: P2)

**Goal**: imprimir el reporte con las muestras por clase y por conjunto, las advertencias de las clases con una sola simulación y las limitaciones, y guardar el mismo contenido en `metadata.json`.

**Independent Test**: generar el reporte y comprobar que los totales por conjunto suman el total de muestras, que las 4 clases aparecen en los 3 conjuntos (incluso con cero) y que Normal y ATWS llevan su advertencia.

### Tests for User Story 3 (escribir primero; deben fallar antes de implementar)

- [X] T023 [P] [US3] Crear `tests/unit/test_reporte.py` con pruebas de: (a) la tabla de conteos por clase y conjunto suma los totales de cada conjunto y el total de muestras; (b) las 4 clases aparecen en los 3 conjuntos, y las celdas en cero se muestran como `0` con una nota; (c) NORM y ATWS llevan la advertencia "una sola simulación: asignada completa a entrenamiento; sin muestras de validación ni de prueba"; (d) las limitaciones conocidas están presentes (Normal y ATWS sin métricas sobre datos no vistos, una muestra por simulación y clases desbalanceadas, simulador único); (e) la comparación con la referencia da `COINCIDE`, `DIFIERE` (con las celdas que difieren), `NO DISPONIBLE` si el archivo no existe y `OMITIDA` con `--sin-referencia`, y compara solo LOCA y LOCAC (ignora NORM y ATWS aunque difieran); (f) el contenido de `metadata.json` cumple los invariantes de `contracts/salidas.md`: las listas de `simulaciones` de dos conjuntos no comparten ningún archivo, `totales` coincide con la suma de `conteos_muestras` y con la primera dimensión de `X_*`, y `escalador.filas_ajuste` es N_train·150
- [X] T024 [P] [US3] Crear `tests/integration/test_cli_reporte.py` con pruebas sobre `origen_sintetico`: (a) la salida estándar contiene las 8 secciones de `contracts/cli.md` en orden; (b) `metadata.json` se escribe con todos los campos de `contracts/salidas.md`; (c) código de salida 0 si la referencia coincide, 2 si los conteos de LOCA o LOCAC difieren (con los artefactos ya publicados y la diferencia en el reporte), 0 con la referencia inexistente (`NO DISPONIBLE`) y 0 con `--sin-referencia` (`OMITIDA`)
- [X] T025 [US3] Ejecutar `pytest tests/unit/test_reporte.py tests/integration/test_cli_reporte.py` y comprobar que T023 y T024 **fallan** antes de implementar

### Implementation for User Story 3

- [X] T026 [P] [US3] Crear `src/preparacion_datos/reporte.py` con: el recuento de muestras por clase y conjunto, la generación de advertencias (clases con una sola simulación y celdas en cero), el texto fijo de limitaciones, `comparar_referencia(ruta, conteos)` que lee solo `sample_counts.LOCA` y `sample_counts.LOCAC` de la referencia, y `formatear_reporte(...)` con las 8 secciones de `contracts/cli.md`
- [X] T027 [US3] Ampliar `src/preparacion_datos/salida.py` con `construir_metadata(...)` según `contracts/salidas.md` y escribir `metadata.json` dentro de la misma publicación atómica (depende de T021 y T026)
- [X] T028 [US3] Ampliar `src/preparacion_datos/cli.py`: opciones `--referencia` y `--sin-referencia`, impresión del reporte en la salida estándar y código de salida 2 cuando la comparación da `DIFIERE` (depende de T017, T026 y T027)
- [X] T029 [US3] Ejecutar `pytest` completo y comprobar que las tres historias pasan

**Checkpoint**: las tres historias funcionan de forma independiente

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Mejoras que afectan a varias historias

- [X] T030 [P] Crear `tests/integration/test_dataset_real.py` con una prueba de extremo a extremo sobre `../IA-Nuclear/NuclearPowerPlantAccidentData/Operation_csv_data` (se omite con `pytest.skip` si la ruta no existe): código de salida 0, conteos 142 / 30 / 30 (70 LOCA y 70 LOCAC en entrenamiento, 15 y 15 en validación y en prueba, 1 Normal y 1 ATWS en entrenamiento), comparación con la referencia `COINCIDE` si existe y origen sin cambios
- [X] T031 [P] Documentar en `README.md` una sección "Preparación de datos" en español con la instalación, el comando `preparar-datos`, los archivos de `data_processed/` y el enlace a `specs/001-preparacion-datos/quickstart.md`
- [X] T032 Revisar que ningún módulo de `src/preparacion_datos/` abra el origen en modo escritura ni escriba fuera de `--salida` (principio IV de la constitución) y que todos los mensajes al usuario estén en español
- [X] T033 Ejecutar las 7 validaciones de `specs/001-preparacion-datos/quickstart.md` con el dataset real y anotar cualquier discrepancia
- [X] T034 Ejecutar `pytest` completo y comprobar que todas las pruebas pasan

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias; empieza de inmediato
- **Foundational (Phase 2)**: depende de Setup; bloquea todas las historias
- **User Stories (Phase 3+)**: dependen de Foundational
  - US1 es el MVP y no depende de otras historias
  - US2 amplía `salida.py` y `cli.py` de US1 (T021 depende de T016 y T017), pero se prueba por separado
  - US3 amplía `salida.py` y `cli.py` de US2 (T027 y T028), pero se prueba por separado
- **Polish (fase final)**: depende de las historias terminadas

### User Story Dependencies

- **US1 (P1)**: tras Foundational; sin dependencias de otras historias
- **US2 (P2)**: tras US1 en el código compartido (`salida.py`, `cli.py`); las pruebas T019 pueden escribirse en paralelo con la implementación de US1
- **US3 (P2)**: tras US2 en el código compartido; `reporte.py` (T026) y las pruebas T023 y T024 pueden prepararse mientras se implementa US2

### Within Each User Story

- Las pruebas se escriben primero y deben fallar antes de implementar (T013, T020, T025)
- Dentro de la historia: lectura/partición/escalado → salida → cli
- La historia termina cuando sus pruebas pasan (T018, T022, T029)

### Parallel Opportunities

- Setup: T002 y T003
- US1, pruebas: T010, T011 y T012 (archivos distintos)
- US1, implementación: T014 y T015 (módulos distintos)
- US3: T023 y T024 (pruebas), luego T026
- Polish: T030 y T031

---

## Parallel Example: User Story 1

```bash
# Escribir juntas las pruebas de la historia 1:
Task: "Pruebas de partición en tests/unit/test_particion.py"
Task: "Pruebas de escalado en tests/unit/test_escalado.py"
Task: "Pruebas de la línea de órdenes en tests/integration/test_cli.py"

# Implementar juntos los módulos independientes:
Task: "Partición por simulación en src/preparacion_datos/particion.py"
Task: "Escalador en src/preparacion_datos/escalado.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (lectura y validación)
3. Completar Phase 3: User Story 1
4. **Parar y validar**: conjuntos sin fuga, escalado solo con entrenamiento y error ante archivo defectuoso
5. Pasar a las demás historias

### Incremental Delivery

1. Setup + Foundational → lectura lista
2. US1 → conjuntos y escalador (MVP)
3. US2 → márgenes térmicos sin escalar
4. US3 → reporte, `metadata.json` y comparación con la referencia
5. Polish → prueba con el dataset real, documentación y validación del quickstart

---

## Notes

- [P] = archivos distintos, sin dependencias pendientes
- [Story] vincula cada tarea con su historia de usuario
- Verificar que las pruebas fallan antes de implementar
- Hacer commit tras cada tarea o grupo lógico, con la forma `feat(001): descripción` (y el trailer `Causa:` si se elimina o reescribe código)
- Evitar tareas vagas, conflictos en un mismo archivo y dependencias entre historias que rompan su independencia

---

## Phase 7: Convergence

- [X] T035 Hacer que `publicar` en `src/preparacion_datos/salida.py` deje la carpeta de salida exactamente como estaba si falla el movimiento de cualquier archivo (guardar copia de los artefactos que va a reemplazar y restaurarlos ante el error) y añadir en `tests/unit/test_salida.py` una prueba que fuerce un fallo a mitad de la publicación y compruebe que la salida previa queda byte a byte igual; si se decide relajar el contrato, corregir en su lugar la frase «Se publican todos juntos o ninguno» de `specs/001-preparacion-datos/contracts/salidas.md` per plan: contracts/salidas.md (partial)
- [X] T036 Exigir nombre numérico (severidad) solo a los archivos de LOCA y LOCAC en `src/preparacion_datos/lectura.py`, ordenando por nombre los de Normal y ATWS, y añadir en `tests/unit/test_lectura.py` una prueba con un CSV de Normal de nombre no numérico que se lea sin error per FR-001 (unrequested)
- [X] T037 Añadir en `tests/integration/test_cli.py` una prueba que ejecute `python -m preparacion_datos` con `subprocess` sobre el dataset sintético y compruebe código de salida 0 y los artefactos escritos per plan: Project Type (partial)
- [X] T038 Justificar `_tolerar_consolas_limitadas` de `src/preparacion_datos/cli.py` en `specs/001-preparacion-datos/research.md` y cubrirla con una prueba en `tests/integration/test_cli.py`, o eliminarla si no se justifica per plan: sin decisión asociada (unrequested)
- [X] T039 Alinear la validación de FR-012 con la spec: validar los valores no numéricos o faltantes en el archivo completo en `src/preparacion_datos/lectura.py`, o bien aclarar en `specs/001-preparacion-datos/spec.md` (FR-012) y en `specs/001-preparacion-datos/research.md` §4 que solo se validan las primeras 150 filas; ajustar `tests/unit/test_lectura.py` en consecuencia (depende de T036) per FR-012 (partial)
