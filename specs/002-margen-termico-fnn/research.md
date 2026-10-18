# Research: Estimación del margen térmico (FNN-SELU)

Fuente: `IA-Nuclear/NuclearPowerPlantAccidentData/pipeline/README_FASE3.md`.

## D1. Contexto causal en vez de estadísticos de toda la ventana

- **Decision**: 4 estadísticos por variable (media, máx., mín., desv.) acumulados hasta `t` → 12 + 48 = 60 entradas.
- **Rationale**: La v1 calculaba los estadísticos sobre los 150 pasos y los repetía en cada `t`: la predicción en `t = 50` conocía lo que pasaría en `t = 1500`.
- **Alternatives considered**: Dar a la FNN memoria recurrente (rompe la arquitectura de 7 capas del plan).

## D2. Partición pareada por severidad

- **Decision**: Reutilizar el `severity_split.json` de la Fase 2 (semilla 42).
- **Rationale**: El split independiente producía R² de PCT en prueba = −1.08.
- **Alternatives considered**: Split independiente por archivo.

## D3. Constante física única

- **Decision**: `DNBR_PHYSICAL_FLOOR = 2.0` en `dataset_fase3.py`, importada por `train_fase3.py` y `evaluate_fase3.py`; λ = 0.1.
- **Rationale**: Entrenamiento penalizaba < 1.0 (nunca ocurre) y la evaluación reportaba < 2.0; el término PINN era inerte.
- **Alternatives considered**: λ = 0.5 (violaciones 21.17 %, pero PCT R² 0.67): descartado.

## D4. Selección por `val_mse`

- **Decision**: El checkpoint se elige por error de regresión puro.
- **Rationale**: Con la penalización activa, `val_loss` fluctuaba por cuántos puntos caían bajo el piso; eligió la época 5 de 1000 con `val_mse = 0.59`.
- **Alternatives considered**: Selección por `val_loss`.

## D5. Ponderación de régimen plano

- **Decision**: `FLAT_REGIME_WEIGHT_BETA = 5.0` aplicada solo al MSE de entrenamiento.
- **Rationale**: Mejora ATWS ~25 % (MAE 18.09 → 13.61) y PCT global (R² 0.842 → 0.903). No es monótono: β = 10 y 20 empeoran.
- **Alternatives considered**: Más datos ATWS, objetivo específico para el régimen "sin cambio" (siguen abiertos en `tasks.md`).

## D6. Transferencia a otra planta

- **Decision**: No transferir el checkpoint; reentrenar con PWR 3L (feature 003).
- **Rationale**: El modelo usa `WLR` y 150 pasos a 10 s; en PWR 3L da R² ≈ −3.6·10⁶.
- **Alternatives considered**: Normalización relativa del estado inicial para transferir (no basta mientras haya `WLR`).

## D7. Unidades del umbral de DNBR (abierto)

- **Decision**: Resuelta en la feature 005 (2026-10-18): no se usa el 1.3 literal; la compuerta de DNBR es un umbral relativo sobre el DNBR nominal de la condición inicial. El piso 2.0 de esta feature es solo de entrenamiento.
- **Rationale**: El plan fija la compuerta en DNBR < 1.3, pero el DNBR de PCTRAN en este dataset parte de ~2.3 y llega a ~141.
- **Alternatives considered**: Compuerta en porcentaje del valor inicial; compuerta sobre el DNBR "real" del simulador.
