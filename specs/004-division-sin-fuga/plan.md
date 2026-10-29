# Implementation Plan: División en entrenamiento, validación y prueba sin fuga de datos (PWR 3L)

**Branch**: `004-division-sin-fuga` | **Date**: 2026-10-28 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/004-division-sin-fuga/spec.md`

## Summary

Dos módulos nuevos en el paquete `preparacion_pwr3l` completan las tareas de agrupación y reparto que 002 dejó pendientes (T012, T013, T016 y T017 de su `tasks.md`). `grupos.py` forma los grupos de corridas que no pueden separarse: LOCA y LOCAC de igual área de rotura (`AREA-<cm2>`), ATWS con su gemela TRIP_OK (`GEMELAS-<a>-<b>`) y el resto, una corrida por grupo. `particion.py` reparte los grupos completos por familia hacia 70/15/15, de mayor a menor tamaño y con los empates sorteados con la semilla (42 por defecto), y devuelve un `Reparto` con el conjunto de cada grupo y de cada corrida y los conteos por clase. `verificacion.py` comprueba de forma independiente que un reparto no tiene fuga (corridas o grupos en dos conjuntos, áreas partidas, gemelas separadas, corridas excluidas dentro) y se ejecuta al final de cada reparto. En NPPAD se añade una verificación equivalente (`preparacion_datos/verificacion.py`) que el comando `preparar-datos` ejecuta tras repartir, sin cambiar el reparto de 001. No se construyen salidas, reporte ni comando PWR 3L (tarea KAN-18).

## Technical Context

**Language/Version**: Python 3.11 o superior (entorno: 3.12 en `.venv`)

**Primary Dependencies**: numpy (generador `default_rng` para el sorteo). Sin dependencias nuevas.

**Storage**: no escribe archivos; trabaja en memoria sobre las corridas ya leídas por `preparacion_pwr3l.lectura`

**Testing**: pytest; pruebas unitarias con corridas construidas en memoria y con el árbol sintético de 002; pruebas de integración con los datasets reales que se omiten si no están (ruta configurable con la variable de entorno `IANUCLEAR_DATOS`)

**Target Platform**: biblioteca Python (Windows 11 en desarrollo)

**Project Type**: biblioteca; la usará el comando `preparar-pwr3l` de KAN-18

**Performance Goals**: agrupar, repartir y verificar 91 corridas en menos de 1 s (la lectura de los datos, de 002, domina el tiempo total)

**Constraints**: determinista; independiente del orden de entrada; los paquetes NPPAD y PWR 3L no se importan entre sí (principio IV); mensajes en español

**Scale/Scope**: dataset real PWR 3L: 109 corridas → 91 usables en 54 grupos: 14 de área (36 LOCA/LOCAC), 15 parejas de gemelas (30 ATWS/TRIP_OK) y 25 individuales (19 NORM y 6 ATWS/TRIP_OK sin pareja usable); NPPAD: el reparto de 001 (202 simulaciones descubiertas)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitución v2.0.0.

| Principio / regla | Evaluación | Cómo se cumple |
|---|---|---|
| I. IA estrictamente consultiva | Cumple (no aplica) | La funcionalidad solo reparte datos; no emite diagnósticos. |
| II. Cero fuga de datos | Cumple | Es el objeto de la funcionalidad: reparto por corrida completa, LOCA/LOCAC de igual área y gemelas ATWS/TRIP_OK en el mismo conjunto, y una verificación independiente que se ejecuta en cada reparto (también en NPPAD). |
| III. Honestidad y reproducibilidad | Cumple | Semilla fija y orden determinista; los desvíos respecto de 70/15/15 tienen una cota definida (FR-008) y se informan en los conteos. |
| IV. Procedencia de datos | Cumple | No se modifica ningún dato ni archivo; cada paquete verifica solo su planta y no importa al otro. |
| V. Alcance acotado a LOCA y ATWS | Cumple | Las OOD quedan fuera de los conjuntos. |
| Restricciones | Cumple | Python; código en `src/`, pruebas en `tests/`; documentación en español. |
| Flujo de desarrollo | Cumple | Ciclo Spec Kit completo; pruebas antes del código; commits `feat(004): …` con `Causa:` si se reescribe código; sesiones de métricas por fase. |

**Nota sobre 002**: `research.md` de 002 (§8) proponía barajar los grupos y asignarlos en ese orden. La segunda aclaración de esta spec cambia el orden a «de mayor a menor tamaño, con empates sorteados»; la regla de déficit y su garantía se mantienen. Ver [research.md](research.md), decisión 3.

**Resultado de la puerta**: sin violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/004-division-sin-fuga/
├── plan.md              # Este archivo (/speckit-plan)
├── research.md          # Fase 0
├── data-model.md        # Fase 1
├── quickstart.md        # Fase 1
├── contracts/
│   └── api.md           # Funciones públicas que usará KAN-18 y comportamiento de preparar-datos
├── checklists/
│   └── requirements.md
└── tasks.md             # Fase 2 (/speckit-tasks)
```

### Source Code (repository root)

```text
src/
├── preparacion_pwr3l/
│   ├── grupos.py           # NUEVO: Grupo, formar_grupos
│   ├── particion.py        # NUEVO: Reparto, metas, repartir
│   └── verificacion.py     # NUEVO: ErrorFuga, verificar_reparto
└── preparacion_datos/
    ├── verificacion.py     # NUEVO: ErrorFuga, verificar_particion (NPPAD)
    └── cli.py              # CAMBIO: verificar la partición tras repartir

tests/
├── datos_reales.py                              # NUEVO: rutas de los datasets reales (IANUCLEAR_DATOS)
├── unit/
│   └── test_verificacion.py                     # NUEVO: verificación NPPAD
├── integration/
│   └── test_verificacion_real.py                # NUEVO: NPPAD real (se omite sin dataset)
└── pwr3l/
    ├── unit/
    │   ├── test_pwr3l_grupos.py                 # NUEVO
    │   ├── test_pwr3l_particion.py              # NUEVO
    │   └── test_pwr3l_verificacion.py           # NUEVO
    └── integration/
        └── test_pwr3l_particion_real.py         # NUEVO: PWR 3L real (se omite sin dataset)
```

**Structure Decision**: los tres módulos PWR 3L completan el paquete de 002 en los nombres que su plan ya preveía (`grupos.py`, `particion.py`); la verificación va en un módulo propio para que sea independiente del código que reparte. NPPAD recibe su propia verificación en su paquete: no se comparte código entre plantas (002, decisión 1).

## Complexity Tracking

Sin violaciones de la constitución que justificar.

## Re-evaluación tras el diseño (Fase 1)

El diseño de [data-model.md](data-model.md) y [contracts/api.md](contracts/api.md) no añade excepciones: `repartir` verifica su propio resultado antes de devolverlo (principio II), la verificación usa los atributos de cada corrida (área, gemela, estado) y no los grupos, así que detecta también errores en `formar_grupos`, y el cambio en `preparar-datos` solo añade una comprobación sin alterar el reparto ni los artefactos de 001. La puerta sigue en **cumple**.
