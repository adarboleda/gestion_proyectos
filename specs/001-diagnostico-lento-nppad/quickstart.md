# Quickstart: Diagnóstico de accidentes sobre NPPAD

Guía de validación de punta a punta. Los detalles de cada paso están en `IA-Nuclear/NuclearPowerPlantAccidentData/pipeline/README_FASE1.md` y `README_FASE2.md`.

## Prerrequisitos

- Python con `torch`, `numpy`, `pandas`, `scikit-learn`, `matplotlib`.
- `NuclearPowerPlantAccidentData/Operation_csv_data/` presente (carpetas `Normal`, `LOCA`, `LOCAC`, `ATWS`).

## Pasos

```bash
cd IA-Nuclear/NuclearPowerPlantAccidentData/pipeline

# Fase 1: preprocesamiento -> ../../data_processed/
python preprocess_fase1.py .. ../../data_processed

# Fase 2: entrenamiento y evaluación -> ../../fase2_output/
python train_fase2.py
python evaluate_fase2.py
python causal_latency_fase2.py
python kfold_stage2.py        # opcional, tarda más (5 modelos)
```

## Resultados esperados

| Verificación | Esperado |
|---|---|
| Conteo de muestras Fase 1 | train 151 / val 34 / test 33; NORM test = 0 |
| Etapa 1 en test (SC-001) | 100 % (33/33) |
| Etapa 2 k-fold (SC-002) | 99.0 % ± 2.0 % |
| Matriz 4×5 (SC-003) | 0 errores; 4 UNCERTAIN (2 LOCA + 2 LOCAC); exactitud combinada 87.9 % |
| Latencia de inferencia (SC-005) | p95 < 10 ms |
| Confirmación causal (SC-006) | 29/33 confirmadas; LOCA 300 s, LOCAC 350 s, ATWS 50 s (medianas) |

## Verificación automática

Ejecutar el bloque "Verificación rápida" de `README_FASE1.md` (sección 9) y de `README_FASE2.md` (sección 9). Ambos deben terminar con `OK`.
