# Quickstart: Normalización solo con entrenamiento y verificación automática del paso de muestreo

## Requisitos previos

Desde la raíz del repositorio con el entorno virtual instalado:

```powershell
.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

## Validaciones

1. **Sin constante de paso en la configuración**:
   Comprobar que `PASO_SEGUNDOS` ya no existe ni en `preparacion_datos.config` ni en `preparacion_pwr3l.config`.
2. **ejecución de NPPAD (`preparar-datos`)**:
   ```powershell
   .venv\Scripts\python.exe -m preparacion_datos --origen "C:\Users\Administrador\Desktop\Nuecleare\IA-Nuclear\NuclearPowerPlantAccidentData\Operation_csv_data" --referencia "C:\Users\Administrador\Desktop\Nuecleare\IA-Nuclear\data_processed\metadata.json"
   ```
   - Termina con código `0`.
   - El reporte impreso indica `paso medido de TIME: 10 s, duración: 1500 s`.
   - `data_processed/metadata.json` contiene `"paso_segundos": 10` y `"duracion_muestra_segundos": 1500`.
3. **Detección de paso inválido**:
   Si se altera un valor de `TIME` en una copia temporal del dataset (salto, valor repetido o paso distinto entre dos archivos), `preparar-datos` y `cargar_corridas` terminan con error nombrando el archivo, la fila y `[variable TIME]`, sin escribir ningún artefacto.
4. **Escalado exclusivo con entrenamiento en ambas plantas**:
   Ejecutar las pruebas unitarias de escalado de NPPAD y PWR 3L:
   ```powershell
   .venv\Scripts\python.exe -m pytest tests/unit/test_escalado.py tests/pwr3l/unit/test_pwr3l_escalado.py -q
   ```
5. **Suite completa**:
   ```powershell
   .venv\Scripts\python.exe -m pytest -q
   ```
