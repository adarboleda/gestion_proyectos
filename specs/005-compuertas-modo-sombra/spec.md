# Feature Specification: Compuertas deterministas, rechazo de la IA y modo sombra (Fase 5)

**Feature Branch**: `005-compuertas-modo-sombra`

**Created**: 2026-10-18

**Status**: En curso (parcial; ventana del plan: 10–23 oct 2026)

**Input**: User description: "Blindar el sistema: que reglas deterministas inquebrantables prevalezcan sobre la IA cuando la seguridad lo pida, que la IA se descarte y se pase a un respaldo tradicional cuando no merezca confianza o los datos cambien de forma imprevista, y probar todo el sistema en modo sombra con registros auditables antes de cualquier uso real."

## Clarifications

### Session 2026-10-18

- Q: ¿Cómo se aplica la compuerta de DNBR? → A: Umbral relativo (caída porcentual respecto al DNBR nominal de la condición inicial), no el 1.3 literal, que nunca se activaría. Solo si el reactor no ha disparado, y no con estimaciones no fiables (ATWS). El porcentaje se calibra con la tabla de DNBR por clase, que se lleva a la experta con el 1.3 literal como referencia.
- Q: ¿Qué es el respaldo en espera fría y qué significa "< 1 s"? → A: Algoritmos deterministas sin IA: setpoints automáticos de la planta de la guía (132.2 bar disparo por presión baja, 118.1 bar HPI, 1.30 bar contención, nivel bajo de GV 17 %…) más el mapeo a E-0, la compuerta ATWS y los monitores de novedad. El "< 1 s" es la latencia de conmutación en software.
- Q: ¿Quién define la "decisión de los expertos" del modo sombra? → A: Dos niveles: referencia automática (la guía de la experta: procedimiento por clase y tiempos de referencia de R03, R09 y R28) y revisión real (la experta anota a ciegas unas 10 corridas).
- Pendiente: valor y escala del límite de PCT (ver la historia 1, escenario 3).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Compuertas de seguridad que mandan sobre la IA (Priority: P1)

Un operador recibe una alerta prioritaria, e instrucción de disparo cuando corresponde, basada en límites físicos fijos, aunque el modelo estadístico diga otra cosa o no tenga confianza.

**Why this priority**: Es la garantía de que ningún error del modelo puede ocultar una condición de seguridad; sin ella el sistema no es defendible ante un regulador.

**Independent Test**: Reproducir corridas donde se cumpla cada condición de compuerta con la salida de la IA forzada a "normal" y verificar que la alerta prioritaria sale igual.

**Acceptance Scenarios**:

1. **Given** una demanda de disparo, el retardo del scram vencido más el margen y el flujo neutrónico todavía alto, **When** el clasificador dice otra cosa, **Then** la alerta ATWS prevalece (ya implementada en el canal rápido).
2. **Given** un margen de ebullición estimado que cae por debajo del umbral relativo de la compuerta (caída porcentual respecto al DNBR nominal de la condición inicial) y un reactor que aún no ha disparado, **When** se evalúa en cualquier instante, **Then** se emite la alerta prioritaria e instrucción de disparo.
3. **Given** una temperatura pico de vaina que supera el límite de la compuerta, **When** se evalúa, **Then** se emite la alerta prioritaria ignorando la probabilidad de la IA [NEEDS CLARIFICATION: ¿qué valor y qué escala usa el límite de PCT? El límite regulatorio habitual (10 CFR 50.46) es 2200 °F ≈ 1204 °C, pero la PCT de PCTRAN en PWR 3L parte de ~550 °C y no pasa de 606 °C, así que ese límite nunca se alcanzaría; el aviso informativo actual es 900 °C. Opciones: A) límite absoluto regulatorio como referencia (nunca se activa en la demo); B) límite relativo (subida desde el valor inicial); C) valor y escala fijados por la experta].

---

### User Story 2 - Rechazo de la IA y respaldo en menos de 1 s (Priority: P1)

Cuando la confianza del clasificador cae por debajo de 80 %, o los datos de los sensores cambian de forma imprevista respecto a lo conocido, el sistema descarta la respuesta de la IA y pasa en menos de 1 s a un respaldo tradicional.

**Why this priority**: Es la defensa contra lo desconocido; sin ella, un evento nuevo recibiría un diagnóstico confiado y equivocado.

**Independent Test**: Inyectar eventos fuera de distribución y degradaciones de confianza y medir que el rechazo y el respaldo se activan en menos de 1 s.

**Acceptance Scenarios**:

1. **Given** una confianza menor a 0.80, **When** se emite el resultado, **Then** se muestra INCIERTO y se activa el respaldo (el INCIERTO ya existe; falta el respaldo explícito).
2. **Given** una divergencia de Kullback-Leibler mayor a 0.1 entre la distribución reciente de sensores y la de entrenamiento, **When** se detecta, **Then** la salida de la IA se rechaza automáticamente.
3. **Given** que el respaldo está activo, **When** el operador mira la consola, **Then** ve claramente que la IA fue rechazada, por qué, y que el respaldo en uso son los setpoints automáticos de la planta (disparo por presión baja 132.2 bar, HPI 118.1 bar, contención 1.30 bar, nivel bajo de generador de vapor 17 %, entre otros de la guía de la experta) más el mapeo a E-0, junto con la compuerta ATWS y los monitores de novedad, que ya son deterministas.
4. **Given** el cambio de la salida de la IA al respaldo, **When** se mide, **Then** la latencia de conmutación (software) es menor a 1 s; esa medida no es el tiempo de detección.

---

### User Story 3 - Fusión de los dos canales (Priority: P2)

El operador ve la alarma temprana del canal rápido de inmediato, la marca "confirmado" cuando el canal lento coincide, y INCIERTO con los dos diagnósticos cuando discrepan.

**Why this priority**: Une los dos resultados del proyecto en una sola salida, pero depende de que cada canal funcione.

**Independent Test**: Alimentar la fusión con salidas de ambos canales (coincidencia, desacuerdo, ausencia de un canal) y comprobar la prioridad de reglas.

**Acceptance Scenarios**:

1. **Given** una alarma del canal rápido, **When** aún no hay confirmación del lento, **Then** se muestra de inmediato como alarma temprana.
2. **Given** que el canal lento confirma la misma clase, **When** se fusiona, **Then** se muestra "diagnóstico confirmado".
3. **Given** que los canales no coinciden, **When** se fusiona, **Then** el resultado es INCIERTO y se muestran ambos diagnósticos.

---

### User Story 4 - Modo sombra con registros auditables (Priority: P2)

El equipo ejecuta el sistema completo en paralelo y en silencio sobre corridas no vistas, registra cada decisión en un log auditable y la compara con la decisión teórica de expertos, para demostrar fiabilidad antes del despliegue.

**Why this priority**: Es la evidencia final para el informe y para el jurado.

**Independent Test**: Reproducir un conjunto de corridas no vistas y verificar que cada instante de decisión tiene su registro y su comparación con la referencia.

**Acceptance Scenarios**:

1. **Given** las 106 corridas de PWR 3L, **When** se reproducen a 1 s, **Then** cada decisión queda en la línea de tiempo "Caso a caso" (ya existe como consola; falta el log auditable exportable).
2. **Given** corridas no vistas de NPPAD, **When** se reproducen a 10 s, **Then** se registran diagnóstico, EOP y alertas y se calcula la tasa de acuerdo con dos niveles de referencia: (1) referencia automática, que es la guía de la experta aplicada como regla (procedimiento esperado por clase y tiempos de referencia medidos en R03, R09 y R28), y (2) revisión real, en la que la experta anota a ciegas una muestra de unas 10 corridas con el procedimiento que esperaría.
3. **Given** un registro de sombra, **When** se audita, **Then** muestra marca de tiempo de simulación, entradas resumidas, diagnóstico, confianza, compuertas activas, EOP recomendado y motivo.

---

### User Story 5 - Eventos fuera de distribución en ambos canales (Priority: P3)

Ante accidentes que el sistema no conoce, la respuesta es INCIERTO o respaldo, nunca un diagnóstico equivocado con confianza alta.

**Why this priority**: Complementa US2 con la verificación de todo el rango de eventos no cubiertos.

**Independent Test**: Medir la fracción de eventos desconocidos que terminan en INCIERTO o respaldo en cada canal.

**Acceptance Scenarios**:

1. **Given** los 6 eventos fuera de distribución de PWR 3L, **When** se evalúan, **Then** los 6 terminan en INCIERTO (cumplido).
2. **Given** las 14 categorías de accidentes de NPPAD no usadas para entrenar el canal lento (FLB, LACP, LLB, LOF, LR, MD, RI, RW, SGATR, SGBTR, SLBIC, SLBOC, SP, TT), **When** se evalúan, **Then** se reporta qué fracción termina en INCIERTO o respaldo.

---

### Edge Cases

- Un ATWS no se distingue de un disparo normal antes de que venza el retardo del scram: la compuerta muestra "ATWS posible" y no confirma antes de tiempo.
- La compuerta de DNBR con el piso físico 2.0 de la feature 002 podría activarse en el 21 % de las estimaciones por ruido en roturas severas: la compuerta debe usar la regla acordada y no el piso del entrenamiento.
- Para ATWS la estimación de DNBR no es fiable (−11.31): una compuerta sobre ese valor daría una activación espuria.
- La regla de desacuerdo entre canales no se puede validar con datos reales porque no existe el mismo transitorio en las dos plantas.
- Un canal ausente (por ejemplo, el lento aún no tiene 1500 s de datos) no debe forzar INCIERTO permanente.
- El respaldo no puede depender del modelo estadístico que acaba de ser rechazado.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST aplicar la compuerta de ATWS (demanda de disparo + retardo del scram + 1.5 s + flujo neutrónico alto) con prioridad sobre el clasificador.
- **FR-002**: El sistema MUST emitir alerta prioritaria e instrucción de disparo cuando el DNBR estimado caiga más que un porcentaje configurable respecto al DNBR nominal de la condición inicial, y solo si el reactor no ha disparado (en un TRIP_OK no se ordena disparo). El 1.3 literal del plan se reporta como referencia, no como regla.
- **FR-002b**: El sistema MUST no activar la compuerta de DNBR con estimaciones no fiables (ATWS, donde la FNN-SELU no es fiable) y MUST reportar la tabla de DNBR por clase que sustenta el porcentaje elegido.
- **FR-003**: El sistema MUST emitir alerta prioritaria cuando la temperatura pico de vaina supere el límite de la compuerta de PCT (valor y escala pendientes de la experta, ver el marcador de la historia 1).
- **FR-004**: El sistema MUST descartar la salida de la IA cuando la confianza sea menor a 0.80.
- **FR-005**: El sistema MUST descartar la salida de la IA cuando la divergencia de Kullback-Leibler de los sensores respecto a la distribución de entrenamiento supere 0.1.
- **FR-006**: El sistema MUST conmutar al respaldo en menos de 1 s desde el rechazo (latencia de software, no tiempo de detección), e informar al operador del rechazo, su motivo y el respaldo en uso. El respaldo son algoritmos deterministas sin IA: setpoints automáticos de la planta de la guía de la experta, mapeo a E-0, compuerta ATWS y monitores de novedad.
- **FR-007**: El sistema MUST implementar la fusión de canales: alarma temprana inmediata, confirmación al coincidir, INCIERTO con ambos diagnósticos al discrepar, y compuerta determinista sobre ambos.
- **FR-008**: El sistema MUST ejecutar un modo sombra que reproduzca corridas no vistas sin actuar sobre nada y registre cada decisión en un log auditable exportable.
- **FR-009**: El sistema MUST comparar cada decisión de sombra con la referencia automática (guía de la experta) y, para la muestra de unas 10 corridas, con la anotación ciega de la experta, y reportar la tasa de acuerdo por clase y por tipo de referencia.
- **FR-010**: El sistema MUST verificar que los eventos fuera de distribución terminen en INCIERTO o respaldo en ambos canales.
- **FR-011**: El sistema MUST declarar la limitación de no poder validar la fusión con el mismo transitorio en las dos plantas.
- **FR-012**: El sistema MUST mantener todas las compuertas y el respaldo como lógica determinista independiente del estado de los modelos.

### Key Entities

- **Compuerta**: regla determinista con condición, estado (inactiva, posible, confirmada), instrucción y prioridad.
- **EventoDeRechazo**: instante, motivo (confianza baja, deriva KL, novedad), valor medido y respaldo activado.
- **EstadoDeRespaldo**: algoritmo tradicional en uso y tiempo de conmutación.
- **RegistroDeSombra**: línea auditable por decisión (instante, resumen de entradas, diagnóstico, confianza, compuertas, EOP, motivo, referencia y acuerdo).
- **ReferenciaDeExpertos**: decisión teórica contra la que se compara cada registro, con dos fuentes: automática (guía de la experta) y revisión ciega de una muestra.
- **ResultadoDeFusion**: diagnóstico final, ambos diagnósticos de entrada y regla aplicada.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En el 100 % de los casos de prueba donde se cumple una condición de compuerta, se emite la alerta prioritaria aunque la salida de la IA se fuerce a normal (0 omisiones).
- **SC-002**: La compuerta de ATWS confirma 20 de 20 ATWS y no marca ningún disparo normal (ya medido: 20/20 y 0/20).
- **SC-003**: En el 100 % de las inyecciones de baja confianza o deriva de datos, el rechazo y el respaldo se activan en menos de 1 s.
- **SC-004**: Cada decisión de las corridas reproducidas en modo sombra tiene un registro auditable completo (100 % de cobertura).
- **SC-005**: La tasa de acuerdo con la referencia automática se reporta por clase y es de al menos 95 % en las clases conocidas, excluyendo INCIERTO (la meta de exactitud del plan); la revisión ciega de unas 10 corridas se reporta aparte.
- **SC-008**: La tabla de DNBR por clase (con el 1.3 literal como referencia) está entregada a la experta y el porcentaje de la compuerta queda justificado con ella.
- **SC-006**: Los 6 eventos fuera de distribución de PWR 3L terminan en INCIERTO (ya medido: 6/6) y se reporta la fracción de las 14 categorías no usadas de NPPAD que termina en INCIERTO o respaldo.
- **SC-007**: En la regla de desacuerdo entre canales, los tres casos (coincidencia, desacuerdo, canal ausente) producen la salida esperada en las pruebas automáticas.

## Assumptions

- Plazo del plan: Fase 5 del 10 al 23 de octubre de 2026 (quedan 5 días hábiles desde la fecha de esta especificación); la redacción empieza el 24 de octubre.
- Ya implementado: compuerta ATWS (canal rápido), monitores físicos de novedad, INCIERTO por confianza < 0.80, regla de fusión con datos sintéticos, reproducción a 1 s de las 106 corridas en la consola.
- No implementado: compuerta de DNBR, compuerta de PCT, rechazo por deriva KL, respaldo en espera fría con conmutación < 1 s, registro de sombra auditable exportable, sombra sobre NPPAD, comparación con referencia de expertos.
- Las alertas térmicas actuales (DNBR 2.5, PCT 900 °C) son orientativas y no sustituyen las compuertas de esta feature.
- La divergencia KL se calculará sobre ventanas deslizantes de las variables de entrada contra su distribución de entrenamiento; en el canal rápido, los monitores físicos de novedad ya cumplen esa función y se reutilizan.
- Las 14 categorías de NPPAD no usadas para entrenar sirven como conjunto fuera de distribución del canal lento.
- La experta del proyecto (autora de la guía de umbrales) confirma el porcentaje de la compuerta de DNBR y fija el valor y la escala del límite de PCT; las decisiones de diseño de la sección *Clarifications* ya están tomadas.
- Dato aportado en la clarificación (a verificar al construir la tabla de DNBR por clase): en PWR 3L el peor ATWS cae un 28 % (de 2.29 a 1.65).
- En PCTRAN la PCT no es una temperatura real de vaina: parte de ~550 °C y no pasa de 606 °C en PWR 3L.
- Todo lo de esta feature es consultivo: la compuerta emite alerta e instrucción al operador, no actúa sobre la planta.
