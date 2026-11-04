# Tasks: Tiempo de detección desde la falla (PWR 3L)

**Input**: Documentos de diseño en `/specs/008-tiempo-desde-falla/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ (`cli.md`, `salidas.md`), quickstart.md

**Tests**: Solicitados (constitución): en cada historia las pruebas se escriben antes del código y se comprueba que fallan.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: archivos distintos, sin dependencias pendientes · **[Story]**: US1, US2, US3
- Código en `src/tiempo_deteccion/`; pruebas en `tests/tiempo/unit/` y `tests/tiempo/integration/`
- No se modifican `clasificador_etapa1` (005) ni `regla_atws` (006): solo se importan
- Commits `feat(008): …`; trailer `Causa:` si se elimina o reescribe código

---

## Phase 1: Setup

- [X] T001 Añadir a `pyproject.toml` el guion `medir-tiempo-deteccion = "tiempo_deteccion.cli:main"` y `resultados_tiempo_deteccion/` al `.gitignore`; reinstalar en modo editable
- [X] T002 [P] Crear `src/tiempo_deteccion/__init__.py`, `src/tiempo_deteccion/__main__.py` y las carpetas `tests/tiempo/unit/` y `tests/tiempo/integration/`

---

## Phase 2: Foundational

- [X] T003 Crear `tests/tiempo/conftest.py`: (a) ayudante que escribe un árbol PWR 3L mínimo con registros `.dat` y `config.json` de cada tipo (FWIV, RCP-A trip, Turbine Trip, AFW, LOCA automática `1:100:50`, LOCA manual `_t60`, extracción de barras con `Scram High Flux`, falla 9 con retardo no cumplido, corrida sin fuente) más su `validacion.json`; (b) fixture de sesión que entrena y publica un modelo de 005 sobre las corridas sintéticas de `tests/etapa1/conftest.py` (cargado por ruta con `importlib`) en una carpeta temporal, con `entrenar-etapa1 --epocas 4`
- [X] T004 Crear `src/tiempo_deteccion/config.py`: `META_DIAGNOSTICO_S = 10`, `META_ATWS_S = 3`, `TOLERANCIA_INCIERTA_S = 2`, patrones del iniciador del registro (research.md §1), falla excluida «8», `SALIDA_POR_DEFECTO = "resultados_tiempo_deteccion"`, `MODELO_POR_DEFECTO = "modelos/etapa1"`, archivos de salida y aviso consultivo

---

## Phase 3: User Story 1 - Saber cuándo ocurrió la falla en cada corrida (Priority: P1) MVP

**Goal**: instante de la falla de cada corrida de evento, con fuente, inicio del validador e incertidumbre.

**Independent Test**: con el árbol sintético, cada corrida da el instante y la fuente esperados, y las inciertas quedan marcadas.

- [X] T005 [P] [US1] Crear `tests/tiempo/unit/test_tiempo_falla.py`: (a) ATWS/TRIP_OK con `FWIV #n Position Change: 0%` → instante de la primera línea con t > 0 y fuente «registro»; las líneas en t = 0 se ignoran; (b) `RCP-A trip`, `Turbine Trip Control Change: True` y `AFW Turbine Valve #1 Position Change: 100%` → «registro»; (c) LOCA automática `fallas=1:100:50` → 50 «programado»; con `1:500:30;6:0:30` → 30; la falla 8 se ignora (`7:0:50;8:0:0` sin línea → 50); (d) LOCA manual `_t60` → 60 «programado»; (e) extracción de barras: `Scram High Flux` no es iniciador → instante programado; una LOCA cuyo registro tiene `Turbine Trip Control Change: True` (consecuencia del scram) → instante programado, porque el registro solo se busca en ATWS y TRIP_OK; (f) inicio del validador más de 2 s antes del instante → `incierta = True` con motivo; (g) sin ninguna fuente → `t = None`, `incierta`; (h) NORM → sin instante; (i) `instantes_falla(origen, corridas)` cubre todas las corridas de evento usables
- [X] T006 [US1] Ejecutar `python -m pytest tests/tiempo/unit/test_tiempo_falla.py` y comprobar que **falla**
- [X] T007 [US1] Crear `src/tiempo_deteccion/falla.py` con la dataclass `InstanteFalla` (campos de data-model.md) e `instante_falla` / `instantes_falla` según research.md §1–§2 (usa `regla_atws.eventos.leer_eventos` y `clasificador_etapa1.eventos.inicios_evento`)
- [X] T008 [US1] Ejecutar las pruebas de T005 y comprobar que pasan

---

## Phase 4: User Story 2 - Medir segundo a segundo cuánto tarda el diagnóstico desde la falla (Priority: P1)

**Goal**: reproducción causal con el modelo de 005, tiempos de diagnóstico y de ATWS, metas, falsas alarmas y publicación.

**Independent Test**: con probabilidades y decisiones conocidas, los tiempos, metas y falsas alarmas son los esperados; el comando publica los resultados.

- [X] T009 [P] [US2] Crear `tests/tiempo/unit/test_tiempo_reproduccion.py`: (a) `verificar_modelo` acepta el modelo cuyo `corridas` coincide con el reparto y lanza `ErrorModelo` si no coincide o no existe; (b) `reproducir` da por corrida 295 τ (5…299) y probabilidades (n, 3) que suman 1; (c) la probabilidad de cada τ no cambia si se alteran los datos posteriores a τ (causalidad); (d) `confirmada` marca la familia con ≥ 0,80 en τ − 1 y τ
- [X] T010 [P] [US2] Crear `tests/tiempo/unit/test_tiempo_atws.py`: con casos de 006 construidos a mano (corrida, conjunto, señal, scram, PWNT): la regla se calibra solo con entrenamiento; para un ATWS detectado da `tiempo_desde_demanda_s = t_decision − t_demanda` y `tiempo_desde_falla_s = t_decision − t_falla`; un ATWS no detectado → tiempos `None`; «posible ATWS» en un no-ATWS cuenta como falsa alarma
- [X] T011 [P] [US2] Crear `tests/tiempo/unit/test_tiempo_evaluacion.py`: (a) tiempo de diagnóstico = primer τ de confirmación de la familia correcta con τ − 1 ≥ t_falla, menos t_falla (también con t_falla fraccionario: 47,5 → τ ≥ 49); (b) sin confirmación → `None` («no detectado»); (c) falsas alarmas de la Etapa 1 en corridas NORM y antes de la falla (episodios y corridas), sin contar las corridas inciertas, que se informan aparte; una confirmación con τ − 1 < t_falla ≤ τ no es falsa alarma; (c2) `primera_familia` y confusión: si tras la falla se confirma primero TRANS en una LOCA y después LOCA, el tiempo es el de LOCA y la corrida cuenta como confusión; (d) meta de diagnóstico: fracción ≤ 10 s en prueba, por familia y por área, excluyendo las inciertas; «sin datos» si no hay corridas; (e) meta de ATWS: fracción ≤ 3 s desde la demanda en validación y prueba, inciertas incluidas (con `tiempo_desde_falla_s` vacío), y la cifra solo de prueba aparte; un ATWS no detectado cuenta como incumplimiento; (f) la validación aparece como referencia, separada de la prueba
- [X] T012 [P] [US2] Crear `tests/tiempo/integration/test_tiempo_cli.py` (modelo sintético de T003; `cargar_corridas`, `instantes_falla` y `construir_casos` del módulo `cli` sustituidos por datos sintéticos): código 0 y publicación de `tiempos.json`, `tiempos.csv`, `lineas_tiempo.csv` y `reporte.txt`; reporte con el aviso consultivo, los tiempos y las metas; dos ejecuciones con `tiempos.json` idéntico; reemplazo sin tocar otros archivos; modelo de otra semilla o inexistente → código 1 y salida sin crear; sin PyTorch → código 3
- [X] T013 [US2] Ejecutar las pruebas de T009–T012 y comprobar que **fallan**
- [X] T014 [P] [US2] Crear `src/tiempo_deteccion/reproduccion.py`: `ErrorModelo`, `verificar_modelo(ruta, reparto)`, `reproducir(clasificador, corridas, inicios)` → `LineaTiempo` por corrida (usa `construir_muestras` y `predecir` de 005 y `confirmadas`) (research.md §3)
- [X] T015 [P] [US2] Crear `src/tiempo_deteccion/atws.py`: `evaluar_atws(casos, fallas)` → calibra con `regla_atws.regla.calibrar` sobre entrenamiento y evalúa validación y prueba, con los tiempos desde la demanda y desde la falla (research.md §4)
- [X] T016 [US2] Crear `src/tiempo_deteccion/evaluacion.py`: `tiempo_diagnostico`, `falsas_alarmas_etapa1`, `resultados_por_corrida`, `metas`, `resumen` y `formatear_reporte` (research.md §5–§6; data-model.md) (depende de T014 y T015)
- [X] T017 [US2] Crear `src/tiempo_deteccion/cli.py` con `main(argv)` según contracts/cli.md: cargar → reparto y `verificar_reparto` → `verificar_modelo` → `instantes_falla` → reproducir validación y prueba → `evaluar_atws` → resultados → publicar los cuatro archivos (carpeta temporal y reemplazo) → imprimir; códigos 1 y 3 (depende de T007, T014–T016)
- [X] T018 [US2] Ejecutar `python -m pytest tests/tiempo` y comprobar que pasan

---

## Phase 5: User Story 3 - Comparar con la medición anterior y conservar la línea de tiempo (Priority: P2)

**Goal**: tiempo desde el inicio del validador junto al tiempo desde la falla, y la línea de tiempo segundo a segundo.

**Independent Test**: la comparación muestra ambos tiempos y su diferencia; `lineas_tiempo.csv` tiene una fila por segundo con la decisión de la regla en su segundo.

- [ ] T019 [P] [US3] Ampliar `tests/tiempo/unit/test_tiempo_evaluacion.py` y `tests/tiempo/integration/test_tiempo_cli.py`: `tiempo_desde_validador_s` calculado como en 005 (inicio redondeado hacia arriba) y su diferencia en el reporte; `lineas_tiempo.csv` con 295 filas por corrida evaluada, columnas de contracts/salidas.md, y `decision_atws` solo en el segundo de decisión de la regla
- [ ] T020 [US3] Ejecutar las pruebas de T019 y comprobar que **fallan**
- [ ] T021 [US3] Implementar en `src/tiempo_deteccion/evaluacion.py` y `src/tiempo_deteccion/cli.py` la comparación con el validador y la exportación de `lineas_tiempo.csv`
- [ ] T022 [US3] Ejecutar `python -m pytest tests/tiempo` y comprobar que pasan

---

## Phase 6: Polish

- [ ] T023 [P] Crear `tests/tiempo/integration/test_tiempo_real.py` (se omite sin `datos_reales.ruta_pwr3l()`, sin PyTorch o sin `modelos/etapa1`): código 0; 72 corridas de evento con instante (29 «registro», 43 «programado») y 5 inciertas (R22, R47, R48, R54, R99); una fila por corrida de evento de validación y prueba en `tiempos.csv`; origen sin cambios (hash)
- [ ] T024 [P] Añadir al `README.md` la sección «Tiempo de detección desde la falla (funcionalidad 008)»: qué mide, de dónde sale el instante de la falla, el comando, los archivos y cómo leer las metas
- [ ] T025 Ejecutar `medir-tiempo-deteccion` con los datos reales dos veces (comprobar `tiempos.json` idéntico), medir el tiempo y anotar los resultados en «Resultados obtenidos» de `specs/008-tiempo-desde-falla/quickstart.md`
- [ ] T026 Ejecutar la suite completa con `IANUCLEAR_DATOS` y comprobar que todo pasa

---

## Dependencies & Execution Order

- Setup → Foundational → US1 → US2 (necesita los instantes de US1) → US3 (amplía US2) → Polish
- Paralelo: T002 con T001; en US2, las pruebas T009–T012 y la implementación de T014 y T015

## Implementation Strategy

1. Setup + Foundational
2. US1: instantes de la falla (MVP: ya corrige la base de toda medición)
3. US2: tiempos, metas y falsas alarmas
4. US3: comparación y líneas de tiempo
5. Polish: datos reales, README y resultados

## Notes

- KAN-25. El informe del Hito 1 (007, KAN-27) podrá leer `tiempos.json`; generarlo queda fuera.
