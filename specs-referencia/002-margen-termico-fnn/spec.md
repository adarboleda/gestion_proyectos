# Feature Specification: Estimación en tiempo real del margen térmico (DNBR y PCT, Fase 3)

**Feature Branch**: `002-margen-termico-fnn`

**Created**: 2026-10-18

**Status**: Implementada (ATWS sin resolver; umbrales por recalibrar)

**Input**: User description: "Estimar de forma continua y rápida el margen de ebullición (DNBR) y la temperatura pico de vaina (PCT) durante un transitorio, sin correr el simulador termohidráulico, y que las estimaciones no sean físicamente absurdas."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Curvas DNBR(t) y PCT(t) causales (Priority: P1)

El sistema entrega, en cada instante del transitorio, una estimación de DNBR y PCT usando solo lo observado hasta ese instante, para complementar el diagnóstico de accidente con la consecuencia térmica en el núcleo.

**Why this priority**: Es la segunda función del sistema según la nota de clarificación funcional (diagnóstico + indicadores térmicos) y alimenta las alertas del operador.

**Independent Test**: Comparar las curvas estimadas con las del simulador sobre las secuencias de prueba y calcular R², error absoluto medio y sesgo.

**Acceptance Scenarios**:

1. **Given** una secuencia LOCA o LOCAC de prueba, **When** se estiman DNBR y PCT, **Then** el ajuste a la curva del simulador supera R² = 0.85 en ambas variables.
2. **Given** un instante `t` cualquiera, **When** se calcula la estimación, **Then** no se usa ningún dato posterior a `t`.
3. **Given** una estimación de DNBR/PCT, **When** se informa al operador, **Then** se presenta como estimación sustituta y no como el cálculo de referencia.

---

### User Story 2 - Estimaciones físicamente plausibles (Priority: P2)

El sistema evita devolver valores térmicos que la física del dataset no permite (por ejemplo, un DNBR por debajo del piso observado), penalizándolos durante el entrenamiento.

**Why this priority**: Una estimación absurda destruye la confianza del operador, pero la penalización es un refinamiento de la P1.

**Independent Test**: Medir la fracción de estimaciones de DNBR bajo el piso físico y verificar que no empeora respecto a la iteración anterior.

**Acceptance Scenarios**:

1. **Given** el conjunto de prueba, **When** se evalúa el modelo, **Then** la tasa de violaciones del piso físico se reporta y se mantiene por debajo del 30 %.
2. **Given** un término de penalización más fuerte, **When** degrada PCT de forma apreciable (R² 0.67), **Then** se descarta y se documenta el motivo.

---

### User Story 3 - Reporte honesto por clase, con el caso ATWS declarado (Priority: P2)

El equipo necesita ver el desempeño por clase de accidente y saber exactamente dónde la estimación falla, para no ocultar que en ATWS el DNBR estimado es físicamente imposible.

**Why this priority**: Evita presentar un R² global que esconde un fallo de seguridad en una clase.

**Independent Test**: Revisar el desglose por clase (LOCA, LOCAC, ATWS) y comprobar que el caso ATWS se reporta con su error y su advertencia.

**Acceptance Scenarios**:

1. **Given** las 3 secuencias ATWS de prueba, **When** se evalúa, **Then** se reportan MAE y sesgo (no R², por varianza casi nula) y el reporte al operador sustituye el número por una advertencia textual.
2. **Given** una nueva iteración del modelo, **When** se compara con la anterior, **Then** la iteración previa queda archivada con sus métricas.

---

### Edge Cases

- ATWS se autoestabiliza y queda congelado: todas sus posiciones tienen "nada cambió todavía" como firma, igual que el instante inicial de LOCA/LOCAC.
- Evaluación sobre otra configuración de planta (PWR 3L): el modelo de NPPAD no transfiere (usa `WLR` y 150 pasos a 10 s); se reentrena aparte (feature 003).
- Los umbrales absolutos del plan (error < 0.1) asumen DNBR 1–3, pero este dataset llega hasta ~141.
- Un DNBR real cercano al piso de 2.0 hace que el ruido normal de predicción cruce el umbral con frecuencia en las roturas más severas.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST estimar DNBR y PCT para cada paso de tiempo de una secuencia de 150 pasos.
- **FR-002**: El sistema MUST derivar el contexto de evolución (media, máximo, mínimo y desviación) usando solo datos hasta el instante `t`.
- **FR-003**: El sistema MUST penalizar durante el entrenamiento los DNBR estimados por debajo del piso físico de 2.0 con una constante única compartida entre entrenamiento y evaluación.
- **FR-004**: El sistema MUST seleccionar el modelo final por el error de regresión de validación y no por la pérdida total (error + penalización).
- **FR-005**: El sistema MUST evaluar siempre sin ponderación, aunque el entrenamiento pondere los regímenes "planos".
- **FR-006**: El sistema MUST reportar MAE, RMSE, R² y sesgo por variable y por clase, el desempeño cerca de límites relevantes y la tasa de violaciones físicas.
- **FR-007**: El sistema MUST mantener un archivo de la iteración anterior para comparación.
- **FR-008**: El sistema MUST declarar que ATWS no es fiable y reemplazar el valor numérico por una advertencia en cualquier reporte al operador.
- **FR-009**: El sistema MUST operar en paralelo con el diagnóstico, sin depender de su salida.
- **FR-010**: El sistema MUST responder en menos de 10 ms por secuencia.

### Key Entities

- **EstadoDePlanta(t)**: 12 variables de planta más 48 estadísticos causales (60 entradas) en el instante `t`.
- **MargenTérmico(t)**: par (DNBR, PCT) estimado en el instante `t`, con su valor de referencia del simulador.
- **EscaladorDeObjetivos**: media y desviación de DNBR y PCT del entrenamiento.
- **PisoFísicoDNBR**: constante 2.0 usada en la penalización y en el reporte de violaciones.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: En el conjunto de prueba, R² de DNBR = 0.924 y R² de PCT = 0.903 (umbral > 0.90 orientativo; DNBR 0.924 y PCT 0.903 lo superan).
- **SC-002**: El R² de PCT en prueba pasa de −1.08 (iteración 1) a 0.903 (iteración 2).
- **SC-003**: Error absoluto medio de PCT = 23.5 °C y sesgo de +10.05 °C en prueba; MAE de DNBR = 10.77 sobre un rango de ~0 a 141.
- **SC-004**: La tasa de violaciones del piso físico es 21.17 % (límite aceptado: < 30 %).
- **SC-005**: Por clase: LOCA R² DNBR 0.910 / PCT 0.933; LOCAC 0.897 / 0.879; ATWS con MAE de DNBR 13.61 y PCT 59.65 °C (caso no resuelto, declarado).
- **SC-006**: La estimación tarda 1–2 ms por secuencia (meta < 10 ms).

## Assumptions

- DNBR y PCT de referencia provienen de PCTRAN; no se validaron contra RELAP5 ni datos de planta.
- El piso de 2.0 se eligió por el mínimo observado en entrenamiento (2.26); el límite clásico de diseño (1.3) no aplica a la escala de este dataset.
- Solo hay 10 secuencias ATWS en entrenamiento y todas con el mismo comportamiento autolimitado.
- NORM tiene una sola secuencia (sin prueba); las métricas de NORM no son representativas.
- Los umbrales absolutos del plan (MAE < 0.1, sesgo < 0.05) deben expresarse como porcentaje del rango antes de usarse como criterio de aceptación.
- El modelo es válido solo dentro del dominio de accidentes de NPPAD/PCTRAN.
