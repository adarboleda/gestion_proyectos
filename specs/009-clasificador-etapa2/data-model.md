# Data Model: Clasificador de Etapa 2

| Entidad | Representación | Campos |
|---|---|---|
| Corrida | `preparacion_pwr3l.descubrimiento.Corrida` (002) | `id`, `clase` ∈ {LOCA, LOCAC}, `area`, `archivo`, `serie` (300 × 33) |
| Canales | `np.ndarray` (300, 2) float64 | columna 0 = desviación pico PWR, 1 = desviación pico PWNT (sin escalar) |
| Escalador | `dict` en `modelo.json` | `media` (2), `escala` (2), `filas_ajuste` |
| Muestras | `clasificador_etapa1.muestras.Muestras` | `x` (n, 30, 2) float32, `y` (0 = LOCA, 1 = LOCAC), `tau`, `k`, `corrida` |
| ResultadoEntrenamiento | dataclass | `modelo`, `historial`, `mejor_epoca`, `pesos` |
| Reporte | `dict` → `reporte.json` | `global`, `horizontes`, `corridas`, `areas`, `metas`, `advertencias`, `entrenamiento`, `reparto` |
| Recomendación | `dict` | `probabilidades` {LOCA, LOCAC} o `None`, `recomendacion` ∈ {LOCA, LOCAC, UNCERTAIN, NO_APLICA}, `aviso` |

Reglas: `y` depende solo de la clase de la corrida; `k = τ − ceil(inicio)` ≥ 0; en entrenamiento `k ≤ 60`.

