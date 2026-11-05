# Tasks: Documentación del dataset (README de la Fase 1 y metadatos)

**Input**: Design documents from `specs/010-documentacion-dataset/`  
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/documentacion.md`  
**Tests**: `tests/documentacion/test_metadata_json.py`, `tests/documentacion/test_readme_fase1.py`  
**Estado**: Completado (12/12 tareas finalizadas, 13/13 pruebas en verde)

---

## Phase 1: Setup y Suite de Pruebas Automatizadas (TDD Red)

- [x] T001 Crear paquete de pruebas `tests/documentacion/__init__.py` y `tests/documentacion/conftest.py` con fixtures y rutas al proyecto
- [x] T002 [P] Crear `tests/documentacion/test_metadata_json.py` con pruebas de esquema JSON, presencia de claves obligatorias, tipos, variables y limitaciones (falla antes de crear metadata.json)
- [x] T003 [P] Crear `tests/documentacion/test_readme_fase1.py` con pruebas de presencia de secciones obligatorias, origen, planta, 12 variables, 7 márgenes, conteos y limitaciones en `docs/README_FASE1.md` (falla antes de crear README_FASE1.md)

---

## Phase 2: User Story 1 - Origen de los Datos y Modelo de Planta (Priority: P1)

- [x] T004 [US1] Redactar en `docs/README_FASE1.md` la sección de antecedentes, procedencia del dataset NPPAD (Universidad Tsinghua, Sci Data 2022), software PCTRAN y licenciamiento MIT
- [x] T005 [US1] Redactar en `docs/README_FASE1.md` la descripción técnica del modelo de planta: reactor PWR de 2 lazos, potencia nominal al 100 %, circuito primario RCS, presurizador, generadores de vapor y sistemas de salvaguardias ECCS

---

## Phase 3: User Story 2 - Variables de Planta y Márgenes Térmicos (Priority: P1)

- [x] T006 [US2] Tabular y describir en `docs/README_FASE1.md` las 12 variables de entrada normalizadas para los modelos Bi-LSTM (P, TAVG, THA, TCA, WRCA, WRCB, LVPZ, LVCR, PWNT, PWR, WECS, WLR), con descripción física, unidades e indicación de escalado en train
- [x] T007 [US2] Tabular y describir en `docs/README_FASE1.md` las 7 variables de margen térmico (DNBR, TPCT, SCMA, SCMB, TSAT, FRCL, FRZR), con categorías (márgenes e indicadores de daño), unidades físicas reales y garantía de no normalización
- [x] T008 [US2] Redactar en `docs/README_FASE1.md` la contextualización de las variables seleccionadas frente al catálogo de 97 parámetros generados por PCTRAN

---

## Phase 4: User Story 3 - Conteos por Clase, Partición y Limitaciones (Priority: P1)

- [x] T009 [US3] Detallar en `docs/README_FASE1.md` los conteos de archivos base (1 NORM, 100 LOCA, 100 LOCAC, 1 ATWS), corrección de carpetas (`Normal` -> NORM) y estrategias de partición sin fuga (group split vs bloques temporales)
- [x] T010 [US3] Declarar exhaustivamente en `docs/README_FASE1.md` las limitaciones conocidas del dataset (NORM sin test, autocorrelación en archivos únicos, fuerte desbalance, generalización acotada, padding y alcance de 12 canales)
- [x] T011 [US3] Construir y validar el archivo `data_processed/metadata.json` con el esquema canónico completo (features, márgenes, mapeo, splits, conteos y limitaciones)

---

## Phase 5: Integración, Verificación y Polish

- [x] T012 Actualizar el `README.md` principal en la raíz agregando la sección de la Fase 1 y enlaces directos; ejecutar la suite de pruebas automatizadas completa y verificar 0 regresiones en el repositorio
