# Contrato: artefactos de salida y escalado

## `metadata.json` en `data_processed/` (NPPAD)

Se mantiene el esquema de la funcionalidad 001, donde `paso_segundos` pasa a ser el valor medido de `TIME` y se añade `duracion_muestra_segundos`:

```json
{
  "version_formato": 1,
  "origen": "<ruta de origen>",
  "semilla": 42,
  "proporciones": {"train": 0.70, "val": 0.15, "test": 0.15},
  "pasos_por_muestra": 150,
  "paso_segundos": 10,
  "duracion_muestra_segundos": 1500,
  "clases": {"NORM": 0, "LOCA": 1, "LOCAC": 2, "ATWS": 3},
  "variables_planta": ["P", "TAVG", "THA", "TCA", "WRCA", "WRCB", "LVPZ", "LVCR", "PWNT", "PWR", "WECS", "WLR"],
  "variables_margen": ["DNBR", "TPCT", "SCMA", "SCMB", "TSAT", "FRCL", "FRZR"],
  "conteos_archivos": {"NORM": 1, "LOCA": 100, "LOCAC": 100, "ATWS": 1},
  "conteos_muestras": {
    "NORM":  {"train": 1,  "val": 0,  "test": 0},
    "LOCA":  {"train": 70, "val": 15, "test": 15},
    "LOCAC": {"train": 70, "val": 15, "test": 15},
    "ATWS":  {"train": 1,  "val": 0,  "test": 0}
  },
  "totales": {"train": 142, "val": 30, "test": 30},
  "simulaciones": {"train": ["..."], "val": ["..."], "test": ["..."]},
  "escalador": {"ajustado_con": "train", "filas_ajuste": 21300, "variables_sin_varianza": []},
  "referencia": {"archivo": "<ruta o null>", "estado": "COINCIDE | DIFIERE | NO DISPONIBLE | OMITIDA", "diferencias": []},
  "advertencias": ["..."],
  "limitaciones": ["..."]
}
```

Invariantes adicionales:
- `duracion_muestra_segundos == pasos_por_muestra * paso_segundos`.
- `paso_segundos` proviene de la medición sobre la columna `TIME`, nunca de una constante en `config.py`.

## Contrato del módulo `preparacion_pwr3l.escalado` (PWR 3L)

- `ajustar_escalador(x_train: np.ndarray) -> Escalador`:
  - Entrada: `x_train` con forma `(N_train, 300, 26)` y `N_train >= 1`.
  - Salida: `Escalador` con `media` `(26,) float64`, `escala` `(26,) float64`, `variables_sin_varianza: list[str]`, `filas_ajuste == N_train * 300`.
- `aplicar(escalador: Escalador, x: np.ndarray) -> np.ndarray`:
  - Entrada: `x` con forma `(N, 300, 26)`.
  - Salida: `ndarray` `(N, 300, 26)` de tipo `float32`, transformado con `media` y `escala` de entrenamiento sin reajustar.
