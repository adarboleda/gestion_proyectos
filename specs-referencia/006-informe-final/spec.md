# Feature Specification: Informe técnico final y documentación consolidada (Fase 6)

**Feature Branch**: `006-informe-final`

**Created**: 2026-10-18

**Status**: Pendiente (ventana del plan: 24 oct – 4 nov 2026)

**Input**: User description: "Consolidar todo el proyecto en un informe técnico final y en documentación coherente: qué se hizo, con qué datos, qué resultados reales se obtuvieron frente a cada meta del plan, qué no se logró y por qué, de modo que un jurado o un revisor técnico pueda auditarlo y reproducirlo."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Informe técnico final auditable (Priority: P1)

Un miembro del jurado o un revisor técnico lee el informe y entiende el problema, los datos, la arquitectura de dos canales, la metodología y los resultados, sin tener que abrir el código para saber qué se hizo.

**Why this priority**: Es el entregable principal de la Fase 6 y de la tesis.

**Independent Test**: Entregar el informe a una persona ajena al código y comprobar que puede responder, solo con él, qué hace el sistema, con qué datos se evaluó y qué límites tiene.

**Acceptance Scenarios**:

1. **Given** el informe terminado, **When** un revisor lo lee, **Then** encuentra el problema, el alcance (LOCA y ATWS, consultivo), la arquitectura de los dos canales y el motivo de no mezclar las plantas.
2. **Given** una cifra del informe, **When** el revisor la busca en los resultados, **Then** la encuentra en un archivo de resultados citado.
3. **Given** el apartado de reproducción, **When** el revisor sigue los comandos, **Then** regenera los resultados citados.

---

### User Story 2 - Metas del plan frente a resultados (Priority: P1)

El jurado ve, en una sola tabla, cada meta del plan de trabajo, cómo se midió, el resultado obtenido y su estado (cumple, parcial, no cumple, no alcanzable), incluidas las que no se lograron.

**Why this priority**: Es lo primero que se pregunta en una defensa; ocultar una meta no cumplida costaría credibilidad.

**Independent Test**: Verificar que cada meta del plan (precisión, tiempo de detección, falsos negativos, DNBR/PCT, EOP/XAI, compuertas, sombra) tiene fila, definición, resultado y fuente.

**Acceptance Scenarios**:

1. **Given** la meta "tiempo de detección < 3 s", **When** se informa, **Then** se define desde cuándo se mide, se separa por canal y por iniciador y se declara el mínimo físico de ATWS.
2. **Given** una meta no cumplida (por ejemplo, ATWS en DNBR o la exactitud estricta de 87.9 %), **When** se informa, **Then** aparece con su causa y su mitigación.
3. **Given** una cifra con dos versiones en documentos antiguos, **When** se informa, **Then** se usa la vigente y se corrige la antigua.

---

### User Story 3 - Documentos corregidos y consistentes (Priority: P2)

El equipo corrige los errores ya identificados en la documentación del proyecto para que ningún documento contradiga al informe.

**Why this priority**: Un error conocido que sigue publicado se convierte en una pregunta incómoda del jurado, pero no bloquea la redacción.

**Independent Test**: Revisar cada documento de la lista de correcciones y verificar que el error ya no aparece.

**Acceptance Scenarios**:

1. **Given** "ventanas de 150 pasos (Δt = 0.05 s)", **When** se corrige, **Then** dice Δt = 10 s para NPPAD y 1 s para PWR 3L.
2. **Given** "tiempo de detección < 3 s" sin definición, **When** se corrige, **Then** se define y se asigna al canal rápido.
3. **Given** "modelo de planta AP1000 por defecto", **When** se corrige, **Then** indica que NPPAD no es AP1000, sino un modelo PCTRAN PWR con otra configuración que PWR 3L.
4. **Given** el ejemplo de XAI con el caudal de fuga, **When** se corrige, **Then** usa una variable medible (presión de contención).

---

### User Story 4 - Material de defensa (Priority: P3)

El equipo dispone de un resumen ejecutivo y de una presentación coherentes con el informe, en español e inglés, y de una guía breve para recorrer las consolas.

**Why this priority**: Facilita la defensa, pero se construye a partir del informe terminado.

**Independent Test**: Revisar que las cifras del resumen y de la presentación coinciden con el informe.

**Acceptance Scenarios**:

1. **Given** el resumen ejecutivo, **When** se compara con el informe, **Then** no hay cifras distintas.
2. **Given** la guía de consolas, **When** se sigue, **Then** muestra los casos clave (LOCA grande, ATWS, TRIP_OK, evento desconocido).

---

### Edge Cases

- Los resultados de la Fase 5 pueden cambiar cifras después de que empiece la redacción; el informe cierra después de la Fase 5.
- Documentos anteriores contienen cifras distintas (por ejemplo, 12 pruebas frente a 17; mediana de ATWS 2.0 s frente a 2.25 s tras corregir el margen de 1.5 s); el informe debe usar solo las vigentes.
- Dos plantas distintas pueden dar la falsa impresión de una sola mejora de 200 s a 1 s; el informe debe presentar la comparación limpia (control) y avisar de lo que no demuestra.
- La falta de bibliografía que justifique el ruido de sensores es una debilidad abierta.
- El informe va dirigido a revisión de cumplimiento normativo nuclear: las afirmaciones consultivas deben ser inequívocas.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El informe MUST describir el problema, el alcance (LOCA y ATWS, IA consultiva y Human-in-the-Loop), la arquitectura de dos canales y la exclusión de ciberataques.
- **FR-002**: El informe MUST documentar los dos datasets (NPPAD y PWR 3L), sus diferencias de planta y muestreo, y por qué no se mezclan.
- **FR-003**: El informe MUST explicar la normalización relativa al estado inicial, la definición del tiempo de detección (y del mínimo físico de ATWS), la ablación de `WLR` y el ruido de sensores con su justificación.
- **FR-004**: El informe MUST incluir la tabla de cumplimiento de metas con definición, fuente y estado de cada una.
- **FR-005**: El informe MUST incluir un capítulo de limitaciones con las de las features 001–005.
- **FR-006**: El informe MUST citar la revisión de literatura (RSL) y los artículos de referencia.
- **FR-007**: El informe MUST describir la metodología de XAI, EOP, compuertas y modo sombra y sus resultados.
- **FR-008**: El informe MUST incluir un apartado de reproducción con comandos y tiempos aproximados.
- **FR-009**: Cada cifra del informe MUST rastrearse a un archivo de resultados citado.
- **FR-010**: Los cuatro errores de documentación identificados MUST corregirse.
- **FR-011**: El informe MUST declarar de forma explícita que el sistema es consultivo y no sustituye la protección de la planta.
- **FR-012**: El informe MUST presentar la comparación de tiempos con su control y declarar lo que la comparación no demuestra.
- **FR-013**: El resumen ejecutivo y la presentación MUST usar las mismas cifras que el informe y existir en español e inglés.

### Key Entities

- **Informe**: capítulos, figuras, tablas y anexos.
- **TablaDeCumplimiento**: meta, definición, método, resultado, estado, fuente.
- **Cifra**: valor reportado con su archivo de origen.
- **CorrecciónDeDocumento**: documento, error, texto correcto, estado.
- **MaterialDeDefensa**: resumen, presentación y guía de consolas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El informe completo está entregado antes del 4 de noviembre de 2026.
- **SC-002**: El 100 % de las metas del plan tienen fila en la tabla de cumplimiento con definición, resultado, estado y fuente.
- **SC-003**: El 100 % de las cifras citadas se rastrean a un archivo de resultados (0 cifras sin fuente).
- **SC-004**: Las 4 correcciones de documentación están hechas y verificadas.
- **SC-005**: Un revisor ajeno al código regenera al menos un resultado por canal siguiendo solo el apartado de reproducción.
- **SC-006**: El resumen ejecutivo y la presentación no contienen ninguna cifra distinta de las del informe (0 discrepancias).
- **SC-007**: Cada meta no cumplida o parcial tiene causa y mitigación escritas.

## Assumptions

- La redacción se hace después de cerrar la Fase 5; si queda trabajo sin terminar, el informe lo declara como límite.
- Formato final del informe: documento de texto (Word o PDF) generado a partir de capítulos en Markdown dentro de `IA-Nuclear/docs/informe/`; el formato exacto lo fija la normativa de la universidad.
- La revisión de literatura (`docs/RSL.docx`) y los 12 artículos de `Articulos/` son la base bibliográfica.
- El informe se escribe en español, con resumen en inglés.
- La justificación bibliográfica del ruido de sensores (tarea abierta de la feature 003) debe resolverse antes de cerrar el capítulo de metodología.
- Los resultados de las features 001–004 son estables; los de la feature 005 se incorporan al terminar.
