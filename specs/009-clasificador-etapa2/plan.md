# Implementation Plan: Clasificador de Etapa 2 (rama caliente o fría) para PWR 3L

**Branch**: `009-clasificador-etapa2` | **Date**: 2026-11-04 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/009-clasificador-etapa2/spec.md`

## Summary

Un paquete nuevo, `clasificador_etapa2`, entrena con un comando (`entrenar-etapa2`) una Bi-LSTM muy pequeña que, en los instantes de evento de las corridas LOCA y LOCAC de PWR 3L, decide si la rotura está en la rama caliente (LOCA) o en la fría (LOCAC). Sus dos únicas entradas son los canales de desviación pico causal de PWR y PWNT (máximo de la media móvil de 3 s en los últimos 15 s menos el valor inicial), escalados solo con entrenamiento. Reutiliza sin modificarlos la lectura de corridas (002), el reparto sin fuga y su verificación (004), el instante de inicio del evento y la arquitectura Bi-LSTM y utilidades de entrenamiento de la Etapa 1 (005). Si la mayor probabilidad es menor que 0,80 se abstiene (UNCERTAIN). La evaluación en prueba informa métricas por horizonte con la abstención, cobertura, errores con confianza y el resultado de cada corrida por área. El modelo guardado ofrece una recomendación consultiva que solo se aplica si la Etapa 1 indicó LOCA.

## Technical Context

**Language/Version**: Python 3.11 o superior (entorno: 3.12 en `.venv`)

**Primary Dependencies**: PyTorch CPU (extra `modelo`, ya declarado en 005), numpy, pandas, scikit-learn; paquetes del proyecto `preparacion_pwr3l` y `clasificador_etapa1` (solo importados)

**Storage**: lee la carpeta PWR 3L (solo lectura) y escribe en `modelos/etapa2/` (configurable): `modelo.pt`, `modelo.json`, `reporte.json`, `reporte.txt`; fuera de git (`modelos/` ya ignorado)

**Testing**: pytest; corridas sintéticas LOCA/LOCAC en memoria con pico de PWR/PWNT solo en rama caliente; pruebas de PyTorch omitidas sin torch; prueba con el dataset real omitida sin datos (`IANUCLEAR_DATOS`)

**Target Platform**: línea de órdenes en Windows 11, CPU

**Project Type**: biblioteca Python con interfaz de línea de órdenes

**Performance Goals**: < 15 min en CPU (SC-005); se esperan segundos (≈ 1 400 muestras de entrenamiento de 30 × 2, red de ≈ 1 000 parámetros)

**Constraints**: determinismo con semilla; canales y ventanas causales; sin NPPAD; sin modificar código de otras funcionalidades; español

**Scale/Scope**: 35 corridas LOCA/LOCAC usables (24 entrenamiento, 6 validación, 5 prueba con el reparto de 004)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitución v2.0.0.

| Principio / regla | Evaluación | Cómo se cumple |
|---|---|---|
| I. IA estrictamente consultiva | Cumple | La salida es probabilidad + recomendación, UNCERTAIN o «no aplica», con aviso consultivo; nada actúa sobre la planta. |
| II. Cero fuga de datos | Cumple | Reparto de 004 con `verificar_reparto`; escalador ajustado solo con filas de entrenamiento; canales causales (solo datos ≤ τ); validación decide la parada; prueba solo al final. |
| III. Honestidad y reproducibilidad | Cumple | Métricas definidas en research §6; se informan aunque no se cumplan SC-001/SC-002; advertencia de 5 corridas de prueba; semilla y modo determinista; un comando regenera todo. |
| IV. Procedencia de datos | Cumple | Solo PWR 3L en lectura. |
| V. Alcance acotado a LOCA y ATWS | Cumple | Subclasificación dentro de la familia LOCA. |
| Restricciones | Cumple | Código en `src/clasificador_etapa2/`, pruebas en `tests/etapa2/`, español. |
| Flujo de desarrollo | Cumple | Ciclo Spec Kit completo, pruebas primero, commits `feat(009)`/`test(009)`/`docs(009)`, sesiones de métricas por fase. |

**Resultado de la puerta**: sin violaciones. Re-chequeo tras el diseño: sin cambios.

## Project Structure

### Documentation (this feature)

```text
specs/009-clasificador-etapa2/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── cli.md           # comando entrenar-etapa2
│   └── salidas.md       # modelo.json, reporte.json, recomendación
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
src/clasificador_etapa2/
├── __init__.py
├── __main__.py
├── config.py         # clases, canales, ventanas, umbral, hiperparámetros
├── canales.py        # desviación pico causal de PWR y PWNT; lectura de PWR del archivo
├── muestras.py       # muestras de evento con ventana de 30 s
├── entrenamiento.py  # Bi-LSTM de 005 con 2 clases, pesos, parada por validación
├── evaluacion.py     # métricas con abstención, horizontes, corridas, áreas, reporte
├── prediccion.py     # cargar(ruta).clasificar(serie, familia_etapa1)
└── cli.py            # entrenar-etapa2

tests/etapa2/
├── conftest.py
├── unit/ (canales, muestras, entrenamiento, evaluacion, prediccion)
└── integration/ (cli, real)
```

**Structure Decision**: paquete independiente, igual que 005 y 006; se añade solo el guion `entrenar-etapa2` a `pyproject.toml`.

## Complexity Tracking

Sin violaciones que justificar.

