# Quickstart: regla de ATWS

```
uv pip install --python .venv/Scripts/python.exe -e ".[dev]"
.venv/Scripts/evaluar-regla-atws          # o: python -m regla_atws
```

Imprime el reporte y escribe `resultados_regla_atws/` (`regla.json`, `evaluacion.csv`, `resumen.json`).

## Validaciones

1. `regla.json → calibrada_con` es `train`. Con la misma semilla el resultado es idéntico.
2. Todos los TRIP_OK con demanda quedan «sin ATWS (flujo caído)» y todas las NORM sin demanda, «sin ATWS (sin demanda)».
3. Cada ATWS detectado tiene `t_deteccion_demanda` ≤ 3 s.
4. `evaluacion.csv` tiene 91 filas (63/15/13).

## Pruebas

```
python -m pytest tests/atws -q
```
