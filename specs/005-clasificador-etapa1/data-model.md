# Data Model: Clasificador de Etapa 1

## Familia

| Familia | Etiqueta | Clases de origen |
|---|---|---|
| NORM | 0 | NORM; y cualquier instante anterior al inicio del evento |
| LOCA | 1 | LOCA, LOCAC |
| TRANS | 2 | ATWS, TRIP_OK |

## Corrida (existente, 002/004)

Se usan `id`, `clase`, `estado` (solo `usable`), `area` (LOCA), `archivo` y `serie` (300, 33), de la que se toman las 26 primeras columnas (`VARIABLES_ENTRADA`). El conjunto sale de `Reparto.conjunto_de_corrida` (004). Ningún campo se modifica.

## Inicio del evento (nuevo, `eventos.py`)

`inicios: dict[id → float | None]`: segundos desde t = 0; `None` solo para NORM. Fuente: `validacion.json` → `validacion_corridas.csv` → `_t<n>` del nombre de la carpeta. Una corrida de evento sin inicio → `ErrorDatos`.

## Muestras (nuevo, `muestras.py`)

`Muestras` (por conjunto):

| Campo | Forma / tipo | Regla |
|---|---|---|
| `x` | (n, 30, 26) float32 | Filas [τ − 29, τ] escaladas; las que faltan al inicio repiten la fila 0 |
| `y` | (n,) int64 | 0 si τ < inicio o corrida NORM; si no, la familia de la corrida |
| `tau` | (n,) int64 | 5 … 299 |
| `k` | (n,) float64 | τ − inicio; `nan` en corridas NORM |
| `corrida` | (n,) str | id de la corrida (todas del mismo conjunto) |

Entrenamiento: NORM completas, τ < inicio y 0 ≤ k ≤ 60. Validación y prueba: todas las τ.

## Modelo entrenado (nuevo)

`modelo.pt`: pesos de la Bi-LSTM. `modelo.json`:

| Clave | Contenido |
|---|---|
| `familias` | `["NORM", "LOCA", "TRANS"]` |
| `variables` | las 26 variables de entrada, en orden |
| `ventana_s`, `tau_min_s`, `horizonte_entrenamiento_s` | 30, 5, 60 |
| `umbral`, `confirmacion_s` | 0.80, 2 |
| `hiperparametros` | unidades 32, capas 1, dropout 0.3, lr, weight decay, lote, épocas máximas, paciencia |
| `semilla` | entero |
| `pesos_clase` | 3 valores |
| `escalador` | `media` (26), `escala` (26), filas de ajuste |
| `historial` | por época: pérdida de entrenamiento, F1 macro de validación |
| `mejor_epoca` | entero |
| `corridas` | ids por conjunto |
| `version` | versión del paquete |
| `entorno` | versión de PyTorch y número de hilos usados |

## Reporte de evaluación (nuevo)

`reporte.json` (y `reporte.txt`):

- `aviso`: «Clasificador consultivo: las salidas son recomendaciones; el operador decide».
- `conjunto_prueba`: corridas y conteo por familia; advertencia de tamaño pequeño.
- `global`: matriz de confusión 3 × 3, precisión, exhaustividad y F1 por familia, F1 macro.
- `horizontes`: para h ∈ {1, 2, 3, 5, 10, 20, 30}: exhaustividad LOCA y TRANS en k = h, F1 macro con las muestras NORM.
- `primeros_30s`: F1 macro (SC-003).
- `deteccion`: por corrida de evento: id, clase, familia, área, inicio, tiempo de confirmación o `null` («no detectada»); resumen por familia y, para LOCA, por área.
- `falsas_alarmas`: instantes, episodios y corridas, en corridas NORM y en tramos previos.
- `metas`: SC-001, SC-002 y SC-003 con su valor obtenido y si se cumplen.
- `validacion`: F1 macro de la mejor época.

## Recomendación (nuevo, `prediccion.py`)

`{"probabilidades": {"NORM": p0, "LOCA": p1, "TRANS": p2}, "recomendacion": "NORM" | "LOCA" | "TRANS" | "INCIERTO", "aviso": str}` con p0 + p1 + p2 = 1; «INCIERTO» si max(p) < 0,80.
