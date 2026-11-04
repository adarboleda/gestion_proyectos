# Auditoría de la funcionalidad 009-clasificador-etapa2

**Fecha**: 2026-11-04 · **Rama**: `009-clasificador-etapa2`

**Fuentes**: [analisis-inicial.md](analisis-inicial.md) (`/speckit-analyze`), `/speckit-converge`, código en `src/clasificador_etapa2/`, pruebas en `tests/etapa2/`, corrida con el dataset real y `speckit-metricas`.

## 1. Resumen

- **Análisis inicial**: 3 hallazgos bajos (U1: validación de serie de entrada en predicción, C1: prueba de rama sin soporte en prueba, C2: verificación de no modificar código ajeno `FR-015`), corregidos antes de implementar en el commit `5a31901`.
- **Convergencia (`/speckit-converge`)**: **`converged`** en la 1.ª pasada. 18/18 tareas completadas (`[X]`), 0 brechas pendientes.
- **Pruebas**: 30 pruebas automatizadas en `tests/etapa2/` (todas en verde). Suite completa del repositorio: **434 pasadas, 1 omitida** (0 fallos).
- **Resultados con el dataset real de PWR 3L**:
  - SC-001: 0 errores con confianza en los primeros 30 s → **CUMPLE** (todas las decisiones con p < 0,80 resultan en abstención `UNCERTAIN`).
  - SC-002: roturas ≥ 50 cm² confirmadas en ≤ 10 s → **NO CUMPLE** (el modelo se abstiene con `UNCERTAIN` en R44 y R83 debido al límite físico de la ventana de 15 s tras el disparo; se reporta honestamente tal como sale).
  - SC-003: 100 % de las corridas de prueba (5 de 5) documentadas en el reporte con su resultado.
  - SC-004: reproducible bit a bit con semilla 42.
  - SC-005: ejecución completa en ~15 segundos en CPU (< 15 minutos).
  - SC-006: 0 fugas de datos entre particiones (verificación estricta de 004).

## 2. Cobertura de requisitos

| Requisito | Tareas | Pruebas |
|---|---|---|
| FR-001 | T005, T007, T009 | `test_etapa2_muestras::test_es_rama_filtra_solo_loca_y_locac_usables`, `test_etapa2_cli` |
| FR-002 | T009, T011 | `test_etapa2_cli::test_corridas_solo_loca_locac_sin_solape_y_escalador_de_entrenamiento` |
| FR-003 | T004, T006 | `test_etapa2_canales::test_desviacion_pico_resta_valor_inicial_y_olvida_tras_15s`, `test_etapa2_canales::test_desviacion_pico_es_estrictamente_causal` |
| FR-004 | T008, T010 | `test_etapa2_entrenamiento::test_escalador_se_ajusta_solo_con_entrenamiento` |
| FR-005 | T005, T007 | `test_etapa2_muestras::test_construir_muestras_entrenamiento_recorta_a_60s_y_evaluacion_usa_todo` |
| FR-006 | T008, T010 | `test_etapa2_entrenamiento::test_pesos_clase_inversos_a_frecuencia` |
| FR-007 | T008, T010 | `test_etapa2_entrenamiento::test_entrenamiento_aprende_y_es_determinista` |
| FR-008 | T008, T009 | `test_etapa2_cli::test_dos_ejecuciones_con_misma_semilla_son_identicas` |
| FR-009 | T012, T013 | `test_etapa2_evaluacion::test_decidir_aplica_umbral_080` |
| FR-010 | T012, T013 | `test_etapa2_evaluacion::test_metricas_segmento_con_abstencion_y_matriz_2x3` |
| FR-011 | T012, T013, T014 | `test_etapa2_evaluacion::test_confirmacion_corrida_correcta_equivocada_y_sin_decision`, `test_etapa2_cli` |
| FR-012 | T009, T011 | `test_etapa2_cli::test_publica_los_cuatro_artefactos_y_configuracion`, `test_etapa2_cli::test_reentrenar_reemplaza_solo_artefactos_propios` |
| FR-013 | T015, T016 | `test_etapa2_prediccion::test_clasificar_devuelve_rama_cuando_supera_umbral`, `test_etapa2_prediccion::test_clasificar_no_aplica_si_etapa1_no_es_loca` |
| FR-014 | T004, T005 | `test_etapa2_canales::test_leer_pwr_falla_si_falta_columna_o_no_es_numerica`, `test_etapa2_muestras::test_construir_muestras_ignora_otras_clases_y_falla_sin_inicio` |
| FR-015 | T017, T018 | `test_etapa2_real::test_entrenamiento_corto_etapa2_con_dataset_real` (comprobado `hash_origen()` y `git diff --stat main -- src/`) |
| SC-001…SC-006 | T008, T012, T014, T017, T018 | `test_etapa2_evaluacion`, `test_etapa2_real`, reporte en `modelos/etapa2/reporte.json` |
