# Quickstart: Canal rápido de detección a 1 s con PWR 3L

Detalle: `IA-Nuclear/RESULTADOS_IMPLEMENTACION_PWR3L.md` y `NuclearPowerPlantAccidentData/pctran_auto/README_AUTOMATIZACION.md`.

## Prerrequisitos

- Las 106 corridas en `IA-Nuclear/PWR 3L/` (incluida `auto/`). Regenerarlas requiere PCTRAN PWR 3LP instalado (`PWR3LP/setup.exe`) y las instrucciones de `README_AUTOMATIZACION.md`.
- Python con `scikit-learn`, `torch`, `pandas`, `openpyxl`, `numpy`.

## Pasos

```bash
cd IA-Nuclear/NuclearPowerPlantAccidentData/pipeline

python preprocess_pwr3l.py            # data_processed_pwr3l/ (106 corridas)
python thermal_pwr3l.py               # FNN-SELU reentrenada (~4 min)  -> pwr3l_output/thermal/
python validate_pwr3l_acceptance.py   # sistema completo (~3 min)      -> pwr3l_output/acceptance/
python build_demo_pwr3l_fase4.py      # consola                        -> demo_operador_pwr3l_fase4.html
python evaluate_pwr3l.py              # comparación y ablaciones       -> pwr3l_output/report.json
python train_temporal_pwr3l.py        # GRU causal                     -> pwr3l_output/temporal_report.json
python explain_pwr3l.py               # importancia por variable       -> pwr3l_output/explanations_pwr3l.json
python -m unittest test_pwr3l -v      # 17 pruebas
```

## Resultados esperados

| Verificación | Esperado |
|---|---|
| Pruebas | 17 OK |
| LOCA/LOCAC ≤ 10 s (SC-001) | 40/40; ≤ 3 s en ≥ 10 cm²: 35/35 |
| ATWS (SC-002) | 14/20 ≤ 3 s; 20/20 dentro del mínimo físico |
| Compuerta (SC-004) | 20/20 ATWS; 0/20 TRIP_OK marcados |
| Falsas alarmas (SC-005) | 0/20 NORM; 0/70 previos al evento |
| Eventos desconocidos (SC-006) | 6/6 INCIERTO; 0/100 falsas novedades |
| Fase 3 en PWR 3L (SC-008) | R² DNBR 0.983; PCT 0.992 |

## Verla funcionar

Abrir `IA-Nuclear/NuclearPowerPlantAccidentData/pipeline/demo_operador_pwr3l_fase4.html` (doble clic) y probar `#vivo:R13` (LOCA grande), `#vivo:R49` (ATWS), `#vivo:R56` (TRIP_OK) y `#vivo:R64` (evento desconocido); la pestaña `#mejora` muestra antes, control y ahora.
