# Contrato: artefactos de `data_processed_pwr3l/`

Se publican todos juntos o ninguno (`preparacion_datos.salida.publicar`). Otros archivos que ya estén en la carpeta no se tocan. No se editan a mano.

| Archivo | Forma y tipo | Contenido |
|---|---|---|
| `X_train.npy`, `X_val.npy`, `X_test.npy` | (N, 300, 26) float32 | Entradas escaladas, en el orden de `config.VARIABLES_ENTRADA` |
| `y_train.npy`, `y_val.npy`, `y_test.npy` | (N,) int64 | 0 = NORM, 1 = LOCA, 2 = LOCAC, 3 = ATWS, 4 = TRIP_OK |
| `margins_train.npy`, `margins_val.npy`, `margins_test.npy` | (N, 300, 7) float64 | Márgenes sin escalar: DNBR, TPCT, SCMA, SCMB, TSAT, FRCL, FRZR |
| `scaler_mean.npy`, `scaler_std.npy` | (26,) float64 | Parámetros ajustados solo con `X_train` |
| `metadata.json` | JSON UTF-8 | Ver abajo |

La fila `i` de `X_<c>`, `y_<c>` y `margins_<c>` corresponde a `metadata.corridas[<c>][i]`.

## `metadata.json`

```json
{
  "version_formato": 1,
  "planta": "PWR 3L",
  "origen": "<ruta>",
  "semilla": 42,
  "proporciones": {"train": 0.7, "val": 0.15, "test": 0.15},
  "pasos_por_muestra": 300,
  "paso_segundos": 1,
  "clases": {"NORM": 0, "LOCA": 1, "LOCAC": 2, "ATWS": 3, "TRIP_OK": 4},
  "variables_entrada": ["P", "...", "RM1"],
  "variables_margen": ["DNBR", "...", "FRZR"],
  "corridas_encontradas": {"<CLASE>": {"usable": 0, "corta": 0, "descartada": 0, "ood": 0}},
  "conteos_muestras": {"<CLASE>": {"train": 0, "val": 0, "test": 0}},
  "totales": {"train": 0, "val": 0, "test": 0},
  "corridas": {"train": ["R01", "..."], "val": [], "test": []},
  "grupos": {"train": {"AREA-2000": ["R03", "..."]}, "val": {}, "test": {}},
  "excluidas": [{"id": "R07", "clase": "LOCAC", "archivo": "...", "motivo": "descartada", "detalle": "..."}],
  "escalador": {"ajustado_con": "train", "filas_ajuste": 0, "variables_sin_varianza": []},
  "advertencias": ["..."],
  "limitaciones": ["..."]
}
```

`corridas_encontradas` incluye la clase `OOD`. La suma de todas sus celdas es el número de corridas encontradas (109 en el dataset real).
