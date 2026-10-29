# Contrato: línea de órdenes y validación del paso de muestreo

## Invocación (NPPAD)

```text
preparar-datos [--origen RUTA] [--salida RUTA] [--semilla N] [--referencia RUTA | --sin-referencia]
python -m preparacion_datos [mismas opciones]
```

Las opciones y códigos de salida (`0`, `1`, `2`) de `preparar-datos` se mantienen idénticos a la funcionalidad 001.

## Salida estándar (sección 1 actualizada en NPPAD)

La sección `1. Origen y configuración` del reporte impreso muestra el paso medido a partir de `TIME` y la duración de muestra resultante:

```text
== 1. Origen y configuración ==
Origen: <ruta>
Semilla: 42 | Reparto 70/15/15 por simulación completa | 150 pasos por muestra (paso medido de TIME: 10 s, duración: 1500 s)
```

## Salida de error para `TIME` (NPPAD y PWR 3L)

Formato general (sin cambios):

```text
ERROR: <archivo relativo al origen>: <causa> [variable TIME]
```

Causas de error asociadas a la columna `TIME`:
- `falta la variable` (`[variable TIME]`): el archivo no tiene la columna `TIME`.
- `valor faltante` / `valor no numérico` / `valor no finito` (`[variable TIME]`): celda inválida en cualquier fila de `TIME`.
- `menos de 2 filas para calcular el paso de muestreo` (`[variable TIME]`): el archivo tiene 0 o 1 fila de datos.
- `el tiempo debe iniciar en 0 s (inicia en <t0> s)` (`[variable TIME]`, solo en PWR 3L): la primera fila no tiene `TIME == 0`.
- `el tiempo no avanza en la fila de datos <k> (paso <dt> s)` (`[variable TIME]`): diferencia `<= 0` entre dos filas consecutivas.
- `paso de muestreo no constante en la fila de datos <k> (esperado <dt0> s, encontrado <dt> s)` (`[variable TIME]`): la diferencia en la fila `<k>` difiere del primer paso del archivo en más de `1e-6` relativo.
- `paso de muestreo (<dt> s) distinto al del resto del dataset (<dt_ref> s en <archivo_ref>)` (`[variable TIME]`): el archivo tiene paso constante interno pero distinto al medido en el primer archivo del dataset.
