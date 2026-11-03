# Auditoría de la funcionalidad 005-clasificador-etapa1

**Fecha**: 2026-11-03 · **Rama**: `005-clasificador-etapa1`

**Fuentes**: [analisis-inicial.md](analisis-inicial.md) (`/speckit-analyze`), dos pasadas de `/speckit-converge`, el código, las pruebas, el entrenamiento con los datos reales y los registros de `speckit-metricas`.

## 1. Resumen

- **Análisis inicial**: 6 hallazgos (0 críticos, 1 medio y 5 bajos), cobertura del 100 % y FR-015 parcial. El responsable aprobó de forma explícita aplicar los 6, en un commit aparte (`094e1b6`).
- **Converge, 1.ª pasada**: 3 hallazgos `partial` (1 medio y 2 bajos), que generaron las tareas T033–T035. Se implementaron solo con inserciones de código (+13 / −0).
- **Converge, 2.ª pasada**: **`converged`**, 0 hallazgos.
- **Estado final**: 35/35 tareas y 50 pruebas de `etapa1`. Con los datos reales, la suite completa da 259 pasadas y 1 omitida antes de las tareas de convergencia; las pruebas de `etapa1` siguen en verde después.
- **Resultado con los datos reales**: cumple SC-002 (0 falsas alarmas) y SC-003 (F1 de los primeros 30 s = 0,927), pero **no cumple SC-001**: las LOCA de 100 cm² se confirman en 19 s, frente a la meta de ≤ 10 s. Se informa tal como sale, como pide la spec.

## 2. Cobertura de requisitos (estado final)

| Requisito | Tareas | Pruebas |
|---|---|---|
| FR-001 tres familias | T004, T008 | `test_etapa1_muestras::test_familias_por_clase` |
| FR-002 reparto 004 + verificación | T013, T017 | `test_etapa1_cli` (fuga → código 1; corridas sin repetir), `test_etapa1_real` (63/15/13) |
| FR-003 26 variables escaladas con entrenamiento | T013, T017 | `test_etapa1_cli::test_corridas_sin_repetir_y_escalador_de_entrenamiento` |
| FR-004 ventana causal de 30 s | T006, T010 | `test_etapa1_muestras` (ventana, relleno, sin filas futuras, filtro de entrenamiento) |
| FR-005 etiqueta según el inicio | T006, T010 | `test_etapa1_muestras` (etiquetas, k, inicio redondeado) |
| FR-006 pesos de clase | T012, T016 | `test_etapa1_entrenamiento::test_pesos_de_clase_inversos_a_la_frecuencia` |
| FR-007 determinismo | T012, T013, T031 | `test_etapa1_entrenamiento`, `test_etapa1_cli`, repetición real (artefactos idénticos) |
| FR-008 parada por validación | T012, T016 | `test_etapa1_entrenamiento` (mejor época, paciencia, sin prueba) |
| FR-009 métricas y horizontes | T019, T022, T033 | `test_etapa1_evaluacion` (globales, horizonte con métricas completas, primeros 30 s) |
| FR-010 tiempo de confirmación | T019, T022, T034 | `test_etapa1_evaluacion` (2 s ≥ 0,80, τ − 1 ≥ inicio, no detectada), reporte por área |
| FR-011 falsas alarmas | T019, T022 | `test_etapa1_evaluacion::test_falsas_alarmas_en_corridas_norm_y_tramos_previos` |
| FR-012 artefactos y regeneración | T013, T020, T023, T035 | `test_etapa1_cli` (modelo, reporte, reemplazo, validación, reparto) |
| FR-013 clasificación consultiva | T025, T027 | `test_etapa1_prediccion` (7 pruebas) |
| FR-014 evento sin inicio | T005, T013 | `test_etapa1_eventos`, `test_etapa1_cli` |
| FR-015 sin modificar origen ni usar NPPAD | T029 | `test_etapa1_real` (hash del origen) |
| SC-001 a SC-007 | T019, T020, T029, T031 | Reporte real (`reporte.json["metas"]`), `test_etapa1_cli`, tiempo de 16,7 s |

## 3. Hallazgos del análisis inicial y su resolución

| ID | Sev. | Hallazgo | Resolución |
|---|---|---|---|
| U1 | MEDIUM | Con un inicio fraccionario, k nunca valdría h | Inicio redondeado hacia arriba al segundo; prueba con 24,5 s |
| U2 | LOW | SC-001 podría no ser evaluable | La meta se informa como «sin datos»; probado |
| C1 | LOW | Faltaba comprobar que el origen no cambia | Hash del origen antes y después en la prueba real |
| C2 | LOW | Código 3 (sin PyTorch) sin prueba | Prueba que simula la falta de PyTorch |
| A1 | LOW | Alcance de la reproducibilidad | Misma máquina y entorno; versión de PyTorch e hilos en `modelo.json` |
| T1 | LOW | «TRANS» sin presentar | Etiqueta presentada en Key Entities |

## 4. Hallazgos de `/speckit-converge`

**Primera pasada**:

| ID | Tipo | Sev. | Hallazgo | Tarea |
|---|---|---|---|---|
| F1 | partial | MEDIUM | En los horizontes solo había exhaustividad de LOCA/TRANS y F1 macro; la spec pedía precisión, exhaustividad y F1 de cada familia (el plan lo había reducido) | T033 |
| F2 | partial | LOW | El reporte impreso no agrupaba los tiempos LOCA por área ni mostraba el reparto | T034 |
| F3 | partial | LOW | Faltaba la clave `validacion` del modelo de datos | T035 |

**Segunda pasada**: `converged`, 0 hallazgos.

## 5. Estado final de las tareas

| Fase | Tareas | Estado | Commits |
|---|---|---|---|
| 1 Setup | T001–T003 | 3/3 | `421e2c5` |
| 2 Foundational | T004–T011 | 8/8 | `e1532db`, `cb1cf79` |
| 3 US1 (MVP) | T012–T018 | 7/7 | `4e5e035`, `cb5285b` |
| 4 US2 | T019–T024 | 6/6 | `e6ed60e`, `aa039d7` |
| 5 US3 | T025–T028 | 4/4 | `4a1e60e`, `ec59f70` |
| 6 Polish | T029–T032 | 4/4 | `ffd56c6`, `2b3422b` |
| 7 Convergence | T033–T035 | 3/3 | `4e01bb8`, `5ab93e0` |
| **Total** | **35** | **35/35** | |

## 6. Observaciones

- **SC-001 no se cumple.** La familia LOCA se reconoce a partir de los 10–20 s (exhaustividad 0 hasta los 5 s, 0,8 a los 10 s y 1,0 a los 20 s), y las roturas de 10 cm² tardan 120 s. No se ajustó el modelo mirando la prueba (principio II). Hipótesis, a verificar solo con validación: la selección por el F1 global (que se estabiliza en la 2.ª época) no premia la rapidez; la media sobre 30 s diluye los primeros segundos del evento; faltan variables de tendencia.
- **Conjunto de prueba pequeño**: 13 corridas (3 NORM, 5 LOCA y 5 TRANS) y solo 2 LOCA ≥ 50 cm². Las cifras tienen mucha incertidumbre.
- **R60** (TRIP_OK manual) toma el instante planificado de su carpeta (48 s), que no coincide con el inicio real de su gemela R22 (13 s). R60 está en entrenamiento.
- **Las horas** son el mínimo por sesión que registra la extensión (0,25 h): el reloj marca unos 43 minutos de trabajo del agente (12:59–13:42). La instalación de PyTorch y la exploración de los datos no están registradas.
- **Proceso**: las dos respuestas de `/speckit-clarify` y la aprobación de las correcciones del análisis las dio el responsable. Todas las tareas de convergencia se implementaron solo con inserciones (0 líneas eliminadas).
