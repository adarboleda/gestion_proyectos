# Quickstart: preprocesamiento PWR 3L

## Instalación

Desde la raíz del repositorio (Python 3.11 o superior):

```
pip install -e ".[dev]"
```

Con `uv` (sin Python en el PATH):

```
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -e ".[dev]"
```

## Ejecución

```
preparar-pwr3l
```

Equivale a `python -m preparacion_pwr3l`. Lee `../IA-Nuclear/PWR 3L` (solo lectura), imprime el reporte y escribe `data_processed_pwr3l/`. Opciones: `--origen`, `--salida`, `--semilla`.

## Validaciones

1. **Sin fuga**: los ids de `metadata.json → corridas` no se repiten entre `train`, `val` y `test`, y cada clave de `grupos` está en un solo conjunto. Las gemelas (p. ej. R92 y R100) y las LOCA/LOCAC de igual área (p. ej. todas las de 2000 cm²) aparecen en el mismo conjunto.
2. **Escalado solo con entrenamiento**: `scaler_mean.npy` es la media de las filas sin escalar de entrenamiento; `X_train` tiene media ≈ 0 y desviación ≈ 1 por variable (tolerancia 1e-4 en float32), salvo variables sin varianza.
3. **Ventanas de 300 s**: `X_*.shape[1] == 300` y `margins_*.shape[1] == 300`.
4. **Cinco clases**: `y_*` solo contiene 0–4; ninguna corrida OOD (R20, R64, R65, R66, R107, R108) aparece en `corridas`.
5. **Cuentas**: la sección 2 del reporte suma 109 corridas (100 de las cinco clases + 6 OOD + 3 descartadas); usables + cortas = 100.
6. **Archivo defectuoso**: copiar la carpeta, quitar la columna `DNBR` de un `plotdata.csv` y ejecutar con `--origen` sobre la copia: termina con código 1, nombra el archivo y no crea la salida.
7. **Origen sin cambios**: el hash de los archivos de `PWR 3L` es igual antes y después.

## Pruebas

```
python -m pytest tests/pwr3l -q        # solo 002 (incluye la carpeta real si existe)
python -m pytest -q                    # 001 + 002
```
