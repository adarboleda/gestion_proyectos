# Implementation Plan: Canal rápido de detección a 1 s con PWR 3L

**Branch**: `003-canal-rapido-pwr3l` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/003-canal-rapido-pwr3l/spec.md`

## Summary

Canal independiente del NPPAD: 106 corridas de PCTRAN PWR 3LP (27 del compañero, 74 automáticas y 5 manuales) → características causales relativas al estado inicial con 26 variables medibles → clasificador HistGradientBoosting de 5 clases con confirmación de 2 s → compuerta determinista de ATWS, monitores físicos de novedad, clasificador de rama y FNN-SELU reentrenada. Evaluación por validación cruzada de 5 particiones por grupos, con ruido y peor caso. El plan original proponía una Bi-LSTM rápida; la comparación (ver research.md) eligió HistGradientBoosting.

## Technical Context

**Language/Version**: Python 3.x

**Primary Dependencies**: scikit-learn (HistGradientBoosting, Random Forest, regresión logística), PyTorch (GRU causal, FNN-SELU), pandas + openpyxl (los `.xls` son `.xlsx`), pyodbc/Jet de 32 bits (automatización de PCTRAN)

**Storage**: Corridas en `PWR 3L/` (Excel + `.dat`); `data_processed_pwr3l/` (`sequences.npz`, `metadata.json`); `pwr3l_output/` (aceptación, térmico, explicaciones)

**Testing**: `python -m unittest test_pwr3l -v` (17 pruebas: 7 unitarias, 4 de integración con corridas reales, 6 de resultados)

**Target Platform**: Windows 11; PCTRAN PWR 3LP demo (GUI + base `.mdb`)

**Project Type**: Pipeline + consola HTML autosuficiente

**Performance Goals**: Detección ≤ 10 s en LOCA/LOCAC, ≤ 3 s en ≥ 10 cm², ATWS ≤ 3 s o dentro del mínimo físico, 0 falsas alarmas, 6/6 eventos desconocidos → INCIERTO, cálculo < 10 ms por paso

**Constraints**: Solo variables medibles (sin `WLR`); causal; no se mezcla con NPPAD; IC 1–3 solamente; 300 s por corrida

**Scale/Scope**: 106 corridas (20 NORM, 20 LOCA, 20 LOCAC, 20 ATWS, 20 TRIP_OK, 6 fuera de distribución); 79 filas en el plan de corridas; validación sobre 100 corridas no OOD

## Constitution Check

| Principio | Cumplimiento |
|---|---|
| I. Consultiva | ✅ Declarado en el reporte y en la consola; no ejecuta acciones. |
| II. Causalidad / sin fuga | ✅ Características causales; validación por grupos con gemelos juntos; OOD nunca entrena; regla de gemelo idéntico (R91 = 33.0 s). |
| III. Honestidad | ✅ Versión anterior corregida y documentada (prueba sellada de 19 corridas, compuerta con 1 de 5 ATWS); límites declarados. |
| IV. Abstención / compuertas | ✅ INCIERTO < 0.80; novedad → INCIERTO; compuerta ATWS prevalece. |
| V. Procedencia | ✅ Solo PWR 3L; sin `WLR` como entrada; NPPAD intacto. |
| VI. Alcance | ✅ LOCA/ATWS; resto → INCIERTO. |

**Post-diseño**: sin violaciones. Ver Complexity Tracking para las decisiones que se apartan del plan inicial.

## Project Structure

### Documentation (this feature)

```text
specs/003-canal-rapido-pwr3l/
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
├── PWR 3L/                               # corridas (NORM, LOCA COLD/HOT/PORV, ATWS, TRIP_OK, auto/)
├── NuclearPowerPlantAccidentData/
│   ├── pctran_auto/                      # automatización de PCTRAN
│   │   ├── plan_corridas_pwr3l.csv, ejecutar_lote.py, validar_corridas.py
│   │   ├── pctran_gui.py, pctran_db.py, jet32.ps1, preparar_manual.py
│   │   └── README_AUTOMATIZACION.md
│   └── pipeline/
│       ├── preprocess_pwr3l.py           # 106 corridas relativas al nominal
│       ├── pwr3l_rapid_detector.py       # características, clasificador, compuerta ATWS, rama, novedad
│       ├── fusion_pwr3l.py               # fusión consultiva
│       ├── eop_mapper.py                 # mapeo de clase a EOP (feature 004)
│       ├── thermal_pwr3l.py              # FNN-SELU reentrenada
│       ├── transfer_fase3_pwr3l.py       # resultado negativo documentado
│       ├── evaluate_pwr3l.py             # comparación y ablaciones
│       ├── train_temporal_pwr3l.py       # GRU causal
│       ├── explain_pwr3l.py              # importancia por permutación
│       ├── validate_pwr3l_acceptance.py  # validación cruzada, peor caso
│       ├── build_demo_pwr3l_fase4.py + demo_operador_pwr3l_fase4.template.html
│       ├── prueba_factibilidad_pwr3l.py, prueba_rama_caliente_fria_pwr3l.py
│       └── test_pwr3l.py
├── data_processed_pwr3l/
└── pwr3l_output/ (acceptance/, thermal/, report.json, temporal_report.json, explanations_pwr3l.json)
```

**Structure Decision**: Proyecto único con carpeta de automatización separada. El canal rápido reutiliza `eop_mapper.py` y la arquitectura de la FNN, pero no comparte datos con la feature 001.

## Complexity Tracking

| Desviación del plan inicial | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| HistGradientBoosting en vez de Bi-LSTM rápida | Mejor exactitud balanceada fuera de muestra (0.972 vs GRU 0.922) con 100 corridas | Una red recurrente con tan pocas corridas se sobreajusta |
| Compuerta determinista + monitores físicos en vez de detector estadístico de novedad | IsolationForest detectó 0–4 % de los OOD, igual que en lo conocido | Solo un modelo de 5 clases no se abstiene ante lo desconocido |
| Automatización escribiendo en la base de PCTRAN | El macro del NPPAD hace clics en coordenadas fijas y no maneja el fin de la demo | Repetir las 74 corridas a mano |
