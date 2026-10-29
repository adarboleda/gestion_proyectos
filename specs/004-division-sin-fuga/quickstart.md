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

Se anotan aquí al ejecutar la tarea de validación con los datos reales.
