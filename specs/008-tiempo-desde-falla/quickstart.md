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

Ejecución del 2026-11-04 con `D:\Personal\IANuclear\PWR 3L` y el modelo `modelos\etapa1` (semilla 42, mejor época de 005). El comando tardó 56 s, terminó con código 0, y dos ejecuciones dieron los cuatro archivos idénticos byte a byte. Con `--semilla 7` terminó con código 1 («el modelo … no corresponde al reparto actual») y no creó la carpeta de salida.

**1. Instante de la falla**: 72 corridas de evento, 29 «registro» y 43 «programado». Hay 5 inciertas, ninguna en prueba:

| Corrida | Conjunto | Instante | Validador | Motivo |
|---|---|---|---|---|
| R22 | entrenamiento | 47,5 s (registro) | 13 s | FWIV cerradas a 47,5 s, pero la planta cambia antes |
| R47 | validación | 45 s (programado) | 1 s | falla 9: PCTran no respetó el retardo |
| R48 | entrenamiento | 20 s (programado) | 1 s | ídem |
| R54 | validación | 45 s (programado) | 1 s | ídem |
| R99 | entrenamiento | 60 s (programado) | 1 s | ídem |

**2. Causalidad**: `lineas_tiempo.csv` tiene 8 260 filas (28 corridas × 295 segundos).

**3. Diagnóstico ≤ 10 s desde la falla (prueba): NO CUMPLE, 5 de 10 (50 %)**

| Corrida | Clase | Área (cm²) | Falla (s) | Fuente | Confirmación | Desde la falla | Desde el validador (005) |
|---|---|---|---|---|---|---|---|
| R19 | LOCAC | 10 | 30 | programado | 151 | 121 s | 120 s |
| R29 | ATWS | — | 2 | registro | 7 | 5 s | 4 s |
| R44 | LOCA | 100 | 50 | programado | 69 | 19 s | 19 s |
| R46 | LOCAC | 5 | 40 | programado | — | no detectado | no detectado |
| R83 | LOCAC | 100 | 35 | programado | 54 | 19 s | 19 s |
| R88 | LOCAC | 10 | 45 | programado | 165 | 120 s | 120 s |
| R95 | ATWS | — | 50 | registro | 52 | 2 s | 2 s |
| R96 | ATWS | — | 26 | registro | 29 | 3 s | 3 s |
| R103 | TRIP_OK | — | 50 | registro | 52 | 2 s | 2 s |
| R104 | TRIP_OK | — | 26 | registro | 29 | 3 s | 3 s |

- **TRANS**: 5 de 5 en ≤ 10 s (mediana 3 s, máximo 5 s).
- **LOCA**: 0 de 5. Detectadas 4, mediana 69,5 s, máximo 121 s.
- Validación (referencia): LOCA 1 de 6 en ≤ 10 s (R80, 3 000 cm², 10 s; las grandes en 10–16 s, las de 20 cm² en 55–56 s); TRANS 4 de 4 en 3 s.
- Medir desde la falla cambia poco frente a 005 (diferencias de −1 a 0 s en prueba). La diferencia grande aparece en las inciertas: en R47 y R54, el validador marca 1 s y la falla programada es a los 45 s.

**4. ATWS ≤ 3 s desde la demanda (validación + prueba): CUMPLE, 6 de 6 (100 %)**. Solo prueba: 3 de 3. Tiempos de 2 a 2,5 s desde la demanda. Desde la falla, como dato: 5 s en R25, R49, R95 y R96, y 35 s en R29, cuya demanda de disparo llega 33 s después del iniciador. En R47, que es incierta, solo hay tiempo desde la demanda (2 s).

**5. Falsas alarmas**:
- **Prueba**: 0 de la Etapa 1 (ni en las corridas NORM R33, R36 y R40, ni antes de la falla) y 0 de la regla.
- **Validación**: 0 de la Etapa 1 y 1 de la regla (R54, TRIP_OK, la misma que informó 006).
- **Confusiones**: ninguna.

**6. Comparación**: cada corrida de evento de `tiempos.csv` tiene `tiempo_diagnostico_s` (desde la falla) y `tiempo_desde_validador_s` (como en 005).

**Conclusión**: la meta de 3 s del ATWS se cumple. La meta de 10 s del diagnóstico se cumple en los transitorios con disparo, pero no en las LOCA pequeñas y medianas (≤ 100 cm²) del conjunto de prueba. Con 13 corridas de prueba, las cifras tienen mucha incertidumbre.
