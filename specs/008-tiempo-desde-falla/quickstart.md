# Quickstart: Tiempo de detección desde la falla

Contratos en [contracts/cli.md](contracts/cli.md) y [contracts/salidas.md](contracts/salidas.md).

## Requisitos

- Entorno del proyecto con PyTorch (ver 005) y el modelo de Etapa 1 publicado:

```powershell
.venv\Scripts\entrenar-etapa1.exe --origen "D:\Personal\IANuclear\PWR 3L" --salida modelos\etapa1
```

## Medir

```powershell
.venv\Scripts\medir-tiempo-deteccion.exe --origen "D:\Personal\IANuclear\PWR 3L" --modelo modelos\etapa1 --salida resultados_tiempo_deteccion
```

## Validaciones

1. **Instante de la falla**: las 72 corridas de evento tienen un instante con su fuente (29 «registro» y 43 «programado»), y 5 son inciertas (R22, R47, R48, R54 y R99).
2. **Causalidad**: `lineas_tiempo.csv` tiene 295 filas por corrida, y la confirmación de cada τ depende solo de τ − 1 y τ.
3. **Diagnóstico ≤ 10 s**: `tiempos.json["metas"]["diagnostico_10s"]`, con valor y estado.
4. **ATWS ≤ 3 s desde la demanda**: `tiempos.json["metas"]["atws_3s"]`.
5. **Falsas alarmas**: Etapa 1 y regla, por conjunto.
6. **Comparación**: `tiempos.csv` muestra el tiempo desde la falla y desde el validador para cada corrida de evento.
7. **Modelo verificado**: con otra semilla (`--semilla 7`) el comando termina con código 1 porque el modelo no corresponde.
8. **Reproducibilidad y tiempo**: dos ejecuciones dan `tiempos.json` idéntico, en menos de 5 minutos.

## Pruebas

```powershell
$env:IANUCLEAR_DATOS = "D:\Personal\IANuclear"
.venv\Scripts\python.exe -m pytest tests/tiempo -q
```

## Resultados obtenidos

Se anotan al ejecutar la validación con los datos reales.
