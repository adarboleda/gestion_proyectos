# Implementation Plan: Hito 1 — informe de resultados preliminares

**Branch**: `007-hito1-resultados-cierre` | **Date**: 2026-11-04 | **Spec**: [spec.md](spec.md) | **Jira**: KAN-27

## Summary

El comando `informe-hito1` lee los archivos que publican las cinco tareas de la Fase 2 y genera `informe_hito1/hito1.md` (para la presentación) y `informe_hito1/hito1.json`. No entrena ni recalcula: solo consolida y da formato. Cada sección cita su tarea, su comando y su archivo, y `hito1.json` guarda el SHA-256 de cada archivo de entrada para poder rastrear cada cifra. Si falta un archivo, el comando se detiene y nombra el comando que lo genera.

## Technical Context

**Language/Version**: Python 3.11 o superior · **Dependencies**: solo la biblioteca estándar y `preparacion_datos.salida.publicar` (no necesita PyTorch) · **Testing**: pytest con archivos JSON sintéticos y, si existen, los resultados reales · **Project Type**: biblioteca con CLI (`informe-hito1`, `python -m informe_hito1`) · **Performance**: < 10 s

## Constitution Check

| Principio | Evaluación | Cómo se cumple |
|---|---|---|
| I. Consultiva | Cumple | El informe empieza con el aviso consultivo y repite los avisos de cada fuente. |
| II. Sin fuga | Cumple | No hay datos ni modelos: solo se leen métricas ya calculadas por cada tarea sobre su conjunto, y el informe dice cuál es. |
| III. Honestidad y reproducibilidad | Cumple | Se muestran las metas que no se cumplen con su definición exacta; la salida es determinista (sin fecha ni rutas absolutas); se incluyen los SHA-256 de las fuentes. |
| IV. Procedencia | Cumple | Solo resultados de PWR 3L. |
| V. Alcance | Cumple | Diagnóstico LOCA/ATWS. |
| Flujo | Cumple | Spec Kit completo; pruebas primero. |

## Project Structure

```text
src/informe_hito1/
├── __init__.py, __main__.py
├── config.py       # fuentes (KAN, responsable, comando, archivo por defecto), aviso
├── fuentes.py      # lectura y validación de los archivos de resultados; SHA-256
├── consolidar.py   # metas, matrices, abstención, tiempos, regla, Etapa 2 → dict del hito
├── informe.py      # Markdown del hito
└── cli.py          # informe-hito1
tests/hito1/
├── conftest.py                     # resultados sintéticos con la forma real de cada archivo
├── unit/test_hito1_fuentes.py, test_hito1_consolidar.py, test_hito1_informe.py
└── integration/test_hito1_cli.py, test_hito1_real.py
```

**Structure Decision**: paquete propio, de solo lectura sobre resultados, sin dependencias de los paquetes de modelo. Así el informe no puede cambiar ninguna cifra.

## Complexity Tracking

Sin violaciones.
