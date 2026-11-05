# Data Model: Documentación del dataset de Fase 1

## 1. Esquema de `data_processed/metadata.json`

```json
{
  "selected_features": [
    "P", "TAVG", "THA", "TCA", "WRCA", "WRCB", 
    "LVPZ", "LVCR", "PWNT", "PWR", "WECS", "WLR"
  ],
  "margin_features": [
    "DNBR", "TPCT", "SCMA", "SCMB", "TSAT", "FRCL", "FRZR"
  ],
  "margin_feature_categories": {
    "thermal_margins": ["DNBR", "TPCT", "SCMA", "SCMB", "TSAT"],
    "damage_indicators": ["FRCL", "FRZR"]
  },
  "class_mapping": {
    "NORM": 0,
    "LOCA": 1,
    "LOCAC": 2,
    "ATWS": 3
  },
  "sequence_length": 150,
  "time_step_seconds": 10,
  "sequence_duration_seconds": 1500,
  "split_ratios_target": {
    "train": 0.70,
    "val": 0.15,
    "test": 0.15
  },
  "seed": 42,
  "sliding_window": {
    "applied_to_classes": ["NORM", "ATWS"],
    "stride": 10,
    "min_windows_val_test": 3,
    "note": "Ventanas generadas mediante bloques temporales NO solapados por split dentro del único archivo disponible para NORM y ATWS."
  },
  "file_counts": {
    "NORM": 1,
    "LOCA": 100,
    "LOCAC": 100,
    "ATWS": 1
  },
  "sample_counts": {
    "NORM": {"train": 1, "val": 1, "test": 0},
    "LOCA": {"train": 70, "val": 15, "test": 15},
    "LOCAC": {"train": 70, "val": 15, "test": 15},
    "ATWS": {"train": 10, "val": 3, "test": 3}
  },
  "known_limitations": [
    "NORM proviene de un único archivo de origen (302 filas, menos de las 450 requeridas para 3 bloques disjuntos); el split 'test' de NORM queda vacío por diseño matemático.",
    "Las muestras de NORM y ATWS provienen de un único archivo cada una; existe autocorrelación temporal entre ventanas de la misma clase.",
    "Fuerte desbalance de clases: LOCA/LOCAC aportan decenas de muestras independientes por split, mientras NORM/ATWS aportan muy pocas ventanas.",
    "NORM cuenta con una sola muestra de entrenamiento en el split estándar.",
    "El conjunto de 12 entradas se enfoca en el lazo primario y neutrónico; variables de lado secundario y contención no forman parte de este vector."
  ],
  "scaler": {
    "fitted_on": "train_only",
    "mean_file": "scaler_mean.npy",
    "std_file": "scaler_std.npy"
  }
}
```

---

## 2. Estructura de `docs/README_FASE1.md`

```markdown
# Fase 1 — Preprocesamiento y Documentación del Dataset NPPAD

1. Objetivo y Resumen Ejecutivo
2. Origen de los Datos y Licenciamiento
3. Modelo de Planta Nuclear (PWR 2 Lazos / PCTRAN)
4. Diccionario de Variables de Entrada (12 canales normalizados)
5. Diccionario de Variables de Margen Térmico (7 canales físicos)
6. Cobertura del Dataset frente a las 97 Variables de PCTRAN
7. Conteos de Archivos y Mapeo de Carpetas
8. Estrategia de Partición y Cero Fuga de Datos
9. Limitaciones Conocidas y Recomendaciones Metodológicas
10. Estructura de Metadatos y Verificación
```

