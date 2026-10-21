# Contrato: línea de órdenes

## Invocación

```text
preparar-datos [--origen RUTA] [--salida RUTA] [--semilla N] [--referencia RUTA | --sin-referencia]
python -m preparacion_datos [mismas opciones]
```

Se ejecuta desde la raíz del repositorio.

| Opción | Por defecto | Significado |
|---|---|---|
| `--origen` | `../IA-Nuclear/NuclearPowerPlantAccidentData/Operation_csv_data` | Carpeta con las subcarpetas `Normal`, `LOCA`, `LOCAC` y `ATWS`. Solo se lee. |
| `--salida` | `data_processed` | Carpeta donde se publican los artefactos (ver [salidas.md](salidas.md)). |
| `--semilla` | `42` | Semilla del reparto por severidad. |
| `--referencia` | `../IA-Nuclear/data_processed/metadata.json` | `metadata.json` del proyecto previo para comparar los conteos de LOCA y LOCAC. |
| `--sin-referencia` | — | Omite la comparación con la referencia. |

## Códigos de salida

| Código | Significado | Efecto en `--salida` |
|---|---|---|
| 0 | Preparación completa; la referencia coincide, no está disponible o fue omitida | Artefactos publicados |
| 1 | Error de entrada: carpeta o subcarpeta de origen inexistente, archivo defectuoso (variable ausente, valores no numéricos o faltantes, menos de 150 pasos) | Sin cambios: no se escribe ningún conjunto |
| 2 | Preparación completa, pero los conteos de LOCA o LOCAC difieren de la referencia | Artefactos publicados; la diferencia queda en el reporte |

## Salida estándar

Reporte en español, con estas secciones en este orden:

1. **Origen y configuración**: ruta de origen, semilla, proporciones 70/15/15, 150 pasos.
2. **Muestras por clase y conjunto**: tabla con filas NORM, LOCA, LOCAC, ATWS y columnas train, val, test y total; las celdas en cero se muestran como `0*` con la nota «* sin muestras». Última fila: totales.
3. **Simulaciones por conjunto**: para cada conjunto, las simulaciones que lo forman agrupadas por clase (FR-009).
4. **Escalador**: ajustado solo con entrenamiento (N filas); lista de variables sin varianza (o «ninguna»).
5. **Advertencias**: una línea por cada clase con una sola simulación («NORM tiene una sola simulación: asignada completa a entrenamiento; no tiene muestras de validación ni de prueba.») y por cada celda en cero de una clase con varias simulaciones.
6. **Limitaciones conocidas**: texto fijo (sin métricas sobre datos no vistos para Normal y ATWS, una muestra por simulación y clases desbalanceadas, simulador único).
7. **Comparación con la referencia**: `COINCIDE`, `DIFIERE` (con las celdas que difieren), `NO DISPONIBLE` u `OMITIDA`; solo LOCA y LOCAC.
8. **Artefactos escritos**: lista de archivos en `--salida`.

## Salida de error

Mensaje en la salida de error, en español, de la forma:

```text
ERROR: <archivo relativo al origen>: <causa> [variable <nombre>]
```

Causas posibles: `falta la variable`, `valor no numérico`, `valor faltante`, `valor no finito`, `menos de 150 pasos (tiene N)`, `no existe la carpeta de clase`.
