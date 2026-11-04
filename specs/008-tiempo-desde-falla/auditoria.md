# Auditoría — 008 Tiempo de detección desde la falla (KAN-25)

## Trazabilidad de eliminaciones (constitución, «Commits»)

- **Commit 2363b19** (`feat(008): tiempo desde el inicio del validador y decisión de ATWS en las líneas de tiempo (US3)`): reescribe 7 líneas de `src/tiempo_deteccion/evaluacion.py` y `cli.py`, escritas en el commit anterior de la misma sesión, para añadir la comparación con el validador y la columna `decision_atws`.
  - Causa: **requisito** (US3).
  - Al commit le falta el trailer `Causa:`; lo detectó `/speckit-converge` (T027).
  - No se reescribe el historial, porque los registros de sesión de métricas apuntan a esos hashes. La causa se anota en `metricas/sesiones/20261104-1630-implementar-cf9c.csv`: las 7 líneas pasan de `loc_elim_sin_clasificar` a `loc_elim_requisito`, con una nota.
