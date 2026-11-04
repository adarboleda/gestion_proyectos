# Contrato: `resultados_regla_atws/`

Publicación todos o ninguno; no se edita a mano.

## `regla.json`

```json
{"version_formato": 1, "calibrada_con": "train", "semilla": 42, "umbral_pwnt_pct": 0.0, "espera_s": 2.0,
 "punto_alto_flujo_pct": 118.0, "meta_s": 3.0, "retardos_s": {"turbine trip": 5.0},
 "retardo_por_defecto_s": 5.0, "margen": {"minimo_atws_pct": 0.0, "maximo_no_atws_pct": 0.0,
 "separacion_pct": 0.0, "solape": false, "falsas_alarmas_entrenamiento": 0},
 "aviso": "Recomendación para el operador: ..."}
```

## `evaluacion.csv`

UTF-8, una fila por corrida usable, ordenada por conjunto (train, val, test) y por el orden de 004.

Columnas: `id, clase, conjunto, es_atws, tipo_senal, fuente_senal, t_senal, retardo, retardo_por_defecto, t_demanda, t_decision, pwnt_decision_pct, recomendacion, motivo, acierto, t_deteccion_demanda, t_deteccion_senal`. Las celdas quedan vacías cuando el dato no aplica.

## `resumen.json`

| Clave | Contenido |
|---|---|
| `version_formato` | Versión del formato |
| `por_conjunto` | `{train|val|test: {atws_detectados, atws_omitidos, falsas_alarmas, rechazos_correctos, total}}` |
| `errores` | Lista de `{id, conjunto, tipo: omision|falsa_alarma, pwnt_decision_pct}` |
| `tiempos` | `{conjunto: {min_s, max_s, cumplen_meta, detectados}}`, medidos desde la demanda |
| `advertencias`, `limitaciones` | Listas de texto |
| `aviso` | Texto de recomendación para el operador |
