# Auditoría de la funcionalidad `007-hito1-resultados` (KAN-27)

**Fecha**: 2026-11-04 · **Ramas**: `007-hito1-resultados` (spec, PR #6) y `007-hito1-resultados-cierre` (desde `main` con 008–011) · **Constitución**: v2.0.0

## 1. Resumen

| Momento | Resultado |
|---|---|
| `/speckit-specify` + `/speckit-clarify` | Spec inicial (con KAN-24/25/26 pendientes), fusionada en el PR #6; actualizada al llegar 008–011 (3 aclaraciones) |
| `/speckit-analyze` | 3 hallazgos (0 críticos, 1 medio, 2 bajos); U1 y A1 aplicados, C1 aceptado |
| Implementación | T001–T014, con las pruebas commiteadas antes que el código |
| `/speckit-converge`, 1.ª pasada | 2 hallazgos de legibilidad → T015–T016 |
| `/speckit-converge`, 2.ª pasada | **converged** |
| Tareas | 16/16 · 31 pruebas de 007 |

## 2. Cobertura

| Requisito | Pruebas |
|---|---|
| FR-001 consolidar sin recalcular | `consolidar` (cada campo igual a la fuente), real (metas, matriz, regla y Etapa 2 iguales a sus archivos) |
| FR-002, FR-005 matriz 3 × 4 y abstención | `consolidar` (matriz, tasas que suman 1; error si no suman), `informe` (fila de la matriz) |
| FR-003 regla | `consolidar`, real |
| FR-004 metas | `consolidar` (008, 005, 009, 006) |
| FR-006 tiempos y falsas alarmas | `consolidar` |
| FR-007 Etapa 2 | `consolidar` (cobertura; «cumple sin decisiones») |
| FR-008 aviso, limitaciones y lectura honesta | `informe` (aviso al inicio, KAN de cada sección, legibilidad) |
| FR-009 errores, todo o nada, reproducible | `fuentes` (ausente, ilegible, clave faltante), `cli` (código 1 sin salida, mismo `hito1.json`, `python -m`) |

## 3. Resultados que conviene conocer (principio III)

- **Las cifras de la Etapa 1 y de 008 regeneradas en esta máquina difieren de las de los entregables 005 y 008.** El diagnóstico ≤ 10 s sale 10 de 10 (en ENTREGABLES-008, 5 de 10), y la Etapa 1 da 3 falsas alarmas en NORM de prueba (en ENTREGABLES-005, 0). La causa es que el reentrenamiento en CPU no es idéntico entre máquinas: la mejor época es la 7, frente a la 2 de 005. El informe usa las cifras de los archivos de esta ejecución y lo declara como limitación. **Recomendación al equipo**: acordar una sola máquina, o publicar y versionar el modelo de Etapa 1 que se presenta, para que todos citen las mismas cifras.
- **Etapa 2 (009)**: en prueba se abstiene en el 100 % de los segundos. Su SC-001 «cumple sin decisiones», y así se muestra.
- **Validación cruzada (011)**: abstención media de 32.8 % con IC [0 %, 81 %]. Es muy variable entre folds, porque cada fold reentrena con solo 5 épocas.

## 4. Decisiones sin aprobación explícita

- Las aclaraciones las eligió el agente, por delegación del responsable.
- Consolidar los archivos publicados en lugar de reentrenar (tercera aclaración).

## 5. Pendientes

- Presentación (diapositivas): la arma el equipo a partir de `hito1.md`.
- Revisar con el equipo las diferencias entre máquinas antes del 19/nov.
