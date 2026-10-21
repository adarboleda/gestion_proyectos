# Data Model: Preparación de datos NPPAD sin fuga de información

## Entidades

### Simulación
Una corrida del simulador, leída de un CSV de solo lectura.

| Campo | Tipo | Regla |
|---|---|---|
| clase | enum {NORM, LOCA, LOCAC, ATWS} | carpetas de origen `Normal`, `LOCA`, `LOCAC`, `ATWS` |
| etiqueta | entero 0–3 | 0 = NORM, 1 = LOCA, 2 = LOCAC, 3 = ATWS |
| severidad | entero 1–100 o vacío | número del archivo (`7.csv` → 7); solo LOCA y LOCAC; Normal y ATWS no tienen |
| archivo | texto | ruta relativa a la carpeta de origen, p. ej. `LOCA/7.csv`; identifica la simulación |
| serie | tabla (150 × 19) | primeros 150 pasos de las 19 variables requeridas, sin valores faltantes ni no finitos |

Cantidades esperadas en el dataset: NORM 1, LOCA 100, LOCAC 100, ATWS 1 (202).

### Muestra
Una por simulación.

| Campo | Forma / tipo | Regla |
|---|---|---|
| X | (150, 12) float32 | variables de planta escaladas con el escalador de entrenamiento |
| margins | (150, 7) float64 | márgenes térmicos en unidades originales, sin escalar, misma fila temporal que X |
| y | int64 | etiqueta de la clase de la simulación |
| simulación de origen | referencia a Simulación | uno a uno |

Variables de planta (orden fijo de las 12 columnas de X): `P, TAVG, THA, TCA, WRCA, WRCB, LVPZ, LVCR, PWNT, PWR, WECS, WLR`.
Márgenes térmicos (orden fijo de las 7 columnas de margins): `DNBR, TPCT, SCMA, SCMB, TSAT, FRCL, FRZR`.

### Conjunto
Uno de `train`, `val`, `test`.

| Campo | Regla |
|---|---|
| simulaciones | lista de simulaciones completas; la unión de los tres conjuntos es el total y la intersección de dos cualesquiera es vacía |
| orden | por etiqueta de clase y luego por severidad numérica; es el orden de las filas de los arreglos |
| composición esperada | train 142 (70 LOCA, 70 LOCAC, 1 NORM, 1 ATWS) · val 30 (15 LOCA, 15 LOCAC) · test 30 (15 LOCA, 15 LOCAC) |

### Partición por severidad
Asignación de cada severidad a un conjunto.

| Campo | Regla |
|---|---|
| severidades | unión de las severidades presentes en LOCA y LOCAC, ordenadas numéricamente |
| reparto | permutación con semilla 42; `n_train = round(0.70·n)`, `n_val = round(0.15·n)`, `n_test = n − n_train − n_val` |
| aplicación | la severidad asignada a un conjunto lleva consigo a la simulación de LOCA y a la de LOCAC que la tengan |
| Normal / ATWS | no entran en la permutación; su única simulación se asigna a `train` |

### Parámetros de escala
| Campo | Forma / tipo | Regla |
|---|---|---|
| media | (12,) float64 | `StandardScaler.mean_`, calculada solo con las filas de `train` (N_train·150) |
| desviación | (12,) float64 | `StandardScaler.scale_`; vale 1.0 para una variable sin varianza en entrenamiento |
| variables sin varianza | lista | variables cuya desviación en entrenamiento es 0; se declaran en el reporte |

### Referencia (opcional)
`metadata.json` del proyecto previo. Solo se leen `sample_counts.LOCA` y `sample_counts.LOCAC` (train/val/test).

### Reporte de preparación
Texto impreso y contenido de `metadata.json`: conteos por clase y por conjunto, simulaciones por conjunto, semilla, proporciones, escalador, advertencias, limitaciones y resultado de la comparación con la referencia.

## Relaciones

- Una Simulación genera exactamente una Muestra.
- Cada Simulación pertenece a exactamente un Conjunto.
- Los Parámetros de escala dependen solo de las Muestras de `train`.
- LOCA N y LOCAC N (misma severidad) pertenecen siempre al mismo Conjunto.

## Reglas de validación

- Toda simulación tiene las 19 variables, al menos 150 filas y valores numéricos finitos en esas 150 filas; si no, la ejecución se detiene con un error que nombra el archivo y la causa, y no se escribe ningún conjunto.
- Forma de salida: `X_*` `(N,150,12)`, `margins_*` `(N,150,7)`, `y_*` `(N,)`, con el mismo `N` y el mismo orden en los tres arreglos de un conjunto.
- La suma de muestras de `train`, `val` y `test` es igual al número de simulaciones leídas.

## Transiciones

Leer y validar todo → repartir → ajustar escalador con `train` → transformar los tres conjuntos → escribir en directorio temporal → publicar en `data_processed/` → imprimir reporte. Un fallo en cualquier paso anterior a "publicar" deja `data_processed/` sin cambios.
