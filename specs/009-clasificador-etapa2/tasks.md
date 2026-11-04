# Tasks: Clasificador de Etapa 2 (rama caliente o fría) para PWR 3L

**Input**: Documentos de diseño en `/specs/009-clasificador-etapa2/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ (`cli.md`, `salidas.md`), quickstart.md

**Tests**: Solicitados (constitución): en cada historia las pruebas se escriben **antes** del código.

## Format: `[ID] [P?] [Story] Description`

## Path Conventions

- Código en `src/clasificador_etapa2/`; pruebas en `tests/etapa2/unit/` y `tests/etapa2/integration/`
- Solo se importan `preparacion_pwr3l` y `clasificador_etapa1`; no se modifican
- Las pruebas que necesitan PyTorch empiezan con `pytest.importorskip("torch")`

---

## Phase 1: Setup

- [ ] T001 Modificar `pyproject.toml`: guion `entrenar-etapa2 = "clasificador_etapa2.cli:main"` y `description` que nombre la Etapa 2
- [ ] T002 [P] Crear `src/clasificador_etapa2/__init__.py`, `src/clasificador_etapa2/__main__.py` y `src/clasificador_etapa2/config.py` (clases, canales, ventanas 30/15/3 s, horizonte 60 s, umbral 0,80, UNCERTAIN, NO_APLICA, horizontes, hiperparámetros, semilla, salida, avisos)

---

## Phase 2: Foundational (canales y muestras)

### Tests

- [ ] T003 Crear `tests/etapa2/conftest.py`: corridas sintéticas LOCA/LOCAC (y algunas NORM/ATWS que deben ignorarse) con `serie` (300, 33), una columna PWR propia y pico de PWR/PWNT solo en rama caliente; áreas coherentes con el reparto de 004; diccionario `inicios`; ayudante para escribir un árbol PWR 3L en CSV con columna `PWR`
- [ ] T004 [P] Crear `tests/etapa2/unit/test_etapa2_canales.py`: `desviacion_pico` en una serie conocida (escalón, rampa, máximo que sale de la ventana a los 15 s), causalidad (cambiar datos posteriores a τ no cambia d(τ)), valor inicial restado; `leer_pwr` lee la columna del archivo y falla con `ErrorDatos` si falta PWR o hay un valor no numérico
- [ ] T005 [P] Crear `tests/etapa2/unit/test_etapa2_muestras.py`: solo LOCA/LOCAC; τ desde ceil(inicio); k ≤ 60 en entrenamiento y completo en evaluación; forma (n, 30, 2); etiqueta 0/1; sin inicio → `ValueError` con la corrida

### Implementation

- [ ] T006 Implementar `src/clasificador_etapa2/canales.py`: `desviacion_pico(x)`, `leer_pwr(origen, corrida)` (reutiliza `_leer_tabla`/`_convertir_columna` de 002) y `canales_corrida(origen, corrida)` → (300, 2)
- [ ] T007 Implementar `src/clasificador_etapa2/muestras.py`: `es_rama(corrida)` y `construir_muestras(corridas, series, inicios, entrenamiento)` con `ventanas` y `Muestras` de 005

---

## Phase 3: User Story 1 - Entrenar (P1) 🎯 MVP

### Tests

- [ ] T008 [P] [US1] Crear `tests/etapa2/unit/test_etapa2_entrenamiento.py`: escalador ajustado solo con entrenamiento (cambiar val/test no lo cambia); pesos inversos registrados; aprende en sintéticas (F1 val ≥ 0,9); determinismo con la semilla; error si falta una rama en entrenamiento
- [ ] T009 [P] [US1] Crear `tests/etapa2/integration/test_etapa2_cli.py`: `main` sobre un árbol sintético publica los 4 artefactos, `modelo.json` con clases, canales, escalador, pesos y corridas solo LOCA/LOCAC sin solape entre conjuntos; sin torch → código 3; origen inexistente → código 1; volver a ejecutar reemplaza solo sus artefactos

### Implementation

- [ ] T010 [US1] Implementar `src/clasificador_etapa2/entrenamiento.py`: `ajustar_escalador_canales`, `escalar`, `entrenar` (Bi-LSTM de 005 con 2 clases, pesos, Adam, parada por F1 de validación, determinista)
- [ ] T011 [US1] Implementar `src/clasificador_etapa2/cli.py`: `entrenar_modelo` (cargar 002 → reparto y verificación 004 → inicios 005 → canales → escalador → muestras → entrenar), `publicar` atómico y `main` con códigos 0/1/3

---

## Phase 4: User Story 2 - Evaluar con abstención (P1)

### Tests

- [ ] T012 [P] [US2] Crear `tests/etapa2/unit/test_etapa2_evaluacion.py`: `decidir` con umbral (0,79 → UNCERTAIN, 0,80 → rama); matriz 2 × 3; precisión/exhaustividad/F1/cobertura/exactitud/errores con valores calculados a mano; horizontes con k == h; confirmación 2 s seguidos, rama equivocada confirmada y «sin decisión»; agrupación por área; metas SC-001/SC-002; advertencia de pocas corridas; reporte de texto con el aviso

### Implementation

- [ ] T013 [US2] Implementar `src/clasificador_etapa2/evaluacion.py`: `decidir`, `metricas`, `confirmacion`, `evaluar`, `formatear_reporte`
- [ ] T014 [US2] Integrar la evaluación en `cli.py` (`agregar_reporte`: `reporte.json` y `reporte.txt` con entrenamiento y reparto) y ampliar `test_etapa2_cli.py` para comprobar que todas las corridas de prueba aparecen en el reporte

---

## Phase 5: User Story 3 - Recomendación tras la Etapa 1 (P2)

### Tests

- [ ] T015 [P] [US3] Crear `tests/etapa2/unit/test_etapa2_prediccion.py`: `cargar` + `clasificar` devuelve dos probabilidades que suman 1; UNCERTAIN bajo 0,80; `NO_APLICA` para NORM, TRANS e INCIERTO sin ejecutar el modelo; forma incorrecta o menos de 1 fila → `ValueError`; aviso consultivo

### Implementation

- [ ] T016 [US3] Implementar `src/clasificador_etapa2/prediccion.py`: `Clasificador` y `cargar(ruta)`

---

## Phase 6: Polish

- [ ] T017 [P] Crear `tests/etapa2/integration/test_etapa2_real.py`: entrenamiento corto con el dataset real (omitido sin datos): no modifica el origen, 24/6/5 corridas LOCA/LOCAC, las 5 de prueba en el reporte
- [ ] T018 Ejecutar `entrenar-etapa2` con los datos reales y la suite completa; documentar resultados en `README.md` (sección Etapa 2) y marcar las tareas

---

## Dependencies

Setup → Foundational → US1 → US2 → US3 → Polish. Dentro de cada fase, las pruebas antes del código.
