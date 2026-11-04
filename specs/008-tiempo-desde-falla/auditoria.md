# Auditoría — 008 Tiempo de detección desde la falla (KAN-25)

Fecha: 2026-11-04. Rama `008-tiempo-desde-falla`. Constitución v2.0.0.

## 1. Cumplimiento de la constitución

| Principio / regla | Evidencia | Estado |
|---|---|---|
| I. IA consultiva | `AVISO` aparece en `tiempos.json`, en `reporte.txt` y como primera línea `# …` de los dos CSV (T029); el comando no actúa sobre nada | Cumple |
| II. Cero fuga | No entrena ni ajusta nada. `verificar_modelo` exige que `modelo.json["corridas"]` coincida con el reparto de 004 (con `--semilla 7` termina con código 1). La regla se calibra con `calibrar()` de 006, que rechaza cualquier caso que no sea de entrenamiento. Cada τ usa la ventana [τ − 29, τ] (prueba de causalidad en `test_tiempo_reproduccion.py`) | Cumple |
| III. Honestidad y reproducibilidad | La meta de diagnóstico se informa como **NO CUMPLE** (5 de 10). Las inciertas se listan con su motivo. Las metas llevan su definición exacta. Dos ejecuciones dan archivos idénticos byte a byte | Cumple |
| IV. Procedencia | Solo PWR 3L, en lectura; el hash del origen no cambia (`test_tiempo_real.py`) | Cumple |
| V. Alcance | Familias LOCA y TRANS, y ATWS | Cumple |
| Estructura e idioma | `src/tiempo_deteccion/` y `tests/tiempo/`; documentación y mensajes en español | Cumple |
| Pruebas primero | Cada historia tiene su commit `test(008)` antes del `feat(008)`, y se comprobó que las pruebas fallaban (T006, T013, T020 y convergencia) | Cumple |
| Commits y trailer `Causa:` | Ver §2 | Cumple con una observación |
| Métricas SDD | 9 sesiones registradas, una por fase | Cumple |

## 2. Trazabilidad de eliminaciones

- **Commit 2363b19** (`feat(008): … (US3)`): reescribe 7 líneas de `evaluacion.py` y `cli.py`, escritas en el commit anterior de la misma sesión, para añadir la comparación con el validador y la columna `decision_atws`.
  - Causa: **requisito** (US3).
  - Al commit le falta el trailer `Causa:`; lo detectó `/speckit-converge` (T027).
  - No se reescribe el historial, porque los registros de sesión de métricas apuntan a esos hashes.
  - La causa se anota en `metricas/sesiones/20261104-1630-implementar-cf9c.csv`: las 7 líneas pasan a `loc_elim_requisito`, con una nota.
  - Aun así, `recolectar` recalcula las causas desde los trailers de git, así que en `resumen-funcionalidades.csv` esas 7 líneas siguen figurando como «sin clasificar».
- **Commit 117aac9** (convergencia): reescribe 8 líneas para añadir columnas y el aviso. Lleva el trailer `Causa: requisito`.
- Desperdicio total: 15 líneas de 857 (1,75 %). Las 15 son reescrituras por requisito; ninguna es un defecto.

## 3. Decisiones tomadas durante la implementación

- **`primera_familia`** solo cuenta LOCA y TRANS. La primera versión contaba también NORM: tras la falla el modelo sigue viendo operación normal, y eso marcaba confusiones falsas. La prueba `test_primera_familia_y_confusion` lo detectó antes del commit; data-model.md se precisó.
- **Tiempo desde el validador**: se calcula como en 005 (inicio redondeado hacia arriba con `inicio_entero`), para que la comparación sea exacta.
- **`atws` en toda corrida evaluada**: hace falta para contar «posible ATWS» en corridas que no son ATWS (FR-009). data-model.md se alineó (T031).
- **Instantes de las 72 corridas** en `tiempos.json["instantes"]`, no solo de validación y prueba, para comprobar SC-001.
- **Reproducción**: usa `ventanas` y `predecir` de 005 con la media y la escala de `modelo.json`. Es equivalente a `construir_muestras(entrenamiento=False)`, sin necesitar etiquetas.

## 4. Convergencia

- **1.ª pasada**: 5 hallazgos, convertidos en T027–T031 (+13 puntos):
  - 1 `contradicts` crítico: el trailer que faltaba.
  - 4 `partial`: la diferencia validador − falla (FR-003/US1-AC4), CSV sin aviso (FR-013), el motivo de la regla (caso límite) y data-model.
- **2.ª pasada**: **`converged`**, 0 hallazgos.

## 5. Verificación

- `tests/tiempo`: 61 pruebas, todas pasan con los datos reales; sin datos, la prueba real se omite.
- Ejecución real: código 0 en 56 s, idéntica en dos ejecuciones; con `--semilla 7`, código 1 sin salida.
- Suite completa con `IANUCLEAR_DATOS`: 405 pasadas en 8 min (402 antes de la convergencia + 3 pruebas nuevas).
