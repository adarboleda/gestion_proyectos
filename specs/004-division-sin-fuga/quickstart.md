# Quickstart: División sin fuga de datos (PWR 3L)

Guía de validación. Interfaces en [contracts/api.md](contracts/api.md); entidades en [data-model.md](data-model.md).

## Requisitos

- Python 3.11 o superior y el entorno del proyecto (`pip install -e ".[dev]"` o `uv pip install -e ".[dev]"`).
- Para las validaciones con datos reales: la carpeta de IA-Nuclear con `PWR 3L/` y `NuclearPowerPlantAccidentData/Operation_csv_data/`. Si no está en `../IA-Nuclear`, indicarla con la variable de entorno `IANUCLEAR_DATOS` (en PowerShell: `$env:IANUCLEAR_DATOS = "C:\Users\User\Desktop\IANuclear"`).

## Pruebas automáticas

```bash
python -m pytest tests/pwr3l -q                     # grupos, reparto, verificación (+ dataset real si está)
python -m pytest tests/unit/test_verificacion.py tests/integration -q   # verificación NPPAD
python -m pytest -q                                 # suite completa
```

## Validaciones con el dataset real de PWR 3L

Ejecutar desde la raíz del repositorio (ajustar la ruta):

```python
from preparacion_pwr3l.lectura import cargar_corridas
from preparacion_pwr3l.grupos import formar_grupos
from preparacion_pwr3l.particion import repartir
from preparacion_pwr3l.verificacion import verificar_reparto

corridas = cargar_corridas(r"C:\Users\User\Desktop\IANuclear\PWR 3L")
reparto = repartir(formar_grupos(corridas))
verificar_reparto(corridas, reparto)   # con todas las corridas, incluidas las excluidas
print(reparto.conteos)
print({c: len(v) for c, v in reparto.corridas.items()})
```

1. **Grupos**: 14 grupos `AREA-*` (el de 2000 cm² con 8 corridas), 15 grupos `GEMELAS-*` y el resto individuales; 91 corridas en total.
2. **Sin fuga**: `repartir` termina sin `ErrorFuga` (la verificación se ejecuta dentro).
3. **Equilibrio**: en cada familia, `|reparto.asignadas − reparto.metas|` es menor que su grupo más grande.
4. **Reproducibilidad**: dos llamadas con la misma semilla dan el mismo `conjunto_de_corrida`; con la lista de corridas invertida, también.
5. **Excluidas**: ninguna de las 9 cortas, 3 descartadas y 6 OOD aparece en `reparto.conjunto_de_corrida`.
6. **Familias**: las tres familias tienen al menos una corrida en cada conjunto.

## Validación con el dataset NPPAD real

7. `preparar-datos --origen "<IA-Nuclear>\NuclearPowerPlantAccidentData\Operation_csv_data" --sin-referencia --salida <carpeta temporal>` termina con código 0: la verificación de fuga de 001 no encuentra violaciones.

## Resultados obtenidos

Ejecutado el 2026-10-28 con `IANUCLEAR_DATOS = C:\Users\User\Desktop\IANuclear`.

**PWR 3L** (109 corridas: 91 usables, 9 cortas, 3 descartadas y 6 OOD):

1. **Grupos**: 54, con 14 `AREA-*` (el de 2000 cm² con 8 corridas), 15 `GEMELAS-*` y 25 individuales. ✔
2. **Sin fuga**: `repartir` y `verificar_reparto` con las 109 corridas, sin violaciones. ✔
3. **Equilibrio**:

| Familia | train (meta) | val (meta) | test (meta) | Grupo mayor |
|---|---|---|---|---|
| NORM (19) | 13 (13,3) | 3 (2,85) | 3 (2,85) | 1 |
| LOCA + LOCAC (36) | 25 (25,2) | 6 (5,4) | 5 (5,4) | 8 |
| ATWS + TRIP_OK (36) | 25 (25,2) | 6 (5,4) | 5 (5,4) | 2 |
| **Total (91)** | **63** | **15** | **13** | |

   Todos los desvíos son menores que el grupo mayor de su familia. ✔
4. **Reproducibilidad**: mismo reparto en dos ejecuciones y con la lista invertida. ✔
5. **Excluidas**: ninguna de las 18 está en un conjunto. ✔
6. **Familias**: las tres tienen corridas en los tres conjuntos. ✔

Conteos por clase (train / val / test): NORM 13/3/3 · LOCA 11/4/1 · LOCAC 14/2/4 · ATWS 12/3/3 · TRIP_OK 13/3/2.

Tiempo de agrupar, repartir y verificar: 0,0015 s (objetivo: menos de 1 s).

**Comparación con el proyecto de referencia**: `split_groups` de IA-Nuclear (`pwr3l_rapid_detector.py`) agrupa solo las gemelas. Replicado con estas mismas 91 corridas y su semilla 42, deja **6 de las 10 áreas con más de una corrida** partidas entre entrenamiento y prueba (2, 50, 200, 500, 2000 y 4000 cm²). Con 004 son **0**.

**NPPAD**: `preparar-datos` con el dataset real y la referencia de IA-Nuclear termina con código 0: 142 / 30 / 30, comparación `COINCIDE` y la verificación de fuga sin violaciones (las 100 severidades, cada una en un solo conjunto). ✔ (validación 7)
