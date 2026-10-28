# Data Model: Preprocesamiento PWR 3L

**Fecha**: 2026-10-28 · **Plan**: [plan.md](plan.md)

## Entidades

### Corrida (`descubrimiento.Corrida`)

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | str | Identificador `R<n>[letra]` (p. ej. `R07b`), único en el origen |
| `clase` | str | NORM, LOCA, LOCAC, ATWS, TRIP_OK u OOD |
| `origen` | str | `manual` (carpetas de clase) o `auto` |
| `archivo` | str | Ruta relativa al origen con `/` (p. ej. `LOCA HOT/R10_LOCA_hot_50cm_t60/R10_plotdata_LOCAH50_t60.xls`); para R27 (descartada, dos archivos) la carpeta |
| `area` | int o None | Área de rotura en cm² (solo LOCA y LOCAC) |
| `gemela` | str o None | Id de la gemela ATWS/TRIP_OK según la tabla fija |
| `estado` | str | `usable`, `ood`, `descartada` o `corta` (se fija tras la lectura) |
| `filas` | int o None | Filas del archivo (solo corridas leídas) |
| `serie` | ndarray o None | (300, 33) float64: 26 entradas seguidas de 7 márgenes (solo `usable`) |

**Reglas de validación** (lectura, archivo completo): columnas `TIME` + 33 presentes; todos los valores de esas columnas numéricos, no faltantes y finitos; `TIME[i] == i` para todo `i`. Defecto → `ErrorDatos(archivo, causa, variable)`. Sin defecto y `filas < 300` → `estado = corta`.

**Etiquetas**: NORM = 0, LOCA = 1, LOCAC = 2, ATWS = 3, TRIP_OK = 4. OOD no tiene etiqueta.

### Grupo (`grupos.Grupo`)

| Campo | Tipo | Descripción |
|---|---|---|
| `clave` | str | `AREA-<cm2>`, `GEMELAS-<Ra>-<Rb>` (ids ordenados) o el id de la corrida |
| `familia` | str | `NORM`, `LOCA` (LOCA+LOCAC) o `ATWS` (ATWS+TRIP_OK) |
| `corridas` | list[Corrida] | Corridas usables del grupo, en orden |

Solo se forman con corridas `usable`. Un grupo de gemelas en el que una no es usable queda con una corrida (la clave se mantiene). Una corrida pertenece a un solo grupo; un grupo, a un solo conjunto.

### Partición

`dict[conjunto -> list[Corrida]]` con `conjunto` en `train`, `val`, `test`, más `dict[clave de grupo -> conjunto]`. Dentro de cada conjunto, las corridas se ordenan por etiqueta y número de corrida; ese es el orden de las filas de los arreglos.

### Escalador (`escalado.Escalador`)

`media` (26,) float64, `escala` (26,) float64, `variables_sin_varianza` list[str], `filas_ajuste` int (= 300 · N_train).

### Exclusión (en el resumen)

| Campo | Descripción |
|---|---|
| `id`, `clase`, `archivo` | De la corrida |
| `motivo` | `ood`, `descartada` o `corta` |
| `detalle` | Texto: motivo de la lista de descartadas, «evento fuera de distribución (no es clase de entrenamiento)» o «tiene N filas; se necesitan 300» |

### Resumen (`reporte.Resumen`)

Origen, semilla, corridas encontradas por clase y estado, conteos de muestras por clase y conjunto (las cinco clases en los tres conjuntos), totales, corridas y grupos por conjunto, exclusiones, datos del escalador, advertencias y limitaciones. Se serializa en `metadata.json` y se imprime como reporte.

## Transiciones

```
descubierta ──(id en descartadas)──────────────► descartada  (no se lee)
     │──────(clase OOD)───────────────────────► ood          (no se lee)
     └─(leer y validar todo el archivo)─┬─ defecto ──► ErrorDatos: se detiene todo, no se escribe nada
                                        ├─ filas < 300 ──► corta  (advertencia)
                                        └─ filas ≥ 300 ──► usable (serie = filas 0..299)
usable ──► grupo ──► conjunto (train | val | test) ──► fila de X/y/margins
```
