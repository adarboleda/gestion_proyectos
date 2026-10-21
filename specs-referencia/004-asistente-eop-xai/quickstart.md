# Quickstart: Asistente EOP y explicabilidad

Detalle: `IA-Nuclear/NuclearPowerPlantAccidentData/pipeline/README_FASE4.md`.

## Prerrequisitos

- Features 001 y 002 ejecutadas (checkpoints de Fase 2 y Fase 3 y caché del split pareado).
- `pip install shap`.
- Para el canal rápido: feature 003 ejecutada (`validate_pwr3l_acceptance.py`).

## Pasos

```bash
cd IA-Nuclear/NuclearPowerPlantAccidentData/pipeline

python evaluate_fase4.py              # -> ../../fase4_output/ (metrics, xai_explanations, eop_reports, shap_*.png)
python explain_pwr3l.py               # -> ../../pwr3l_output/explanations_pwr3l.json
python build_demo_pwr3l_fase4.py      # -> demo_operador_pwr3l_fase4.html
```

## Resultados esperados

| Verificación | Esperado |
|---|---|
| Recomendaciones sobre 33 muestras (SC-001) | 13 LOCA, 13 LOCAC, 3 ATWS, 4 INCIERTO |
| LOCA/LOCAC y ATWS (SC-002) | `["E-0","E-1","ES-1.2"]` y `["FR-S.1"]` con caveat |
| XAI (SC-003) | 8 explicaciones con `narrative`; PWR cae y WECS sube en LOCA |
| Contrafácticos (SC-004) | etapa 2: 6/6 encontrados; etapa 1: 1/8 |
| Consolas (SC-006) | Se abren con doble clic; botón ES/EN; enlaces `#vivo:R13`, `#R49`, `#mejora`, `#fases` |

## Verificación automática

Ejecutar el bloque de la sección 10 de `README_FASE4.md` (termina con `OK: verificación Fase 4 pasó`) y `python -m unittest test_pwr3l -v` para las pruebas de consola y de fusión.
