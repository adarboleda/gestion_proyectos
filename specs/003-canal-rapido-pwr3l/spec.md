# Feature Specification: Canal rápido de detección a 1 s con PWR 3L

**Feature Branch**: `003-canal-rapido-pwr3l`

**Created**: 2026-10-18

**Status**: Implementada y validada (límites declarados)

**Input**: User description: "Detectar y clasificar LOCA, ATWS y operación normal en segundos usando solo variables medibles en sala de control, a partir de simulaciones de otra planta a 1 dato por segundo, sin falsas alarmas, y respondiendo 'incierto' ante eventos que el sistema no conoce."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Corridas de simulación confiables (Priority: P1)

Un ingeniero de simulación necesita un conjunto de corridas de la planta PWR 3L (1 dato por segundo) generadas de forma repetible y verificadas una a una, con clases balanceadas y con casos de contraste, para que el detector se entrene y se pruebe con datos sin defectos.

**Why this priority**: Sin corridas buenas (la R07 contaminada lo demostró) cualquier detector aprende un "normal" falso; todo lo demás depende de esto.

**Independent Test**: Ejecutar la validación de corridas sobre todo el conjunto y verificar que cada corrida queda marcada utilizable, dudosa o a repetir, y que hay 20 corridas por clase.

**Acceptance Scenarios**:

1. **Given** un plan de corridas (clase, condición inicial, falla, retardo), **When** se ejecuta el lote, **Then** cada corrida genera sus datos y un veredicto de calidad automático.
2. **Given** una corrida que arranca con la presión ya cayendo, **When** se valida, **Then** se excluye del entrenamiento.
3. **Given** un ATWS, **When** se arma el conjunto, **Then** existe su gemelo con el disparo funcionando (TRIP_OK) para el mismo evento.

---

### User Story 2 - Detección temprana de LOCA/LOCAC (Priority: P1)

Ante una fuga de refrigerante, el sistema la identifica en segundos desde su inicio, sin usar el caudal de fuga (que no se mide en planta).

**Why this priority**: Es la meta de seguridad principal del canal rápido y la razón por la que existe.

**Independent Test**: Medir, por corrida evaluada con modelos que no la vieron y con ruido de sensores, el tiempo desde el inicio de la fuga hasta el diagnóstico confirmado.

**Acceptance Scenarios**:

1. **Given** una rotura de cualquier tamaño, **When** se evalúa en el peor caso, **Then** se detecta en 10 s o menos.
2. **Given** una rotura de 10 cm² o más, **When** se evalúa, **Then** se detecta en 3 s o menos.
3. **Given** una rotura de 2–5 cm², **When** se evalúa, **Then** se detecta y se reporta su tiempo como límite declarado.

---

### User Story 3 - ATWS frente a disparo normal (Priority: P1)

El sistema distingue un ATWS (el reactor no se dispara cuando debía) de un disparo normal ante el mismo evento, con una regla determinista que no se equivoque en ninguna corrida.

**Why this priority**: ATWS activa la boración de emergencia; una falsa alarma tiene un costo alto y un ATWS no detectado es el peor error.

**Independent Test**: Evaluar la compuerta sobre los 20 ATWS y sus 20 gemelos TRIP_OK y contar confirmaciones y falsos positivos.

**Acceptance Scenarios**:

1. **Given** una demanda de disparo y el retardo normal del scram vencido más 1.5 s con el flujo neutrónico todavía alto, **When** se evalúa, **Then** se confirma ATWS.
2. **Given** el mismo evento con el disparo funcionando, **When** se evalúa, **Then** el sistema reporta TRIP_OK y retira cualquier "ATWS posible".
3. **Given** el intervalo antes de que venza el retardo del scram, **When** aún no se puede distinguir, **Then** el sistema muestra "ATWS posible", no una confirmación.

---

### User Story 4 - Sin falsas alarmas y "incierto" ante lo desconocido (Priority: P1)

En operación normal el sistema no alarma, y ante un evento que no conoce (rotura de tubos de generador de vapor, rotura de vapor, rotura de letdown, PORV abierta) responde INCIERTO mostrando el motivo.

**Why this priority**: Un sistema que da falsas alarmas se ignora, y uno que clasifica con confianza un evento desconocido engaña al operador.

**Independent Test**: Contar alarmas en las corridas NORM y en los tramos previos al evento, y verificar el resultado en las 6 corridas fuera de distribución.

**Acceptance Scenarios**:

1. **Given** una corrida de operación normal, **When** se evalúa, **Then** no se emite ninguna alarma.
2. **Given** un evento fuera de distribución, **When** un monitor físico sale de su envolvente, **Then** el diagnóstico es INCIERTO con el motivo y el valor anormal.
3. **Given** un evento conocido, **When** se evalúa, **Then** los monitores de novedad no se disparan.

---

### User Story 5 - Rama caliente o fría en roturas grandes (Priority: P2)

Para un LOCA, el sistema estima la rama afectada usando la excursión de potencia previa al disparo.

**Why this priority**: Caracterización adicional pedida, pero con límite físico en roturas pequeñas.

**Independent Test**: Medir el acierto de la rama en roturas de 50 cm² o más.

**Acceptance Scenarios**:

1. **Given** una rotura de 50 cm² o más, **When** se estima la rama, **Then** acierta en la gran mayoría de los casos y reporta "sin decidir" cuando la señal no basta.
2. **Given** una rotura menor a 5 cm², **When** la excursión de potencia es menor que el ruido, **Then** no se asigna rama.

---

### User Story 6 - Margen térmico en la planta del canal rápido (Priority: P2)

El sistema estima DNBR y PCT también para PWR 3L, con un modelo entrenado con esa planta, sin caudal de fuga y a 1 s.

**Why this priority**: Complementa el diagnóstico con la consecuencia térmica; el modelo de NPPAD no se transfiere.

**Independent Test**: Medir R² fuera de muestra y los errores en el DNBR mínimo y en la PCT máxima de cada corrida.

**Acceptance Scenarios**:

1. **Given** corridas no vistas, **When** se estiman DNBR y PCT, **Then** el ajuste supera R² = 0.95.
2. **Given** el modelo de NPPAD aplicado a esta planta, **When** se prueba, **Then** el fallo de transferencia queda documentado y no se usa.

---

### User Story 7 - Demostrar que el tiempo bajó (Priority: P3)

El equipo muestra al jurado, de forma que no dependa de comparar plantas distintas, cuánto bajó el tiempo de detección frente al canal lento.

**Why this priority**: Es el argumento de valor del canal rápido, pero no una función de seguridad.

**Independent Test**: Comparar el tiempo del canal rápido con el del mismo detector bajo la regla del canal lento sobre las mismas corridas.

**Acceptance Scenarios**:

1. **Given** las mismas corridas y el mismo modelo, **When** se cambia la regla (1 dato cada 10 s con 3 evaluaciones frente a 1 dato por segundo con 2 s), **Then** la mediana de LOCA baja de 24.5 s a 1.0 s.
2. **Given** la comparación con la Fase 2 sobre NPPAD, **When** se presenta, **Then** se advierte que mezcla dos plantas y solo da el orden de magnitud.

---

### Edge Cases

- Un ATWS y un disparo normal son físicamente iguales antes de que venza el retardo del scram (rotor bloqueado 4.0 s, barras 3.0 s, pérdida de agua de alimentación 3.0 s, pérdida de red 4.0 s, turbina 6.5 s de mínimo físico).
- Algunas fallas del simulador ignoran el retardo (disparo de turbina), no tienen efecto (inserción de barras, dilución de boro) o hacen caer la demo (extracción de barras con magnitud 30).
- Solo sirven las condiciones iniciales 1–3; las 4, 5, 6, 22 y 23 arrancan con alarmas o con tiempo desfasado.
- La combinación LOCA + pérdida de red engaña a la estimación de rama (R78).
- La demo dura 300 s por corrida, es determinista y no trae ruido de sensores.
- Los gemelos manuales difieren levemente (rociado del presurizador), lo que podría dar una pista no física de presión.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST generar corridas de PWR 3L de forma automática desde un plan editable y validar cada una (inicio real frente al plan, ausencia de contaminación inicial, condición inicial válida).
- **FR-002**: El sistema MUST mantener 20 corridas por clase (NORM, LOCA, LOCAC, ATWS, TRIP_OK) y 6 corridas fuera de distribución usadas solo para prueba.
- **FR-003**: El sistema MUST expresar cada variable relativa al estado inicial de su corrida y usar solo datos causales.
- **FR-004**: El sistema MUST usar únicamente variables medibles en sala de control como entrada; el caudal de fuga se usa solo como etiqueta.
- **FR-005**: El sistema MUST clasificar en NORM, TRANS, TRIP_OK, ATWS o LOCA, confirmando con 2 s seguidos de confianza de 0.80 o más y respondiendo INCIERTO en otro caso.
- **FR-006**: El sistema MUST confirmar ATWS con una compuerta determinista (demanda de disparo + retardo del scram propio de la señal + 1.5 s + flujo neutrónico sobre el 20 %) que prevalezca sobre el clasificador.
- **FR-007**: El sistema MUST monitorear radiación fuera de contención, asimetría de presión entre generadores de vapor, PORV abierta con presión baja y presión de contención sin radiación, con umbral de 1.5 veces la envolvente de las corridas conocidas, y responder INCIERTO con el motivo.
- **FR-008**: El sistema MUST estimar la rama caliente/fría con la excursión de potencia previa al scram enclavada.
- **FR-009**: El sistema MUST estimar DNBR y PCT con un modelo entrenado con PWR 3L.
- **FR-010**: El sistema MUST evaluar por validación cruzada de 5 particiones por grupos (cada ATWS junto a su gemelo), tres veces por corrida (sin ruido y con dos realizaciones) y reportar el peor caso.
- **FR-011**: El sistema MUST aplicar ruido de sensores fijo por instrumento (presión 0.4 bar, presión de GV 0.25 bar, temperaturas 0.5 °C, niveles 1 %, flujo neutrónico y potencia 0.5 puntos, caudales 1.5 % del fondo de escala, radiación 5 %).
- **FR-012**: El sistema MUST comparar el modelo elegido con al menos una alternativa simple y una recurrente y reportar ablaciones.
- **FR-013**: El sistema MUST fusionar las salidas en este orden de prioridad: novedad → compuerta ATWS → desacuerdo con el canal lento → clase confirmada.
- **FR-014**: El sistema MUST ser consultivo y declarar sus límites en el reporte de resultados.

### Key Entities

- **CorridaPWR3L**: simulación de 300 s a 1 s con clase, condición inicial, fallas, inicio real, señal de disparo requerido, gemelo y estado (usar / repetir / descartar / fuera de distribución).
- **Gemelo**: pareja ATWS/TRIP_OK del mismo evento y el mismo instante, con y sin falla de no-disparo.
- **Detección**: clase confirmada, confianza, alarma temprana, compuerta, novedad y rama.
- **MonitorDeNovedad**: regla física con su envolvente de referencia.
- **ResultadoDeAceptación**: criterio, valor medido y veredicto (cumple / parcial / no cumple).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: LOCA/LOCAC se detectan en 10 s o menos en 40 de 40 corridas (mediana 1 s, máximo 6 s); en 3 s o menos en 35 de 35 roturas de 10 cm² o más.
- **SC-002**: ATWS: 14 de 20 en 3 s o menos y 20 de 20 dentro de su mínimo físico; alarma temprana en 3 s o menos en 20 de 20.
- **SC-003**: TRIP_OK: 20 de 20 en 10 s o menos (mediana 2.25 s).
- **SC-004**: La compuerta confirma 20 de 20 ATWS y marca 0 de 20 disparos normales como ATWS.
- **SC-005**: Cero falsas alarmas: 0 de 20 corridas NORM y 0 de 70 corridas con alarma antes del evento.
- **SC-006**: Los 6 eventos fuera de distribución terminan en INCIERTO y 0 de 100 corridas conocidas disparan una falsa novedad.
- **SC-007**: Rama caliente/fría: 25 de 28 correctas en roturas de 50 cm² o más (parcial: 1 equivocada, 2 sin decidir).
- **SC-008**: El margen térmico alcanza R² 0.983 en DNBR y 0.992 en PCT, con error medio de PCT de 6.6 °C.
- **SC-009**: La exactitud balanceada por segundo, fuera de muestra, es 0.971; el modelo elegido (0.972) supera a Random Forest (0.964), GRU causal (0.922) y regresión logística (0.899).
- **SC-010**: La mediana de detección de LOCA baja de 24.5 s (control con la regla del canal lento) a 1.0 s, unas 24 veces.
- **SC-011**: Las 17 pruebas automáticas pasan.

## Assumptions

- PWR 3L (2705 MWt, 1 s) y NPPAD (2895 MWt, 10 s) son plantas distintas; no se mezclan datos ni se afirma que sea el mismo transitorio.
- El ruido de sensores es un supuesto de ingeniería que falta justificar con bibliografía.
- El margen de 1.5 s de la compuerta ATWS es criterio de ingeniería de la guía de umbrales de la experta, no un valor citado de los procedimientos.
- Los monitores de novedad se eligieron conociendo las 6 corridas fuera de distribución; no hay evidencia para otros eventos desconocidos (por ejemplo, dilución de boro).
- El simulador demo dura 300 s y es determinista; una licencia completa permitiría corridas más largas (pregunta abierta).
- Existe una señal digital de demanda de disparo en sala de control (anunciador o interruptores).
- La regla de desacuerdo con el canal lento solo se probó con datos sintéticos.
