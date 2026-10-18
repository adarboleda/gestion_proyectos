# Especificaciones del proyecto IANuclear

Spec Kit de `IA-Nuclear/` (Sistema de Asistencia Inteligente para Reactores PWR, LOCA/ATWS). Las features 001–004 documentan de forma retroactiva lo ya construido; la 005 y la 006 son el trabajo que falta. Principios del proyecto: `../.specify/memory/constitution.md`.

| # | Feature | Fases del plan | Estado | Tareas abiertas |
|---|---|---|---|---|
| [001](001-diagnostico-lento-nppad/spec.md) | Diagnóstico sobre NPPAD (canal lento, Bi-LSTM) | 1–2 | Implementada | T040–T044 (ablación sin `WLR`, etc.) |
| [002](002-margen-termico-fnn/spec.md) | Margen térmico DNBR/PCT (FNN-SELU) | 3 | Implementada, ATWS sin resolver | T030–T034 |
| [003](003-canal-rapido-pwr3l/spec.md) | Canal rápido a 1 s con PWR 3L | 2b, 3b (plan PWR 3L) | Implementada y validada | T040–T044 |
| [004](004-asistente-eop-xai/spec.md) | Asistente EOP + XAI + consolas | 4 | Implementada | T030–T034 |
| [005](005-compuertas-modo-sombra/spec.md) | Compuertas deterministas, rechazo y modo sombra | 5 | **En curso (parcial)** | Casi todas; decisiones tomadas, falta solo el límite de PCT (T000b) |
| [006](006-informe-final/spec.md) | Informe técnico final y documentación | 6 | Pendiente | Todas |

## Feature activa

`.specify/feature.json` apunta a `specs/005-compuertas-modo-sombra` (plazo del plan: 23 oct 2026).

## Archivos por feature

`spec.md` (qué y por qué) · `plan.md` (cómo) · `research.md` (decisiones) · `data-model.md` · `quickstart.md` · `tasks.md` · `checklists/requirements.md`. La 005 añade `contracts/shadow-log.md`; la 006 omite `data-model.md` por no manejar datos.

## Cómo seguir

1. Hoy: T006b (tabla de DNBR por clase) y enviar T000b a la experta (porcentaje de DNBR, límite de PCT, muestra ciega).
2. `/speckit-analyze` para revisar coherencia entre spec, plan y tareas.
3. `/speckit-implement` sobre la 005.
4. Al cerrar la 005, pasar a la 006.
