# Implementation Plan: Estimación del margen térmico (FNN-SELU)

**Branch**: `002-margen-termico-fnn` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-margen-termico-fnn/spec.md`

## Summary

Red prealimentada de 7 capas con activación SELU (Qi Lu et al. 2021) que estima DNBR(t) y PCT(t) timestep a timestep sobre 60 entradas (12 variables + 48 estadísticos causales). Pérdida = MSE + λ·penalización física del piso de DNBR (λ = 0.1), con ponderación de regímenes planos (β = 5) solo en entrenamiento. Segunda iteración: corrige fuga de futuro, partición por severidad, constante física única y criterio de checkpoint por `val_mse`.

## Technical Context

**Language/Version**: Python 3.x

**Primary Dependencies**: PyTorch (CPU), NumPy, scikit-learn (R²), matplotlib

**Storage**: Archivos `.npy` (caché del split pareado), `model_fase3_best.pt`, `metrics_fase3.json`, escaladores de objetivos

**Testing**: Bloque "Verificación rápida" de `README_FASE3.md` §10 (aserciones sobre R², sesgo, violaciones, ATWS, latencia)

**Target Platform**: Windows 11, CPU

**Project Type**: Pipeline de ciencia de datos

**Performance Goals**: R² > 0.90 (DNBR 0.924 ✅, PCT 0.903 ✅); MAE/sesgo absolutos del plan sin cumplir (umbrales mal calibrados); latencia < 10 ms ✅

**Constraints**: Sin fuga de futuro; piso físico 2.0 único; evaluación sin ponderar; checkpoint por `val_mse`

**Scale/Scope**: 143 362 parámetros; arquitectura 60→256→256→128→128→64→64→2; Adam lr 1e-3, weight decay 1e-4, batch 32, paciencia 60; AlphaDropout 0.1; inicialización LeCun normal

## Constitution Check

| Principio | Cumplimiento |
|---|---|
| I. Consultiva | ✅ Estimaciones informativas; no son compuertas de seguridad (esas son feature 005). |
| II. Causalidad / sin fuga | ✅ Estadísticos acumulados hasta `t`; split pareado por severidad; escaladores solo con train. |
| III. Honestidad | ✅ v1 archivada en `fase3_output_v1_archive/`; fallo de ATWS documentado con 3 valores de β probados. |
| IV. Abstención / compuertas | ⚠️ Las alertas térmicas son consultivas; la compuerta DNBR < 1.3 no existe aún (feature 005). |
| V. Procedencia | ✅ NPPAD solo; el checkpoint no transfiere a PWR 3L (resultado negativo documentado). |
| VI. Alcance | ✅ Dominio de accidentes de NPPAD. |

**Post-diseño**: sin violaciones; la advertencia de IV se resuelve en la feature 005.

## Project Structure

### Documentation (this feature)

```text
specs/002-margen-termico-fnn/
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
├── NuclearPowerPlantAccidentData/pipeline/
│   ├── severity_paired_margins_fase3.py   # split pareado para márgenes
│   ├── dataset_fase3.py                   # contexto causal, DNBR_PHYSICAL_FLOOR, sample_weight
│   ├── model_fase3.py                     # FNN-SELU
│   ├── train_fase3.py                     # entrenamiento (MSE ponderado + PINN)
│   ├── evaluate_fase3.py                  # métricas y gráficos
│   └── README_FASE3.md
├── fase3_output/                          # checkpoint, métricas, gráficos
└── fase3_output_v1_archive/               # iteración 1
```

**Structure Decision**: Proyecto único. Consume `data_processed/` (feature 001) y la partición de severidades cacheada por la Fase 2.

## Complexity Tracking

| Violación | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| Ponderación de "régimen plano" (β = 5) | ATWS y el instante inicial de LOCA comparten la firma "nada cambió" y eran el 100 % del error de ATWS | MSE sin ponderar: ATWS predicho en −15.8; se probó β = 10 y 20 y empeoraron |
| Piso físico 2.0 en vez de 1.3 | En la escala PCTRAN del dataset el DNBR mínimo de entrenamiento es 2.26 | Usar 1.0 dejaba el término PINN inerte (nunca se alcanza) |
