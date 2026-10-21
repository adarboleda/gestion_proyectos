# Implementation Plan: Preparación de datos NPPAD sin fuga de información

**Branch**: `001-preparacion-datos` | **Date**: 2026-10-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-preparacion-datos/spec.md`

## Summary

Un comando de línea de órdenes lee las 202 simulaciones NPPAD de las carpetas `Normal`, `LOCA`, `LOCAC` y `ATWS`, toma los primeros 150 pasos de cada una como una muestra, reparte las simulaciones completas en entrenamiento, validación y prueba (70/15/15, semilla 42), escala las 12 variables de planta con un escalador ajustado solo con entrenamiento, conserva sin escalar las 7 variables de margen térmico y escribe los arreglos, el escalador y un `metadata.json` en `data_processed/`. Imprime un reporte con los conteos por clase y conjunto y las limitaciones. Enfoque técnico: paquete Python `preparacion_datos` en `src/` (pandas/numpy para leer y transformar, scikit-learn `StandardScaler` para escalar), con toda la validación hecha en memoria antes de escribir nada, de modo que un archivo defectuoso detenga la ejecución sin dejar conjuntos parciales.

## Technical Context

**Language/Version**: Python 3.11 o superior (entorno de desarrollo: 3.13.7)

**Primary Dependencies**: pandas (3.0), numpy (2.3), scikit-learn (1.8, `StandardScaler`)

**Storage**: archivos locales; entrada en CSV de solo lectura, salida en `.npy` y `.json` dentro de `data_processed/`

**Testing**: pytest 9; pruebas unitarias con datos sintéticos y una prueba de integración de extremo a extremo contra el dataset real (se omite si la ruta no existe)

**Target Platform**: línea de órdenes en Windows 11 (desarrollo), sin dependencias específicas del sistema

**Project Type**: biblioteca Python con una interfaz de línea de órdenes (`python -m preparacion_datos` y el guion `preparar-datos`)

**Performance Goals**: sin objetivo cuantitativo; el dataset ocupa decenas de MB y la preparación completa debe terminar en segundos (se lee `nrows=150` por archivo)

**Constraints**: el dataset original es de solo lectura; ejecución determinista; ningún conjunto se escribe si algún archivo es defectuoso; documentación y mensajes en español

**Scale/Scope**: 202 simulaciones (1 Normal, 100 LOCA, 100 LOCAC, 1 ATWS) → 202 muestras de forma (150, 12) más márgenes (150, 7); 142 en entrenamiento, 30 en validación y 30 en prueba

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitución v2.0.0.

| Principio / regla | Evaluación | Cómo se cumple |
|---|---|---|
| I. IA estrictamente consultiva | Cumple (no aplica) | La funcionalidad solo prepara datos; no hay salida hacia la planta ni diagnóstico. |
| II. Cero fuga de datos | Cumple | Partición por simulación completa; el escalador se ajusta solo con entrenamiento (`fit` sobre `X_train`, `transform` sobre los tres); LOCA y LOCAC de igual severidad van al mismo conjunto (ver nota abajo); no hay información posterior a `t` porque cada muestra son los primeros 150 pasos. |
| III. Honestidad y reproducibilidad | Cumple | Semilla fija, orden determinista, un solo comando, `metadata.json` y reporte con las limitaciones (Normal y ATWS sin validación ni prueba, desbalance de clases). |
| IV. Procedencia de datos | Cumple | El origen se abre solo para lectura y la prueba de integración verifica que no cambia; solo se usan las cuatro carpetas de NPPAD, una sola planta. |
| V. Alcance acotado a LOCA y ATWS | Cumple | Las demás carpetas del dataset se ignoran; no se usa ningún dato de planta real. |
| Restricciones | Cumple | Python; código en `src/preparacion_datos/`; pruebas en `tests/`; documentación en español. |
| Flujo de desarrollo | Cumple | Spec Kit completo; pruebas automáticas para partición, escalado, validación de archivos y no modificación del origen; commits `feat(001): descripción` con trailer `Causa:` cuando se elimine o reescriba código. |

**Nota sobre la entrada del plan**: el plan pedido dice que "LOCA y LOCAC se reparten por separado". La spec (FR-004) y la constitución (principio II) exigen que la simulación de LOCA y la de LOCAC de igual severidad vayan al mismo conjunto. Se resuelve repartiendo las 100 severidades una sola vez (70/15/15, semilla 42) y aplicando esa misma asignación a ambas clases: cada clase conserva sus propios conteos 70/15/15 y se respeta la regla. Ver [research.md](research.md), decisión 1.

**Resultado de la puerta**: sin violaciones. Se re-evalúa tras el diseño (abajo).

## Project Structure

### Documentation (this feature)

```text
specs/001-preparacion-datos/
├── plan.md              # Este archivo (/speckit-plan)
├── research.md          # Fase 0
├── data-model.md        # Fase 1
├── quickstart.md        # Fase 1
├── contracts/
│   ├── cli.md           # Contrato de la línea de órdenes
│   └── salidas.md       # Contrato de los artefactos de data_processed/
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 (/speckit-tasks; no lo crea este comando)
```

### Source Code (repository root)

```text
pyproject.toml                       # paquete, dependencias y guion preparar-datos
src/
└── preparacion_datos/
    ├── __init__.py
    ├── __main__.py                  # python -m preparacion_datos
    ├── config.py                    # clases, variables, 150 pasos, proporciones, semilla
    ├── lectura.py                   # descubrir simulaciones, leer y validar CSV
    ├── particion.py                 # reparto por simulación completa
    ├── escalado.py                  # StandardScaler ajustado solo con entrenamiento
    ├── salida.py                    # armar arreglos, escritura atómica, metadata.json
    ├── reporte.py                   # reporte impreso y comparación con la referencia
    └── cli.py                       # argumentos, orquestación, códigos de salida

tests/
├── conftest.py                      # dataset sintético de CSV en un directorio temporal
├── unit/
│   ├── test_lectura.py
│   ├── test_particion.py
│   ├── test_escalado.py
│   └── test_reporte.py
└── integration/
    ├── test_cli.py                  # extremo a extremo con datos sintéticos
    ├── test_margenes.py             # márgenes térmicos sin escalar y alineados
    ├── test_cli_reporte.py          # reporte impreso, metadata.json y referencia
    └── test_dataset_real.py         # dataset NPPAD real (se omite si no está)

data_processed/                      # generado por el comando; no se edita a mano
```

**Structure Decision**: proyecto único con diseño `src/` y un módulo por responsabilidad del flujo (leer, repartir, escalar, escribir, reportar), de modo que cada comportamiento crítico de la constitución (partición, escalado, validación de entrada) tenga su prueba unitaria. `data_processed/` es salida regenerable con el comando.

## Complexity Tracking

Sin violaciones de la constitución que justificar.

## Re-evaluación tras el diseño (Fase 1)

El diseño de [data-model.md](data-model.md) y [contracts/](contracts/) no añade excepciones: la validación completa precede a toda escritura (principio II y FR-012), la salida se escribe en un directorio temporal y se publica de una vez, y el reporte declara las limitaciones (principio III). La puerta sigue en **cumple**.
