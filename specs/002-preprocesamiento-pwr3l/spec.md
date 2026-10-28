# Feature Specification: Preprocesamiento PWR 3L en ventanas de 300 s y cinco clases

**Feature Branch**: `002-preprocesamiento-pwr3l`

**Created**: 2026-10-28

**Status**: Draft

**Jira**: KAN-18 «Adaptar el preprocesamiento a ventanas de 300 s y cinco clases» (responsable: Marcelo Acuña)

**Input**: User description: "Preparar los datos de las 106 simulaciones PWR 3L (1 dato por segundo) que están en `PWR 3L` (carpetas `ATWS`, `LOCA COLD`, `LOCA HOT`, `LOCA PORV`, `NORM`, `TRIP_OK` y `auto\R*_<CLASE>`, cada corrida con su archivo de datos de planta), en muestras de 300 pasos de 1 s con cinco clases: NORM, LOCA, LOCAC, ATWS y TRIP_OK. Las corridas OOD (eventos desconocidos) no son una clase de entrenamiento. Es una planta distinta de NPPAD (2705 MWt) y no debe mezclarse con ella."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Conjuntos de 300 s y cinco clases sin fuga (Priority: P1)

Un analista toma las corridas PWR 3L de las cinco clases de entrenamiento (operación normal NORM, LOCA de rama caliente, LOCA de rama fría LOCAC, ATWS y transitorio con disparo correcto del reactor TRIP_OK) y obtiene conjuntos de entrenamiento, validación y prueba en los que ninguna corrida ni ningún par de corridas emparejadas queda repartido entre dos conjuntos. Cada muestra es una secuencia de 300 pasos de 1 s (los primeros 300 s de su corrida), con las variables medibles en sala de control escaladas usando solo entrenamiento.

**Why this priority**: Es el núcleo de la tarea KAN-18. Sin conjuntos sin fuga, cualquier clasificador posterior del canal rápido mostraría métricas infladas; además, LOCA y LOCAC deben quedar como clases separadas y TRIP_OK debe existir como clase para distinguir un disparo correcto de un ATWS.

**Independent Test**: Ejecutar la preparación y comprobar automáticamente que (a) los identificadores de corrida de dos conjuntos cualesquiera no se cruzan, (b) las corridas emparejadas comparten conjunto, (c) cada muestra tiene 300 pasos y (d) los parámetros de escala coinciden con los calculados solo sobre entrenamiento.

**Acceptance Scenarios**:

1. **Given** las corridas de las cinco clases, **When** se preparan los conjuntos, **Then** cada corrida usable aporta exactamente una muestra de 300 pasos con su etiqueta (NORM, LOCA, LOCAC, ATWS o TRIP_OK) y cae en un solo conjunto.
2. **Given** una corrida ATWS y su gemela TRIP_OK (mismo escenario, con y sin fallo del disparo), **When** se asignan a los conjuntos, **Then** ambas van al mismo conjunto.
3. **Given** corridas de LOCA y de LOCAC de igual severidad, **When** se asignan a los conjuntos, **Then** van todas al mismo conjunto.
4. **Given** los conjuntos formados, **When** se escalan las variables de entrada, **Then** los parámetros de escala se calculan solo con entrenamiento y se guardan para aplicarlos sin recalcular.
5. **Given** la misma configuración y los mismos datos, **When** se repite la preparación, **Then** se obtienen exactamente la misma asignación y los mismos valores.

---

### User Story 2 - Márgenes térmicos conservados aparte y sin escalar (Priority: P2)

Para cada muestra, el analista dispone de las 7 variables de margen térmico (DNBR, temperatura pico de vaina, dos márgenes de subenfriamiento, temperatura de saturación y dos fracciones de daño) en sus unidades originales, alineadas paso a paso con las variables de entrada de esa misma muestra.

**Why this priority**: Sirven de referencia para evaluar el margen térmico y no son entradas medibles. Deben quedar intactas, pero los conjuntos pueden probarse sin ellas.

**Independent Test**: Para una muestra elegida, comparar sus 7 márgenes con los del archivo de origen en las mismas filas y comprobar que son idénticos.

**Acceptance Scenarios**:

1. **Given** una muestra de 300 pasos, **When** se consultan sus márgenes, **Then** hay 7 valores por paso, en las mismas posiciones temporales que las entradas, sin escalar.
2. **Given** los conjuntos escalados, **When** se revisan los márgenes, **Then** ninguno forma parte de las entradas ni de los parámetros de escala.

---

### User Story 3 - Reporte de conteos, corridas excluidas y limitaciones (Priority: P2)

El analista recibe un reporte con las muestras por clase y por conjunto, las corridas y grupos de cada conjunto, todas las corridas que no aportaron muestra con su motivo (fuera de distribución, descartadas por el equipo o demasiado cortas) y las limitaciones conocidas.

**Why this priority**: El dataset PWR 3L es pequeño (unas 20 corridas por clase); el analista necesita ver exactamente qué entró, qué no y por qué para juzgar las métricas posteriores.

**Independent Test**: Generar el reporte y verificar que cada corrida encontrada aparece en exactamente una categoría (en un conjunto, fuera de distribución, descartada o corta) y que los totales cuadran.

**Acceptance Scenarios**:

1. **Given** la preparación terminada, **When** se lee el reporte, **Then** muestra una tabla de muestras por clase y conjunto con las cinco clases en los tres conjuntos, incluso con cero, y totales que cuadran.
2. **Given** corridas que no aportan muestra, **When** se lee el reporte, **Then** cada una aparece nombrada con su motivo.
3. **Given** una clase sin muestras en algún conjunto, **When** se genera el reporte, **Then** esa celda aparece con cero y una advertencia visible.

---

### Edge Cases

- Una corrida con menos de 300 pasos (el simulador terminó antes): [NEEDS CLARIFICATION: ¿se detiene la preparación nombrando el archivo, se excluye la corrida con aviso o se completan los pasos que faltan?]
- Corridas fuera de distribución (OOD, p. ej. PORV trabada, rotura de tubos del generador de vapor, rotura de línea de vapor): no son una clase de entrenamiento; no aportan muestras y se listan en el reporte.
- Corridas que el equipo ya descartó (R07, contaminada y repetida como R07b; R27 y R28, intentos de mitigación y boración): no aportan muestras y se listan con su motivo.
- Una carpeta manual con dos archivos de datos (R27: tramo fallido y tramo de mitigación) o una carpeta sin archivo de datos.
- Un archivo con variables requeridas ausentes, valores no numéricos, faltantes o no finitos, o con un tiempo que no avanza de 1 s en 1 s desde 0: la preparación se detiene con un error que nombra el archivo y la causa.
- Dos carpetas con el mismo identificador de corrida, o una carpeta automática con una clase desconocida.
- Corridas emparejadas en las que una de las dos no aporta muestra: la otra se asigna sola, sin romper la regla de no compartir conjunto.
- LOCA y LOCAC de la misma severidad: [NEEDS CLARIFICATION: ¿qué significa «igual severidad» en PWR 3L, donde las corridas no están numeradas por severidad como en NPPAD?]
- Una variable de entrada sin variación en entrenamiento: se informa en lugar de producir valores no válidos.
- Los formatos de archivo difieren entre corridas manuales (libros de Excel con extensión `.xls`, o texto separado por comas) y automáticas (texto separado por comas).
- Re-ejecución sobre una salida previa: mismo resultado, sin restos de ejecuciones anteriores.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST descubrir las corridas de las carpetas de clase manuales (`ATWS`, `LOCA COLD`, `LOCA HOT`, `LOCA PORV`, `NORM`, `TRIP_OK`) y de la carpeta `auto` (`R<n>_<CLASE>`), leer sus datos de planta en los dos formatos presentes y MUST NOT modificar ningún archivo de origen.
- **FR-002**: El sistema MUST asignar la clase por la carpeta: `NORM`→NORM, `LOCA HOT`→LOCA, `LOCA COLD`→LOCAC, `ATWS`→ATWS, `TRIP_OK`→TRIP_OK, `LOCA PORV`→OOD y, en `auto`, el sufijo del nombre; con las etiquetas NORM = 0, LOCA = 1, LOCAC = 2, ATWS = 3 y TRIP_OK = 4. LOCA y LOCAC MUST quedar como clases separadas.
- **FR-003**: Las corridas OOD MUST NOT aportar muestras a ningún conjunto y MUST listarse en el reporte.
- **FR-004**: Las corridas descartadas por el equipo (R07, R27 y R28) MUST NOT aportar muestras, MUST listarse en el reporte con su motivo y la lista MUST estar documentada.
- **FR-005**: El sistema MUST producir exactamente una muestra por corrida usable, formada por sus primeros 300 pasos consecutivos de 1 s (de 0 s a 299 s), con su etiqueta y el identificador de la corrida.
- **FR-006**: Ante una corrida de clase de entrenamiento con menos de 300 pasos, el sistema MUST [NEEDS CLARIFICATION: detenerse, excluirla con aviso o completarla].
- **FR-007**: El sistema MUST asignar cada corrida usable completa a exactamente uno de los conjuntos de entrenamiento, validación o prueba, con un reparto cercano a 70 % / 15 % / 15 % y una semilla fija.
- **FR-008**: El sistema MUST asignar al mismo conjunto las corridas emparejadas: cada ATWS con su gemela TRIP_OK, y las corridas de LOCA y LOCAC de igual severidad.
- **FR-009**: El sistema MUST usar como entrada de cada muestra solo variables medibles en sala de control (presión, temperaturas, caudales y niveles del primario y del secundario, flujo neutrónico, inyección y carga, y presión, temperatura y radiación de contención) y MUST NOT usar el caudal de fuga ni otras variables no medibles.
- **FR-010**: El sistema MUST calcular los parámetros de escala de las variables de entrada solo con entrenamiento, aplicarlos a los tres conjuntos y persistirlos.
- **FR-011**: El sistema MUST conservar para cada muestra las 7 variables de margen térmico en sus unidades originales, sin escalar y alineadas paso a paso con las entradas.
- **FR-012**: El sistema MUST emitir un reporte con las muestras por clase y conjunto, las corridas y grupos de cada conjunto, todas las corridas sin muestra con su motivo y las limitaciones conocidas.
- **FR-013**: El reporte MUST advertir de forma visible toda clase sin muestras en un conjunto y toda corrida de clase de entrenamiento que no aporte muestra.
- **FR-014**: El sistema MUST detenerse con un error que nombre el archivo y la causa, sin escribir ningún conjunto, cuando falten variables requeridas, haya valores no numéricos, faltantes o no finitos, el tiempo no avance de 1 s en 1 s desde 0, una carpeta no tenga exactamente un archivo de datos, la clase sea desconocida o un identificador de corrida se repita; MUST NOT rellenar valores en silencio.
- **FR-015**: El sistema MUST producir el mismo resultado al repetir la preparación con los mismos datos y la misma configuración.
- **FR-016**: El sistema MUST regenerar todos los resultados con una sola ejecución documentada, en una salida propia, separada de la de NPPAD; los artefactos generados MUST NOT editarse a mano.

### Key Entities

- **Corrida**: una simulación PWR 3L de unos 300 s con una fila por segundo; tiene identificador (`R<n>`, p. ej. `R07b`), clase, origen (manual o automática), archivo de datos y, cuando aplica, gemela o severidad.
- **Muestra**: los primeros 300 pasos de una corrida usable, con las variables de entrada escaladas, los márgenes térmicos, la etiqueta y el identificador de la corrida.
- **Variables de entrada**: las 26 variables medibles en sala de control (P, TAVG, THA, THB, TCA, TCB, WRCA, WRCB, LVPZ, LVCR, PWNT, PSGA, PSGB, NSGA, NSGB, WFWA, WFWB, WSTA, WSTB, TBLD, WHPI, WCHG, WECS, PRB, TRB, RM1).
- **Márgenes térmicos**: DNBR, TPCT, SCMA, SCMB, TSAT, FRCL y FRZR, sin escalar y no usados como entrada.
- **Grupo**: conjunto de corridas emparejadas que deben ir juntas (gemelas ATWS/TRIP_OK; LOCA y LOCAC de igual severidad); una corrida sin pareja forma su propio grupo.
- **Conjunto**: entrenamiento, validación o prueba; contiene grupos completos.
- **Corrida excluida**: corrida encontrada que no aporta muestra, con su motivo (OOD, descartada o corta).
- **Reporte de preparación**: conteos, corridas y grupos por conjunto, corridas excluidas, advertencias y limitaciones.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de las corridas usables aparece en exactamente un conjunto y la verificación automática de intersección entre conjuntos da cero coincidencias, también a nivel de grupo.
- **SC-002**: El 100 % de los pares de corridas emparejadas que aportan muestra comparten conjunto.
- **SC-003**: Los parámetros de escala coinciden con los calculados solo sobre entrenamiento, y cambiar los datos de validación o prueba no altera ninguno.
- **SC-004**: Los 7 márgenes de una muestra coinciden en el 100 % de los valores con los del archivo de origen.
- **SC-005**: El 100 % de las corridas encontradas aparece en exactamente una categoría del reporte (conjunto, OOD, descartada o corta), y la suma de muestras por clase y conjunto es igual al total de muestras.
- **SC-006**: Dos ejecuciones con los mismos datos y configuración producen conjuntos y reporte idénticos.
- **SC-007**: Los archivos de origen quedan sin cambios tras la preparación, comprobado comparando su contenido antes y después.
- **SC-008**: El analista obtiene los conjuntos y el reporte con una sola ejecución documentada, sin pasos manuales.

## Assumptions

- La carpeta `PWR 3L` está disponible localmente. Contiene 109 carpetas de corrida: 35 manuales y 74 automáticas; R27 tiene dos archivos de datos. Sin las 3 descartadas quedan 106 corridas: 20 por cada una de las cinco clases y 6 OOD (R20, R64, R65, R66, R107 y R108).
- Las carpetas cuyo nombre empieza por `_` (calibración, pruebas de fallas y respaldos) no son datos del plan y se ignoran, igual que los archivos sueltos de la raíz.
- Las corridas duran unos 300 s; los primeros 300 pasos cubren el tramo previo al evento, el evento y la respuesta del sistema de protección, que es lo que necesita el canal rápido.
- La etiqueta es una por muestra (la clase de la corrida), aunque en las corridas de accidente los primeros segundos son operación normal; el etiquetado paso a paso queda para la iteración del clasificador.
- Las gemelas ATWS/TRIP_OK son las del plan de corridas del proyecto (R21–R59, R22–R60, R23–R61, R24–R62, R29–R63, R26–R53 y las automáticas R47–R54 … R98–R106).
- El estado «REVISAR» que asigna el validador de corridas del proyecto (evento antes de lo planeado, poco tramo previo) no impide usar la corrida; el estado «REPETIR» solo lo tenía R07, que ya está descartada.
- Se propone un reparto 70 % / 15 % / 15 % por grupos con semilla fija; con unas 20 corridas por clase, validación y prueba tendrán solo unas 3 por clase.
- Construir el clasificador queda fuera de esta funcionalidad, igual que las transformaciones de las entradas (cambios respecto al estado inicial, ruido de sensores).
