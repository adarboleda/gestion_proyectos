# Implementation Plan: Diagnóstico de accidentes sobre NPPAD (canal lento)

**Branch**: `001-diagnostico-lento-nppad` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-diagnostico-lento-nppad/spec.md`

## Summary

Preprocesar NPPAD (Fase 1) y entrenar un clasificador jerárquico de dos Bi-LSTM (Fase 2): Etapa 1 NORM / familia LOCA / ATWS y Etapa 2 rama caliente / fría. La Etapa 2 solo funcionó tras tres correcciones: partición pareada por severidad, canal de "desviación pico" de `PWR`/`PWNT` (causal) y criterio de checkpoint que prioriza la confianza ante empates de F1. El resultado es el **canal lento** de confirmación (minutos); el canal rápido (feature 003) cubre la detección en segundos.

## Technical Context

**Language/Version**: Python 3.x (entorno local Windows)

**Primary Dependencies**: PyTorch 2.13 (CPU), NumPy, pandas, scikit-learn 1.9 (escalado, métricas, baselines), matplotlib

**Storage**: Archivos: CSV de entrada (`Operation_csv_data/`), tensores `.npy` + `metadata.json` (`data_processed/`), checkpoints `.pt` y métricas `.json` (`fase2_output/`)

**Testing**: Scripts de "verificación rápida" de `README_FASE1.md` y `README_FASE2.md` (aserciones sobre formas, métricas y checkpoints); validación cruzada de 5 particiones para Etapa 2

**Target Platform**: Windows 11, CPU

**Project Type**: Pipeline de ciencia de datos / librería de scripts (sin servidor)

**Performance Goals**: Inferencia < 10 ms (cumplido, p95 ≈ 2.5 ms); exactitud > 95 % (cumplida con INCIERTO excluido; 87.9 % contándolo); 0 falsos negativos (cumplido)

**Constraints**: Dataset original intacto; sin fuga de futuro; escaladores solo con train; dato a 10 s/paso

**Scale/Scope**: 202 corridas útiles (1 NORM, 100 LOCA, 100 LOCAC, 1 ATWS); 151/34/33 muestras train/val/test; 13 891 y 27 795 parámetros (Etapa 1 y 2)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Cumplimiento |
|---|---|
| I. Consultiva | ✅ El clasificador no actúa sobre la planta; solo emite diagnóstico. |
| II. Causalidad / sin fuga | ✅ Partición por archivo y por severidad pareada; escaladores solo con train; canal de pico = máximo acumulado. ⚠️ NORM/ATWS con ventanas autocorrelacionadas (declarado). |
| III. Honestidad | ✅ 4 iteraciones documentadas; iteración 1 archivada; limitaciones en `metadata.json`. |
| IV. Abstención | ✅ UNCERTAIN con confianza < 0.80; regla sostenida de 3 evaluaciones. |
| V. Procedencia | ✅ Solo NPPAD. ⚠️ Usa `WLR` (no medible): la ablación está pendiente (T040). |
| VI. Alcance | ✅ NORM/LOCA/LOCAC/ATWS. |

**Post-diseño**: sin violaciones nuevas. Las dos advertencias están justificadas en Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/001-diagnostico-lento-nppad/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository `IA-Nuclear/`)

```text
IA-Nuclear/
├── NuclearPowerPlantAccidentData/
│   ├── Operation_csv_data/              # entrada (no modificar)
│   └── pipeline/
│       ├── preprocess_fase1.py          # Fase 1
│       ├── severity_paired_data.py      # split pareado + canal de desviación pico
│       ├── dataset_fase2.py             # Dataset PyTorch + pesos de clase
│       ├── model_fase2.py               # BiLSTMAccidentClassifier
│       ├── train_fase2.py               # entrenamiento Etapa 1 y 2
│       ├── evaluate_fase2.py            # matriz 4x5, ROC, métricas
│       ├── causal_latency_fase2.py      # latencia/confirmación causal
│       ├── kfold_stage2.py              # validación cruzada Etapa 2
│       ├── README_FASE1.md, README_FASE2.md, EXPLICACION_DATOS_Y_SALIDAS_FASE2.md
├── data_processed/                      # salida Fase 1
└── fase2_output/                        # salida Fase 2 (+ baseline_flat_4class_archive/)
```

**Structure Decision**: Proyecto único tipo pipeline. El código propio vive solo en `NuclearPowerPlantAccidentData/pipeline/` y las salidas en carpetas de nivel raíz generadas por los scripts.

## Complexity Tracking

| Violación / Advertencia | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| Ventanas deslizantes sobre una sola corrida (NORM, ATWS) | El dataset original solo trae un archivo por clase | Un group-split por archivo es imposible con n = 1; se declara que las métricas son orientativas |
| `WLR` como entrada del canal lento | Estaba en la selección de sensores del plan original | Quitarla requiere reentrenar y comparar; se programa como ablación (T040) en vez de ocultarla |
| Dos modelos Bi-LSTM con hiperparámetros distintos | Etapa 1 y 2 resuelven problemas de dificultad distinta | Un solo modelo plano dio 60.6 % en 4 clases |
