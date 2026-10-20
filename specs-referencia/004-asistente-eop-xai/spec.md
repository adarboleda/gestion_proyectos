# Feature Specification: Asistente de procedimientos de emergencia (EOP) y explicabilidad (Fase 4)

**Feature Branch**: `004-asistente-eop-xai`

**Created**: 2026-10-18

**Status**: Implementada (con mejoras abiertas)

**Input**: User description: "Traducir el diagnóstico y las estimaciones térmicas en algo útil para el operador: qué procedimiento de emergencia consultar, qué sensores justifican el diagnóstico y qué tendría que cambiar para que el diagnóstico fuera otro, todo en una consola que deje claro que el sistema solo aconseja."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Procedimiento recomendado según el diagnóstico (Priority: P1)

Un operador de sala de control ve, junto al diagnóstico, qué procedimiento de emergencia conviene consultar y con qué prioridad, más alertas informativas de margen térmico bajo o temperatura alta.

**Why this priority**: Es la razón de ser del asistente: convertir un diagnóstico estadístico en una acción de consulta concreta.

**Independent Test**: Para cada muestra de prueba, comprobar que el procedimiento recomendado corresponde a su diagnóstico final y que las alertas térmicas se calculan de las curvas estimadas.

**Acceptance Scenarios**:

1. **Given** un diagnóstico LOCA o LOCAC, **When** se mapea, **Then** se recomienda E-0, luego E-1 y ES-1.2 (con la rama estimada cuando existe).
2. **Given** un diagnóstico ATWS, **When** se mapea, **Then** se recomienda FR-S.1 con prioridad y se advierte que la estimación térmica no es fiable para este régimen.
3. **Given** un diagnóstico INCIERTO, **When** se mapea, **Then** se pide continuar el monitoreo o validar con el operador y no se fuerza un procedimiento.
4. **Given** el canal rápido, **When** el diagnóstico es TRANS o TRIP_OK, **Then** se indica "vigilar el disparo" o E-0 → ES-0.1 respectivamente.

---

### User Story 2 - Explicación de qué sensores justifican el diagnóstico (Priority: P1)

El operador ve, en lenguaje claro y con valores físicos, qué sensores sostienen el diagnóstico ("PWR cae + WECS sube → LOCA") y cuáles no cambiaron cuando eso es lo relevante (ATWS).

**Why this priority**: La confianza regulatoria y del operador depende de entender el porqué; se pide expresamente en el plan.

**Independent Test**: Revisar las explicaciones de las muestras representativas y comprobar que las variables citadas son físicamente coherentes con el accidente.

**Acceptance Scenarios**:

1. **Given** un diagnóstico, **When** se explica, **Then** se citan las 1–2 variables más influyentes con su valor inicial y su valor extremo en unidades físicas.
2. **Given** una variable importante que no cambia en la ventana (ATWS), **When** se explica, **Then** se dice que "se mantuvo estable" y no que "cambió".
3. **Given** el canal rápido, **When** se muestra un diagnóstico, **Then** la consola incluye una línea "Por qué" con los valores medibles que lo respaldan, solo con lo ya ocurrido.

---

### User Story 3 - Explicación contrafáctica (Priority: P2)

El operador puede preguntar "¿qué tendría que cambiar para que el procedimiento recomendado fuera otro?" y recibir una respuesta mínima, o la indicación honesta de que no existe una respuesta simple.

**Why this priority**: Reduce la carga cognitiva en estrés, pero es un refinamiento de la explicación.

**Independent Test**: Para las muestras representativas, verificar que el contrafáctico se reporta como "encontrado" con la variable y el porcentaje, o como "no encontrado" sin forzar una respuesta.

**Acceptance Scenarios**:

1. **Given** un diagnóstico, **When** se busca el contrafáctico, **Then** se mueve la muestra hacia el perfil medio de la segunda clase más probable, variable por variable, hasta que el diagnóstico cambie.
2. **Given** que ninguna combinación de hasta 2 variables lo logra, **When** se reporta, **Then** se declara como límite del método.

---

### User Story 4 - Consola del operador (Priority: P2)

El equipo y el jurado ven los resultados en una consola autosuficiente (sin servidor), en español o inglés, con reproducción paso a paso del transitorio, para las muestras representativas del canal lento y para las 106 corridas del canal rápido.

**Why this priority**: Hace visible y auditable el comportamiento del sistema; no es función de seguridad.

**Independent Test**: Abrir cada consola con doble clic, cambiar de idioma, reproducir un transitorio y verificar que solo se muestra lo ya ocurrido.

**Acceptance Scenarios**:

1. **Given** una consola abierta en el navegador, **When** se pulsa reproducir, **Then** diagnóstico, confianza, EOP y curvas avanzan con el tiempo sin mostrar el futuro.
2. **Given** el botón ES/EN, **When** se cambia el idioma, **Then** cambia toda la consola y la elección se comparte entre las dos consolas.
3. **Given** cualquier pantalla, **When** se muestra una recomendación, **Then** se declara que es consultiva.

---

### Edge Cases

- En los primeros ~450–550 s de una secuencia LOCA, el canal lento puede diagnosticar ATWS con alta confianza (antes de la rotura el estado es indistinguible); una lectura temprana no debe tomarse como definitiva.
- La alerta de margen térmico bajo se dispara en las 33 muestras de prueba porque usa el mínimo de toda la ventana y el inicio de cualquier secuencia ya está bajo el umbral orientativo.
- Para ATWS, la estimación térmica es físicamente imposible (DNBR −11.31): la advertencia textual sustituye al número.
- Un diagnóstico muy seguro es difícil de revertir con 1–2 variables: el contrafáctico de la etapa 1 casi nunca se encuentra.
- No se modelan los procedimientos de enfriamiento del núcleo (FR-C.1/C.2/C.3), que necesitan termopares de salida del núcleo y nivel de vasija que el canal rápido no usa.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST traducir cada diagnóstico en un procedimiento recomendado mediante lógica determinista (sin IA): LOCA/LOCAC → E-0, E-1, ES-1.2; ATWS → FR-S.1; NORM → vigilancia; INCIERTO → monitoreo/validar con el operador; TRANS → E-0 con la instrucción de vigilar el disparo solicitado; TRIP_OK → E-0, ES-0.1.
- **FR-002**: El sistema MUST calcular alertas térmicas informativas con umbrales orientativos (DNBR bajo 2.5 en la escala de PCTRAN, PCT sobre 900 °C) y marcarlas como no regulatorias.
- **FR-003**: El sistema MUST sustituir el valor térmico de ATWS por una advertencia textual mientras la estimación no sea fiable.
- **FR-004**: El sistema MUST explicar cada diagnóstico con la importancia por variable, citando valores físicos y reportando como "estable" lo que no cambió.
- **FR-005**: El sistema MUST explicar el diagnóstico del canal rápido con importancia por permutación y con la línea "Por qué" (ATWS, LOCA/LOCAC, INCIERTO, TRIP_OK).
- **FR-006**: El sistema MUST ofrecer una explicación contrafáctica de la etapa 1 y de la etapa 2 que reporte "no encontrado" cuando corresponda.
- **FR-007**: El sistema MUST mostrar umbrales automáticos de la guía de umbrales de la experta (disparo por presión baja 132.2 bar, arranque de HPI 118.1 bar, acumuladores 43.27 bar, RHR 11.36 bar, contención 1.30 bar).
- **FR-008**: El sistema MUST entregar consolas autosuficientes que reproduzcan solo cálculos ya hechos, con botón ES/EN compartido y reproducción causal paso a paso.
- **FR-009**: El sistema MUST declarar en cada consola y reporte que el asistente es consultivo.
- **FR-010**: El sistema MUST no reentrenar ni modificar los modelos de las features 001–003.

### Key Entities

- **ResultadoEOP**: diagnóstico, confianza, lista de procedimientos, guía textual, alertas térmicas y advertencia de ATWS.
- **Explicación**: método (SHAP u oclusión / permutación), variables ordenadas por importancia y frase narrativa.
- **Contrafáctico**: variable(s), porcentaje de interpolación y clase objetivo, o "no encontrado".
- **MuestraRepresentativa**: selección determinista de muestras (una por clase, los casos límite, NORM de validación y dos casos correctos con confianza ≥ 80 %).
- **Consola**: página autosuficiente con datos precalculados embebidos.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Las 33 muestras de prueba reciben una recomendación coherente con su diagnóstico: 13 LOCA, 13 LOCAC, 3 ATWS y 4 INCIERTO.
- **SC-002**: Toda recomendación LOCA/LOCAC incluye los tres procedimientos E-0, E-1 y ES-1.2, y toda ATWS incluye FR-S.1 con advertencia térmica.
- **SC-003**: Las 8 muestras representativas tienen explicación con variables físicamente coherentes (PWR cae y WECS sube en LOCA; variables estables en ATWS).
- **SC-004**: El contrafáctico de la etapa 2 se encuentra en las 6 muestras donde se probó; el de la etapa 1 en 1 de 8 (resultado declarado, no forzado).
- **SC-005**: Cada diagnóstico del canal rápido muestra su "Por qué" en las pestañas En vivo y Caso a caso para las 106 corridas.
- **SC-006**: Las consolas se abren con doble clic sin servidor, cambian de idioma en un clic y la elección persiste entre ambas.
- **SC-007**: El mapeo clase → procedimiento coincide con la guía de umbrales de la experta, incluido el margen de 1.5 s de la compuerta ATWS.

## Assumptions

- Los procedimientos E-0, E-1, ES-1.2, FR-S.1 y ES-0.1 son los estándar de la industria PWR; los umbrales son de la guía "Thresholds, Procedures and Timing" (Basic Data Set #1, W 3-Loop).
- El criterio de paso a ES-1.2 (~15 bar) es aproximado y no confirmado para esta planta.
- Los umbrales de alerta térmica son orientativos y no son las compuertas de seguridad (esas pertenecen a la feature 005).
- Las consolas no ejecutan ningún modelo: muestran cálculos hechos en Python.
- Los ejemplos de explicación del plan original usan una variable no medible (`WLR`); deben cambiarse por variables medibles (tarea en la feature 006).
- El plan pedía SHAP o LIME; para el canal rápido se eligió importancia por permutación.
