# Tasks: Preprocesamiento PWR 3L en ventanas de 300 s y cinco clases

**Input**: Documentos de diseño en `/specs/002-preprocesamiento-pwr3l/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ (`cli.md`, `salidas.md`), quickstart.md

**Tests**: Solicitados: en cada historia las pruebas se escriben **antes** de la implementación y se comprueba que fallan (la constitución exige pruebas automáticas para todo comportamiento crítico: descubrimiento, validación, grupos, reparto, escalado).

**Organization**: Tareas agrupadas por historia de usuario para implementar y probar cada una por separado.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede ejecutar en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: historia de usuario (US1, US2, US3)
- Rutas relativas a la raíz del repositorio

## Path Conventions

- Código en `src/preparacion_pwr3l/`; pruebas en `tests/pwr3l/unit/` y `tests/pwr3l/integration/` con prefijo `test_pwr3l_`
- Salida generada en `data_processed_pwr3l/` (no se edita a mano)
- Commits `feat(002): …`, `test(002): …`, `docs(002): …`; si un commit elimina o reescribe código, trailer `Causa: requisito|defecto|refactor`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Paquete nuevo y dependencias

- [ ] T001 Modificar `pyproject.toml`: añadir `openpyxl>=3.1` a `dependencies`, el guion `preparar-pwr3l = "preparacion_pwr3l.cli:main"` y actualizar `description` para nombrar las dos preparaciones (NPPAD y PWR 3L)
- [ ] T002 [P] Crear `src/preparacion_pwr3l/__init__.py` (docstring en español) y `src/preparacion_pwr3l/__main__.py` que llama a `preparacion_pwr3l.cli.main()` y termina con su código; crear `tests/pwr3l/unit/` y `tests/pwr3l/integration/`
- [ ] T003 [P] Añadir `data_processed_pwr3l/` al `.gitignore` de la raíz (research.md decisión 10)
- [ ] T004 Reinstalar en modo editable (`uv pip install -e ".[dev]"` o `pip install -e ".[dev]"`) y comprobar que `pytest --collect-only -q` no da errores

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Descubrimiento, lectura y validación de las corridas, de las que dependen las tres historias

**CRITICAL**: Ninguna historia puede empezar antes de terminar esta fase

### Tests (escribir primero; deben fallar)

- [ ] T005 Crear `tests/pwr3l/conftest.py` con la fixture de sesión `arbol_pwr3l` (solo lectura) que construye en un directorio temporal un árbol PWR 3L pequeño: carpetas manuales `NORM` (R01 en `.xls` = libro xlsx), `LOCA HOT` (R09 2000 cm², R10 50 cm, CSV), `LOCA COLD` (R03 2000 cm², R07 descartada), `ATWS` (R21, R27 con dos archivos de datos), `TRIP_OK` (R59 gemela de R21, CSV), `LOCA PORV` (R20 OOD) y `auto/` (`R<n>_<CLASE>` con `plotdata.csv` y `config.json`: varias NORM, LOCA y LOCAC con áreas repetidas, pares ATWS/TRIP_OK de la tabla, una OOD, una corrida corta de 295 filas y carpetas `_respaldos` y un archivo suelto que deben ignorarse); columnas `TIME` + 26 entradas + 7 márgenes + `WLR`, 301 filas (salvo la corta), valores deterministas distintos por corrida; y la fixture `copia_pwr3l` (copia por prueba) con ayudantes para corromper un archivo (quitar columna, texto, vacío, `inf`, salto de tiempo), añadir carpetas y calcular el hash de todo el árbol
- [ ] T006 [P] Crear `tests/pwr3l/unit/test_pwr3l_descubrimiento.py`: clase por carpeta (FR-002) y por sufijo en `auto`; id `R<n>[letra]`; orden por etiqueta y número (`R07b` tras `R07`); se ignoran `_*`, `.*` y archivos sueltos; descartadas (R07, R27) y OOD (R20, `auto/*_OOD`) se marcan sin leerse (R27 con dos archivos no da error); área de rotura desde el nombre de carpeta y desde `config.json`; gemela según la tabla; `ErrorDatos` con ruta y causa para: carpeta no reconocida, clase desconocida en `auto`, nombre sin id, id repetido, sin archivo de datos, más de un archivo de datos, LOCA sin área, origen inexistente
- [ ] T007 [P] Crear `tests/pwr3l/unit/test_pwr3l_lectura.py`: lectura de CSV y de libro xlsx con extensión `.xls`; serie (300, 33) con las filas 0–299 y el orden de columnas de `config`; valores idénticos al texto del CSV (comparar con `float()` sobre el texto); corrida de 295 filas → estado `corta` con `filas = 295`, sin serie; `ErrorDatos` para variable ausente, valor no numérico, vacío, `inf`, tiempo que no empieza en 0 o salta, también cuando el defecto está después de la fila 300; formato del mensaje `ERROR: <archivo>: <causa> [variable <v>]`

### Implementation

- [ ] T008 Crear `src/preparacion_pwr3l/config.py`: carpetas manuales → clase, clases de `auto`, etiquetas NORM 0 … TRIP_OK 4, `VARIABLES_ENTRADA` (26, orden de research §6), `VARIABLES_MARGEN` (7), `PASOS = 300`, `PASO_SEGUNDOS = 1`, proporciones 0.70/0.15/0.15, `SEMILLA = 42`, `DESCARTADAS` (R07, R27, R28 con motivo), `GEMELAS` (19 pares de research §7), familias de clase y rutas por defecto de `contracts/cli.md`
- [ ] T009 Crear `src/preparacion_pwr3l/descubrimiento.py` con `ErrorDatos`, la dataclass `Corrida` (data-model.md) y `descubrir_corridas(origen)` según research §2–§3 y §7 (área y gemela) (depende de T008)
- [ ] T010 Crear `src/preparacion_pwr3l/lectura.py` con `leer_corrida(origen, corrida)` (valida el archivo completo, fija `filas`, `estado` y `serie`) y `cargar_corridas(origen)` (descubre, lee solo las de las cinco clases y se detiene en el primer defecto) según research §4–§5 (depende de T009)
- [ ] T011 Ejecutar `pytest tests/pwr3l/unit/test_pwr3l_descubrimiento.py tests/pwr3l/unit/test_pwr3l_lectura.py` y comprobar que pasan

**Checkpoint**: corridas descubiertas, validadas y clasificadas en usables, cortas, descartadas y OOD

---

## Phase 3: User Story 1 - Conjuntos de 300 s y cinco clases sin fuga (Priority: P1) MVP

**Goal**: conjuntos train/val/test por grupos de corridas completas, entradas escaladas solo con entrenamiento, 300 pasos y cinco clases.

**Independent Test**: ejecutar el comando sobre el árbol sintético y comprobar intersecciones vacías, gemelas y áreas en el mismo conjunto, forma (N, 300, 26) y escalador de entrenamiento.

### Tests (escribir primero; deben fallar)

- [ ] T012 [P] [US1] Crear `tests/pwr3l/unit/test_pwr3l_grupos.py`: gemelas ATWS/TRIP_OK en un grupo `GEMELAS-<a>-<b>`; LOCA y LOCAC de igual área en un grupo `AREA-<cm2>`, también con repeticiones dentro de una clase; NORM y corridas sin pareja en grupos propios; una gemela corta deja a la otra sola; cada corrida en exactamente un grupo; familia de cada grupo
- [ ] T013 [P] [US1] Crear `tests/pwr3l/unit/test_pwr3l_particion.py`: cada grupo en exactamente un conjunto y cada corrida en uno; ningún grupo partido; proporciones por familia dentro de ±1 grupo de la meta con grupos de tamaño 1; misma semilla → mismo resultado; resultado independiente del orden de entrada; semilla distinta → puede cambiar; orden de filas por etiqueta y número
- [ ] T014 [P] [US1] Crear `tests/pwr3l/unit/test_pwr3l_escalado.py`: media y escala iguales (rtol 1e-12) a las de las filas de entrenamiento aplanadas; `X_train` escalado con media |m| < 1e-4 y desviación |s − 1| < 1e-4 por variable; cambiar val/test no altera los parámetros; variable sin varianza informada y sin `nan`/`inf`; salida float32 con la misma forma
- [ ] T015 [US1] Crear `tests/pwr3l/integration/test_pwr3l_cli.py` (usa `copia_pwr3l`): `main([...])` devuelve 0 y publica `X_*`, `y_*`, `scaler_*`; `X_*.shape[1:] == (300, 26)`; `y` solo en 0–4; ninguna corrida OOD, descartada o corta en los conjuntos; ids sin intersección entre conjuntos; gemelas y áreas en el mismo conjunto; `scaler_mean` = media de las entradas sin escalar de las corridas de entrenamiento; dos ejecuciones dan archivos idénticos byte a byte; archivo defectuoso → código 1, mensaje con el archivo en la salida de error y la salida no se crea; hash del árbol igual antes y después; `python -m preparacion_pwr3l` con `subprocess` devuelve 0

### Implementation

- [ ] T016 [US1] Crear `src/preparacion_pwr3l/grupos.py` con la dataclass `Grupo` y `formar_grupos(corridas_usables)` (research §7)
- [ ] T017 [US1] Crear `src/preparacion_pwr3l/particion.py` con `repartir(grupos, semilla)` → conjunto por grupo y corridas por conjunto (research §8) (depende de T016)
- [ ] T018 [P] [US1] Crear `src/preparacion_pwr3l/escalado.py` con `ajustar_escalador(x_train)` y `aplicar(escalador, x)` (research §9)
- [ ] T019 [US1] Crear `src/preparacion_pwr3l/salida.py` con `construir_conjunto(corridas)` → `x` (N, 300, 26) float64 y `y` (N,) int64, en el orden de la partición (depende de T010)
- [ ] T020 [US1] Crear `src/preparacion_pwr3l/cli.py` con `main(argv)`: argumentos de `contracts/cli.md`, tolerancia de consola (research §12), cargar → agrupar → repartir → construir → escalar → `preparacion_datos.salida.publicar`; código 1 ante `ErrorDatos` u `OSError` (depende de T016–T019)
- [ ] T021 [US1] Ejecutar `pytest tests/pwr3l` y comprobar que pasan las pruebas de US1

**Checkpoint**: MVP: conjuntos sin fuga con cinco clases y ventanas de 300 s

---

## Phase 4: User Story 2 - Márgenes térmicos conservados aparte (Priority: P2)

**Goal**: márgenes (N, 300, 7) sin escalar y alineados con las entradas.

**Independent Test**: comparar los márgenes de una muestra con el archivo de origen.

### Tests (escribir primero; deben fallar)

- [ ] T022 [US2] Crear `tests/pwr3l/integration/test_pwr3l_margenes.py`: `margins_*.npy` existe con forma (N, 300, 7) float64; para una corrida CSV y una xlsx, sus márgenes son idénticos a las filas 0–299 del archivo (comparación exacta); ninguna variable de margen está en `VARIABLES_ENTRADA` ni cambia el tamaño de los parámetros de escala (26)

### Implementation

- [ ] T023 [US2] Ampliar `construir_conjunto` en `src/preparacion_pwr3l/salida.py` para devolver también los márgenes y publicar `margins_<conjunto>.npy` desde `src/preparacion_pwr3l/cli.py`
- [ ] T024 [US2] Ejecutar `pytest tests/pwr3l` y comprobar que pasan

**Checkpoint**: US1 y US2 funcionan por separado

---

## Phase 5: User Story 3 - Reporte de conteos, corridas excluidas y limitaciones (Priority: P2)

**Goal**: reporte impreso y `metadata.json` con conteos, grupos, exclusiones, advertencias y limitaciones.

**Independent Test**: generar el reporte y comprobar que cada corrida encontrada está en una sola categoría y que los totales cuadran.

### Tests (escribir primero; deben fallar)

- [ ] T025 [P] [US3] Crear `tests/pwr3l/unit/test_pwr3l_reporte.py`: tabla de muestras con las 5 clases × 3 conjuntos, ceros incluidos y marcados con `*`; totales que cuadran; advertencia por cada celda en cero y por cada corrida corta (con archivo y filas); cada exclusión (OOD, descartada, corta) con id, clase, motivo y detalle; `corridas_encontradas` suma el total de corridas descubiertas; las 9 secciones de `contracts/cli.md` en orden
- [ ] T026 [US3] Ampliar `tests/pwr3l/integration/test_pwr3l_cli.py`: el reporte se imprime en la salida estándar con las 9 secciones; `metadata.json` cumple `contracts/salidas.md` (claves, `corridas[c][i]` alineado con la fila `i`, grupos por conjunto, exclusiones y escalador); la suma de categorías es igual al número de carpetas de corrida del árbol

### Implementation

- [ ] T027 [US3] Crear `src/preparacion_pwr3l/reporte.py` con `Resumen`, `construir_resumen(...)`, `generar_advertencias(...)`, las limitaciones y `formatear_reporte(resumen, artefactos)` (contracts/cli.md)
- [ ] T028 [US3] Añadir `construir_metadata(resumen)` y `serializar_metadata(...)` en `src/preparacion_pwr3l/salida.py` (contracts/salidas.md)
- [ ] T029 [US3] Integrar en `src/preparacion_pwr3l/cli.py`: publicar `metadata.json` con los demás artefactos e imprimir el reporte tras publicar
- [ ] T030 [US3] Ejecutar `pytest tests/pwr3l` y comprobar que pasan

**Checkpoint**: las tres historias funcionan

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T031 Crear `tests/pwr3l/integration/test_pwr3l_dataset_real.py` (se omite si `../IA-Nuclear/PWR 3L` no existe): código 0; 109 corridas encontradas (100 de las cinco clases, 6 OOD, 3 descartadas); las corridas con menos de 300 filas aparecen como cortas con su número de filas; R07b usable y R07 descartada; ninguna OOD en los conjuntos; la tabla `GEMELAS` coincide con `gemelo_de` de cada `config.json` de `auto`; las restricciones de grupo se cumplen; hash del origen sin cambios
- [ ] T032 [P] Añadir al `README.md` una sección «Preprocesamiento PWR 3L (funcionalidad 002)»: qué hace, instalación, `preparar-pwr3l`, opciones, artefactos y limitaciones, sin tocar la sección de 001
- [ ] T033 Ejecutar las validaciones de `specs/002-preprocesamiento-pwr3l/quickstart.md` con el dataset real y anotar en `quickstart.md` los conteos obtenidos
- [ ] T034 Ejecutar la suite completa (`python -m pytest -q`, 001 + 002) y comprobar que todo pasa

---

## Dependencies & Execution Order

- **Setup (Phase 1)** → **Foundational (Phase 2)** → **US1 (Phase 3)** → US2 (Phase 4) y US3 (Phase 5) → **Polish (Phase 6)**
- US2 depende de `salida.py` y `cli.py` de US1; US3 depende de `cli.py` de US1. US2 y US3 tocan archivos distintos salvo `cli.py` y `salida.py`: hacerlas en serie.
- Dentro de cada historia: pruebas (deben fallar) → modelos/lógica → integración en `cli.py` → ejecutar pruebas.

### Parallel Opportunities

- T002 y T003; T006 y T007; T012, T013 y T014 (archivos de prueba distintos); T018 junto con T016–T017; T025 y T026 (archivos de prueba distintos); T032 junto con T031.

```text
# US1, pruebas en paralelo:
Task: "Grupos en tests/pwr3l/unit/test_pwr3l_grupos.py"
Task: "Reparto en tests/pwr3l/unit/test_pwr3l_particion.py"
Task: "Escalado en tests/pwr3l/unit/test_pwr3l_escalado.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 + Phase 2 (descubrimiento y lectura)
2. Phase 3 (US1)
3. **Parar y validar**: sin fuga por grupos, 300 pasos, cinco clases, escalado de entrenamiento, error ante archivo defectuoso

### Incremental Delivery

1. Setup + Foundational → corridas clasificadas
2. US1 → conjuntos y escalador (MVP)
3. US2 → márgenes
4. US3 → reporte y `metadata.json`
5. Polish → carpeta real, README, quickstart, suite completa

---

## Notes

- [P] = archivos distintos, sin dependencias pendientes
- Verificar que las pruebas fallan antes de implementar
- Commit tras cada grupo lógico (`feat(002)`, `test(002)`, `docs(002)`), con `Causa:` si se reescribe código
- No tocar el código ni las pruebas de 001 salvo para importar `publicar`
