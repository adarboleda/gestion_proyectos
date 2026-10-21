# Data Model: Estimación del margen térmico (FNN-SELU)

## Entidades

### EntradaFNN
| Campo | Forma | Regla |
|---|---|---|
| X | (N, 150, 60) | 12 variables de planta + 48 estadísticos causales (media, máx., mín., desv. de cada una, acumulados hasta `t`) |
| sample_weight | (N, 150) | peso por paso; sube cuanto más "plano" esté el estado (std causal ≈ 0); `FLAT_REGIME_WEIGHT_BETA = 5.0`; solo en entrenamiento |

### SalidaFNN
| Campo | Forma | Regla |
|---|---|---|
| y_hat | (N, 150, 2) | [DNBR(t), PCT(t)] normalizados; se desnormalizan con `scaler_targets_mean/std.npy` |
| y_ref | (N, 150, 2) | `margins_*.npy` (DNBR y PCT de PCTRAN, unidades físicas) |

### Pérdida
```
L_total = MSE(pred_norm, target_norm) + λ_pinn · L_pinn
L_pinn  = mean(ReLU(DNBR_PHYSICAL_FLOOR − DNBR_pred_raw))      # unidades físicas
λ_pinn = 0.1 ; DNBR_PHYSICAL_FLOOR = 2.0
```

### Checkpoint
`model_fase3_best.pt`: `model_state_dict`, `model_config` (input 60, salida 2), `target_names`, `target_mean/std`, época, `val_mse`, `val_loss`, `lambda_pinn`, hiperparámetros.

### MétricasPorClase
LOCA (15 secuencias), LOCAC (15), ATWS (3): MAE, RMSE, R², sesgo, violaciones. R² de ATWS "no informativo" (varianza ≈ 0).

## Reglas de validación

- Capas lineales aplicadas a la última dimensión (operación timestep-wise); la secuencia completa no se mezcla en el tiempo.
- Ninguna característica en `t` usa pasos > `t`.
- Las métricas de evaluación nunca usan `sample_weight`.
- La partición de severidades es la misma de la Fase 2 (70/15/15).
