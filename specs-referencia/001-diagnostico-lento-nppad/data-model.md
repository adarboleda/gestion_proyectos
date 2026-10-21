# Data Model: Diagnóstico de accidentes sobre NPPAD

## Entidades

### CorridaNPPAD
| Campo | Tipo | Regla |
|---|---|---|
| clase | enum {NORM, LOCA, LOCAC, ATWS} | carpeta real: `Normal`, `LOCA`, `LOCAC`, `ATWS` |
| severidad | entero 1–100 (LOCA/LOCAC) | % de 100 cm²; NORM y ATWS no tienen severidad |
| serie | tabla (filas × 97 variables) | 1 fila cada 10 s; ordenada por `TIME` |
| n_corridas | NORM 1, LOCA 100, LOCAC 100, ATWS 1 | |

### Ventana
| Campo | Forma / tipo | Regla |
|---|---|---|
| X | (N, 150, 12) float32 | variables: P, TAVG, THA, TCA, WRCA, WRCB, LVPZ, LVCR, PWNT, PWR, WECS, WLR; normalizadas |
| y | (N,) int64 | 0 = NORM, 1 = LOCA, 2 = LOCAC, 3 = ATWS |
| margins | (N, 150, 7) float32 | DNBR, TPCT, SCMA, SCMB, TSAT, FRCL, FRZR; **sin normalizar** |
| índice | misma posición `i` en X, y, margins | |

### CanalPico (solo Etapa 2)
| Campo | Regla |
|---|---|
| PWR_PEAKDEV, PWNT_PEAKDEV | `running_max(raw(0..t)) − raw(0)`; causal; escalador propio solo con train |
| input_size Etapa 2 | 14 = 12 + 2 |

### Escalador
| Campo | Regla |
|---|---|
| mean, std (12,) | ajustados solo con X_train; guardados en `scaler_mean.npy`, `scaler_std.npy` |

### ParticionSeveridad
| Campo | Regla |
|---|---|
| train / val / test | 70 / 15 / 15 severidades; sin intersección; mismo reparto para LOCA y LOCAC; semilla 42 |

### Diagnostico
| Campo | Valores |
|---|---|
| clase_final | NORM, LOCA, LOCAC, ATWS, UNCERTAIN |
| confianza | [0, 1]; < 0.80 → UNCERTAIN |
| etapa_decisora | 1 o 2 |

## Relaciones y transiciones

- Etapa 1 recibe X (12 canales) y decide NORM / familia LOCA / ATWS.
- Solo si Etapa 1 = familia LOCA con confianza ≥ 0.80, se ejecuta Etapa 2 con 14 canales.
- Si cualquier etapa queda bajo 0.80 → `UNCERTAIN`.
- Confirmación causal: el diagnóstico pasa a "confirmado" tras `sustain_count = 3` evaluaciones consecutivas con la misma clase y confianza ≥ 0.80.

## Reglas de validación

- Ninguna severidad pertenece a más de un conjunto.
- NORM y ATWS: bloques de filas disjuntos, ventanas de 150 pasos con paso 10; NORM sin ventanas de prueba (302 < 450 filas).
- Pesos de clase Etapa 1: NORM 10.0 (con tope), LOCA 0.3595, ATWS 5.0333; Etapa 2: 1.0 / 1.0.
