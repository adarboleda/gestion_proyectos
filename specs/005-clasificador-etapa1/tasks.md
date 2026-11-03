# Tasks: Clasificador de Etapa 1 (familia del evento) para PWR 3L

**Input**: Documentos de diseño en `/specs/005-clasificador-etapa1/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ (`cli.md`, `salidas.md`), quickstart.md

**Tests**: Solicitados: la constitución exige pruebas automáticas para todo comportamiento crítico. En cada historia las pruebas se escriben **antes** del código y se comprueba que fallan.

**Organization**: Las tareas se agrupan por historia de usuario para poder implementar y probar cada una por separado.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: se puede ejecutar en paralelo (archivos distintos, sin dependencias pendientes)
- **[Story]**: historia de usuario a la que pertenece (US1, US2, US3)
- Todas las rutas son relativas a la raíz del repositorio

## Path Conventions

- Código en `src/clasificador_etapa1/`; pruebas en `tests/etapa1/unit/` y `tests/etapa1/integration/`
- Solo se importa `preparacion_pwr3l`, nunca `preparacion_datos` (principio IV)
- Las pruebas que necesitan PyTorch empiezan con `pytest.importorskip("torch")`
- Commits `feat(005): descripción`; con el trailer `Causa: requisito|defecto|refactor` si se elimina o reescribe código

---

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 Modificar `pyproject.toml`: extra opcional `modelo = ["torch>=2.2"]`, guion `entrenar-etapa1 = "clasificador_etapa1.cli:main"` y `description` que nombre también el clasificador de Etapa 1; añadir `modelos/` al `.gitignore`
- [X] T002 [P] Crear `src/clasificador_etapa1/__init__.py` (docstring en español), `src/clasificador_etapa1/__main__.py` (llama a `clasificador_etapa1.cli.main()` y sale con su código) y las carpetas `tests/etapa1/unit/` y `tests/etapa1/integration/`
- [X] T003 Instalar PyTorch para CPU (`--index-url https://download.pytorch.org/whl/cpu`) y el paquete en modo editable; comprobar que `python -m pytest --collect-only -q` no da errores

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Inicio de los eventos y construcción de las muestras, que usan las tres historias

### Tests (escribir primero; deben fallar)

- [X] T004 Crear `tests/etapa1/conftest.py` con una fixture `sinteticas` que construye en memoria corridas `preparacion_pwr3l.descubrimiento.Corrida` usables con `serie` (300, 33): ruido pequeño alrededor de un estado estable y, desde un instante de inicio, una señal distinta por familia (LOCA: cae `P` y sube `WECS`; ATWS/TRIP_OK: cae `WFWA`/`WFWB` y sube `TAVG`), con NORM, LOCA, LOCAC, ATWS y TRIP_OK, áreas y gemelas coherentes, un diccionario `inicios` y un reparto (`formar_grupos` + `repartir` de 004); y un ayudante para escribir un árbol PWR 3L mínimo con `validacion.json`, `validacion_corridas.csv` y una carpeta manual `_t<n>` sin validación
- [X] T005 [P] Crear `tests/etapa1/unit/test_etapa1_eventos.py`: inicio desde `validacion.json` (automáticas); desde `validacion_corridas.csv` por identificador, ignorando filas `[mitigation]`; desde `_t<n>` del nombre de la carpeta si no hay validación; `None` para NORM; corrida de evento sin ninguna fuente → `ErrorDatos` que nombra el archivo; `inicios_evento(origen, corridas)` cubre todas las usables
- [X] T006 [P] Crear `tests/etapa1/unit/test_etapa1_muestras.py`: una muestra por τ = 5…299 en validación/prueba; ventana = filas [τ − 29, τ] y, con τ < 29, relleno repitiendo la fila 0; etiqueta NORM si τ < inicio y familia si τ ≥ inicio, con el inicio redondeado hacia arriba al segundo (un inicio de 24,5 s etiqueta como evento desde τ = 25 y da k = 0 en τ = 25); `k = τ − inicio` y `nan` en NORM; en entrenamiento solo NORM completas, τ < inicio y 0 ≤ k ≤ 60; formas y tipos de data-model.md («`x` (n, 30, 26) float32», «`y` (n,) int64», «`tau` (n,) int64», «`k` (n,) float64»); todas las muestras de un conjunto vienen de corridas de ese conjunto; ninguna fila posterior a τ en su ventana
- [X] T007 Ejecutar `python -m pytest tests/etapa1/unit/test_etapa1_eventos.py tests/etapa1/unit/test_etapa1_muestras.py` y comprobar que **fallan**

### Implementation

- [X] T008 Crear `src/clasificador_etapa1/config.py`: `FAMILIAS = ("NORM", "LOCA", "TRANS")`, clase → familia (NORM→NORM, LOCA/LOCAC→LOCA, ATWS/TRIP_OK→TRANS), `VENTANA_S = 30`, `TAU_MIN_S = 5`, `HORIZONTE_ENTRENAMIENTO_S = 60`, `UMBRAL = 0.80`, `CONFIRMACION_S = 2`, `HORIZONTES_S = (1, 2, 3, 5, 10, 20, 30)`, hiperparámetros (32 unidades, 1 capa, dropout 0.3, lr 1e-3, weight decay 1e-4, lote 256, 40 épocas, paciencia 6), `SEMILLA = 42`, `SALIDA_POR_DEFECTO = "modelos/etapa1"` y el texto del aviso consultivo
- [X] T009 Crear `src/clasificador_etapa1/eventos.py` con `inicio_evento(origen, corrida)` e `inicios_evento(origen, corridas)` según research.md §2
- [X] T010 Crear `src/clasificador_etapa1/muestras.py` con la dataclass `Muestras` y `construir_muestras(corridas, series_escaladas, inicios, entrenamiento: bool)` según research.md §3
- [X] T011 Ejecutar las pruebas de T005 y T006 y comprobar que pasan

**Checkpoint**: inicios y muestras listos

---

## Phase 3: User Story 1 - Entrenar el clasificador de las tres familias (Priority: P1) MVP

**Goal**: entrenar la Bi-LSTM con pesos de clase y parada por validación, de forma determinista, y guardar el modelo y su configuración.

**Independent Test**: entrenar con las corridas sintéticas y comprobar que se guardan los artefactos, que solo participan entrenamiento y validación y que dos ejecuciones con la misma semilla son idénticas.

### Tests for User Story 1 (escribir primero; deben fallar)

- [X] T012 [P] [US1] Crear `tests/etapa1/unit/test_etapa1_entrenamiento.py`: (a) `pesos_clase(y)` = `N / (3 · n_c)`, mayores para las familias raras; (b) la Bi-LSTM devuelve (lote, 3) y su salida con softmax suma 1; (c) con las corridas sintéticas el F1 macro de validación supera 0,9; (d) dos entrenamientos con la misma semilla dan los mismos pesos de la red y el mismo historial; (e) el modelo devuelto es el de la mejor época de validación y la parada temprana respeta la paciencia; (f) el entrenamiento no recibe muestras de prueba
- [X] T013 [P] [US1] Crear `tests/etapa1/integration/test_etapa1_cli.py` (sustituye `cargar_corridas` e `inicios_evento` del módulo `cli` por las corridas sintéticas): `main([...])` devuelve 0 y publica `modelo.pt` y `modelo.json` con las claves de data-model.md; `modelo.json["corridas"]` sin repeticiones entre conjuntos; el escalador coincide con el ajuste sobre las series de entrenamiento; dos ejecuciones con la misma semilla dan `modelo.json` idéntico; volver a ejecutar reemplaza los artefactos sin tocar otros archivos; una corrida de evento sin inicio → código 1 y la salida sin crear; fuga en el reparto → código 1; sin PyTorch (importación simulada que falla) → código 3 y la salida sin crear
- [X] T014 [US1] Ejecutar `python -m pytest tests/etapa1/unit/test_etapa1_entrenamiento.py tests/etapa1/integration/test_etapa1_cli.py` y comprobar que **fallan**

### Implementation for User Story 1

- [X] T015 [P] [US1] Crear `src/clasificador_etapa1/modelo.py` con `BiLSTMEtapa1` (research.md §4: LSTM bidireccional de 1 capa y 32 unidades, último estado hacia delante y hacia atrás más la media temporal, dropout 0.3, lineal a 3)
- [X] T016 [US1] Crear `src/clasificador_etapa1/entrenamiento.py` con `pesos_clase`, `fijar_semilla` y `entrenar(muestras_train, muestras_val, hiperparametros, semilla)` → modelo, historial y mejor época (research.md §5) (depende de T015)
- [X] T017 [US1] Crear `src/clasificador_etapa1/cli.py` con `main(argv)`: opciones de contracts/cli.md; cargar → agrupar → repartir → `verificar_reparto(corridas, reparto)` → inicios → escalador de 003 ajustado con las series de entrenamiento → muestras → entrenar → publicar `modelo.pt` y `modelo.json` en una carpeta temporal y reemplazar solo esos archivos; códigos 1 (datos o fuga) y 3 (sin PyTorch) (depende de T009, T010 y T016)
- [X] T018 [US1] Ejecutar las pruebas de T012 y T013 y comprobar que pasan

**Checkpoint**: el modelo se entrena y se guarda (MVP)

---

## Phase 4: User Story 2 - Evaluar qué tan rápido y qué tan bien decide (Priority: P1)

**Goal**: reporte de evaluación sobre prueba: métricas globales y por horizonte, tiempos de confirmación, falsas alarmas y metas.

**Independent Test**: evaluar predicciones conocidas y comprobar cada métrica; con el comando, comprobar que el reporte tiene una entrada de detección por corrida de evento de prueba.

### Tests for User Story 2 (escribir primero; deben fallar)

- [X] T019 [P] [US2] Crear `tests/etapa1/unit/test_etapa1_evaluacion.py` con probabilidades construidas a mano: (a) matriz de confusión, precisión, exhaustividad y F1 por familia y F1 macro; (b) horizonte h: exhaustividad LOCA y TRANS en k = h y F1 macro con las muestras NORM (research.md §6); (c) F1 macro de los primeros 30 s; (d) confirmación: 2 segundos seguidos ≥ 0,80, con τ − 1 ≥ inicio; un solo segundo no confirma; «no detectada» → `None`; (e) tiempos por familia y por área de rotura; (f) falsas alarmas: instantes, episodios y corridas en corridas NORM y en tramos previos; una predicción con probabilidad < 0,80 no cuenta; (g) metas SC-001 (LOCA ≥ 50 cm² en ≤ 10 s), SC-002 (0 falsas alarmas en corridas NORM) y SC-003 (F1 macro de los primeros 30 s ≥ 0,80) con su valor y si se cumplen; si no hay corridas que la evalúen (p. ej. ninguna LOCA ≥ 50 cm² en prueba), la meta se informa como «sin datos»; (h) una familia sin corridas de prueba aparece con cero y sin métricas inventadas
- [X] T020 [US2] Ampliar `tests/etapa1/integration/test_etapa1_cli.py`: `reporte.json` y `reporte.txt` publicados; una entrada de detección por corrida de evento de prueba; la suma de la matriz de confusión es el número de muestras de prueba; el reporte impreso tiene el aviso consultivo, las métricas, la tabla de horizontes, las detecciones, las falsas alarmas y las metas
- [X] T021 [US2] Ejecutar `python -m pytest tests/etapa1/unit/test_etapa1_evaluacion.py tests/etapa1/integration/test_etapa1_cli.py` y comprobar que **fallan** las pruebas nuevas

### Implementation for User Story 2

- [X] T022 [US2] Crear `src/clasificador_etapa1/evaluacion.py` con `metricas`, `por_horizonte`, `tiempos_confirmacion`, `falsas_alarmas`, `metas` y `evaluar(modelo, muestras_prueba, corridas, inicios)` → diccionario del reporte (data-model.md, «Reporte de evaluación»), y `formatear_reporte(reporte)` → texto
- [X] T023 [US2] Integrar en `src/clasificador_etapa1/cli.py`: evaluar en prueba, publicar `reporte.json` y `reporte.txt` junto al modelo e imprimir el reporte (depende de T017 y T022)
- [X] T024 [US2] Ejecutar `python -m pytest tests/etapa1` y comprobar que pasan

**Checkpoint**: entrenamiento y evaluación completos

---

## Phase 5: User Story 3 - Obtener una recomendación para datos nuevos (Priority: P2)

**Goal**: cargar el modelo guardado y clasificar una secuencia con salida consultiva.

**Independent Test**: cargar un modelo guardado, clasificar una serie y comprobar probabilidades, recomendación o «INCIERTO» y aviso.

### Tests for User Story 3 (escribir primero; deben fallar)

- [X] T025 [P] [US3] Crear `tests/etapa1/unit/test_etapa1_prediccion.py`: con un modelo entrenado y publicado sobre las corridas sintéticas, `cargar(ruta).clasificar(serie)` devuelve tres probabilidades que suman 1; la recomendación es la familia más probable si ≥ 0,80 y «INCIERTO» si no (forzando probabilidades bajas); el aviso es el texto consultivo; el resultado coincide con escalar con `modelo.json["escalador"]` y pasar la ventana al modelo; serie que no es (T, 26) o con T < 5 → `ValueError`
- [X] T026 [US3] Ejecutar `python -m pytest tests/etapa1/unit/test_etapa1_prediccion.py` y comprobar que **falla**

### Implementation for User Story 3

- [X] T027 [US3] Crear `src/clasificador_etapa1/prediccion.py` con `cargar(ruta)` y `Clasificador.clasificar(serie)` (research.md §10; contracts/salidas.md)
- [X] T028 [US3] Ejecutar `python -m pytest tests/etapa1` y comprobar que pasan las tres historias

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T029 [P] Crear `tests/etapa1/integration/test_etapa1_real.py` (se omite sin `datos_reales.ruta_pwr3l()` o sin PyTorch): `main` con `--epocas 2` sobre el dataset real en una carpeta temporal devuelve 0; `modelo.json["corridas"]` con 63 / 15 / 13; una entrada de detección por corrida de evento de prueba; el hash de los archivos del origen es igual antes y después (FR-015)
- [X] T030 [P] Añadir al `README.md` una sección «Clasificador de Etapa 1 (funcionalidad 005)»: qué distingue, instalación de PyTorch, `entrenar-etapa1`, artefactos, cómo leer el reporte y uso de `clasificar`, sin tocar las demás secciones
- [X] T031 Entrenar con el dataset real y la configuración por defecto, repetir en otra carpeta para comprobar la reproducibilidad, medir el tiempo y anotar los resultados (métricas, horizontes, detecciones, falsas alarmas y metas) en la sección «Resultados obtenidos» de `specs/005-clasificador-etapa1/quickstart.md`
- [X] T032 Ejecutar la suite completa (`python -m pytest -q`, con `IANUCLEAR_DATOS`) y comprobar que todo pasa

---

## Dependencies & Execution Order

- **Setup (Phase 1)** → **Foundational (Phase 2)** → historias
- **US1 (Phase 3)**: tras Foundational
- **US2 (Phase 4)**: la evaluación (T022) solo necesita un modelo y muestras; su integración en el comando (T023) depende de T017
- **US3 (Phase 5)**: necesita un modelo publicado (US1)
- **Polish (Phase 6)**: tras las tres historias

### Parallel Opportunities

- T002 con T001
- Foundational: T005 y T006
- US1: T012 y T013 (pruebas); T015 en paralelo con las pruebas de US2
- US2: T019 en paralelo con la implementación de US1
- Polish: T029 y T030

---

## Implementation Strategy

1. Setup + Foundational → inicios y muestras
2. US1 → modelo entrenado y guardado (MVP)
3. US2 → reporte de evaluación
4. US3 → clasificación consultiva
5. Polish → dataset real, README y resultados

---

## Notes

- La Etapa 2 (rama caliente o fría; ATWS o TRIP_OK) queda fuera.
- [P] = archivos distintos, sin dependencias pendientes

---

## Phase 7: Convergence

- [X] T033 Añadir a cada horizonte de `por_horizonte` en `src/clasificador_etapa1/evaluacion.py` las métricas completas por familia (precisión, exhaustividad, F1 y matriz de confusión con `metricas()` sobre las muestras del horizonte), conservar la tabla resumida del texto y probarlo en `tests/etapa1/unit/test_etapa1_evaluacion.py` per FR-009, US2/AC1 (partial)
- [X] T034 Imprimir en `formatear_reporte` (`src/clasificador_etapa1/evaluacion.py`) el resumen del tiempo de confirmación de LOCA por área de rotura y el reparto (corridas y muestras por conjunto), y comprobarlo en `tests/etapa1/integration/test_etapa1_cli.py` per US2/AC4, contracts/cli.md (partial)
- [X] T035 Añadir `reporte["validacion"]` con el F1 macro y la mejor época de validación en `src/clasificador_etapa1/cli.py` y comprobarlo en `tests/etapa1/integration/test_etapa1_cli.py` per data-model.md: Reporte de evaluación (partial)
