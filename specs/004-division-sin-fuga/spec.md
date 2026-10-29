# Feature Specification: División en entrenamiento, validación y prueba sin fuga de datos (PWR 3L)

**Feature Branch**: `004-division-sin-fuga`

**Created**: 2026-10-28

**Status**: Draft

**Input**: User description: "División en entrenamiento, validación y prueba sin fuga de datos para las corridas PWR 3L (tarea de Jira asignada a Abner Arboleda). El analista necesita repartir las corridas usables de PWR 3L (NORM, LOCA rama caliente, LOCAC rama fría, ATWS y TRIP_OK) en entrenamiento, validación y prueba dividiendo por corrida completa, nunca por fila. En LOCA y LOCAC, el mismo tamaño de rotura (área en cm²) debe caer en el mismo conjunto para ambas ramas: división pareada por severidad. Además, cada ATWS y su gemela TRIP_OK (mismo escenario con y sin fallo del disparo) deben ir al mismo conjunto. El reparto debe acercarse a 70/15/15 sin partir ningún grupo, ser reproducible con una semilla, y verificarse automáticamente que no hay fuga (ninguna corrida ni grupo en dos conjuntos). Las corridas cortas, descartadas y OOD no entran en ningún conjunto. Esta funcionalidad completa las tareas de agrupación y partición pendientes de la funcionalidad 002 (grupos.py y particion.py) y no construye la salida, el reporte ni el comando, que son de otra tarea."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Agrupar las corridas que no pueden separarse (Priority: P1)

Un analista toma las corridas usables de PWR 3L y obtiene grupos de corridas que deben ir siempre juntas: todas las LOCA y LOCAC con el mismo tamaño de rotura forman un grupo, cada ATWS forma un grupo con su gemela TRIP_OK, y cada corrida restante forma su propio grupo. Cada corrida usable pertenece a exactamente un grupo.

**Why this priority**: Es la base de la división sin fuga. Si una LOCA y una LOCAC con la misma rotura, o un ATWS y su gemela TRIP_OK, quedaran en grupos distintos, podrían caer en entrenamiento y en prueba, y el clasificador sería evaluado con escenarios que ya vio: las métricas saldrían infladas.

**Independent Test**: Formar los grupos con un conjunto de corridas conocido y comprobar que cada corrida está en un solo grupo, que todas las LOCA/LOCAC de una misma área comparten grupo y que cada pareja de gemelas comparte grupo.

**Acceptance Scenarios**:

1. **Given** una LOCA y una LOCAC usables con la misma área de rotura, **When** se forman los grupos, **Then** ambas quedan en el mismo grupo.
2. **Given** dos LOCA usables con la misma área de rotura (repetición dentro de una rama), **When** se forman los grupos, **Then** ambas quedan en el mismo grupo que las LOCAC de esa área.
3. **Given** un ATWS y su gemela TRIP_OK, ambos usables, **When** se forman los grupos, **Then** quedan juntos en un grupo.
4. **Given** un ATWS cuya gemela TRIP_OK no es usable (por ejemplo, es corta), **When** se forman los grupos, **Then** el ATWS forma un grupo solo y la gemela no aparece en ningún grupo.
5. **Given** una corrida NORM usable, **When** se forman los grupos, **Then** forma un grupo propio.

---

### User Story 2 - Repartir los grupos en entrenamiento, validación y prueba (Priority: P1)

El analista reparte los grupos completos en entrenamiento, validación y prueba con proporciones cercanas a 70/15/15, sin partir ningún grupo, y obtiene siempre el mismo reparto con la misma semilla.

**Why this priority**: Es el resultado que pide la tarea. Sin un reparto equilibrado, validación o prueba podrían quedar casi vacías o sin alguna familia de accidentes, y no servirían para evaluar.

**Independent Test**: Repartir un conjunto de grupos conocido y comprobar que cada grupo está en exactamente un conjunto, que los conteos por familia se acercan a 70/15/15 dentro del margen definido y que dos ejecuciones con la misma semilla dan el mismo reparto.

**Acceptance Scenarios**:

1. **Given** los grupos formados, **When** se reparten, **Then** cada grupo completo queda en exactamente un conjunto.
2. **Given** las corridas de una familia (NORM; LOCA y LOCAC; ATWS y TRIP_OK), **When** se reparten, **Then** el número de corridas de la familia en cada conjunto se aparta de su meta (70 %, 15 %, 15 %) menos que el tamaño del grupo más grande de esa familia.
3. **Given** las mismas corridas y la misma semilla, **When** se repite el reparto, aunque las corridas lleguen en otro orden, **Then** se obtiene exactamente la misma asignación.
4. **Given** una semilla distinta, **When** se reparte, **Then** la asignación puede cambiar, pero sigue cumpliendo todas las reglas anteriores.

---

### User Story 3 - Verificar automáticamente que no hay fuga (Priority: P2)

El analista dispone de una verificación automática que, dado un reparto, confirma que no hay fuga de datos o señala exactamente qué corrida o grupo la provoca.

**Why this priority**: La garantía de cero fuga es un principio no negociable del proyecto. Una verificación independiente del reparto permite detectar errores futuros (por ejemplo, si otra tarea modifica el reparto o añade corridas) en lugar de confiar en que el código de reparto es correcto.

**Independent Test**: Pasar a la verificación un reparto correcto y comprobar que no informa nada; después pasarle repartos alterados a propósito (una corrida en dos conjuntos, un área partida, una pareja de gemelas separada, una corrida excluida dentro de un conjunto) y comprobar que detecta cada caso y nombra las corridas y los conjuntos implicados.

**Acceptance Scenarios**:

1. **Given** un reparto correcto, **When** se verifica, **Then** la verificación termina sin señalar ninguna violación.
2. **Given** un reparto donde una corrida aparece en dos conjuntos, **When** se verifica, **Then** la verificación lo detecta y nombra la corrida y los dos conjuntos.
3. **Given** un reparto donde dos corridas LOCA/LOCAC de la misma área están en conjuntos distintos, **When** se verifica, **Then** la verificación lo detecta y nombra el área, las corridas y los conjuntos.
4. **Given** un reparto donde un ATWS y su gemela TRIP_OK están en conjuntos distintos, **When** se verifica, **Then** la verificación lo detecta y nombra la pareja.
5. **Given** un reparto que incluye una corrida corta, descartada u OOD, **When** se verifica, **Then** la verificación lo detecta y nombra la corrida.

---

### Edge Cases

- Un grupo más grande que la meta de validación o de prueba de su familia (en el dataset real, el área de 2000 cm² reúne 8 corridas, y la meta de validación de la familia LOCA es de unas 5 corridas): el reparto no lo parte y el desvío queda dentro del margen de FR-008.
- Una gemela cuya pareja no es usable (en el dataset real: R29, R48, R99 y R106 tienen su pareja corta): queda sola en su grupo; no hay fuga posible porque la pareja no está en ningún conjunto.
- Un área de rotura con una sola corrida usable (en el dataset real: 5, 3000, 7700 y 8500 cm²): forma un grupo de una corrida.
- Una LOCA o LOCAC usable sin área de rotura conocida: la división se detiene con un error que nombra la corrida, porque no se puede garantizar el emparejamiento.
- Una familia con menos de tres grupos: algún conjunto queda sin corridas de esa familia; el resumen de conteos lo hace visible con un cero.
- Una clase cuyas corridas son todas cortas: queda con cero corridas en los tres conjuntos.
- Ninguna corrida usable: la división se detiene con un error.
- Las corridas llegan en distinto orden: el reparto no cambia.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST incluir en la división solo las corridas usables de las cinco clases (NORM, LOCA, LOCAC, ATWS, TRIP_OK); las corridas cortas, descartadas y OOD MUST NOT aparecer en ningún conjunto.
- **FR-002**: El sistema MUST agrupar todas las corridas usables LOCA y LOCAC que tienen exactamente la misma área de rotura en un único grupo, incluidas las repeticiones dentro de una misma rama.
- **FR-003**: El sistema MUST agrupar cada ATWS con su gemela TRIP_OK, según la tabla de gemelas del proyecto, cuando ambas son usables; si solo una es usable, esa forma un grupo propio.
- **FR-004**: El sistema MUST formar un grupo propio con cada corrida usable no cubierta por FR-002 ni FR-003.
- **FR-005**: Cada corrida usable MUST pertenecer a exactamente un grupo, y cada grupo MUST tener un identificador que indique su origen (área de rotura, pareja de gemelas o corrida individual).
- **FR-006**: El sistema MUST asignar cada grupo completo a exactamente uno de los conjuntos de entrenamiento, validación o prueba; ningún grupo MUST quedar repartido entre dos conjuntos.
- **FR-007**: El sistema MUST repartir los grupos por familia (NORM; LOCA y LOCAC; ATWS y TRIP_OK) con metas de 70 %, 15 % y 15 % de las corridas usables de cada familia.
- **FR-008**: Para cada familia y conjunto, la diferencia entre el número de corridas asignadas y su meta MUST ser menor que el tamaño del grupo más grande de esa familia.
- **FR-009**: El sistema MUST producir la misma asignación con las mismas corridas y la misma semilla, sin depender del orden en que lleguen las corridas.
- **FR-010**: La semilla MUST poder elegirse; si no se indica, MUST usarse 42.
- **FR-011**: El sistema MUST ofrecer una verificación automática de un reparto que compruebe: (a) cada corrida usable está en exactamente un conjunto; (b) ningún grupo está en más de un conjunto; (c) todas las corridas LOCA/LOCAC de una misma área están en el mismo conjunto; (d) cada pareja de gemelas usables está en el mismo conjunto; (e) ninguna corrida excluida (corta, descartada u OOD) está en un conjunto. Ante cualquier violación MUST detenerse con un error que nombre las corridas, el área o la pareja y los conjuntos implicados.
- **FR-012**: El sistema MUST entregar, para uso de la tarea de salida y reporte, el conjunto asignado a cada grupo y a cada corrida, la lista ordenada de corridas de cada conjunto y los conteos de corridas por clase y conjunto, con las cinco clases presentes en los tres conjuntos aunque tengan cero.
- **FR-013**: El sistema MUST detenerse con un error que nombre la corrida cuando una corrida LOCA o LOCAC usable no tenga área de rotura, y con un error cuando no haya ninguna corrida usable.
- **FR-014**: La división MUST trabajar sobre las corridas ya leídas y MUST NOT modificar sus datos ni los archivos de origen.
- **FR-015**: [NEEDS CLARIFICATION: ¿La verificación automática de fuga debe aplicarse también al reparto NPPAD de la funcionalidad 001 (LOCA y LOCAC de igual severidad), o solo a PWR 3L?]

### Key Entities

- **Corrida usable**: una corrida PWR 3L de una de las cinco clases, leída y con al menos 300 pasos; tiene identificador, clase, área de rotura (solo LOCA y LOCAC) y, si es ATWS o TRIP_OK, una posible gemela.
- **Corrida excluida**: una corrida corta, descartada u OOD; nunca entra en un conjunto.
- **Grupo**: corridas que deben ir siempre al mismo conjunto; tiene un identificador de origen (área, pareja o corrida), una familia y una o más corridas.
- **Familia**: NORM; LOCA y LOCAC; ATWS y TRIP_OK. Cada grupo pertenece a una sola familia y las metas 70/15/15 se calculan por familia.
- **Conjunto**: entrenamiento, validación o prueba; contiene grupos completos.
- **Reparto**: la asignación de cada grupo y de cada corrida a un conjunto, con la semilla usada y los conteos por clase y conjunto.
- **Violación de fuga**: una regla de FR-011 incumplida, con las corridas y los conjuntos que la provocan.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Con las corridas reales de PWR 3L, la verificación automática informa 0 violaciones: 0 corridas en dos conjuntos, 0 grupos partidos, el 100 % de las áreas de rotura en un solo conjunto y el 100 % de las parejas de gemelas usables juntas.
- **SC-002**: En cada familia, el número de corridas de cada conjunto se aparta de su meta 70/15/15 menos que el tamaño del grupo más grande de esa familia.
- **SC-003**: Dos repartos con las mismas corridas y la misma semilla son idénticos en el 100 % de las corridas, también si las corridas llegan en otro orden.
- **SC-004**: La verificación detecta el 100 % de las fugas introducidas a propósito en las pruebas (corrida repetida, área partida, gemelas separadas, corrida excluida incluida).
- **SC-005**: 0 corridas cortas, descartadas u OOD aparecen en algún conjunto.
- **SC-006**: Con las corridas reales, cada una de las tres familias tiene al menos una corrida en cada conjunto.

## Assumptions

- Las corridas llegan ya descubiertas y leídas por la funcionalidad 002 (91 usables en el dataset real: NORM 19, LOCA 16, LOCAC 20, ATWS 18 y TRIP_OK 18), con su área de rotura y su gemela ya determinadas.
- «Mismo tamaño de rotura» significa exactamente la misma área en cm², tomada del nombre de la carpeta o de la descripción de la corrida. Áreas distintas, aunque cercanas (por ejemplo, 7700 y 8500 cm²), son grupos distintos.
- La tabla de gemelas ATWS/TRIP_OK es la del proyecto (19 parejas) y no se modifica.
- Cada corrida aporta una sola muestra, así que las proporciones 70/15/15 se cuentan en corridas.
- Con grupos de tamaño desigual no se puede cortar exactamente 70/15/15; se acepta el desvío acotado de FR-008 y se procura que los grupos grandes no desequilibren validación y prueba.
- Construir los arreglos de salida, el escalado aplicado a los conjuntos, el reporte impreso, los metadatos y el comando de PWR 3L queda fuera: pertenecen a la tarea KAN-18 (funcionalidad 002). Esta funcionalidad entrega el reparto y su verificación para que esa tarea los use.
- El proyecto de referencia agrupa solo las gemelas ATWS/TRIP_OK y deja cada LOCA y LOCAC como grupo propio; esta funcionalidad corrige esa fuga potencial entre ramas con la misma rotura.
