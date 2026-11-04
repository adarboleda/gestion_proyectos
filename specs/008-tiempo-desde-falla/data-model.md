# Data Model: Tiempo de detección desde la falla

## InstanteFalla (`falla.py`)

| Campo | Tipo | Regla |
|---|---|---|
| `t` | float o None | segundos desde el inicio de la corrida |
| `fuente` | str | «registro», «programado» o «ninguna» |
| `detalle` | str | línea del registro, «config.json fallas=7:0:50» o «carpeta _t60» |
| `inicio_validador` | float o None | inicio de 005 (`inicios_evento`) |
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
| `tiempo_diagnostico_s` | `t_confirmacion − t_falla`, o None («no detectado») |
| `tiempo_desde_validador_s` | el mismo cálculo desde el inicio del validador (comparación) |
| `atws` | solo ATWS/TRIP_OK: recomendación de la regla, `t_demanda`, `t_decision`, `tiempo_desde_demanda_s`, `tiempo_desde_falla_s` |
| `falsas_alarmas` | episodios de la Etapa 1 antes de la falla (o en toda la corrida NORM); `posible ATWS` sin ATWS |

## Resumen y metas

- `diagnostico`: por familia y total (prueba, y validación como referencia): corridas, detectadas, ≤ 10 s, mediana y máximo; LOCA por área.
- `atws`: ATWS de validación y prueba: detectados, ≤ 3 s desde la demanda, tiempos.
- `falsas_alarmas`: Etapa 1 (corridas NORM y antes de la falla) y regla (no-ATWS), por conjunto.
- `inciertas`: lista con motivo.
- `metas`: `diagnostico_10s` y `atws_3s` con `meta`, `valor`, `cumple` (true/false/«sin datos»).

## Errores

- `ErrorModelo`: el modelo guardado no existe o no corresponde al reparto → código 1.
- Los errores de datos (`ErrorDatos`), de fuga (`ErrorFuga`) y la falta de PyTorch siguen los códigos de 005 (1 y 3).
