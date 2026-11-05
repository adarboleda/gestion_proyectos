# Feature Specification: Hito 1 — informe de resultados preliminares del diagnóstico rápido

**Feature Branch**: `007-hito1-resultados` (spec, PR #6) · `007-hito1-resultados-cierre` (resto)

**Created**: 2026-11-04 · **Updated**: 2026-11-04 (con 008, 009, 010 y 011 ya en `main`)

**Status**: Draft

**Jira**: KAN-27 «HITO 1 — Presentación de resultados preliminares» (responsable: Marcelo Acuña, con Abner Arboleda y Christian Bonifaz) · Fase 2

**Input**: User description: "Demostración del diagnóstico: matriz de confusión, tiempos de detección frente a las metas (10 s y 3 s) y tasa de abstención. Un informe reproducible que junte los resultados de la Fase 2: Etapa 1 (005), regla de ATWS (006), tiempo de detección desde la falla (008), Etapa 2 (009) y evaluación con abstención y validación cruzada (011)."

## Clarifications

### Session 2026-11-04

> Respuestas elegidas por el agente por delegación del responsable, con la opción recomendada.

- Q: ¿Qué es la «tasa de abstención» del Hito 1? → A: La que publica la evaluación del diagnóstico de KAN-26 (011): proporción de segundos en los que la confianza máxima de la Etapa 1 es menor que 0.80 («UNCERTAIN»), con su intervalo de Wilson al 95 %. El Hito **no la recalcula**: la toma de 011.
- Q: ¿Qué se hace con los resultados de tareas que aún no están? → A: *(Respuesta original, cuando faltaban KAN-24, KAN-25 y KAN-26)* se listaban como pendientes. *Actualización del 2026-11-04*: las tres ya están en `main`, así que si falta el archivo de resultados de cualquiera, el comando se detiene y dice qué comando hay que ejecutar. No se inventan cifras.
- Q: ¿El Hito ejecuta los entrenamientos o lee sus resultados? → A: Lee los archivos que publican los comandos de cada tarea (`entrenar-etapa1`, `evaluar-regla-atws`, `medir-tiempo-deteccion`, `entrenar-etapa2` y `evaluar-diagnostico`). Así cada cifra es exactamente la de su responsable, y el quickstart documenta el orden en que se ejecutan.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Informe del Hito 1 con un comando (Priority: P1)

El equipo ejecuta los comandos de la Fase 2 y después uno más, `informe-hito1`. Obtiene un informe en Markdown, listo para la presentación, con:

- las metas del diagnóstico rápido (≤ 10 s desde la falla; ATWS ≤ 3 s desde la demanda) y su estado;
- la matriz de confusión de la Etapa 1 con la columna «UNCERTAIN»;
- la tasa de abstención y la de errores con confianza alta;
- la validación cruzada;
- los tiempos por corrida;
- la regla de ATWS;
- la Etapa 2;
- las falsas alarmas y las limitaciones.

**Why this priority**: Es lo que pide KAN-27.

**Independent Test**: Generar el informe con archivos de resultados conocidos y comprobar que cada cifra coincide con su archivo de origen y que cada meta muestra su definición, su valor y su estado.

**Acceptance Scenarios**:

1. **Given** los resultados de 005, 006, 008, 009 y 011, **When** se genera el informe, **Then** tiene la matriz 3 × 4 (NORM, LOCA, TRANS × NORM, LOCA, TRANS, UNCERTAIN) de prueba, la tabla de la regla por conjunto y los tiempos por corrida.
2. **Given** las metas de 10 s y 3 s, **When** se genera el informe, **Then** cada una aparece con su definición exacta, el valor medido, el conjunto y si se cumple.
3. **Given** la evaluación de 011, **When** se genera el informe, **Then** aparecen la tasa de abstención, la de errores con confianza alta y la exactitud con abstención, con sus intervalos de confianza, y la validación cruzada.
4. **Given** que falta un archivo de resultados, **When** se genera el informe, **Then** el comando se detiene y nombra el archivo y el comando que lo produce.

---

### User Story 2 - Trazabilidad de cada cifra (Priority: P1)

Cada cifra del informe indica de qué tarea y de qué archivo sale. `hito1.json` es reproducible.

**Why this priority**: Principio III (honestidad y reproducibilidad).

**Acceptance Scenarios**:

1. **Given** los mismos archivos de resultados, **When** se genera dos veces, **Then** `hito1.json` es idéntico.
2. **Given** el informe, **When** se lee, **Then** cada sección dice de qué tarea (KAN) y de qué archivo sale, y sobre qué conjunto se midió.

### Edge Cases

- Falta un archivo de resultados, o tiene un formato inesperado: se detiene nombrándolo.
- Metas sin datos en prueba: se muestran como «sin datos».
- Las tareas usan modelos distintos (008 lee el modelo de Etapa 1 publicado; 011 puede reentrenar): el informe dice qué modelo usó cada una.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST generar el informe en una sola ejecución a partir de los archivos publicados por `entrenar-etapa1` (005), `evaluar-regla-atws` (006), `medir-tiempo-deteccion` (008), `entrenar-etapa2` (009) y `evaluar-diagnostico` (011), sin reentrenar ni recalcular métricas.
- **FR-002**: El informe MUST incluir la matriz de confusión de la Etapa 1 con abstención (3 × 4) en prueba, tal como la publica 011, y las métricas por familia de 005.
- **FR-003**: El informe MUST incluir la tabla de la regla de ATWS por conjunto (006).
- **FR-004**: El informe MUST mostrar las metas con su definición exacta, valor, conjunto y estado. Las metas son: diagnóstico ≤ 10 s desde la falla y ATWS ≤ 3 s desde la demanda (008), más las metas propias de 005, 006, 009 y 011.
- **FR-005**: El informe MUST incluir la tasa de abstención, la de errores con confianza alta y la exactitud con abstención de 011, con sus intervalos, y la validación cruzada.
- **FR-006**: El informe MUST incluir los tiempos de detección por corrida de prueba (008) y las falsas alarmas (005, 006 y 008).
- **FR-007**: El informe MUST incluir los resultados de la Etapa 2 (009) y sus metas.
- **FR-008**: El informe MUST mostrar de forma visible que el sistema es consultivo (principio I), declarar las limitaciones y dar una lectura honesta de las metas que no se cumplen (principio III).
- **FR-009**: El sistema MUST detenerse con un error que nombre el archivo y el comando que lo genera cuando falte o sea ilegible un archivo de resultados; MUST publicar `hito1.md` y `hito1.json` todos o ninguno; y con los mismos archivos MUST producir el mismo `hito1.json`.

### Key Entities

- **Fuente**: tarea (KAN), comando y archivo de resultados.
- **Meta**: definición exacta, valor medido, conjunto, estado (cumple, no cumple o sin datos) y fuente.
- **Sección**: título, fuente y contenido del informe.

## Success Criteria *(mandatory)*

- **SC-001**: El informe tiene la matriz con abstención, las dos metas de tiempo, la tasa de abstención, la validación cruzada, la regla de ATWS y la Etapa 2.
- **SC-002**: El 100 % de las cifras coincide con su archivo de origen (comprobado por prueba automática).
- **SC-003**: Dos ejecuciones con los mismos archivos dan el mismo `hito1.json`.
- **SC-004**: El informe se genera en menos de 10 s; los comandos de las tareas, en menos de 15 min en total en CPU.

## Assumptions

- Los comandos de cada tarea se ejecutan con sus valores por defecto (semilla 42, reparto de 004) en el orden del quickstart.
- La presentación (diapositivas) la arma el equipo a partir de `hito1.md`; este informe no produce diapositivas.
