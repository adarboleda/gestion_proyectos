# Data Model: División sin fuga de datos (PWR 3L)

## Corrida (existente, 002)

Definida en `preparacion_pwr3l.descubrimiento.Corrida`. Campos que usa esta funcionalidad:

| Campo | Uso |
|---|---|
| `id` | Identificador `R<n>[letra]`; clave de los grupos individuales y de las parejas |
| `clase` | NORM, LOCA, LOCAC, ATWS, TRIP_OK u OOD |
| `estado` | Solo `usable` entra en los conjuntos; `corta`, `descartada` y `ood` quedan excluidas |
| `area` | cm² enteros, solo LOCA/LOCAC; obligatoria si la corrida es usable |
| `gemela` | Identificador de la gemela ATWS/TRIP_OK según la tabla del proyecto, o `None` |
| `archivo` | Se usa en los mensajes de error |

No se modifica ningún campo.

## Grupo (nuevo, `grupos.py`)

| Campo | Tipo | Regla |
|---|---|---|
| `clave` | str | `AREA-<cm2>`, `GEMELAS-<a>-<b>` (orden natural de identificador) o `<Rid>` |
| `familia` | str | NORM, LOCA o ATWS (`config.FAMILIAS` de su primera corrida) |
| `corridas` | list[Corrida] | 1 o más corridas usables, ordenadas con `clave_orden`; todas de la misma familia |
| `tamano` | int (propiedad) | `len(corridas)` |

Invariantes: cada corrida usable está en exactamente un grupo; un `AREA` solo tiene LOCA/LOCAC con esa área; un `GEMELAS` tiene exactamente un ATWS y su TRIP_OK.

## Reparto (nuevo, `particion.py`)

| Campo | Tipo | Contenido |
|---|---|---|
| `semilla` | int | Semilla usada |
| `grupos` | list[Grupo] | Todos los grupos, en orden de clave |
| `conjunto_de_grupo` | dict[str, str] | clave de grupo → `train` / `val` / `test` |
| `conjunto_de_corrida` | dict[str, str] | id de corrida → conjunto |
| `corridas` | dict[str, list[Corrida]] | conjunto → corridas ordenadas con `clave_orden` |
| `conteos` | dict[str, dict[str, int]] | clase → conjunto → número de corridas; las 5 clases y los 3 conjuntos siempre presentes |
| `metas` | dict[str, dict[str, float]] | familia → conjunto → meta (0.70·n, 0.15·n, 0.15·n) |
| `asignadas` | dict[str, dict[str, int]] | familia → conjunto → corridas asignadas |

Invariantes: verificado por `verificar_reparto` antes de salir de `repartir`; `|asignadas − metas| < tamaño del grupo más grande de la familia`.

## ErrorFuga (nuevo, uno por paquete)

Excepción con `violaciones: list[str]`, una por regla incumplida, y mensaje `FUGA DE DATOS: <n> violación(es)` seguido de una línea por violación. Ejemplos de líneas:

- `la corrida R10 está en train y en test`
- `el área de 50 cm² está partida: R10 (train), R04 (val)`
- `las gemelas R21 (train) y R59 (test) están en conjuntos distintos`
- `la corrida R41 (corta) está en val`
- `el grupo AREA-2000 está partido entre train y val`
- NPPAD: `la severidad 37 está partida: LOCA/37.csv (train), LOCAC/37.csv (test)`

## Transiciones

`corridas leídas (002)` → `formar_grupos` → `list[Grupo]` → `repartir(grupos, semilla)` → `Reparto` (verificado) → KAN-18 construye arreglos, reporte y metadatos.
