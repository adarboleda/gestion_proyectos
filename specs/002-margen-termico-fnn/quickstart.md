# Quickstart: Estimación del margen térmico (FNN-SELU)

Detalle completo: `IA-Nuclear/NuclearPowerPlantAccidentData/pipeline/README_FASE3.md`.

## Prerrequisitos

- Feature 001 ejecutada (`data_processed/` con `margins_*.npy`, `scaler_*.npy`, `metadata.json`).
- Partición de severidades de la Fase 2 (se construye sola si falta).

## Pasos

```bash
cd IA-Nuclear/NuclearPowerPlantAccidentData/pipeline
python severity_paired_margins_fase3.py   # opcional: inspeccionar el split pareado
python train_fase3.py                     # -> ../../fase3_output/model_fase3_best.pt
python evaluate_fase3.py                  # métricas y gráficos en ../../fase3_output/
```

## Resultados esperados

| Verificación | Esperado |
|---|---|
| R² DNBR / PCT (SC-001) | 0.924 / 0.903 |
| MAE DNBR / PCT | 10.77 / 23.48 °C |
| Sesgo PCT | ≈ +10.05 °C |
| Violaciones del piso 2.0 (SC-004) | ≈ 21 % (< 30 %) |
| ATWS (SC-005) | MAE DNBR ≈ 13.61 (< 18.0); DNBR predicho ≈ −11.3 (limitación declarada) |
| Latencia (SC-006) | ≈ 1–2 ms (< 10 ms) |

## Verificación automática

Ejecutar el bloque de la sección 10 de `README_FASE3.md`; debe terminar con `OK: verificación Fase 3 pasó`.
