# Contrato: salidas de la Etapa 2

## `modelo.json`

`clases` ["LOCA","LOCAC"], `canales` ["PWR","PWNT"], `ventana_s` 30, `ventana_pico_s` 15, `media_movil_s` 3, `horizonte_entrenamiento_s` 60, `umbral` 0.8, `confirmacion_s` 2, `hiperparametros`, `semilla`, `pesos_clase`, `escalador` {`media`, `escala`, `filas_ajuste`}, `historial`, `mejor_epoca`, `muestras` {train, val, test}, `corridas` {train, val, test}, `version`, `entorno`.

## `reporte.json`

- `aviso`: texto consultivo.
- `global`: `matriz` (2 × 3, filas LOCA/LOCAC, columnas LOCA/LOCAC/UNCERTAIN), `por_clase` {precision, exhaustividad, f1}, `f1_macro`, `cobertura`, `exactitud_decisiones`, `errores_confianza`, `muestras`.
- `horizontes`: lista por h ∈ {1,2,3,5,10,20,30} con los mismos campos.
- `primeros_30s`: mismos campos con 0 ≤ k ≤ 30.
- `corridas`: por corrida `{corrida, clase, area, confirmada, correcta, tiempo_s, error_confirmado}`.
- `areas`: por rango `{rango, corridas, correctas, errores, sin_decision}`.
- `metas`: SC-001 y SC-002 con `valor` y `cumple`.
- `advertencias`, `entrenamiento`, `reparto`.

## Recomendación (`Clasificador.clasificar`)

```json
{"probabilidades": {"LOCA": 0.93, "LOCAC": 0.07}, "recomendacion": "LOCA", "aviso": "..."}
{"probabilidades": null, "recomendacion": "NO_APLICA", "aviso": "..."}
```
