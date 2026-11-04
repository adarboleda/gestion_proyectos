# Data Model: Tiempo de detección desde la falla

## InstanteFalla (`falla.py`)

| Campo | Tipo | Regla |
|---|---|---|
| `t` | float o None | segundos desde el inicio de la corrida |
| `fuente` | str | «registro», «programado» o «ninguna» |
| `detalle` | str | línea del registro, «config.json fallas=7:0:50» o «carpeta _t60» |
| `inicio_validador` | float o None | inicio de 005 (`inicios_evento`); en las salidas se acompaña de `diferencia_validador_s` = inicio_validador − t |
| `incierta` | bool | `t` es None o `inicio_validador < t − 2` |
| `motivo` | str o None | por qué es incierta |

## LineaTiempo (`reproduccion.py`)

Por corrida: arreglos alineados por τ = 5…299: `tau` (int), `probabilidades` (n, 3) en orden NORM, LOCA, TRANS, y `confirmada` (n,) con la familia confirmada o «» (ninguna).

## ResultadoCorrida (`evaluacion.py`)

| Campo | Contenido |
|---|---|
| `corrida`, `clase`, `familia`, `conjunto`, `area` | identificación (`familia`: NORM, LOCA o TRANS) |
| `falla` | `InstanteFalla` |
| `t_confirmacion` | primer τ de confirmación de la familia correcta tras la falla, o None |
| `primera_familia` | primera familia de evento (LOCA o TRANS) confirmada con τ − 1 ≥ t_falla, o «» (ninguna); si no es la correcta, la corrida es una «confusión» |
| `tiempo_diagnostico_s` | `t_confirmacion − t_falla`, o None («no detectado») |
| `tiempo_desde_validador_s` | el mismo cálculo desde el inicio del validador (comparación) |
| `atws` | toda corrida evaluada (hace falta para contar «posible ATWS» sin ATWS, FR-009): recomendación de la regla, motivo, `t_demanda`, `t_decision`, `tiempo_desde_demanda_s` y `tiempo_desde_falla_s` (estos dos solo en ATWS detectados) |
| `falsas_alarmas` | episodios de la Etapa 1 antes de la falla (o en toda la corrida NORM; no se cuentan en las inciertas); `posible ATWS` sin ATWS (en todas) |

## Resumen y metas

- `diagnostico`: por familia y total (prueba, y validación como referencia): corridas, detectadas, ≤ 10 s, mediana y máximo; LOCA por área.
- `atws`: todos los ATWS de validación y prueba (inciertos incluidos) y, aparte, solo prueba: detectados, ≤ 3 s desde la demanda, tiempos.
- `confusiones`: corridas de evento cuya `primera_familia` no es la correcta, por conjunto.
- `falsas_alarmas`: Etapa 1 (corridas NORM y antes de la falla) y regla (no-ATWS), por conjunto.
- `inciertas`: lista con motivo; se excluyen solo de la meta de diagnóstico.
- `metas`: `diagnostico_10s` y `atws_3s` con `meta`, `valor`, `cumple` (true/false/«sin datos»).

## Errores

- `ErrorModelo`: el modelo guardado no existe o no corresponde al reparto → código 1.
- Los errores de datos (`ErrorDatos`), de fuga (`ErrorFuga`) y la falta de PyTorch siguen los códigos de 005 (1 y 3).
