# Implementation Plan: Regla determinista de ATWS

**Branch**: `006-regla-atws` | **Date**: 2026-11-04 | **Spec**: [spec.md](spec.md) | **Jira**: KAN-22

**Input**: Feature specification from `/specs/006-regla-atws/spec.md`

## Summary

Un comando (`evaluar-regla-atws`) reutiliza `preparacion_pwr3l` para obtener las 91 corridas usables (002) y su reparto sin fuga (004, semilla 42). Después:
1. Lee el registro de eventos (`*.dat`) de cada corrida.
2. Determina la señal de disparo: la primera señal del sistema de protección o PWNT ≥ 118 %.
3. Calibra con entrenamiento los retardos de la lógica de protección por tipo de señal y el umbral de flujo.
4. Evalúa en los tres conjuntos: en el primer segundo a ≥ 2 s de la demanda, si PWNT/PWNT(0) supera el umbral, recomienda «posible ATWS».

Publica `regla.json`, `evaluacion.csv` y `resumen.json` en `resultados_regla_atws/` e imprime un reporte con la tabla por conjunto y los tiempos de detección frente a la meta de 3 s. Va en un paquete nuevo, `regla_atws`, en `src/`.

## Technical Context

**Language/Version**: Python 3.11 o superior (desarrollo: CPython 3.12 en `.venv` con `uv`)

**Primary Dependencies**: numpy; `preparacion_pwr3l` (lectura de 002, grupos y reparto de 004); `preparacion_datos.salida.publicar` (001). Sin dependencias nuevas.

**Storage**: entrada de solo lectura (carpeta `PWR 3L`: datos y `*.dat`); salida `.json` y `.csv` en `resultados_regla_atws/`

**Testing**: pytest; árbol sintético con perfiles de PWNT y registros de eventos, más prueba con la carpeta real (`tests/datos_reales.py`; se omite si no existe)

**Target Platform**: línea de órdenes en Windows 11

**Project Type**: biblioteca con interfaz de línea de órdenes (`evaluar-regla-atws`, `python -m regla_atws`)

**Performance Goals**: dominado por la lectura de 002 (≈ 30 s con la carpeta real)

**Constraints**: calibración solo con entrenamiento; causal (la decisión en `t` usa datos hasta `t`); determinista; salida marcada como recomendación

**Scale/Scope**: 91 corridas (63/15/13), de ellas 18 ATWS (12/3/3)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio / regla | Evaluación | Cómo se cumple |
|---|---|---|
| I. IA estrictamente consultiva | Cumple | La salida es «posible ATWS» / «sin ATWS» como recomendación para el operador; el reporte y los archivos lo dicen; nada actúa sobre la planta ni sustituye la protección. |
| II. Cero fuga de datos | Cumple | Retardos y umbral se calibran solo con las corridas de entrenamiento del reparto de 004; la decisión en `t` usa PWNT hasta `t` y la demanda, que es anterior. |
| III. Honestidad y reproducibilidad | Cumple | Se informan omisiones, falsas alarmas, margen y la definición exacta de la meta (≤ 3 s desde la demanda); un comando regenera todo. |
| IV. Procedencia de datos | Cumple | Solo PWR 3L, en solo lectura; no se usa NPPAD. |
| V. Alcance LOCA/ATWS | Cumple | Detección de ATWS. |
| Restricciones y flujo | Cumple | Python, `src/regla_atws/`, `tests/atws/`, español; Spec Kit completo; pruebas primero. |

**Resultado de la puerta**: sin violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/006-regla-atws/
├── plan.md, research.md, data-model.md, quickstart.md
├── contracts/ (cli.md, salidas.md)
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/regla_atws/
├── __init__.py, __main__.py
├── config.py        # señales de disparo, alto flujo 118 %, espera 2 s, meta 3 s, rutas
├── eventos.py       # registro de eventos: lectura, tipo de señal, primera señal, instante del scram
├── regla.py         # calibración de retardos y umbral; evaluación de una corrida
├── reporte.py       # resumen por conjunto, tiempos, advertencias, reporte impreso
└── cli.py           # orquestación con preparacion_pwr3l y publicación

tests/atws/
├── conftest.py                          # árbol sintético con PWNT y *.dat
├── unit/test_atws_eventos.py, test_atws_regla.py, test_atws_reporte.py
└── integration/test_atws_cli.py, test_atws_dataset_real.py
```

**Structure Decision**: paquete propio. La dependencia de 002 y 004 es explícita: importa sus funciones, no sus archivos de salida, así que el reparto no puede desalinearse. La rama sale de `002-preprocesamiento-pwr3l-cierre` y debe fusionarse después de ella.

## Complexity Tracking

Sin violaciones.

## Re-evaluación tras el diseño (Fase 1)

El diseño mantiene la calibración en entrenamiento (la evaluación recibe la regla ya calibrada, sin acceso a val/test) y marca toda salida como recomendación. La puerta sigue en **cumple**.
