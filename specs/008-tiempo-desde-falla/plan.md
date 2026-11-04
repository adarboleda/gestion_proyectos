# Implementation Plan: Tiempo de detección desde la falla (PWR 3L)

**Branch**: `008-tiempo-desde-falla` | **Date**: 2026-11-04 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/008-tiempo-desde-falla/spec.md`

## Summary

Un paquete nuevo, `tiempo_deteccion`, con el comando `medir-tiempo-deteccion`, mide cuánto tarda el diagnóstico rápido desde la falla, sin entrenar ni ajustar nada:

1. **Instante de la falla** (`falla.py`).
   - Si es una corrida de transitorio con disparo (ATWS o TRIP_OK), se usa la primera línea del iniciador en el Transient Report: cierre de una FWIV, «RCP-A trip», «Turbine Trip Control Change» o apertura de la válvula de la turbina del AFW.
   - En otro caso se usa el instante programado: el retardo de la falla iniciadora en `config.json`, o el `_t<n>` de la carpeta.
   - Se marca «incierta» la corrida en la que el validador ve cambios más de 2 s antes.
2. **Reproducción causal segundo a segundo** (`reproduccion.py`).
   - El clasificador de Etapa 1 guardado por 005 da, en cada τ, las probabilidades de la ventana de 30 s hasta τ.
   - La familia se confirma con la regla sostenida de 005 (≥ 0,80 dos segundos seguidos).
3. **Tiempo de ATWS** (`atws.py`): la regla de 006, calibrada solo con entrenamiento, aporta su segundo de decisión y su demanda de disparo.
4. **Resultados** (`evaluacion.py`): tiempos de diagnóstico desde la falla y, para comparar, desde el inicio del validador; tiempos de ATWS desde la demanda y desde la falla; metas de 10 s y 3 s; falsas alarmas y líneas de tiempo.

Antes de evaluar, el comando comprueba que el modelo guardado corresponde al reparto sin fuga actual.

## Technical Context

**Language/Version**: Python 3.11 o superior (entorno: 3.12 en `.venv`)

**Primary Dependencies**: los paquetes del proyecto `preparacion_pwr3l` (002–004), `clasificador_etapa1` (005, con PyTorch del extra `modelo`) y `regla_atws` (006); numpy. Sin dependencias nuevas.

**Storage**: lee la carpeta PWR 3L y `modelos/etapa1/` (solo lectura); escribe en `resultados_tiempo_deteccion/` (configurable): `tiempos.json`, `tiempos.csv`, `lineas_tiempo.csv` y `reporte.txt`, fuera de git

**Testing**: pytest; pruebas unitarias con registros y probabilidades construidos a mano; integración con un modelo de 005 entrenado sobre corridas sintéticas; prueba real omitida sin datos (`IANUCLEAR_DATOS`) o sin modelo

**Target Platform**: línea de órdenes en Windows 11, CPU

**Project Type**: biblioteca Python con interfaz de línea de órdenes

**Performance Goals**: evaluación completa (validación + prueba: 28 corridas × 295 segundos) en menos de 5 minutos; la lectura de las 109 corridas domina (~10 s)

**Constraints**: causal (cada decisión solo con datos hasta su segundo); sin reentrenar; determinista; sin NPPAD; mensajes en español

**Scale/Scope**: datos reales: 72 corridas de evento usables (29 con instante del registro, 43 programado, 5 inciertas: R22, R47, R48, R54, R99, ninguna en prueba); evaluación de 15 corridas de validación y 13 de prueba

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitución v2.0.0.

| Principio / regla | Evaluación | Cómo se cumple |
|---|---|---|
| I. IA estrictamente consultiva | Cumple | El reporte y los archivos declaran que el diagnóstico y la regla son recomendaciones; nada actúa sobre la planta. |
| II. Cero fuga de datos | Cumple | No se entrena ni ajusta nada: se usa el modelo de 005 (verificado contra el reparto de 004) y la regla de 006 calibrada solo con entrenamiento; cada decisión usa datos hasta su segundo. |
| III. Honestidad y reproducibilidad | Cumple | Cada meta con su definición exacta y su resultado tal como sale; las corridas inciertas se informan aparte, no se ocultan; comparación con la medición anterior; un comando, determinista. |
| IV. Procedencia de datos | Cumple | Solo PWR 3L, en lectura; NPPAD no se usa. |
| V. Alcance acotado a LOCA y ATWS | Cumple | Mide la detección de las familias LOCA y transitorio con disparo y del ATWS. |
| Restricciones | Cumple | Python; `src/tiempo_deteccion/`, `tests/tiempo/`; español. |
| Flujo de desarrollo | Cumple | Ciclo Spec Kit completo; pruebas primero; commits `feat(008): …`; sesiones de métricas por fase. |

**Resultado de la puerta**: sin violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/008-tiempo-desde-falla/
├── plan.md, research.md, data-model.md, quickstart.md
├── contracts/
│   ├── cli.md           # comando medir-tiempo-deteccion
│   └── salidas.md       # tiempos.json, tiempos.csv, lineas_tiempo.csv, reporte.txt
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
pyproject.toml                         # CAMBIO: guion medir-tiempo-deteccion
.gitignore                             # CAMBIO: resultados_tiempo_deteccion/
src/tiempo_deteccion/                  # NUEVO
├── __init__.py, __main__.py
├── config.py                          # metas, tolerancia de incertidumbre, iniciadores del registro
├── falla.py                           # instante de la falla y su fuente; inciertas
├── reproduccion.py                    # Etapa 1 segundo a segundo con el modelo guardado; verificación del modelo
├── atws.py                            # regla de 006: demanda, decisión y tiempos
├── evaluacion.py                      # tiempos, metas, falsas alarmas, comparación y reporte
└── cli.py                             # orquestación y publicación

tests/tiempo/                          # NUEVO
├── conftest.py                        # registros sintéticos y modelo de 005 entrenado en sintético
├── unit/test_tiempo_falla.py
├── unit/test_tiempo_reproduccion.py
├── unit/test_tiempo_atws.py
├── unit/test_tiempo_evaluacion.py
├── integration/test_tiempo_cli.py
└── integration/test_tiempo_real.py
```

**Structure Decision**: un paquete de evaluación separado que solo lee lo que producen 005 y 006, sin modificarlos; así la medición no puede alterar el modelo ni la regla.

## Complexity Tracking

Sin violaciones de la constitución que justificar.

## Re-evaluación tras el diseño (Fase 1)

[data-model.md](data-model.md) y [contracts/](contracts/) mantienen la puerta: el modelo se carga y se verifica, la regla se calibra con `calibrar()` de 006 sobre las corridas de entrenamiento, y la reproducción usa `construir_muestras` de 005 (ventanas solo con datos hasta τ). **Cumple**.
