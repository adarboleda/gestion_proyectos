# Informe de análisis de especificación (inicial)

**Funcionalidad**: `004-division-sin-fuga`

**Fecha**: 2026-10-28

**Alcance**: `spec.md`, `plan.md` y `tasks.md` contrastados con la constitución v2.0.0, antes de `/speckit-implement`. Análisis de solo lectura: no se modificó ningún archivo. Las correcciones aprobadas se aplican después, en un commit aparte.

## Hallazgos

| ID | Categoría | Severidad | Ubicación | Resumen | Recomendación |
|----|-----------|-----------|-----------|---------|---------------|
| U1 | Subespecificación | MEDIUM | spec FR-011(e); tasks T018; contracts/api.md | `repartir` verifica con las corridas de los grupos (solo usables), así que la regla (e) «ninguna corrida excluida en un conjunto» no puede fallar dentro de `repartir`. La garantía completa depende de que quien llama (KAN-18) ejecute `verificar_reparto` con todas las corridas, y el contrato no lo exige. | En contracts/api.md, que el uso previsto llame a `verificar_reparto(corridas, reparto)` con todas las corridas; en T021, verificar con todas las corridas reales, incluidas las 18 excluidas. |
| C1 | Hueco de cobertura | LOW | plan (Performance Goals «< 1 s»); tasks | El objetivo de rendimiento no tiene tarea que lo mida. | Medir en T021 el tiempo de agrupar, repartir y verificar, y anotarlo en el quickstart. |
| C2 | Hueco de cobertura | LOW | spec Edge Cases (familia con menos de 3 grupos; clase con todas sus corridas cortas); T008 | Ninguna prueba cubre una familia con uno o dos grupos ni una clase sin corridas usables. | Añadir a T008 esos dos casos (ceros en los conteos). |
| C3 | Hueco de cobertura | LOW | spec FR-014; T004, T008 | Ninguna prueba comprueba que agrupar y repartir no modifican las corridas. | Añadir a T004 y T008 una comprobación de que `estado`, `area`, `gemela` y `serie` no cambian. |
| T1 | Terminología | LOW | spec Input y FR-015 | «Severidad», «tamaño de rotura» y «área de rotura» se usan para el área en cm² de PWR 3L y para el número de severidad (1–100) de NPPAD. | Una frase en Assumptions que fije cada significado. |
| D1 | Duplicación | LOW | spec FR-008 y SC-002 | SC-002 repite el texto de FR-008. | Aceptable: SC-002 lo hace medible con los datos reales. Sin cambio. |
| I1 | Inconsistencia | LOW | specs/002 tasks.md T012, T013, T016, T017 | 002 las sigue mostrando sin marcar, aunque 004 las cubre. | No editar 002 (pertenece a KAN-18); anotarlo en el documento de entregables de 004. |

## Cobertura de requisitos

| Requisito | ¿Tarea? | Tareas | Notas |
|---|---|---|---|
| FR-001 solo usables | Sí | T004(f), T012(e), T021 | |
| FR-002 grupos por área | Sí | T004(a,b), T006 | |
| FR-003 gemelas | Sí | T004(c,d), T006 | |
| FR-004 grupos individuales | Sí | T004(e), T006 | |
| FR-005 una corrida en un grupo; clave de origen | Sí | T004(c,g), T006 | |
| FR-006 grupo completo en un conjunto | Sí | T008(b), T010 | |
| FR-007 familias, 70/15/15, mayor primero | Sí | T008(a,d), T010 | |
| FR-008 cota del desvío | Sí | T008(c), T021 | |
| FR-009 reproducible e independiente del orden | Sí | T004(h), T008(e), T021 | |
| FR-010 semilla 42 | Sí | T008(i) | |
| FR-011 verificación a–e | Sí | T012, T016, T018 | Véase U1 |
| FR-012 conteos y listas | Sí | T008(g,h) | |
| FR-013 errores de entrada | Sí | T004(i,j) | |
| FR-014 no modificar | Parcial | — | Véase C3 |
| FR-015 verificación NPPAD | Sí | T013, T014, T017, T019, T022 | |
| SC-001 a SC-007 | Sí | SC-001/005/006: T021; SC-002: T008(c), T021; SC-003: T008(e), T021; SC-004: T012; SC-007: T022 | |

## Alineación con la constitución

Sin conflictos.

- **Principio I**: no aplica (no hay diagnósticos).
- **Principio II**: es el objeto de la funcionalidad; la verificación es independiente del reparto y se ejecuta en PWR 3L y en NPPAD.
- **Principio III**: semilla fija, orden determinista y desvío acotado y medido.
- **Principio IV**: no se modifican datos; los paquetes de cada planta no se importan entre sí.
- **Principio V**: las OOD quedan fuera.
- **Flujo de desarrollo**: pruebas primero (T005, T009, T015), `src/`, `tests/`, español y commits `feat(004):`.

## Tareas sin requisito directo (esperado)

T001, T002, T003, T005, T007, T009, T011, T015, T020, T024 y T025: infraestructura y ejecución de pruebas.

## Métricas

- **Requisitos**: 22 (15 FR y 7 SC).
- **Tareas**: 25.
- **Cobertura**: 100 % con al menos una tarea; FR-014 parcial.
- **Ambigüedades**: 1. **Duplicaciones**: 1.
- **Problemas críticos**: 0 (1 MEDIUM, 6 LOW).

## Próximas acciones y decisión

No hay problemas CRITICAL; se puede pasar a `/speckit-implement`. El responsable aprobó de forma explícita aplicar **U1, C1, C2, C3 y T1** antes de implementar; D1 e I1 quedan sin cambio, como se recomienda.
