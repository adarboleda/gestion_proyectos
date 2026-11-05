# Feature Specification: Documentación del dataset (README de la Fase 1 y metadatos)

**Feature Branch**: `010-documentacion-dataset`  
**Created**: 2026-11-04  
**Status**: Draft  
**Input**: User description: "Documentar el dataset (README de la Fase 1 y metadatos): Describir origen de los datos, modelo de planta, variables, conteo por clase y conjunto, y limitaciones conocidas."

---

## Clarifications

### Session 2026-11-04

- Q1: ¿Dónde deben alojarse el README de la Fase 1 y los metadatos dentro de la estructura del proyecto?  
  → A1: La documentación técnica exhaustiva debe publicarse en `docs/README_FASE1.md` (y referenciada en `README.md`), y los metadatos canónicos legibles por máquina deben residir en `data_processed/metadata.json`, manteniendo compatibilidad con la referencia de `IA-Nuclear`.
- Q2: ¿Qué nivel de detalle se requiere para las variables y limitaciones?  
  → A2: Se deben tabular formalmente las 12 variables de entrada del clasificador (con nombre, descripción física, unidades e indicación de normalización), las 7 variables de margen térmico (con nombre, unidades, categoría y garantía de no normalización), y el contexto de las 97 variables de PCTRAN. Las limitaciones deben detallar explícitamente: (1) NORM sin muestras de test por restricción de filas ($302 < 450$), (2) autocorrelación temporal en NORM y ATWS, (3) fuerte desbalance de clases (100 vs 1 archivo), (4) NORM con muestra única en train, y (5) alcance de 12 canales limitado a primario/neutrónico sin lado secundario.
- Q3: ¿Cómo se valida automatizadamente la documentación y los metadatos?  
  → A3: Mediante una suite de pruebas automatizadas en `tests/documentacion/` que verifique la existencia de los archivos, la validez del JSON, el cumplimiento de la estructura de metadatos, la coherencia de los conteos ($151/34/33$ en muestras de referencia o las $199$ simulaciones completas) y la presencia textual de todas las limitaciones obligatorias.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Descripción del origen de los datos y modelo de planta (Priority: P1)

Un analista de seguridad nuclear o un nuevo desarrollador del equipo consulta la documentación de la Fase 1 para comprender con precisión física y operativa el origen de los datos de simulación: software PCTRAN, desarrollo de la Universidad Tsinghua (dataset NPPAD), tipo de reactor PWR (reactor de agua a presión de 2 lazos), condición inicial al 100 % de potencia y cobertura de escenarios de transitorios accidentales.

**Why this priority**: Es la base contextual indispensable. Sin conocer la planta de referencia (PWR de 2 lazos) ni el simulador (PCTRAN / Tsinghua), cualquier hipótesis termohidráulica o evaluación de aprendizaje automático carece de fundamento físico.

**Independent Test**: Verificar que `docs/README_FASE1.md` contiene la sección dedicada de antecedentes y origen, citando el trabajo Sci Data 2022 de NPPAD, el simulador PCTRAN, el modelo PWR y las condiciones de inicialización.

**Acceptance Scenarios**:
1. **Given** un lector que abre `docs/README_FASE1.md`, **When** examina la sección de antecedentes, **Then** encuentra la atribución al dataset NPPAD (Universidad Tsinghua, Sci Data 9, 766, 2022), el simulador PCTRAN y la licencia MIT.
2. **Given** la descripción del modelo de planta, **When** se detalla el sistema nuclear, **Then** se identifica como un PWR de 2 lazos con lazo primario RCS, presurizador, generadores de vapor y sistemas ECCS (inyección de seguridad a alta/baja presión y acumuladores).

---

### User Story 2 - Catálogo y especificación de variables de planta y márgenes térmicos (Priority: P1)

Un ingeniero de Machine Learning necesita saber con exactitud cuáles variables componen el tensor de entrada de los modelos de clasificación y cuáles pertenecen a los márgenes térmicos reservados para evaluación y el HMI de operador.

**Why this priority**: Garantiza la coherencia de dimensiones y previene errores críticos como normalizar indebidamente márgenes térmicos o introducir variables espurias en el clasificador.

**Independent Test**: Comprobar que en `docs/README_FASE1.md` y `data_processed/metadata.json` están listadas exactamente las 12 variables de entrada y las 7 variables de margen térmico, con sus descripciones, unidades físicas y especificación de escalado.

**Acceptance Scenarios**:
1. **Given** la tabla de variables de entrada, **When** se verifican los nombres, **Then** figuran exactamente las 12 variables (`P`, `TAVG`, `THA`, `TCA`, `WRCA`, `WRCB`, `LVPZ`, `LVCR`, `PWNT`, `PWR`, `WECS`, `WLR`) con sus unidades físicas (bar, °C, t/hr, %, m).
2. **Given** la tabla de márgenes térmicos, **When** se verifican sus nombres, **Then** figuran exactamente las 7 variables (`DNBR`, `TPCT`, `SCMA`, `SCMB`, `TSAT`, `FRCL`, `FRZR`), categorizadas en márgenes térmicos e indicadores de daño, y con indicación expresa de que se conservan en unidades físicas reales sin normalizar.
3. **Given** el archivo `data_processed/metadata.json`, **When** se parsea con un validador JSON, **Then** las claves `selected_features` y `margin_features` coinciden exactamente con la documentación textual.

---

### User Story 3 - Conteo por clase, partición sin fuga y limitaciones conocidas (Priority: P1)

Un auditor del proyecto o un científico de datos revisa los conteos de archivos y de muestras por clase y split (`train`, `val`, `test`), la estrategia de división por corrida completa y ventaneo en archivo único, y la declaración formal de las limitaciones termohidráulicas y estadísticas del dataset.

**Why this priority**: La integridad metodológica y la honestidad técnica (Principio V de la Constitución v2.0.0) exigen documentar con transparencia el desbalance de clases, la falta de muestras de prueba en NORM y la autocorrelación en datos continuos.

**Independent Test**: Ejecutar pruebas automatizadas que contrasten `metadata.json` y `README_FASE1.md` verificando que los conteos de archivos (1 NORM, 100 LOCA, 100 LOCAC, 1 ATWS) y las limitaciones conocidas están explícitamente declarados.

**Acceptance Scenarios**:
1. **Given** la tabla de conteo de archivos, **When** se consulta el desglose base, **Then** se reportan 1 archivo de NORM, 100 de LOCA, 100 de LOCAC y 1 de ATWS (total 202 archivos en el dataset de origen).
2. **Given** la partición de muestras, **When** se examinan los splits, **Then** se detalla el reparto (70 % train, 15 % val, 15 % test) y el conteo de muestras por clase y conjunto tanto para la estrategia de simulación única por archivo como para la estrategia de ventaneo de la referencia ($151/34/33$).
3. **Given** la sección de limitaciones conocidas, **When** se inspeccionan los puntos declarados, **Then** figuran: (1) NORM sin muestras de test por longitud ($302 < 450$ filas), (2) autocorrelación temporal en NORM y ATWS, (3) fuerte desbalance entre LOCA/LOCAC y NORM/ATWS, (4) única muestra en train de NORM, y (5) restricción de entradas al lazo primario/neutrónico sin incluir variables de lado secundario ni contención.

---

### Edge Cases

- Si `data_processed/metadata.json` ya existe en el espacio de trabajo, debe validarse y complementarse sin sobreescribir inadvertidamente parámetros de escaladores reales existentes.
- Si un usuario lee `README_FASE1.md` sin acceso a los CSV originales de NPPAD, el documento debe ser autosuficiente para comprender la física, las dimensiones y las limitaciones.
- Diferencias entre la estrategia de 1 muestra por simulación (implementada en `src/preparacion_datos/`) y la estrategia de ventaneo temporal de la referencia (`IA-Nuclear` con $151/34/33$ muestras): la documentación debe explicar claramente ambas modalidades para que no haya confusión entre los integrantes del equipo.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST proveer el documento técnico `docs/README_FASE1.md` describiendo la Fase 1 del proyecto.
- **FR-002**: `docs/README_FASE1.md` MUST describir el origen de los datos: dataset NPPAD (Universidad Tsinghua, 2022), software PCTRAN, licencia MIT y antecedentes del proyecto.
- **FR-003**: `docs/README_FASE1.md` MUST describir el modelo de planta nuclear de reactor de agua a presión (PWR) de 2 lazos, potencia nominal al 100 %, y los sistemas asociados (RCS, presurizador, generadores de vapor, ECCS).
- **FR-004**: `docs/README_FASE1.md` MUST tabular las 12 variables de entrada normalizadas para los modelos Bi-LSTM, indicando acrónimo, descripción y unidad física.
- **FR-005**: `docs/README_FASE1.md` MUST tabular las 7 variables de margen térmico, indicando acrónimo, descripción, unidad física, categoría (margen térmico o daño) y confirmando que no se normalizan.
- **FR-006**: `docs/README_FASE1.md` MUST contextualizar las 19 variables frente al total de 97 parámetros registrados en las simulaciones de PCTRAN.
- **FR-007**: `docs/README_FASE1.md` MUST detallar los conteos de archivos base por clase: NORM (1), LOCA (100), LOCAC (100) y ATWS (1), explicando el mapeo de carpetas de origen (`Normal` $\to$ NORM).
- **FR-008**: `docs/README_FASE1.md` MUST documentar la partición de datos sin fuga de información (70 % train, 15 % val, 15 % test), detallando la estrategia de reparto por archivo y la de bloques temporales disjuntos.
- **FR-009**: `docs/README_FASE1.md` MUST declarar detalladamente las 6 limitaciones conocidas del dataset (NORM sin test, autocorrelación de archivo único, desbalance severo, generalización limitada de operación normal, padding y alcance de 12 canales).
- **FR-010**: El sistema MUST proveer el archivo de metadatos `data_processed/metadata.json` con formato JSON estructurado y codificación UTF-8.
- **FR-011**: `data_processed/metadata.json` MUST incluir las claves `selected_features`, `margin_features`, `margin_feature_categories`, `class_mapping`, `sequence_length`, `time_step_seconds`, `sequence_duration_seconds`, `split_ratios_target`, `file_counts`, `sample_counts`, `known_limitations` y `scaler`.
- **FR-012**: El sistema MUST actualizar el [README.md](file:///c:/Users/Administrador/Desktop/gestion/gestion_proyectos/README.md) en la raíz del repositorio, agregando un enlace y resumen de la documentación del dataset de la Fase 1.
- **FR-013**: El sistema MUST proveer una suite de pruebas automatizadas en `tests/documentacion/` que verifique la existencia, validez de formato y consistencia de los archivos de documentación y metadatos.
- **FR-014**: El sistema MUST NOT modificar el código de los paquetes existentes (`preparacion_datos`, `preparacion_pwr3l`, `clasificador_etapa1`, `clasificador_etapa2`, `regla_atws`, `tiempo_deteccion`).

### Key Entities

- **Dataset NPPAD**: Conjunto de simulaciones en CSV producido con PCTRAN por la Universidad Tsinghua para reactores PWR.
- **README_FASE1**: Documento Markdown maestro que detalla técnica, física y metodológicamente la preparación de datos de Fase 1.
- **Metadatos Canónicos (`metadata.json`)**: Diccionario JSON legible por máquina que consolida las variables, particiones, conteos y limitaciones.
- **Variables de Entrada (12)**: Sensores de planta del lazo primario y flujo neutrónico normalizados con escalador ajustado exclusivamente en entrenamiento.
- **Variables de Margen (7)**: Indicadores de estado de seguridad y degradación térmica conservados en unidades físicas directas.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docs/README_FASE1.md` existe, supera las 120 líneas de documentación técnica y cubre el 100 % de los puntos solicitados (origen, planta, 12 variables, 7 márgenes, conteos y 5+ limitaciones).
- **SC-002**: `data_processed/metadata.json` es un JSON sintácticamente válido que contiene las 12 variables de entrada, las 7 variables de margen y las limitaciones conocidas.
- **SC-003**: El 100 % de las pruebas automatizadas en `tests/documentacion/` pasa exitosamente.
- **SC-004**: Cero regresiones en la suite global del proyecto (las 434 pruebas previas continúan en verde).
- **SC-005**: El `README.md` principal contiene la sección de documentación de Fase 1 con enlaces directos.

---

## Assumptions

- El dataset de referencia de Fase 1 es NPPAD (PCTRAN, 10 s de paso de muestreo, 150 pasos = 1500 s).
- No se requiere alterar la lógica de cálculo numérico de `src/preparacion_datos/` ni reprocesar archivos de datos en disco.
- Se documentan tanto la partición estándar de `preparacion_datos` (1 muestra por simulación completa) como la de ventaneo de la referencia `IA-Nuclear` ($151/34/33$), aclarando la relación entre ambas.
