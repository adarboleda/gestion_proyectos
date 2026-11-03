# Implementation Plan: Clasificador de Etapa 1 (familia del evento) para PWR 3L

**Branch**: `005-clasificador-etapa1` | **Date**: 2026-11-03 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/005-clasificador-etapa1/spec.md`

## Summary

Un paquete nuevo, `clasificador_etapa1`, entrena con un comando (`entrenar-etapa1`) una Bi-LSTM pequeña que clasifica cada segundo de una corrida PWR 3L en tres familias: NORM, LOCA (LOCA + LOCAC) y TRANS (transitorio con disparo: ATWS + TRIP_OK). El comando reutiliza lo ya construido: la lectura de corridas (002), el reparto sin fuga y su verificación (004) y el escalado ajustado solo con entrenamiento (003). Para cada segundo τ ≥ 5 s, la muestra son los últimos 30 s hasta τ (rellenados con la primera fila si la corrida es más corta) y su etiqueta depende del instante de inicio del evento, que se toma del validador del proyecto. El entrenamiento usa pesos de clase inversos a la frecuencia, se detiene según el F1 macro de validación y es determinista con la semilla. La evaluación sobre las corridas de prueba informa métricas por familia y por horizonte (1–30 s), el tiempo de confirmación de cada evento (confianza ≥ 0,80 dos segundos seguidos) y las falsas alarmas. El modelo guardado ofrece una clasificación consultiva de una secuencia nueva.

## Technical Context

**Language/Version**: Python 3.11 o superior (entorno: 3.12 en `.venv`)

**Primary Dependencies**: PyTorch (CPU, `torch>=2.2`, como extra opcional `modelo` para no imponerlo a la preparación de datos); numpy, scikit-learn (métricas) y los paquetes del proyecto `preparacion_pwr3l`

**Storage**: lee la carpeta PWR 3L (solo lectura) y escribe en `modelos/etapa1/` (configurable): `modelo.pt`, `modelo.json`, `reporte.json`, `reporte.txt`; carpeta regenerable, fuera de git

**Testing**: pytest; pruebas unitarias con corridas sintéticas en memoria (señales separables por familia); pruebas de PyTorch omitidas si no está instalado; prueba con el dataset real omitida sin datos (`IANUCLEAR_DATOS`)

**Target Platform**: línea de órdenes en Windows 11, CPU sin aceleración gráfica

**Project Type**: biblioteca Python con interfaz de línea de órdenes

**Performance Goals**: entrenar y evaluar las 91 corridas en menos de 15 minutos en CPU (SC-006); con unas 9 000 muestras de entrenamiento de 30 × 26 y una red de unos 16 000 parámetros se esperan pocos segundos por época

**Constraints**: determinismo con la semilla (PyTorch en modo determinista y generador propio para barajar); ventana causal (solo datos hasta τ); sin datos de NPPAD; mensajes y documentación en español

**Scale/Scope**: 91 corridas usables (63 entrenamiento, 15 validación, 13 prueba); 295 instantes por corrida (τ = 5…299)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitución v2.0.0.

| Principio / regla | Evaluación | Cómo se cumple |
|---|---|---|
| I. IA estrictamente consultiva | Cumple | La clasificación devuelve probabilidades y una recomendación (o «INCIERTO»), con el aviso explícito de que es una recomendación consultiva; nada actúa sobre la planta. El reporte lo declara en su encabezado. |
| II. Cero fuga de datos | Cumple | Reparto por grupos de 004 con `verificar_reparto` antes de entrenar; escalado ajustado solo con entrenamiento (003); cada muestra usa solo datos hasta τ (la dirección hacia atrás de la Bi-LSTM recorre la ventana, nunca datos posteriores a τ); la validación decide la parada y la prueba solo se usa al final. |
| III. Honestidad y reproducibilidad | Cumple | Métricas con definición exacta (research §6–§8) y reportadas aunque no alcancen las metas de SC-001 a SC-003; advertencia del tamaño pequeño del conjunto de prueba; semilla y modo determinista; un solo comando regenera todo; los artefactos no se editan a mano. |
| IV. Procedencia de datos | Cumple | Solo PWR 3L, abierto en lectura; NPPAD no se usa. |
| V. Alcance acotado a LOCA y ATWS | Cumple | Las familias son LOCA y transitorio con disparo (ATWS y su contraste TRIP_OK, ya definidos en 002); las OOD quedan fuera. |
| Restricciones | Cumple | Python; código en `src/clasificador_etapa1/`, pruebas en `tests/etapa1/`; documentación en español. |
| Flujo de desarrollo | Cumple | Ciclo Spec Kit completo; pruebas antes del código; commits `feat(005): …` con `Causa:` si se reescribe código; sesiones de métricas por fase. |

**Resultado de la puerta**: sin violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/005-clasificador-etapa1/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── cli.md           # comando entrenar-etapa1
│   └── salidas.md       # modelo.pt, modelo.json, reporte.json, reporte.txt y clasificar()
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
pyproject.toml                        # CAMBIO: extra «modelo» (torch), guion entrenar-etapa1
.gitignore                            # CAMBIO: modelos/
src/clasificador_etapa1/              # NUEVO
├── __init__.py
├── __main__.py
├── config.py                         # familias, ventana, horizontes, umbral, hiperparámetros
├── eventos.py                        # instante de inicio del evento de cada corrida
├── muestras.py                       # ventanas de 30 s por segundo, etiquetas y k
├── modelo.py                         # Bi-LSTM
├── entrenamiento.py                  # pesos de clase, entrenamiento determinista, parada temprana
├── evaluacion.py                     # métricas, horizontes, confirmación, falsas alarmas
├── prediccion.py                     # cargar el modelo guardado y clasificar (consultivo)
└── cli.py                            # orquestación, artefactos y reporte

tests/etapa1/                         # NUEVO
├── conftest.py                       # corridas sintéticas con señal por familia
├── unit/test_etapa1_eventos.py
├── unit/test_etapa1_muestras.py
├── unit/test_etapa1_entrenamiento.py
├── unit/test_etapa1_evaluacion.py
├── unit/test_etapa1_prediccion.py
├── integration/test_etapa1_cli.py
└── integration/test_etapa1_real.py   # dataset real (se omite sin datos)
```

**Structure Decision**: un paquete propio para el modelo, separado de la preparación de datos, porque tiene una dependencia pesada (PyTorch) que la preparación no necesita. Solo depende de `preparacion_pwr3l` (lectura, grupos, reparto, verificación y escalado), nunca de `preparacion_datos` (principio IV).

## Complexity Tracking

Sin violaciones de la constitución que justificar.

## Re-evaluación tras el diseño (Fase 1)

El diseño de [data-model.md](data-model.md) y [contracts/](contracts/) no añade excepciones: las ventanas solo contienen filas hasta τ, el relleno al inicio repite la primera fila (dato pasado, no inventa futuro), las métricas usan solo prueba y la clasificación guarda los parámetros de escala de entrenamiento. La puerta sigue en **cumple**.
