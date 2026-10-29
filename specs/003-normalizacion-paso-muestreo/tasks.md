# Tasks: Normalización solo con entrenamiento y verificación automática del paso de muestreo

**Input**: Documentos de diseño en `/specs/003-normalizacion-paso-muestreo/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ (`cli.md`, `salidas.md`), quickstart.md

**Tests**: Solicitados por la constitución: todo comportamiento crítico debe tener pruebas automáticas en `tests/` escritas antes de implementar (verificación de `TIME`, paso común entre archivos, normalización exclusiva con entrenamiento y metadatos/reporte).

**Organization**: Tareas agrupadas por historia de usuario para implementar y probar cada historia de manera independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede ejecutar en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: historia de usuario (`[US1]`, `[US2]`, `[US3]`)
- Rutas relativas a la raíz del repositorio

## Path Conventions

- Código de NPPAD en `src/preparacion_datos/`; código de PWR 3L en `src/preparacion_pwr3l/`
- Pruebas de NPPAD en `tests/unit/` y `tests/integration/`; pruebas de PWR 3L en `tests/pwr3l/unit/`
- Commits `feat(003): …`, `test(003): …`, `docs(003): …`; cuando un commit elimine o reescriba código existente incluye el trailer `Causa: requisito|defecto|refactor`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Limpiar constantes de paso asumido en las configuraciones de ambas plantas y dejar la línea base de pruebas lista.

- [ ] T001 [P] Modificar `src/preparacion_datos/config.py`: añadir `VARIABLE_TIEMPO = "TIME"` y eliminar la constante fija `PASO_SEGUNDOS = 10` (FR-001)
- [ ] T002 [P] Modificar `src/preparacion_pwr3l/config.py`: eliminar la constante fija `PASO_SEGUNDOS = 1` (FR-001)
- [ ] T003 Corregir en `tests/pwr3l/unit/test_pwr3l_lectura.py` la prueba `test_libro_xlsx_con_extension_xls` para comparar contra los valores serializados en el archivo `.xls` (xlsx) con `openpyxl` en lugar del generador en memoria (research.md §6)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Actualizar las entidades de datos (`Simulacion` y `Corrida`) para transportar el paso de muestreo medido de cada archivo.

**CRITICAL**: Debe completarse antes de las historias US1 y US3.

- [ ] T004 [P] Añadir el atributo `paso_segundos: Optional[float] = None` a la dataclass `Simulacion` en `src/preparacion_datos/lectura.py` (data-model.md §1)
- [ ] T005 [P] Añadir el atributo `paso_segundos: Optional[float] = None` a la dataclass `Corrida` en `src/preparacion_pwr3l/descubrimiento.py` (data-model.md §2)

**Checkpoint**: Entidades listas para almacenar el paso medido en ambas plantas.

---

## Phase 3: User Story 1 - El paso de muestreo se mide, no se supone (Priority: P1) 🎯 MVP

**Goal**: Medir el paso de muestreo de cada archivo a partir de las diferencias consecutivas de `TIME` en el archivo completo, tolerar redondeo numérico de hasta `1e-6` relativo, exigir en PWR 3L inicio en `0 s`, detener con `ErrorDatos` si hay menos de 2 filas, si el tiempo no avanza, si el paso cambia dentro de un archivo o si dos archivos del mismo dataset tienen pasos distintos, sin escribir ningún artefacto.

**Independent Test**: Ejecutar las pruebas unitarias e integración de lectura de NPPAD y PWR 3L comprobando que se mide el paso real y que cualquier anomalía en `TIME` (en cualquier fila del archivo o entre archivos) lanza `ErrorDatos` con archivo, fila y `[variable TIME]`.

### Tests for User Story 1 (escribir primero; deben fallar)

- [ ] T006 [P] [US1] Ampliar `tests/unit/test_lectura.py` (NPPAD) con pruebas para: comprobación de que `PASO_SEGUNDOS` no existe en `preparacion_datos.config`; medición de `paso_segundos == 10` desde `TIME`; aceptación de paso constante distinto de 10 s (p. ej. 5 s en todo el dataset) y de ruido de redondeo dentro de `1e-6` relativo; `ErrorDatos` con `[variable TIME]` cuando falta `TIME`, hay valor vacío/no numérico/no finito en `TIME`, el archivo tiene menos de 2 filas, el tiempo se repite o retrocede, el paso cambia dentro del archivo (tanto antes como después de la fila 150, indicando fila y los dos valores de paso) o un archivo tiene un paso distinto al del resto del dataset en `cargar_simulaciones` (FR-001 a FR-004, SC-001, SC-002)
- [ ] T007 [P] [US1] Ampliar `tests/integration/test_cli.py` (NPPAD) con pruebas de extremo a extremo donde un archivo con paso no constante o con paso distinto al resto detiene `preparar-datos` con código 1, nombra el archivo y `[variable TIME]` en `stderr`, y no crea ni altera la carpeta de salida (FR-005, SC-001)
- [ ] T008 [P] [US1] Ampliar `tests/pwr3l/unit/test_pwr3l_lectura.py` (PWR 3L) con pruebas para: comprobación de que `PASO_SEGUNDOS` no existe en `preparacion_pwr3l.config`; medición de `paso_segundos == 1` en corridas usables y cortas (`None` en descartadas y OOD); aceptación de otro paso constante común (p. ej. 2 s desde 0) y redondeo `< 1e-6`; `ErrorDatos` con `[variable TIME]` cuando el archivo tiene menos de 2 filas, `TIME` no empieza en 0, el tiempo se repite o retrocede, el paso cambia en cualquier fila (incluidas filas `>= 300`, mostrando los dos pasos) o una corrida tiene paso distinto al del resto en `cargar_corridas` y `obtener_paso_comun` (FR-001 a FR-004, FR-006, FR-008, SC-001, SC-002, SC-005)

### Implementation for User Story 1

- [ ] T009 [US1] Implementar en `src/preparacion_datos/lectura.py` la lectura y validación de `VARIABLE_TIEMPO` en todas las filas del archivo, el cálculo del paso con `np.diff` y tolerancia relativa `1e-6`, la asignación de `paso_segundos` en `Simulacion` y la verificación de paso común entre todos los archivos en `cargar_simulaciones(origen)` (depende de T001, T004, T006, T007)
- [ ] T010 [P] [US1] Implementar en `src/preparacion_pwr3l/lectura.py` el cálculo del paso desde `TIME` (conservando la regla `TIME[0] == 0`), la validación de avance y constancia con tolerancia `1e-6` en todo el archivo, la asignación de `corrida.paso_segundos`, la verificación de paso común en `cargar_corridas(origen)` y la función `obtener_paso_comun(corridas)` (depende de T002, T005, T008)
- [ ] T011 [US1] Ejecutar `pytest tests/unit/test_lectura.py tests/pwr3l/unit/test_pwr3l_lectura.py` y comprobar que pasan todas las pruebas de lectura de ambas plantas

**Checkpoint**: El paso de muestreo se mide automáticamente de `TIME` y detiene el proceso ante cualquier inconsistencia en NPPAD y PWR 3L.

---

## Phase 4: User Story 2 - Las variables de entrada se normalizan solo con entrenamiento (Priority: P1)

**Goal**: Garantizar en ambas plantas que el escalador (`StandardScaler`) se ajuste únicamente con `X_train` en `float64`, transforme `train`, `val` y `test` a `float32` sin reajustar, maneje variables sin varianza con escala `1.0` e informe sus nombres, y rechace con `ValueError` conjuntos vacíos o con dimensiones/formas inválidas.

**Independent Test**: Ejecutar `pytest tests/unit/test_escalado.py tests/pwr3l/unit/test_pwr3l_escalado.py` verificando parámetros, invariancia ante cambios en `val`/`test`, manejo de varianza cero y rechazo de formas incorrectas.

### Tests for User Story 2 (escribir primero; deben fallar)

- [ ] T012 [P] [US2] Ampliar `tests/unit/test_escalado.py` (NPPAD) con pruebas de validación de `ValueError` cuando `x_train` está vacío (`(0, 150, 12)`) o cuando `x_train` o `x` en `aplicar` no tienen 3 dimensiones o no coinciden con `(PASOS, 12)` (p. ej. si se pasan las 19 columnas incluyendo márgenes), y soporte de `aplicar` sobre un conjunto vacío `(0, 150, 12)` (FR-009 a FR-012, SC-003, SC-004)
- [ ] T013 [P] [US2] Crear `tests/pwr3l/unit/test_pwr3l_escalado.py` (PWR 3L) con pruebas para las 26 variables de `VARIABLES_ENTRADA` y 300 pasos: media y escala iguales (`rtol=1e-12`) a las de `X_train` aplanado; `X_train` escalado con `|media| < 1e-4` y `|std - 1| < 1e-4`; cambiar `val` o `test` no altera los parámetros; variable sin varianza queda con escala `1.0`, salida `0.0` finita y se lista en `variables_sin_varianza`; `aplicar` sobre arreglo vacío `(0, 300, 26)` devuelve `(0, 300, 26)` `float32`; `ValueError` ante entrenamiento vacío o forma distinta de `(N, 300, 26)` (FR-009 a FR-013, SC-003, SC-004)

### Implementation for User Story 2

- [ ] T014 [P] [US2] Actualizar `src/preparacion_datos/escalado.py` para validar que `x_train` sea 3D no vacío de forma `(N, 150, 12)` y que `aplicar` valide forma `(N, 150, 12)` y soporte `N == 0` sin error (depende de T012)
- [ ] T015 [P] [US2] Crear `src/preparacion_pwr3l/escalado.py` con la dataclass `Escalador`, `ajustar_escalador(x_train)` y `aplicar(escalador, x)` para forma `(N, 300, 26)` usando `PASOS` y `VARIABLES_ENTRADA` de `preparacion_pwr3l.config`, ajustando solo con entrenamiento y validando formas y entrenamiento no vacío (depende de T013)
- [ ] T016 [US2] Ejecutar `pytest tests/unit/test_escalado.py tests/pwr3l/unit/test_pwr3l_escalado.py` y comprobar que pasan todas las pruebas de normalización

**Checkpoint**: Normalización exclusiva con entrenamiento verificada en NPPAD (12 variables) y PWR 3L (26 variables).

---

## Phase 5: User Story 3 - El paso medido queda registrado (Priority: P2)

**Goal**: Publicar el paso medido (`paso_segundos`) y la duración de muestra (`duracion_muestra_segundos`) en `metadata.json` y en el reporte impreso de NPPAD, sin usar constantes fijas, y dejar disponible el paso común medido en PWR 3L.

**Independent Test**: Ejecutar `pytest tests/unit/test_reporte.py tests/integration/test_cli_reporte.py` y comprobar que `metadata.json` y el reporte reflejan el paso medido y la duración calculada.

### Tests for User Story 3 (escribir primero; deben fallar)

- [ ] T017 [P] [US3] Ampliar `tests/unit/test_reporte.py` (inicializando `paso_segundos=10` en `construir()`) para comprobar que `Resumen` y `construir_metadata` incluyen `paso_segundos` (tomado de las simulaciones medidas) y `duracion_muestra_segundos == 150 * paso_segundos`, y que `formatear_reporte` muestra el paso medido de `TIME` y la duración en la sección 1 (FR-007, SC-002)
- [ ] T018 [P] [US3] Actualizar `tests/integration/test_cli_reporte.py` para verificar `paso_segundos` y `duracion_muestra_segundos` en `metadata.json` y en el reporte impreso, incluyendo el caso de un dataset sintético con un paso distinto (p. ej. 5 s → duración 750 s) (FR-001, FR-007, SC-002, SC-005)

### Implementation for User Story 3

- [ ] T019 [US3] Actualizar `src/preparacion_datos/reporte.py`, `src/preparacion_datos/salida.py` y `src/preparacion_datos/cli.py` para propagar el `paso_segundos` medido a `Resumen`, calcular `duracion_muestra_segundos`, incluirlos en `metadata.json` y mostrarlos en la sección 1 del reporte impreso, sin importar `PASO_SEGUNDOS` (depende de T009, T017, T018)
- [ ] T020 [US3] Ejecutar `pytest tests/unit/test_reporte.py tests/integration/test_cli.py tests/integration/test_cli_reporte.py` y comprobar que pasan

**Checkpoint**: Las tres historias de usuario están completas y probadas.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificación contra los datasets reales de `IA-Nuclear`, documentación y suite completa.

- [ ] T021 Ampliar `tests/integration/test_dataset_real.py` para verificar que con el dataset real de NPPAD `metadata["paso_segundos"] == 10` y `metadata["duracion_muestra_segundos"] == 1500`, y que en `tests/pwr3l/unit/test_pwr3l_lectura.py` `obtener_paso_comun` devuelve `1` sobre el árbol sintético (SC-002, SC-006)
- [ ] T022 Ejecutar la suite completa de pruebas (`pytest -q`) y las validaciones de `specs/003-normalizacion-paso-muestreo/quickstart.md` comprobando que el 100 % de las pruebas de 001, 002 y 003 pasan (SC-005, SC-006)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias previas.
- **Foundational (Phase 2)**: depende de Phase 1; bloquea US1 y US3.
- **User Story 1 (Phase 3, P1)**: depende de Phase 2.
- **User Story 2 (Phase 4, P1)**: independiente de Phase 2 y de US1 (opera sobre arreglos en memoria); puede ejecutarse en paralelo con US1.
- **User Story 3 (Phase 5, P2)**: depende de US1 (necesita el paso medido por `lectura.py`).
- **Polish (Phase 6)**: depende de US1, US2 y US3.

### Parallel Opportunities

- T001 y T002 en Phase 1; T004 y T005 en Phase 2.
- T006, T007 y T008 (pruebas de US1 en archivos distintos).
- T009 y T010 (implementación de lectura en NPPAD y PWR 3L).
- T012 y T013 (pruebas de US2); T014 y T015 (implementación de escalado en NPPAD y PWR 3L).
- T017 y T018 (pruebas de US3).

## Parallel Example: User Story 2

```text
Task: "Ampliar tests/unit/test_escalado.py (NPPAD)"
Task: "Crear tests/pwr3l/unit/test_pwr3l_escalado.py (PWR 3L)"
Task: "Actualizar src/preparacion_datos/escalado.py"
Task: "Crear src/preparacion_pwr3l/escalado.py"
```

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

1. Completar Phase 1 (Setup) y Phase 2 (Foundational).
2. Completar Phase 3 (US1: medición y validación del paso de muestreo en NPPAD y PWR 3L).
3. Completar Phase 4 (US2: normalización exclusiva con entrenamiento en NPPAD y PWR 3L).
4. Completar Phase 5 (US3: publicación del paso y duración en reporte y `metadata.json`).
5. Completar Phase 6 (validación con datos reales y suite completa).
