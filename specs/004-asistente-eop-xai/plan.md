# Implementation Plan: Asistente EOP y explicabilidad

**Branch**: `004-asistente-eop-xai` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/004-asistente-eop-xai/spec.md`

## Summary

Tres componentes que consumen los modelos ya entrenados sin modificarlos: (1) `EOPMapper`, árbol de decisión determinista que traduce clase en procedimiento y calcula alertas térmicas; (2) explicabilidad local (SHAP `GradientExplainer` con fallback por oclusión para la Bi-LSTM; importancia por permutación para el canal rápido); (3) contrafácticos por interpolación hacia el perfil medio de la segunda clase más probable. Dos consolas HTML autosuficientes (canal lento y canal rápido) con datos precalculados y botón ES/EN.

## Technical Context

**Language/Version**: Python 3.x (consolas: HTML + JavaScript sin dependencias de servidor)

**Primary Dependencies**: `shap`, PyTorch, scikit-learn; Google Fonts solo para tipografía de la consola

**Storage**: `fase4_output/` (`metrics_fase4.json`, `xai_explanations.json`, `eop_reports.txt`, gráficos SHAP); `pwr3l_output/explanations_pwr3l.json`; consolas HTML

**Testing**: Bloque de "Verificación rápida" de `README_FASE4.md` §10; pruebas de consola y de fusión en `test_pwr3l.py`

**Target Platform**: Navegador moderno abierto con `file:///`; Windows 11 para el pipeline

**Project Type**: Módulo determinista + XAI + consola web estática

**Performance Goals**: Mapeo EOP instantáneo (stdlib); consola sin cálculo de IA en el navegador

**Constraints**: Consultivo; no reentrena; datos de consola precalculados; el EOP y las alertas se recalculan en el navegador por JavaScript como puerto de `eop_mapper.py`

**Scale/Scope**: 33 muestras de prueba + 34 de validación (canal lento), 8 explicaciones representativas, 106 corridas (canal rápido), 5 pestañas en la consola del canal rápido

## Constitution Check

| Principio | Cumplimiento |
|---|---|
| I. Consultiva | ✅ Declarado en cada consola y reporte. |
| II. Causalidad / sin fuga | ✅ La reproducción usa prefijos `[0, t)`; el "Por qué" solo usa lo ocurrido. |
| III. Honestidad | ✅ El caveat de ATWS, los contrafácticos "no encontrados" y la alerta térmica sobre-conservadora se declaran. |
| IV. Abstención | ✅ INCIERTO no fuerza procedimiento. |
| V. Procedencia | ✅ Cada consola identifica su canal y su planta. |
| VI. Alcance | ✅ Solo procedimientos de LOCA, ATWS y disparo; FR-C.x queda fuera. |

**Post-diseño**: sin violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/004-asistente-eop-xai/
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
├── NuclearPowerPlantAccidentData/pipeline/
│   ├── eop_mapper.py                       # mapeo determinista + alertas térmicas
│   ├── xai_shap_fase4.py                   # SHAP / oclusión
│   ├── xai_counterfactual.py               # contrafácticos
│   ├── evaluate_fase4.py                   # orquestación y salidas
│   ├── explain_pwr3l.py                    # permutación del canal rápido
│   ├── demo_operador_fase4.html            # consola del canal lento
│   ├── demo_operador_pwr3l_fase4.html      # consola del canal rápido (+ .template.html)
│   ├── build_demo_pwr3l_fase4.py
│   └── README_FASE4.md
├── fase4_output/                           # metrics_fase4.json, xai_explanations.json, eop_reports.txt, shap_*.png
└── docs/Thresholds_EOP_Timeline_simplified.pdf
```

**Structure Decision**: Proyecto único. `eop_mapper.py` es compartido por los dos canales.

## Complexity Tracking

| Decisión | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| Importancia por permutación en el canal rápido (no SHAP) | El clasificador es un árbol de gradiente con picos enclavados; la permutación es directa y estable | Entrenar y mantener un explainer SHAP adicional sin ganancia para el operador |
| Datos de consola precalculados | La consola debe abrirse con doble clic sin servidor | Servir un modelo vivo en el navegador (añade infraestructura y un punto de fallo) |
