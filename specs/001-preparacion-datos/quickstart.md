# Quickstart: Preparación de datos NPPAD

Guía de ejecución y validación. Los detalles de formato están en [contracts/cli.md](contracts/cli.md), [contracts/salidas.md](contracts/salidas.md) y [data-model.md](data-model.md).

## Requisitos

- Python 3.11 o superior.
- El dataset NPPAD en `../IA-Nuclear/NuclearPowerPlantAccidentData/Operation_csv_data` (carpetas `Normal`, `LOCA`, `LOCAC`, `ATWS`), o su ruta indicada con `--origen`.
- Opcional: `../IA-Nuclear/data_processed/metadata.json` para la comparación de referencia.

## Instalación

Desde la raíz del repositorio:

```bash
pip install -e ".[dev]"
```

## Ejecución

```bash
preparar-datos
```

Equivale a `python -m preparacion_datos`. Con otra ruta de origen: `preparar-datos --origen RUTA`.

## Resultado esperado con el dataset actual

- Código de salida 0.
- Reporte impreso con los conteos:

| Clase | train | val | test |
|---|---|---|---|
| NORM | 1 | 0 | 0 |
| LOCA | 70 | 15 | 15 |
| LOCAC | 70 | 15 | 15 |
| ATWS | 1 | 0 | 0 |
| **Total** | **142** | **30** | **30** |

- Advertencias de que NORM y ATWS tienen una sola simulación y no tienen muestras de validación ni de prueba.
- Comparación con la referencia: `COINCIDE` para LOCA y LOCAC.
- En `data_processed/`: `X_train/val/test.npy`, `y_*.npy`, `margins_*.npy`, `scaler_mean.npy`, `scaler_std.npy` y `metadata.json`.

## Validaciones

1. **Formas y tipos**: `X_train` es `(142, 150, 12)` float32, `margins_train` es `(142, 150, 7)` float64 y `y_train` es `(142,)` int64; los de validación y prueba tienen `N = 30`.
2. **Sin fuga**: las listas `simulaciones` de `metadata.json` no comparten ningún archivo, y cada severidad de LOCA y de LOCAC está en el mismo conjunto.
3. **Escalado solo con entrenamiento**: en `X_train` la media por variable es cercana a 0 y la desviación cercana a 1; `scaler_mean.npy` coincide con la media de las filas de entrenamiento sin escalar.
4. **Márgenes sin escalar**: los valores de `margins_*` coinciden con los del CSV de origen en las mismas filas.
5. **Reproducibilidad**: ejecutar dos veces y comprobar que los archivos de `data_processed/` son idénticos.
6. **Origen intacto**: el contenido de la carpeta de origen no cambia tras la ejecución.
7. **Archivo defectuoso**: con una copia del origen en la que a un CSV se le quite una de las 19 columnas, el comando termina con código 1, nombra el archivo y la causa y no crea ni modifica `data_processed/`.

## Pruebas automáticas

```bash
pytest
```

Incluye pruebas unitarias con datos sintéticos y una prueba de extremo a extremo con el dataset real que se omite si la ruta de origen no existe.
