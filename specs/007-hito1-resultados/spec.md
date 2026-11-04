# Feature Specification: Hito 1 — informe de resultados preliminares del diagnóstico rápido

**Feature Branch**: `007-hito1-resultados`

**Created**: 2026-11-04

**Status**: Draft

**Jira**: KAN-27 «HITO 1 — Presentación de resultados preliminares» (responsable: Marcelo Acuña, con Abner Arboleda y Christian Bonifaz) · Fase 2

**Input**: User description: "Demostración del diagnóstico: matriz de confusión, tiempos de detección frente a las metas (10 s y 3 s) y tasa de abstención. Un informe reproducible que junte lo que ya está hecho en la Fase 2 (clasificador de Etapa 1 de 005 y regla de ATWS de 006) y deje marcado lo que falta (Etapa 2, KAN-24; tiempo desde la falla, KAN-25; evaluación con validación cruzada, KAN-26)."

## Clarifications

### Session 2026-11-04

> Respuestas elegidas por el agente por delegación del responsable, con la opción recomendada.

- Q: ¿Qué es la «tasa de abstención» del Hito 1? → A: El porcentaje de segundos del conjunto de prueba en los que el clasificador de Etapa 1 no alcanza la confianza mínima (0.80) en ninguna familia y responde «INCIERTO». Se informa en total y por familia verdadera. La evaluación completa, con validación cruzada, es KAN-26 (Christian) y no se adelanta aquí.
- Q: ¿Qué se hace con los resultados de tareas que aún no están (KAN-24, KAN-25, KAN-26)? → A: El informe los lista como pendientes, con su responsable y lo que aportarán. No se calculan ni se inventan; el informe se regenera con un comando cuando estén.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Informe del Hito 1 con un comando (Priority: P1)

El equipo ejecuta un comando y obtiene un informe en Markdown, listo para la presentación, con:
- la matriz de confusión de la Etapa 1 en prueba;
- los tiempos de detección frente a las dos metas (LOCA ≥ 50 cm² en ≤ 10 s; ATWS en ≤ 3 s);
- la tasa de abstención;
- las falsas alarmas;
- lo que queda pendiente.

**Why this priority**: Es lo que pide KAN-27; sin él no hay presentación reproducible.

**Independent Test**: Ejecutar el comando con resultados conocidos de la Etapa 1 y de la regla de ATWS y comprobar que el informe muestra esas cifras, las metas con «cumple»/«no cumple» y las secciones pendientes.

**Acceptance Scenarios**:

1. **Given** los resultados de la Etapa 1 y de la regla, **When** se genera el informe, **Then** tiene la matriz de confusión 3 × 3 (NORM, LOCA, TRANS) con los totales y la de la regla 2 × 2 (ATWS / no-ATWS) por conjunto.
2. **Given** las metas de 10 s y 3 s, **When** se genera el informe, **Then** cada meta aparece con su definición exacta, el valor medido y si se cumple.
3. **Given** el clasificador de Etapa 1, **When** se genera el informe, **Then** la tasa de abstención aparece en total y por familia.
4. **Given** tareas aún no hechas, **When** se genera el informe, **Then** aparecen como pendientes con su responsable.

---

### User Story 2 - Resultados reproducibles y sin fuga (Priority: P1)

Las cifras del informe salen de los comandos del proyecto con la semilla 42 y el reparto sin fuga de 004. No se editan a mano.

**Why this priority**: Principios II y III.

**Independent Test**: Dos ejecuciones dan el mismo informe; las métricas son las de prueba (no de entrenamiento).

**Acceptance Scenarios**:

1. **Given** la misma semilla y los mismos datos, **When** se genera dos veces, **Then** `hito1.json` es idéntico.
2. **Given** el informe, **When** se lee, **Then** cada cifra dice sobre qué conjunto se midió.

### Edge Cases

- La Etapa 1 necesita PyTorch: sin él, el comando se detiene con un mensaje que lo dice.
- Un conjunto de prueba sin LOCA ≥ 50 cm² o sin ATWS: la meta aparece como «sin datos».
- Falsas alarmas de la regla en validación o prueba: se nombran.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST generar el informe con una sola ejecución, usando la Etapa 1 de 005 y la regla de 006 con la misma semilla y el reparto de 004.
- **FR-002**: El informe MUST incluir la matriz de confusión de la Etapa 1 en prueba (familias NORM, LOCA, TRANS), con precisión, exhaustividad y F1 por familia.
- **FR-003**: El informe MUST incluir la matriz de la regla de ATWS (detectados, omitidos, falsas alarmas, rechazos correctos) por conjunto.
- **FR-004**: El informe MUST comparar con su definición exacta: (a) LOCA ≥ 50 cm² confirmada en ≤ 10 s desde el inicio del evento (Etapa 1, prueba); (b) ATWS detectado en ≤ 3 s desde la demanda de disparo (regla, validación y prueba).
- **FR-005**: El informe MUST incluir la tasa de abstención de la Etapa 1 en prueba (segundos con confianza < 0.80), en total y por familia verdadera.
- **FR-006**: El informe MUST incluir las falsas alarmas: Etapa 1 en corridas NORM y en tramos previos al evento; regla en validación y prueba.
- **FR-007**: El informe MUST listar como pendientes KAN-24, KAN-25 y KAN-26, con responsable, sin inventar cifras.
- **FR-008**: El informe MUST decir de forma visible que el sistema es consultivo (principio I) y declarar las limitaciones (pocas corridas, sin ruido, un simulador).
- **FR-009**: El sistema MUST publicar `hito1.md` y `hito1.json` todos o ninguno, y producir el mismo `hito1.json` con los mismos datos y semilla.

### Key Entities

- **Resultados de Etapa 1**: reporte de 005 más las probabilidades por segundo en prueba (para la abstención).
- **Resultados de la regla**: regla calibrada y resumen de 006.
- **Meta**: definición exacta, valor medido, conjunto y estado (cumple, no cumple o sin datos).
- **Pendiente**: tarea, responsable y qué aportará.

## Success Criteria *(mandatory)*

- **SC-001**: El informe tiene las dos matrices, las dos metas de tiempo, la tasa de abstención y los pendientes.
- **SC-002**: Todas las cifras coinciden con las de los comandos de 005 y 006 con semilla 42.
- **SC-003**: Dos ejecuciones dan el mismo `hito1.json`.
- **SC-004**: El informe se genera en menos de 5 minutos en CPU.

## Assumptions

- La Etapa 1 se reentrena de forma determinista (semilla 42) en lugar de leer un modelo guardado, que no se versiona. Dura ~20 s.
- La presentación (diapositivas) la arma el equipo a partir de `hito1.md`; este informe no produce diapositivas.
