# Auditoría de la funcionalidad 011-evaluacion-diagnostico

**Fecha**: 2026-11-04 · **Rama**: `011-evaluacion-diagnostico`

**Fuentes**: [analisis-inicial.md](analisis-inicial.md) (`/speckit-analyze`), `/speckit-converge`, código en `src/evaluacion_diagnostico/`, pruebas en `tests/evaluacion_diagnostico/` y `speckit-metricas`.

## 1. Resumen

- **Análisis inicial**: 0 hallazgos bloqueantes; verificación de consistencia entre spec, plan y tareas aprobada.
- **Convergencia (`/speckit-converge`)**: **`converged`** en la 1.ª pasada. 12/12 tareas completadas (`[x]`), 0 brechas pendientes.
- **Pruebas**: 10 pruebas automatizadas en `tests/evaluacion_diagnostico/` (todas en verde). Suite global del repositorio: **439 pasadas, 19 omitidas** (0 fallos).
- **Resultados y Criterios de Éxito**:
  - SC-001: Reporte simultáneo de exactitud con abstención, tasa de abstención y errores con confianza alta tanto en validación como en prueba cumpliendo la identidad de partición exhaustiva $\text{Acc}_{\text{abst}} + \text{Tasa}_{\text{abst}} + \text{Tasa}_{\text{err}} = 1.0$ → **CUMPLE**.
  - SC-002: Matriz de confusión rectangular $3 \times 4$ con desglose por filas (`NORM`, `LOCA`, `TRANS`) y columna de abstención `UNCERTAIN` → **CUMPLE**.
  - SC-003: Intervalos de confianza al 95 % mediante Wilson score interval para todas las proporciones sin colapso a 0 en casos extremos → **CUMPLE**.
  - SC-004: Validación cruzada agrupada (*Group K-Fold*, $k=5$) sin fuga de severidad ni gemelos ATWS, reportando media, desviación estándar e intervalo $t$-Student al 95 % → **CUMPLE**.
  - SC-005: Publicación atómica de `evaluacion_diagnostico.json` y `evaluacion_diagnostico.txt` mediante el CLI `evaluar-diagnostico` con códigos de salida 0/1/3 → **CUMPLE**.

## 2. Cobertura de requisitos

| Requisito | Tareas | Pruebas |
|---|---|---|
| FR-001 | T003, T004 | `test_metricas::test_matriz_confusion_con_abstencion` |
| FR-002 | T003, T004 | `test_metricas::test_metricas_conjuntas_suma_uno_y_valores_exactos` |
| FR-003 | T003, T004 | `test_metricas::test_metricas_conjuntas_suma_uno_y_valores_exactos` |
| FR-004 | T003, T004 | `test_metricas::test_metricas_conjuntas_suma_uno_y_valores_exactos` |
| FR-005 | T003, T004 | `test_metricas::test_intervalo_wilson_propiedades_basicas` |
| FR-006 | T003, T004 | `test_metricas::test_metricas_conjuntas_suma_uno_y_valores_exactos` |
| FR-007 | T005, T006 | `test_validacion_cruzada::test_particionar_kfold_por_grupos_sin_fuga` |
| FR-008 | T005, T006 | `test_validacion_cruzada::test_agregar_metricas_folds` |
| FR-009 | T007, T008 | `test_evaluacion_cli::test_formatear_reporte_y_construir_json` |
| FR-010 | T007, T008 | `test_evaluacion_cli::test_formatear_reporte_y_construir_json` |
| FR-011 | T007, T009 | `test_evaluacion_cli::test_cli_parser_y_salida_en_carpeta` |
| FR-012 | T007, T009 | `test_evaluacion_cli::test_cli_falta_torch`, `test_evaluacion_cli::test_cli_error_datos` |
| FR-013 | T007, T008 | `test_evaluacion_cli::test_formatear_reporte_y_construir_json` |
| FR-014 | T010, T012 | `test_etapa1_cli`, suite completa sin regresiones |
| SC-001…SC-005 | T001–T012 | `tests/evaluacion_diagnostico/` (10 pruebas pasando al 100 %) |
