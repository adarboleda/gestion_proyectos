# Quickstart: regla de ATWS

```
uv pip install --python .venv/Scripts/python.exe -e ".[dev]"
.venv/Scripts/evaluar-regla-atws          # o: python -m regla_atws
```

Imprime el reporte y escribe `resultados_regla_atws/` (`regla.json`, `evaluacion.csv`, `resumen.json`).

## Validaciones

1. `regla.json → calibrada_con` es `train`. Con la misma semilla el resultado es idéntico.
2. Todos los TRIP_OK con demanda quedan «sin ATWS (flujo caído)», salvo los de un tipo de señal sin retardo medido en entrenamiento (con la carpeta real, R54). Todas las NORM quedan «sin ATWS (sin demanda)».
3. Cada ATWS detectado tiene `t_deteccion_demanda` ≤ 3 s.
4. `evaluacion.csv` tiene 91 filas (63/15/13).

## Resultado con la carpeta real (2026-11-04)

`evaluar-regla-atws`: ≈ 30 s, código 0.

**Regla calibrada con entrenamiento (63 corridas)**:
- Umbral: **PWNT > 19.3 %** del inicial.
- Margen: ATWS con menor flujo 32.9 % (R26, LOOP) y no-ATWS con mayor flujo 5.7 %; separación de 27.2 puntos, sin solape.
- Retardos (s): `low sg level` 1, `rcp-a trip` 2.5, `scram high flux` 0.5, `scram high prz level` 0.5, `scram lo rx press` 0.5. Para un tipo no visto se usa el mayor: 2.5 s.

| Conjunto | ATWS detectados | Omitidos | Falsas alarmas | Rechazos correctos | Total |
|---|---|---|---|---|---|
| train | 12 | 0 | 0 | 51 | 63 |
| val | 3 | 0 | **1 (R54)** | 11 | 15 |
| test | 3 | 0 | 0 | 10 | 13 |

**Tiempos de detección**:
- Los 18 ATWS se detectan en 2–2.5 s desde la demanda: **meta de 3 s cumplida en 18 de 18**.
- Desde la señal del anunciador: 3 a 5 s (5 s en los de pérdida de caudal, por los 2.5 s de la lógica).

**Falsa alarma R54 (TRIP_OK, validación)**: es un disparo de turbina, cuyo scram llega 5 s después de la señal. Con el reparto de 004, la única TRIP_OK de turbina usable cae en validación (su gemela R55 es corta), así que el tipo «turbine trip» no tiene retardo medido en entrenamiento. Recibe el mayor de entrenamiento (2.5 s) y la regla mira el flujo antes del scram.

**No se corrigió**: cambiar la regla mirando validación sería fuga (principio II). Mejora propuesta para validar con la experta: tomar los retardos de la lógica de protección de su documentación de diseño (turbina 5 s), no solo de los datos de entrenamiento.

## Pruebas

```
python -m pytest tests/atws -q
```
