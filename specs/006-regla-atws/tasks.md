# Tasks: Regla determinista de ATWS

**Input**: Documentos de diseño en `/specs/006-regla-atws/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ (`cli.md`, `salidas.md`), quickstart.md

**Tests**: en cada historia las pruebas se escriben **antes** que el código y se comprueba que fallan.

## Format: `[ID] [P?] [Story] Description`

- Código en `src/regla_atws/`; pruebas en `tests/atws/unit/` y `tests/atws/integration/` con prefijo `test_atws_`
- Commits `feat(006)`, `test(006)`, `docs(006)`; trailer `Causa:` si se reescribe código

---

## Phase 1: Setup

- [ ] T001 Añadir a `pyproject.toml` el guion `evaluar-regla-atws = "regla_atws.cli:main"` y nombrar 006 en `description`
- [ ] T002 [P] Crear `src/regla_atws/__init__.py` y `src/regla_atws/__main__.py`; crear `tests/atws/unit/` y `tests/atws/integration/`
- [ ] T003 [P] Añadir `resultados_regla_atws/` al `.gitignore`

---

## Phase 2: Foundational (registro de eventos y señal de disparo)

### Tests (escribir primero; deben fallar)

- [ ] T004 Crear `tests/atws/conftest.py` con un árbol PWR 3L sintético que `preparacion_pwr3l` acepte: las cinco clases, `config.json` coherentes con la tabla de gemelas y `transientlist.dat` por corrida. Los perfiles de PWNT son: TRIP_OK cae a 6 % tras la demanda + retardo; ATWS se queda alto (40–90 %); un ATWS sin señal en el registro sube a ≥ 118 % (extracción de barras); LOCA con «Scram Lo RX Press» y scram; NORM sin señal. Ayudantes para quitar o duplicar un `.dat` y para cambiar el PWNT de una corrida
- [ ] T005 [P] Crear `tests/atws/unit/test_atws_eventos.py`. Casos:
  - lectura de líneas `NNNNNN.N sec, texto` en latin-1;
  - tipo normalizado (`Low SG Level 17.0 %` → `low sg level`, `Turbine Trip Control Change: True` → `turbine trip`, `Scram High Prz Level93.4 %` → `scram high prz level`);
  - primera señal sin contar `Reactor Scram`;
  - alto flujo cuando llega antes o no hay señal;
  - instante del scram;
  - errores sin `.dat`, con dos `.dat` y con `.dat` ilegible

### Implementation

- [ ] T006 Crear `src/regla_atws/config.py`: señales de disparo, `PUNTO_ALTO_FLUJO = 118.0`, `ESPERA_S = 2.0`, `META_S = 3.0`, salida por defecto y aviso consultivo
- [ ] T007 Crear `src/regla_atws/eventos.py` con `Senal`, `leer_eventos(origen, corrida)`, `tipo_senal(texto)`, `primera_senal(eventos, pwnt)` e `instante_scram(eventos)` (research §1 y §6)
- [ ] T008 Ejecutar `pytest tests/atws/unit/test_atws_eventos.py`

---

## Phase 3: User Stories 1 y 2 — recomendación por corrida, calibración solo con entrenamiento y evaluación (P1)

### Tests (escribir primero; deben fallar)

- [ ] T009 [P] [US1] Crear `tests/atws/unit/test_atws_regla.py`. Casos:
  - retardo por tipo = el mayor de entrenamiento; un tipo no visto recibe el mayor de todos;
  - umbral = punto medio cuando hay separación, y el mayor que no omite ATWS cuando se solapan, contando las falsas alarmas;
  - evaluación con flujo caído, flujo alto, sin demanda y decisión fuera de la ventana;
  - `t_decision = ⌈t_d + 2⌉` y tiempo de detección desde la demanda en [2, 3) s;
  - la calibración solo recibe corridas de entrenamiento
- [ ] T010 [US2] Crear `tests/atws/integration/test_atws_cli.py`. Casos:
  - código 0 y publica `regla.json` y `evaluacion.csv`;
  - una fila por corrida usable, con su conjunto de 004;
  - cambiar el PWNT de una corrida de validación o prueba no cambia `regla.json`;
  - todos los ATWS sintéticos detectados y ningún TRIP_OK, LOCA ni NORM como ATWS;
  - reproducible byte a byte;
  - sin `.dat` → código 1 sin salida;
  - origen sin cambios;
  - `python -m regla_atws`

### Implementation

- [ ] T011 [US1] Crear `src/regla_atws/regla.py` con `Regla`, `Resultado`, `calibrar_retardos`, `calibrar_umbral`, `calibrar` y `evaluar_corrida` (research §2–§4)
- [ ] T012 [US2] Crear `src/regla_atws/cli.py`: corridas (002), grupos y reparto con verificación (004), señales, calibración con train, evaluación de todas y publicación de `regla.json` y `evaluacion.csv` (depende de T007 y T011)
- [ ] T013 Ejecutar `pytest tests/atws`

---

## Phase 4: User Story 3 — reporte para el Hito 1 (P2)

### Tests (escribir primero; deben fallar)

- [ ] T014 [P] [US3] Crear `tests/atws/unit/test_atws_reporte.py`. Casos:
  - tabla por conjunto que cuadra con los resultados;
  - errores nombrados;
  - tiempos y meta de 3 s;
  - advertencia por señal no vista en entrenamiento;
  - aviso consultivo en el reporte y en `resumen.json`;
  - las 8 secciones en orden

### Implementation

- [ ] T015 [US3] Crear `src/regla_atws/reporte.py` con `resumir(resultados, regla)` y `formatear_reporte(...)` (contracts/cli.md y salidas.md)
- [ ] T016 [US3] Integrar en `src/regla_atws/cli.py`: publicar `resumen.json` e imprimir el reporte
- [ ] T017 Ejecutar `pytest tests/atws`

---

## Phase 5: Polish

- [ ] T018 Crear `tests/atws/integration/test_atws_dataset_real.py` (se omite sin datos). Casos:
  - 91 filas (63/15/13) y 18 ATWS;
  - la regla calibrada separa entrenamiento;
  - R97 tiene demanda por alto flujo;
  - los TRIP_OK por turbina tienen retardo de 5 s;
  - origen sin cambios
- [ ] T019 [P] Añadir al `README.md` la sección «Regla determinista de ATWS (funcionalidad 006)»
- [ ] T020 Ejecutar `evaluar-regla-atws` con la carpeta real y anotar el resultado en `quickstart.md`
- [ ] T021 Ejecutar la suite completa y comprobar que todo pasa

---

## Dependencies

Setup → Foundational → US1/US2 → US3 → Polish. Se pueden hacer en paralelo T002 con T003, T005 tras T004, T009 con T010 y T019 con T018.
