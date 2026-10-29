# Implementation Plan: Normalización solo con entrenamiento y verificación automática del paso de muestreo

**Branch**: `003-normalizacion-paso-muestreo` | **Date**: 2026-10-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-normalizacion-paso-muestreo/spec.md`

## Summary

Eliminar el supuesto de paso de muestreo fijo en las dos preparaciones de datos del repositorio (`preparacion_datos` para NPPAD y `preparacion_pwr3l` para PWR 3L): calcular el paso de muestreo a partir de las diferencias consecutivas de la columna `TIME` en el archivo completo de cada corrida/simulación, detener el proceso con `ErrorDatos` si el tiempo no avanza, si el paso cambia dentro de un archivo o si dos archivos del mismo dataset tienen pasos distintos, y publicar el paso medido (`paso_segundos`) y la duración de muestra (`duracion_muestra_segundos`) en los metadatos y el reporte de NPPAD (y dejar el paso medido en cada `Corrida` y una función de paso común lista en PWR 3L). Asimismo, reforzar la normalización de `preparacion_datos.escalado` con validación de conjunto de entrenamiento no vacío y forma `(N, 150, 12)`, e implementar el módulo `preparacion_pwr3l.escalado` (`StandardScaler` ajustado exclusivamente con entrenamiento sobre las 26 variables de entrada de forma `(N, 300, 26)`), sin tocar grupos, partición, salida, reporte ni CLI de `002`, que corresponden a otras tareas del equipo.

## Technical Context

**Language/Version**: Python 3.11 o superior (entorno de desarrollo: CPython 3.12 en `.venv` gestionado con `uv`)

**Primary Dependencies**: pandas (3.1), numpy (2.5), scikit-learn (1.9, `StandardScaler`), openpyxl (3.1)

**Storage**: archivos locales; entrada de solo lectura (`.csv`, `.xls`/`.xlsx`), salida `.npy` y `.json` en `data_processed/` (NPPAD)

**Testing**: pytest 9; pruebas unitarias e integración sobre datasets sintéticos (`tests/conftest.py` y `tests/pwr3l/conftest.py`) y pruebas de extremo a extremo con los datasets reales si están disponibles

**Target Platform**: línea de órdenes multiplataforma (desarrollo en Windows 11), sin dependencias externas del sistema

**Project Type**: biblioteca Python con interfaz de línea de órdenes (`preparacion_datos` y `preparacion_pwr3l`)

**Performance Goals**: validación vectorizada con NumPy (`np.diff`) sobre la columna `TIME`, añadiendo sobrecarga despreciable (< 50 ms en los 202 CSV de NPPAD)

**Constraints**: origen de solo lectura; ejecución determinista; ningún artefacto se escribe si algún archivo tiene paso inválido o inconsistente; separación estricta entre NPPAD y PWR 3L (principio IV); alcance limitado exclusivamente a la verificación del paso de muestreo y normalización con entrenamiento; documentación y mensajes en español

**Scale/Scope**: 202 simulaciones en NPPAD (paso medido 10 s, muestras de 150 pasos = 1500 s, 12 variables de entrada) y 100 corridas leídas de las 5 clases en PWR 3L (paso medido 1 s, muestras de 300 pasos = 300 s, 26 variables de entrada)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitución v2.0.0.

| Principio / regla | Evaluación | Cómo se cumple |
|---|---|---|
| I. IA estrictamente consultiva | Cumple (no aplica) | Solo prepara y valida datos; no actúa sobre la planta ni emite diagnósticos operativos. |
| II. Cero fuga de datos | Cumple | En ambas plantas, `ajustar_escalador` calcula media y desviación estándar únicamente sobre `X_train` y `aplicar` transforma `train`, `val` y `test` sin reajustar; se valida que `X_train` no esté vacío y tenga la forma esperada. |
| III. Honestidad y reproducibilidad | Cumple | El paso de muestreo deja de asumirse por constante de configuración y pasa a medirse de `TIME` en todas las filas del archivo; cualquier anomalía detiene la ejecución nombrando archivo, fila y valores. Se reporta el paso real medido y la duración de muestra. |
| IV. Procedencia de datos | Cumple | Los archivos de origen se abren solo para lectura; `preparacion_datos` y `preparacion_pwr3l` mantienen sus propios módulos y configuraciones sin mezclar datos de ambas plantas. |
| V. Alcance acotado a LOCA y ATWS | Cumple | Opera sobre los datasets simulados de accidentes LOCA/ATWS definidos en 001 y 002. |
| Restricciones | Cumple | Python; código en `src/`; pruebas en `tests/`; documentación y mensajes en español. |
| Flujo de desarrollo | Cumple | Flujo Spec Kit completo (`specify → clarify → plan → tasks → analyze → implement`); pruebas antes de implementar; commits `feat(003): …` con trailer `Causa:` cuando se elimine o reescriba código; sesiones registradas con `speckit-metricas`. |

**Resultado de la puerta**: sin violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/003-normalizacion-paso-muestreo/
├── plan.md              # Este archivo (/speckit-plan)
├── research.md          # Fase 0: decisiones técnicas
├── data-model.md        # Fase 1: entidades e invariantes
├── quickstart.md        # Fase 1: guía de verificación
├── contracts/
│   ├── cli.md           # Contrato actualizado de reporte y errores de paso de muestreo
│   └── salidas.md       # Contrato actualizado de metadata.json y artefactos de escalado
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
src/
├── preparacion_datos/               # Planta NPPAD (001)
│   ├── config.py                    # + VARIABLE_TIEMPO = "TIME", se elimina PASO_SEGUNDOS fijo
│   ├── lectura.py                   # + validación y medición de TIME por archivo y paso común del dataset
│   ├── escalado.py                  # + validación de forma (N, 150, 12) y entrenamiento no vacío
│   ├── reporte.py                   # + paso_segundos y duracion_muestra_segundos medidos en Resumen y reporte
│   ├── salida.py                    # + paso_segundos y duracion_muestra_segundos en metadata.json desde Resumen
│   └── cli.py                       # pasa paso_segundos medido a construir_resumen
└── preparacion_pwr3l/               # Planta PWR 3L (002)
    ├── config.py                    # se elimina PASO_SEGUNDOS fijo
    ├── descubrimiento.py            # + campo paso_segundos en Corrida
    ├── lectura.py                   # + medición general de paso en TIME (desde 0 s) y verificación de paso común
    └── escalado.py                  # NUEVO: Escalador, ajustar_escalador y aplicar para (N, 300, 26)

tests/
├── unit/
│   ├── test_lectura.py              # + pruebas de paso medido, no constante, no creciente, <2 filas y discordante
│   ├── test_escalado.py             # + pruebas de entrenamiento vacío y forma inválida
│   └── test_reporte.py              # + pruebas de paso_segundos y duracion_muestra_segundos en reporte y metadata
├── integration/
│   ├── test_cli.py                  # + prueba de parada sin escribir artefactos ante TIME inválido
│   └── test_cli_reporte.py          # + verificación de paso_segundos y duracion_muestra_segundos
└── pwr3l/
    └── unit/
        ├── test_pwr3l_lectura.py    # corrección de redondeo xlsx + pruebas de paso medido y discordante
        └── test_pwr3l_escalado.py   # NUEVO: pruebas unitarias del escalador de 26 variables (N, 300, 26)
```

**Structure Decision**: se interviene únicamente en los módulos de configuración, lectura, escalado y metadatos/reporte de `preparacion_datos` (001) y en `config.py`, `descubrimiento.py`, `lectura.py` y el nuevo `escalado.py` de `preparacion_pwr3l` (002). No se crean ni modifican `grupos.py`, `particion.py`, `salida.py`, `reporte.py` ni `cli.py` de `preparacion_pwr3l` para respetar la división de tareas del equipo.

## Complexity Tracking

Sin violaciones de la constitución que justificar.

## Re-evaluación tras el diseño (Fase 1)

El diseño detallado en [research.md](research.md), [data-model.md](data-model.md) y [contracts/](contracts/) mantiene todos los principios constitucionales:
- Toda lectura y verificación de `TIME` ocurre en memoria antes de escribir cualquier archivo.
- Ningún parámetro de normalización consulta datos fuera de `train`.
- Las dos plantas continúan completamente separadas en paquetes y pruebas independientes.
La puerta sigue en **cumple**.
