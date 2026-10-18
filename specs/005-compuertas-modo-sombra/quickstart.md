# Quickstart: Compuertas deterministas, rechazo de la IA y modo sombra

Guía de validación prevista (los scripts de la fila "nuevo" se crean con `tasks.md`).

## Prerrequisitos

- Features 001–004 ejecutadas.
- Sección *Clarifications* de `spec.md` leída (DNBR relativo, respaldo por setpoints, referencia automática + ciega). Pendiente solo el límite de PCT de la experta.
- `python dnbr_by_class.py` ejecutado y su tabla entregada a la experta.

## Pasos

```bash
cd IA-Nuclear/NuclearPowerPlantAccidentData/pipeline

python -m unittest test_fase5 -v                 # nuevo: compuertas, rechazo < 1 s, fusión
python shadow_mode.py --planta pwr3l             # nuevo: 106 corridas a 1 s  -> ../../fase5_output/
python shadow_mode.py --planta nppad             # nuevo: corridas de prueba y 14 categorías OOD a 10 s
python build_demo_pwr3l_fase4.py                 # consola con vista de log y estado de respaldo
```

## Resultados esperados

| Verificación | Esperado |
|---|---|
| Compuertas con IA forzada a normal (SC-001) | 0 omisiones |
| Compuerta ATWS (SC-002) | 20/20 ATWS; 0/20 TRIP_OK marcados |
| Rechazo y respaldo (SC-003) | < 1 s en el 100 % |
| Cobertura del log (SC-004) | 100 % de las decisiones con registro |
| Acuerdo con la referencia (SC-005) | ≥ 95 % en clases conocidas, excluyendo INCIERTO |
| OOD (SC-006) | PWR 3L 6/6 INCIERTO; fracción de las 14 categorías de NPPAD reportada |
| Fusión (SC-007) | los 3 casos pasan |

## Qué abrir

`fase5_output/shadow_summary.json` para el resumen y `fase5_output/shadow_log_*.jsonl` para auditar cada decisión.
