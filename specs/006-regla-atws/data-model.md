# Data Model: Regla determinista de ATWS

## Señal (`eventos.Senal`)

| Campo | Tipo | Descripción |
|---|---|---|
| `tiempo` | float | s desde el inicio de la corrida |
| `tipo` | str | Tipo normalizado (`low sg level`, `turbine trip`, `rcp-a trip`, `scram lo rx press`, `scram high flux`, …) |
| `fuente` | str | `registro` (línea del `.dat`) o `alto flujo` (PWNT ≥ 118 %) |

## Regla (`regla.Regla`)

| Campo | Descripción |
|---|---|
| `umbral` | % del PWNT inicial |
| `retardos` | dict tipo → s (medidos en entrenamiento) |
| `retardo_por_defecto` | mayor retardo de entrenamiento |
| `espera` | 2.0 s |
| `minimo_atws`, `maximo_no_atws` | flujos en la decisión, en entrenamiento |
| `solape` | bool |
| `falsas_alarmas_entrenamiento` | int |

## Resultado por corrida (`regla.Resultado`)

| Campo | Descripción |
|---|---|
| `id`, `clase`, `conjunto` | Corrida y conjunto de 004 |
| `es_atws` | Verdad de la corrida |
| `tipo_senal`, `fuente_senal`, `t_senal` | Señal de disparo |
| `retardo`, `retardo_por_defecto` | Retardo aplicado; bool si fue el de por defecto |
| `t_demanda`, `t_decision` | s |
| `pwnt_decision` | % del PWNT inicial |
| `recomendacion` | `posible ATWS` o `sin ATWS` |
| `motivo` | `flujo alto`, `flujo caído`, `sin demanda` o `decisión fuera de la ventana` |
| `acierto` | bool |
| `t_deteccion_demanda`, `t_deteccion_senal` | Solo ATWS detectados |

## Resumen

- **Por conjunto**: `atws_detectados`, `atws_omitidos`, `falsas_alarmas`, `rechazos_correctos`, `total`.
- **Errores**: lista con cada omisión o falsa alarma.
- **Tiempos de detección**: mínimo, máximo y cumplimiento de la meta (≤ 3 s desde la demanda).
- **Advertencias** y **limitaciones**.
