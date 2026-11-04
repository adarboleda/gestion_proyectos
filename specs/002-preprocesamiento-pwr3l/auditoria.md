# Auditoría de la funcionalidad `002-preprocesamiento-pwr3l` (KAN-18)

**Fecha**: 2026-11-04 · **Rama de cierre**: `002-preprocesamiento-pwr3l-cierre` (desde `main`) · **Constitución**: v2.0.0

## 1. Resumen

| Momento | Resultado |
|---|---|
| `/speckit-analyze` (antes de implementar) | 8 hallazgos: 0 críticos, 3 medios, 5 bajos; cobertura 100 %; sin conflictos con la constitución ([analisis-inicial.md](analisis-inicial.md)) |
| Correcciones del análisis | Las 8, aplicadas antes de programar en un commit propio (`73c553e`) |
| Implementación, 1.ª parte | Fases 1–2 (T001–T011); fusionada en `main` con el PR #2 |
| Iteraciones del equipo | 003 (Christian) y 004 (Abner) hicieron T012–T014 y T016–T018 (escalado, grupos, reparto, verificación de fuga) |
| Implementación, cierre | T015 y T019–T034 sobre `main`, usando los módulos de 003 y 004 |
| `/speckit-converge`, 1.ª pasada | 4 hallazgos → T035–T038, resueltos |
| `/speckit-converge`, 2.ª pasada | **converged**: 0 hallazgos |
| Tareas | 38/38 |

## 2. Cómo se integró con 003 y 004

La rama `002-preprocesamiento-pwr3l` siguió avanzando después del PR #2 con versiones propias de `grupos.py`, `particion.py` y `escalado.py`, mientras 003 y 004 hacían las suyas en `main`. Para no duplicar ni reemplazar el trabajo del equipo, **el cierre se hizo desde `main`**: se tomaron de esa rama solo `salida.py`, `reporte.py`, `cli.py` y sus pruebas, y se adaptaron a:

- el `Reparto` de 004 (`reparto.grupos`, `conjunto_de_grupo`, `corridas`, `semilla`) y su `verificar_reparto`, que `cli.py` vuelve a llamar con **todas** las corridas (incluidas cortas, descartadas y OOD), como pide su docstring;
- el escalado de 003 (`ajustar_escalador`/`aplicar` con validación de forma);
- el paso de muestreo medido por 003 (`obtener_paso_comun`), que ahora se publica en `metadata.json` y en el reporte en lugar de la constante `PASO_SEGUNDOS`, que 003 quitó.

Las versiones de `grupos`, `particion` y `escalado` de la rama 002 **no se llevan a `main`**: quedan solo en el historial de esa rama.

## 3. Cobertura de requisitos

| Requisito | Pruebas |
|---|---|
| FR-001 descubrir y leer sin modificar | descubrimiento, lectura; cli y real: hash del origen sin cambios |
| FR-002 clase por carpeta, etiquetas 0–4 | descubrimiento |
| FR-003, FR-004 OOD y descartadas listadas | descubrimiento, reporte, cli, real (6 OOD, R07/R27/R28) |
| FR-005 una muestra de 300 pasos | lectura; cli (forma (N, 300, 26)) |
| FR-006 cortas excluidas con aviso | lectura, reporte, real (9 cortas con sus filas) |
| FR-007, FR-008 reparto por grupos sin fuga | particion y verificacion (004); cli y real (restricciones de grupo) |
| FR-009 26 entradas, sin WLR | lectura, cli |
| FR-010 escalado solo con train | escalado (003); cli (media = filas de train) |
| FR-011 márgenes sin escalar | margenes (CSV y xlsx idénticos al archivo) |
| FR-012, FR-013 reporte y advertencias | reporte (9 secciones, exclusiones, celdas en cero, clase sin usables); cli (metadata.json) |
| FR-014 defectos detienen | descubrimiento, lectura, cli (código 1 sin salida; sin usables) |
| FR-015 reproducible | particion; cli (byte a byte) |
| FR-016 un comando, salida propia | cli (`python -m`, valores por defecto); quickstart con la carpeta real |

## 4. Hallazgos de converge

| ID | Hallazgo | Tarea | Resolución |
|---|---|---|---|
| G1 | `data-model.md`: `archivo` es la carpeta para todas las descartadas y OOD, no solo R27 | T035 | Corregido |
| G2 | El contrato de la CLI no nombraba `el archivo no existe` ni `no hay corridas usables` | T036 | Corregido |
| G3 | `config.json` ilegible sin prueba | T037 | Prueba añadida |
| G4 | «no hay corridas usables» de `cli.py` sin prueba | T038 | Prueba añadida |

## 5. Decisiones sin aprobación explícita

- Las tres respuestas de `/speckit-clarify` las eligió el agente con la opción recomendada, por delegación del responsable (anotadas en la spec).
- Integrar el cierre sobre `main` en vez de fusionar la rama 002 fue decisión del agente, para conservar el trabajo de 003 y 004.

## 6. Pendientes

- La tabla de gemelas y la lista de descartadas son fijas en `config.py`.
- El reparto de 004 da 63/15/13 (la rama 002 daba 62/15/14): cambia el orden en que se asignan los grupos (de mayor a menor), no las reglas. Las cifras de esta auditoría son las de `main`.
