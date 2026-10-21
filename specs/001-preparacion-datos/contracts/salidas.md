# Contrato: artefactos de `data_processed/`

Se publican todos juntos o ninguno. Para cada conjunto `S` en `train`, `val`, `test`, con `N_S` muestras:

| Archivo | Forma | Tipo | Contenido |
|---|---|---|---|
| `X_S.npy` | (N_S, 150, 12) | float32 | 12 variables de planta escaladas, en el orden de `variables_planta` |
| `y_S.npy` | (N_S,) | int64 | 0 = NORM, 1 = LOCA, 2 = LOCAC, 3 = ATWS |
| `margins_S.npy` | (N_S, 150, 7) | float64 | 7 márgenes térmicos en unidades originales, sin escalar, en el orden de `variables_margen` |
| `scaler_mean.npy` | (12,) | float64 | media de cada variable de planta en entrenamiento |
| `scaler_std.npy` | (12,) | float64 | desviación de cada variable de planta en entrenamiento (1.0 si no tiene varianza) |
| `metadata.json` | — | JSON UTF-8 | ver abajo |

La fila `i` de `X_S`, `y_S` y `margins_S` corresponde a la misma muestra; las filas siguen el orden de `simulaciones[S]` en `metadata.json`.

Reconstrucción del valor original de una variable de planta: `X * scaler_std + scaler_mean`.

## `metadata.json`

```json
{
  "version_formato": 1,
  "origen": "<ruta de origen>",
  "semilla": 42,
  "proporciones": {"train": 0.70, "val": 0.15, "test": 0.15},
  "pasos_por_muestra": 150,
  "paso_segundos": 10,
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
  "simulaciones": {
    "train": ["Normal/1.csv", "LOCA/3.csv", "LOCAC/3.csv", "ATWS/1.csv"],
    "val": [],
    "test": []
  },
  "escalador": {"ajustado_con": "train", "filas_ajuste": 21300, "variables_sin_varianza": []},
  "referencia": {"archivo": "<ruta o null>", "estado": "COINCIDE | DIFIERE | NO DISPONIBLE | OMITIDA", "diferencias": []},
  "advertencias": [
    "NORM tiene una sola simulación: asignada completa a entrenamiento; no tiene muestras de validación ni de prueba.",
    "ATWS tiene una sola simulación: asignada completa a entrenamiento; no tiene muestras de validación ni de prueba."
  ],
  "limitaciones": [
    "Normal y ATWS no tienen métricas sobre datos no vistos: provienen de una sola simulación cada una.",
    "Una muestra por simulación (primeros 150 pasos); las clases quedan muy desbalanceadas (1 / ~100 / ~100 / 1).",
    "Datos de un único simulador (PCTRAN) y una única configuración de planta; no hay datos de planta real."
  ]
}
```

(Las listas de `simulaciones` se muestran abreviadas; contienen todas las simulaciones del conjunto, en el orden de las filas.)

Invariantes comprobables:

- La intersección de dos listas de `simulaciones` cualesquiera es vacía.
- `totales[S]` es igual a la suma de `conteos_muestras[*][S]` y a la primera dimensión de `X_S`.
- Si una clase tiene cero muestras en un conjunto, aparece con `0` y existe una advertencia que la menciona.
