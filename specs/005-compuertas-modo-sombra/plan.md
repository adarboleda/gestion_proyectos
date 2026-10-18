# Implementation Plan: Compuertas deterministas, rechazo de la IA y modo sombra

**Branch**: `005-compuertas-modo-sombra` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/005-compuertas-modo-sombra/spec.md`

**Nota**: Q1 (DNBR), el respaldo y la referencia de expertos quedaron resueltos en la sección *Clarifications* de `spec.md` (2026-10-18). Solo el **valor y la escala del límite de PCT** siguen pendientes de la experta; la compuerta de PCT se implementa con umbral configurable.

## Summary

Capa determinista nueva (`safety_gates.py`) y capa de rechazo (`reject_fallback.py`) que envuelven la fusión existente (`fusion_pwr3l.py`) y el mapeo EOP (`eop_mapper.py`). Un ejecutor de modo sombra (`shadow_mode.py`) reproduce corridas no vistas, escribe un log auditable en JSON Lines y compara con la referencia de expertos. La compuerta ATWS y los monitores de novedad ya existen y se reutilizan sin cambios.

## Technical Context

**Language/Version**: Python 3.x

**Primary Dependencies**: NumPy, SciPy o NumPy puro para la divergencia KL con histogramas, scikit-learn (ya usado), PyTorch (modelos existentes)

**Storage**: `fase5_output/` con `shadow_log_*.jsonl`, `shadow_summary.json`, `gates_report.json`

**Testing**: `unittest` en un nuevo `test_fase5.py` (compuertas con la IA forzada, rechazo < 1 s, fusión con tres casos, cobertura del log)

**Target Platform**: Windows 11, CPU

**Project Type**: Módulo de librería + script de sombra + extensión de la consola existente

**Performance Goals**: Conmutación al respaldo < 1 s tras el rechazo; cálculo de compuertas despreciable frente a los 10 ms por paso

**Constraints**: Compuertas independientes del estado de los modelos; consultivo; sin modificar los modelos de 001–003; registros inmutables (solo se añaden)

**Scale/Scope**: 106 corridas de PWR 3L a 1 s + subconjunto de NPPAD a 10 s (corridas de prueba y las 14 categorías fuera de distribución)

## Constitution Check

| Principio | Cumplimiento / acción |
|---|---|
| I. Consultiva | ✅ Las compuertas emiten alerta e instrucción al operador; el log declara `advisory_only = true`. |
| II. Causalidad / sin fuga | ✅ La sombra reproduce con prefijos `[0, t)`; KL se calcula solo con ventanas pasadas; ninguna corrida de sombra se usó para entrenar. |
| III. Honestidad | ✅ Se reportan los límites: fusión sin datos reales comunes, referencia de expertos y brecha del DNBR. |
| IV. Abstención y compuertas | ✅ Es el objetivo de esta feature. |
| V. Procedencia | ✅ Cada canal conserva su planta; el log identifica el canal. |
| VI. Alcance | ✅ LOCA/ATWS; el resto se rechaza como INCIERTO. |

**Gate de planificación**: ✅ El diseño avanza. ⚠️ Solo el límite de PCT depende de la experta; el resto está decidido.

## Project Structure

### Documentation (this feature)

```text
specs/005-compuertas-modo-sombra/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── shadow-log.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository `IA-Nuclear/`)

```text
IA-Nuclear/
├── NuclearPowerPlantAccidentData/pipeline/
│   ├── safety_gates.py                # NUEVO: DNBR relativo, PCT, ATWS (reutiliza atws_gate_series)
│   ├── dnbr_by_class.py               # NUEVO: tabla de DNBR por clase para la experta (1.3 literal como referencia)
│   ├── reject_fallback.py             # NUEVO: confianza < 0.80, deriva KL > 0.1, respaldo < 1 s
│   ├── fusion_pwr3l.py                # EXISTENTE: se extiende con rechazo y compuertas
│   ├── fusion_channels.py             # NUEVO: fusión canal rápido + lento sobre NPPAD y PWR 3L
│   ├── shadow_mode.py                 # NUEVO: reproducción, log auditable, comparación
│   ├── eop_mapper.py                  # EXISTENTE: sin cambios de lógica
│   ├── build_demo_pwr3l_fase4.py      # EXISTENTE: añade vista de log y estado de respaldo
│   ├── test_fase5.py                  # NUEVO
│   └── README_FASE5.md                # NUEVO
└── fase5_output/                      # NUEVO: shadow_log_*.jsonl, shadow_summary.json, gates_report.json
```

**Structure Decision**: Proyecto único; las capas nuevas son módulos separados para que la lógica determinista no importe nada de los modelos estadísticos.

## Complexity Tracking

| Decisión | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| Módulos de compuertas sin importar los modelos | Garantiza independencia (FR-012) | Mezclarlas con `fusion_pwr3l.py` acopla la seguridad al estado de la IA |
| Log en JSON Lines | Auditable, apendable y fácil de analizar | Un JSON único se reescribe entero y pierde trazabilidad |
