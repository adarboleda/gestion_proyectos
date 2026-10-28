# Contrato: línea de órdenes `preparar-pwr3l`

## Invocación

```
preparar-pwr3l [--origen RUTA] [--salida RUTA] [--semilla N]
python -m preparacion_pwr3l [mismas opciones]
```

| Opción | Por defecto | Descripción |
|---|---|---|
| `--origen` | `../IA-Nuclear/PWR 3L` | Carpeta PWR 3L (solo lectura) |
| `--salida` | `data_processed_pwr3l` | Carpeta donde se publican los artefactos |
| `--semilla` | `42` | Semilla del reparto de grupos |

## Códigos de salida

| Código | Significado |
|---|---|
| 0 | Preparación completa; artefactos publicados y reporte impreso en la salida estándar |
| 1 | Error de datos (archivo o carpeta defectuosa) o de escritura; mensaje en la salida de error; no se publica ningún artefacto |
| 2 | Argumentos inválidos (lo produce `argparse`) |

## Mensaje de error de datos

```
ERROR: <ruta relativa al origen>: <causa> [variable <nombre>]
```

Causas: `no existe la carpeta de origen`, `carpeta no reconocida`, `nombre de corrida no reconocido`, `clase desconocida`, `identificador de corrida repetido (también en <otra ruta>)`, `no hay archivo de datos`, `hay más de un archivo de datos`, `no se pudo determinar el área de rotura`, `archivo ilegible (<tipo>)`, `falta la variable`, `valor no numérico`, `valor faltante`, `valor no finito`, `el tiempo no avanza de 1 s en 1 s desde 0 (fila <i>)`, `no hay corridas de la clase <CLASE>`.

## Reporte (salida estándar)

```
REPORTE DE PREPARACIÓN DE DATOS PWR 3L
== 1. Origen y configuración ==        origen, semilla, 300 pasos de 1 s, 26 entradas, 7 márgenes
== 2. Corridas encontradas ==          tabla por clase: usables, cortas, descartadas, OOD, total
== 3. Muestras por clase y conjunto == tabla 5 clases × train/val/test con totales; * en celdas en cero
== 4. Grupos y corridas por conjunto == por conjunto: número de corridas y cada grupo con sus ids
== 5. Corridas sin muestra ==          cada corrida excluida: id, clase, motivo y detalle
== 6. Escalador ==                     ajustado solo con entrenamiento (filas); variables sin varianza
== 7. Advertencias ==                  clase sin muestras en un conjunto; corridas cortas
== 8. Limitaciones conocidas ==
== 9. Artefactos escritos ==
```
