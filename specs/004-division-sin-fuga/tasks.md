# Tasks: División en entrenamiento, validación y prueba sin fuga de datos (PWR 3L)

**Input**: Documentos de diseño en `/specs/004-division-sin-fuga/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md

**Tests**: Solicitados: la constitución exige pruebas automáticas para todo comportamiento crítico. En cada historia las pruebas se escriben **antes** del código y se comprueba que fallan.

**Organization**: Las tareas se agrupan por historia de usuario para poder implementar y probar cada una por separado.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede ejecutar en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: historia de usuario a la que pertenece (US1, US2, US3)
- Todas las rutas son relativas a la raíz del repositorio

## Path Conventions

- Código PWR 3L en `src/preparacion_pwr3l/`, código NPPAD en `src/preparacion_datos/`; pruebas en `tests/` (PWR 3L en `tests/pwr3l/`)
- Los paquetes NPPAD y PWR 3L no se importan entre sí (principio IV)
- Commits con la forma `feat(004): descripción`; si un commit elimina o reescribe código, añadir el trailer `Causa: requisito|defecto|refactor`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Rutas de los datasets reales y carpeta de pruebas de integración PWR 3L

- [X] T001 Crear `tests/datos_reales.py` con `raiz_ianuclear()` (variable de entorno `IANUCLEAR_DATOS`; si no está, `../IA-Nuclear` respecto de la raíz del repositorio), `ruta_pwr3l()` (`<raíz>/PWR 3L`) y `ruta_nppad()` (`<raíz>/NuclearPowerPlantAccidentData/Operation_csv_data`), sin depender de que existan (research.md decisión 6)
- [X] T002 [P] Crear la carpeta `tests/pwr3l/integration/` y comprobar que `python -m pytest --collect-only -q` sigue sin errores

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Fábrica de corridas en memoria para las pruebas unitarias de las tres historias

**CRITICAL**: Ninguna historia puede empezar hasta terminar esta fase

- [X] T003 Añadir a `tests/pwr3l/conftest.py` una fixture `fabricar` que crea objetos `preparacion_pwr3l.descubrimiento.Corrida` en memoria con `id`, `clase`, `estado` (por defecto `usable`), `area` y `gemela` (por defecto la de `config.GEMELAS`), y un ayudante `corridas_variadas()` con NORM, LOCA/LOCAC con áreas repetidas y únicas, gemelas completas, una gemela con pareja corta y corridas corta, descartada y OOD; sin tocar las fixtures existentes de 002

**Checkpoint**: se pueden escribir las pruebas de las historias

---

## Phase 3: User Story 1 - Agrupar las corridas que no pueden separarse (Priority: P1) MVP

**Goal**: formar los grupos `AREA-<cm2>`, `GEMELAS-<a>-<b>` y `<Rid>` con todas las corridas usables, cada una en exactamente un grupo.

**Independent Test**: formar los grupos con corridas conocidas y comprobar que cada corrida está en un solo grupo, que las LOCA/LOCAC de una misma área comparten grupo y que cada pareja de gemelas comparte grupo.

### Tests for User Story 1 (escribir primero; deben fallar)

- [X] T004 [P] [US1] Crear `tests/pwr3l/unit/test_pwr3l_grupos.py` con pruebas de: (a) LOCA y LOCAC de la misma área en un grupo `AREA-<cm2>`, también con repeticiones dentro de una rama; (b) áreas distintas (p. ej. 7700 y 8500) en grupos distintos; (c) ATWS y TRIP_OK gemelas usables en un grupo `GEMELAS-<a>-<b>` con `<a>`/`<b>` en orden natural de identificador; (d) gemela con pareja corta → grupo individual `<Rid>` y la corta en ningún grupo; (e) NORM → grupo individual; (f) corridas corta, descartada y OOD fuera de todos los grupos; (g) cada corrida usable en exactamente un grupo y `familia` correcta (NORM, LOCA, ATWS); (h) mismo resultado con la lista invertida y orden por familia y clave; (i) LOCA usable sin área → `ErrorDatos` que nombra el archivo; (j) ninguna corrida usable → `ValueError`; (k) con el árbol sintético de 002 (`copia_pwr3l` + `cargar_corridas`), las corridas usables quedan todas agrupadas; (l) agrupar no modifica `estado`, `area`, `gemela` ni `serie` de ninguna corrida (FR-014)
- [X] T005 [US1] Ejecutar `python -m pytest tests/pwr3l/unit/test_pwr3l_grupos.py` y comprobar que T004 **falla** antes de implementar

### Implementation for User Story 1

- [X] T006 [US1] Crear `src/preparacion_pwr3l/grupos.py` con la dataclass `Grupo` (`clave`: «`AREA-<cm2>`, `GEMELAS-<a>-<b>` (orden natural de identificador) o `<Rid>`»; `familia`: «NORM, LOCA o ATWS (`config.FAMILIAS` de su primera corrida)»; `corridas`: «1 o más corridas usables, ordenadas con `clave_orden`; todas de la misma familia»; propiedad `tamano`) y `formar_grupos(corridas)` según research.md decisión 1 y contracts/api.md
- [X] T007 [US1] Ejecutar `python -m pytest tests/pwr3l/unit/test_pwr3l_grupos.py` y comprobar que pasa

**Checkpoint**: los grupos funcionan solos (MVP de la agrupación)

---

## Phase 4: User Story 2 - Repartir los grupos en entrenamiento, validación y prueba (Priority: P1)

**Goal**: repartir los grupos completos por familia hacia 70/15/15, de mayor a menor tamaño con empates sorteados, de forma reproducible.

**Independent Test**: repartir grupos conocidos y comprobar que cada grupo está en un solo conjunto, que el desvío por familia es menor que su grupo más grande y que la misma semilla da el mismo reparto.

### Tests for User Story 2 (escribir primero; deben fallar)

- [X] T008 [P] [US2] Crear `tests/pwr3l/unit/test_pwr3l_particion.py` con pruebas de: (a) `metas(n)` = 0.70·n, 0.15·n, 0.15·n; (b) cada grupo en exactamente un conjunto y `conjunto_de_corrida` con exactamente las corridas usables; (c) cota de FR-008: con 200 combinaciones aleatorias de tamaños de grupo (1 a 8) y semillas, en cada familia y conjunto `|asignadas − metas| < tamaño del grupo más grande de la familia`; (d) orden de mayor a menor: un grupo más grande que la meta de validación, siendo el mayor de su familia, va a `train`; (e) misma semilla → mismo reparto, también con la lista de grupos invertida o barajada; (f) alguna semilla distinta de 42 da otra asignación; (g) `conteos` con las 5 clases y los 3 conjuntos, ceros incluidos, que suman el total de corridas usables; (h) `corridas[conjunto]` ordenadas con `clave_orden`; (i) semilla por defecto 42 y registrada en `Reparto.semilla`; (j) una familia con 1 y con 2 grupos: cada grupo en un conjunto y los conjuntos vacíos de esa familia con 0 en `asignadas`; (k) una clase sin corridas usables aparece con 0 en los tres conjuntos de `conteos`; (l) repartir no modifica `estado`, `area`, `gemela` ni `serie` de ninguna corrida (FR-014)
- [X] T009 [US2] Ejecutar `python -m pytest tests/pwr3l/unit/test_pwr3l_particion.py` y comprobar que T008 **falla** antes de implementar

### Implementation for User Story 2

- [X] T010 [US2] Crear `src/preparacion_pwr3l/particion.py` con `metas(n)`, la dataclass `Reparto` (campos de data-model.md: `semilla`, `grupos`, `conjunto_de_grupo`, `conjunto_de_corrida`, `corridas`, `conteos`, `metas`, `asignadas`) y `repartir(grupos, semilla=SEMILLA)` según research.md decisión 3: un solo `numpy.random.default_rng(semilla)`, familias en orden NORM, LOCA, ATWS, grupos ordenados por clave, posición de sorteo con `permutation`, reparto por tamaño descendente con desempate por sorteo, al conjunto de mayor déficit con desempate train → val → test (depende de T006)
- [X] T011 [US2] Ejecutar `python -m pytest tests/pwr3l/unit/test_pwr3l_particion.py tests/pwr3l/unit/test_pwr3l_grupos.py` y comprobar que pasan

**Checkpoint**: grupos y reparto funcionan; falta la verificación independiente

---

## Phase 5: User Story 3 - Verificar automáticamente que no hay fuga (Priority: P2)

**Goal**: una verificación independiente del reparto PWR 3L y del reparto NPPAD de 001 que detecta cualquier fuga y la describe.

**Independent Test**: verificar un reparto correcto (sin violaciones) y repartos alterados a propósito (cada violación detectada y nombrada).

### Tests for User Story 3 (escribir primero; deben fallar)

- [X] T012 [P] [US3] Crear `tests/pwr3l/unit/test_pwr3l_verificacion.py` con pruebas de `verificar_reparto(corridas, reparto)`: (a) un reparto de `repartir` no lanza nada; (b) corrida en dos conjuntos → `ErrorFuga` que nombra la corrida y los dos conjuntos; (c) área partida → nombra el área, las corridas y sus conjuntos; (d) gemelas separadas → nombra la pareja; (e) corrida corta, descartada u OOD dentro de un conjunto → nombra la corrida y su estado; (f) grupo partido → nombra el grupo; (g) corrida usable sin conjunto → la nombra; (h) varias violaciones a la vez → todas en `ErrorFuga.violaciones` y el mensaje empieza por `FUGA DE DATOS`; (i) `repartir` nunca devuelve un reparto con fuga: si se fuerza una agrupación errónea (área repartida en dos grupos), `repartir` lanza `ErrorFuga`
- [X] T013 [P] [US3] Crear `tests/unit/test_verificacion.py` con pruebas de `preparacion_datos.verificacion.verificar_particion`: (a) la partición de `preparacion_datos.particion.repartir` sobre el dataset sintético (`origen_sintetico` + `cargar_simulaciones`) no lanza nada; (b) simulación en dos conjuntos → `ErrorFuga` que nombra el archivo y los conjuntos; (c) LOCA y LOCAC de igual severidad en conjuntos distintos → nombra la severidad y los archivos; (d) varias violaciones juntas
- [X] T014 [P] [US3] Ampliar `tests/integration/test_cli.py` con una prueba que sustituye `preparacion_datos.cli.repartir` (monkeypatch) por una partición con fuga y comprueba: código de salida 1, `FUGA DE DATOS` en la salida de error y la carpeta de salida sin crear
- [X] T015 [US3] Ejecutar `python -m pytest tests/pwr3l/unit/test_pwr3l_verificacion.py tests/unit/test_verificacion.py tests/integration/test_cli.py` y comprobar que T012–T014 **fallan** antes de implementar

### Implementation for User Story 3

- [X] T016 [P] [US3] Crear `src/preparacion_pwr3l/verificacion.py` con `ErrorFuga` (atributo `violaciones`, mensaje `FUGA DE DATOS: <n> violación(es)` y una línea por violación) y `verificar_reparto(corridas, reparto)` con las reglas a–e de research.md decisión 4, calculadas desde `area`, `gemela` y `estado` de cada corrida, no desde los grupos
- [X] T017 [P] [US3] Crear `src/preparacion_datos/verificacion.py` con su propio `ErrorFuga` y `verificar_particion(particion)` (research.md decisión 5); sin importar nada de `preparacion_pwr3l`
- [X] T018 [US3] Hacer que `repartir` en `src/preparacion_pwr3l/particion.py` llame a `verificar_reparto` con las corridas de los grupos antes de devolver el reparto (depende de T010 y T016)
- [X] T019 [US3] Hacer que `main` en `src/preparacion_datos/cli.py` llame a `verificar_particion` justo después de `repartir` y, ante `ErrorFuga`, escriba el mensaje en la salida de error y devuelva 1 sin publicar nada (depende de T017)
- [X] T020 [US3] Ejecutar `python -m pytest tests/pwr3l tests/unit tests/integration` y comprobar que pasan las tres historias y que las pruebas de 001, 002 y 003 siguen en verde

**Checkpoint**: las tres historias funcionan de forma independiente

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validación con los datasets reales y documentación

- [ ] T021 [P] Crear `tests/pwr3l/integration/test_pwr3l_particion_real.py` (se omite si `datos_reales.ruta_pwr3l()` no existe): 91 corridas usables; 54 grupos (14 `AREA`, 15 `GEMELAS`, 25 individuales) y el grupo `AREA-2000` con 8 corridas; `repartir` sin `ErrorFuga` y `verificar_reparto` sin violaciones con **todas** las corridas reales, incluidas las 18 excluidas (U1); tiempo de agrupar, repartir y verificar menor que 1 s (C1); cota de FR-008 por familia; ninguna de las 9 cortas, 3 descartadas y 6 OOD en un conjunto; las tres familias con al menos una corrida en cada conjunto; mismo reparto en dos ejecuciones y con la lista invertida
- [ ] T022 [P] Crear `tests/integration/test_verificacion_real.py` (se omite si `datos_reales.ruta_nppad()` no existe): `cargar_simulaciones` + `repartir` de 001 + `verificar_particion` sin violaciones, y cada severidad LOCA/LOCAC presente en un solo conjunto (SC-007)
- [ ] T023 [P] Añadir al `README.md` una sección «División sin fuga de datos (funcionalidad 004)» en español: qué garantiza, cómo se usa desde Python (`formar_grupos`, `repartir`, `verificar_reparto`), la verificación añadida a `preparar-datos` y la variable `IANUCLEAR_DATOS` para las pruebas reales, sin tocar las demás secciones
- [ ] T024 Ejecutar las validaciones de `specs/004-division-sin-fuga/quickstart.md` con los datasets reales y anotar los conteos obtenidos en su sección «Resultados obtenidos»
- [ ] T025 Ejecutar la suite completa (`python -m pytest -q`, con `IANUCLEAR_DATOS` apuntando a los datos reales) y comprobar que todo pasa

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias
- **Foundational (Phase 2)**: depende de Setup; bloquea las historias
- **US1 (Phase 3)**: tras Foundational
- **US2 (Phase 4)**: `repartir` usa `Grupo` (T010 depende de T006); sus pruebas pueden escribirse en paralelo con US1
- **US3 (Phase 5)**: la verificación (T016, T017) no depende de US1/US2; su integración en `repartir` (T018) sí depende de T010
- **Polish (Phase 6)**: tras las tres historias

### Within Each User Story

- Pruebas primero y comprobar que fallan (T005, T009, T015)
- Implementación → integración → ejecución de pruebas (T007, T011, T020)

### Parallel Opportunities

- Setup: T002 con T001
- US3, pruebas: T012, T013 y T014 (archivos distintos)
- US3, implementación: T016 y T017 (paquetes distintos)
- Polish: T021, T022 y T023

---

## Parallel Example: User Story 3

```bash
# Pruebas de la verificación, juntas:
Task: "Verificación PWR 3L en tests/pwr3l/unit/test_pwr3l_verificacion.py"
Task: "Verificación NPPAD en tests/unit/test_verificacion.py"
Task: "Fuga en preparar-datos en tests/integration/test_cli.py"

# Implementación de las dos verificaciones, juntas:
Task: "verificar_reparto en src/preparacion_pwr3l/verificacion.py"
Task: "verificar_particion en src/preparacion_datos/verificacion.py"
```

---

## Implementation Strategy

### MVP First

1. Phase 1 y Phase 2
2. Phase 3 (US1): grupos sin fuga
3. Phase 4 (US2): reparto equilibrado y reproducible
4. **Parar y validar** con el árbol sintético

### Incremental Delivery

1. Setup + Foundational → fábrica de corridas
2. US1 → grupos
3. US2 → reparto
4. US3 → verificación independiente en PWR 3L y NPPAD
5. Polish → datasets reales, README y quickstart

---

## Notes

- Esta funcionalidad cubre las tareas T012, T013, T016 y T017 de `specs/002-preprocesamiento-pwr3l/tasks.md`; el escalado PWR 3L (T014, T018 de 002) ya lo hizo 003. Salida, reporte y comando PWR 3L siguen en 002 (KAN-18).
- [P] = archivos distintos, sin dependencias pendientes
- Hacer commit tras cada grupo lógico, con la forma `feat(004): descripción`
