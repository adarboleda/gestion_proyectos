# Implementation Plan: Preprocesamiento PWR 3L en ventanas de 300 s y cinco clases

**Branch**: `002-preprocesamiento-pwr3l` | **Date**: 2026-10-28 | **Spec**: [spec.md](spec.md) | **Jira**: KAN-18

**Input**: Feature specification from `/specs/002-preprocesamiento-pwr3l/spec.md`

## Summary

Un comando de línea de órdenes (`preparar-pwr3l`) recorre la carpeta `PWR 3L` (carpetas de clase manuales y `auto/`), clasifica cada corrida por su carpeta, aparta las OOD y las descartadas por el equipo sin leerlas, valida el archivo completo de cada corrida de las cinco clases (NORM, LOCA, LOCAC, ATWS, TRIP_OK), excluye con aviso las que tienen menos de 300 pasos, toma los primeros 300 pasos de cada una como una muestra, forma grupos de corridas emparejadas (gemelas ATWS/TRIP_OK y LOCA/LOCAC con la misma área de rotura), reparte los grupos completos en entrenamiento, validación y prueba (≈ 70/15/15, semilla 42), escala las 26 variables medibles con un escalador ajustado solo con entrenamiento, conserva sin escalar los 7 márgenes térmicos y publica los arreglos y un `metadata.json` en `data_processed_pwr3l/`. Imprime un reporte con conteos, grupos, corridas excluidas y limitaciones. Enfoque técnico: un paquete nuevo `preparacion_pwr3l` en `src/`, separado de `preparacion_datos` (principio IV), que reutiliza solo la publicación «todos o ninguno» de 001.

## Technical Context

**Language/Version**: Python 3.11 o superior (entorno de desarrollo: CPython 3.12 en un `.venv` creado con `uv`)

**Primary Dependencies**: pandas (3.1), numpy (2.5), scikit-learn (1.9, `StandardScaler`), openpyxl (3.1; los `.xls` de PCTran son libros xlsx)

**Storage**: archivos locales; entrada de solo lectura (`.csv`, `.xls`/`.xlsx`, `config.json`), salida `.npy` y `.json` en `data_processed_pwr3l/`

**Testing**: pytest 9; pruebas unitarias e integración con un árbol PWR 3L sintético (CSV, libros xlsx con extensión `.xls` y `config.json`) y una prueba de extremo a extremo contra la carpeta real (se omite si no existe)

**Target Platform**: línea de órdenes en Windows 11 (desarrollo), sin dependencias del sistema

**Project Type**: biblioteca Python con interfaz de línea de órdenes (`python -m preparacion_pwr3l` y el guion `preparar-pwr3l`)

**Performance Goals**: sin objetivo cuantitativo; leer los 36 libros de Excel domina el tiempo (≈ 1–3 s cada uno). Se espera menos de 2 minutos en total

**Constraints**: origen de solo lectura; ejecución determinista; ningún conjunto se escribe si algún archivo es defectuoso; no se mezcla con NPPAD (paquete, comando y salida propios); documentación y mensajes en español

**Scale/Scope**: 109 carpetas de corrida → 3 descartadas, 6 OOD y 100 de las cinco clases; con las 9 cortas excluidas quedan 91 muestras de forma (300, 26) más márgenes (300, 7)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitución v2.0.0.

| Principio / regla | Evaluación | Cómo se cumple |
|---|---|---|
| I. IA estrictamente consultiva | Cumple (no aplica) | Solo se preparan datos; no hay diagnóstico ni salida hacia la planta. |
| II. Cero fuga de datos | Cumple | Partición por grupo de corridas completas; gemelas ATWS/TRIP_OK y LOCA/LOCAC de igual área en el mismo grupo; escalador ajustado solo con `X_train`; cada muestra son los primeros 300 pasos, sin información de otra corrida. |
| III. Honestidad y reproducibilidad | Cumple | Semilla fija y orden determinista; un comando; el reporte y `metadata.json` nombran cada corrida excluida con su motivo y las limitaciones (pocas corridas por clase, grupo de 2000 cm² grande, etiqueta por corrida). No se rellenan pasos. |
| IV. Procedencia de datos | Cumple | `PWR 3L` se abre solo para lectura (prueba de hash antes/después); paquete, comando y carpeta de salida distintos de los de NPPAD; ningún dato NPPAD entra en esta preparación. |
| V. Alcance acotado a LOCA y ATWS | Cumple | Las clases son las del detector LOCA/ATWS (NORM y TRIP_OK son los contrastes necesarios); los eventos OOD no se entrenan. |
| Restricciones | Cumple | Python; código en `src/preparacion_pwr3l/`; pruebas en `tests/`; documentación en español. |
| Flujo de desarrollo | Cumple | Spec Kit completo; pruebas primero para descubrimiento, validación, grupos, reparto, escalado y reporte; commits `feat(002): …` con `Causa:` cuando se reescriba código. |

**Nota sobre la reutilización de 001**: se importa `preparacion_datos.salida.publicar` (publicación todos o ninguno, genérica). No se reutilizan la lectura ni el escalado de 001 porque llevan fijas las variables y la forma de NPPAD; copiarlas y cambiarlas en el mismo paquete mezclaría las dos plantas en un solo módulo.

**Resultado de la puerta**: sin violaciones. Se re-evalúa tras el diseño (abajo).

## Project Structure

### Documentation (this feature)

```text
specs/002-preprocesamiento-pwr3l/
├── plan.md              # Este archivo (/speckit-plan)
├── research.md          # Fase 0: decisiones
├── data-model.md        # Fase 1
├── quickstart.md        # Fase 1
├── contracts/
│   ├── cli.md           # Contrato de la línea de órdenes y del reporte
│   └── salidas.md       # Contrato de los artefactos de data_processed_pwr3l/
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
pyproject.toml                       # + openpyxl, + guion preparar-pwr3l
src/
├── preparacion_datos/               # 001 (NPPAD); solo se reutiliza salida.publicar
└── preparacion_pwr3l/
    ├── __init__.py
    ├── __main__.py                  # python -m preparacion_pwr3l
    ├── config.py                    # clases, carpetas, variables, 300 pasos, descartadas, gemelas
    ├── descubrimiento.py            # recorrer PWR 3L, clase, id, archivo, área, gemela
    ├── lectura.py                   # leer CSV y xlsx, validar el archivo completo, 300 pasos
    ├── grupos.py                    # grupos de corridas emparejadas
    ├── particion.py                 # reparto de grupos completos 70/15/15
    ├── escalado.py                  # StandardScaler ajustado solo con entrenamiento
    ├── salida.py                    # armar arreglos y metadata.json
    ├── reporte.py                   # resumen y reporte impreso
    └── cli.py                       # argumentos, orquestación, códigos de salida

tests/
├── conftest.py                      # (001) sin cambios
└── pwr3l/
    ├── conftest.py                  # árbol PWR 3L sintético
    ├── unit/
    │   ├── test_pwr3l_descubrimiento.py
    │   ├── test_pwr3l_lectura.py
    │   ├── test_pwr3l_grupos.py
    │   ├── test_pwr3l_particion.py
    │   ├── test_pwr3l_escalado.py
    │   └── test_pwr3l_reporte.py
    └── integration/
        ├── test_pwr3l_cli.py              # extremo a extremo con el árbol sintético
        ├── test_pwr3l_margenes.py         # márgenes sin escalar y alineados
        └── test_pwr3l_dataset_real.py     # carpeta PWR 3L real (se omite si no está)

data_processed_pwr3l/                # generado por el comando; no se versiona ni se edita
```

**Structure Decision**: un paquete por planta. `preparacion_pwr3l` tiene un módulo por responsabilidad, como 001, más `descubrimiento.py` (la estructura de carpetas de PWR 3L es más compleja que la de NPPAD) y `grupos.py` (el emparejamiento es la regla crítica del principio II). Las pruebas de 002 van en `tests/pwr3l/` para no tocar las de 001; sus archivos llevan el prefijo `test_pwr3l_` porque pytest (modo de importación por defecto, sin `__init__.py`) no admite dos módulos de prueba con el mismo nombre.

## Complexity Tracking

Sin violaciones de la constitución que justificar.

## Re-evaluación tras el diseño (Fase 1)

El diseño de [data-model.md](data-model.md) y [contracts/](contracts/) no añade excepciones: toda la validación ocurre en memoria antes de publicar (FR-014), la publicación es todos o ninguno, los grupos se forman antes del reparto y el reparto opera sobre grupos (principio II), y el reporte da cuenta de cada corrida encontrada (principio III). La puerta sigue en **cumple**.
