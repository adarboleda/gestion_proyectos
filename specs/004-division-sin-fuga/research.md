# Research: División sin fuga de datos (PWR 3L)

Decisiones técnicas de la funcionalidad 004. Parte de `specs/002-preprocesamiento-pwr3l/research.md` §7 y §8 y de la medición del dataset real con la lectura de 002 (91 corridas usables).

## 1. Grupos de corridas emparejadas

- **Decisión**: `formar_grupos(corridas)` toma todas las corridas, se queda con las de estado `usable` y clase de entrenamiento, y forma: (a) un grupo `AREA-<cm2>` por cada área de rotura con todas las LOCA y LOCAC usables de esa área; (b) un grupo `GEMELAS-<a>-<b>` por cada pareja de gemelas con las dos corridas usables (`<a>` y `<b>` en orden natural de identificador); (c) un grupo `<Rid>` por cada corrida restante. Los grupos se devuelven ordenados por familia y clave.
- **Razón**: FR-002 a FR-005. El área y la gemela ya las fija el descubrimiento de 002 (`Corrida.area`, `Corrida.gemela`), así que agrupar no vuelve a leer nombres ni `config.json`.
- **Igualdad de área**: exacta, en cm² enteros (supuesto de la spec). 7700 y 8500 cm² son grupos distintos.
- **Gemela no usable**: la otra queda como grupo individual (`<Rid>`), no como `GEMELAS`. En el dataset real pasa con R29, R48, R99 y R106.
- **Errores**: LOCA/LOCAC usable sin área → `ErrorDatos(archivo, "corrida LOCA sin área de rotura")` (FR-013); ninguna corrida usable → `ValueError`.
- **Alternativas**: agrupar por rangos de área (no lo pide la tarea y mezclaría severidades distintas); agrupar también NORM parecidas (sin criterio objetivo; queda como limitación D1 de 002).

## 2. Familias y metas

- **Decisión**: familias NORM; LOCA (LOCA + LOCAC); ATWS (ATWS + TRIP_OK), según `config.FAMILIAS`. Metas por familia: `0.70·n`, `0.15·n` y `0.15·n` corridas, en coma flotante (sin redondear).
- **Razón**: FR-007. Un grupo nunca mezcla familias: un `AREA` solo tiene LOCA/LOCAC y un `GEMELAS` solo ATWS/TRIP_OK.

## 3. Orden de reparto y regla de déficit

- **Decisión**: un solo generador `numpy.random.default_rng(semilla)`; para cada familia en orden fijo (NORM, LOCA, ATWS), los grupos ordenados por clave reciben una posición de sorteo con `permutation`, y se reparten por tamaño descendente con la posición de sorteo como desempate. Cada grupo va al conjunto con mayor déficit (`meta − asignado`), con desempate train → val → test.
- **Razón**: FR-007, FR-009 y la segunda aclaración. Repartir primero los grupos grandes los manda donde hay más hueco (normalmente entrenamiento), y los pequeños ajustan validación y prueba.
- **Garantía (FR-008)**: mientras quedan grupos, la suma de déficits es positiva, así que el conjunto elegido tiene déficit `d > 0`. (1) Exceso: tras asignar un grupo de tamaño `g`, el exceso de ese conjunto es `g − d < g ≤ g_max`. (2) Defecto: si al final un conjunto `s` tuviera déficit `D ≥ g_max`, todo conjunto `t` con exceso lo recibió cuando su déficit era mayor o igual que el de `s` en ese momento (que era ≥ D), y su exceso sería `≤ g − D ≤ 0`; contradicción. Por tanto `|asignado − meta| < g_max` en cada conjunto. Las pruebas lo comprueban con repartos aleatorios.
- **Independencia del orden de entrada**: los grupos se ordenan por clave antes del sorteo y las corridas de cada conjunto se ordenan con `descubrimiento.clave_orden`.
- **Alternativas**: orden sorteado puro (002 §8; con el grupo de 8 corridas de 2000 cm² puede llevar validación a 9 corridas frente a una meta de 5,4); mandar a entrenamiento todo grupo mayor que la meta de validación (esa área nunca se evaluaría); `GroupShuffleSplit` (no estratifica ni acota el desvío).

## 4. Verificación independiente de fuga (PWR 3L)

- **Decisión**: `verificar_reparto(corridas, reparto)` recibe todas las corridas (también las excluidas) y comprueba, a partir de los atributos de cada corrida y no de los grupos: (a) cada corrida usable está en exactamente un conjunto; (b) cada grupo del reparto tiene todas sus corridas en un mismo conjunto; (c) todas las LOCA/LOCAC usables de un área comparten conjunto; (d) cada pareja de gemelas usables comparte conjunto; (e) ninguna corrida corta, descartada u OOD está en un conjunto. Junta todas las violaciones y lanza `ErrorFuga` con una línea por violación.
- **Razón**: FR-011. Al no depender de `formar_grupos`, también detecta un error de agrupación. Juntar todas las violaciones da un diagnóstico completo de una vez.
- **Uso**: `repartir` llama a `verificar_reparto` antes de devolver el reparto, así que un reparto con fuga nunca sale del módulo.

## 5. Verificación del reparto NPPAD (001)

- **Decisión**: `preparacion_datos/verificacion.py` con `verificar_particion(particion)`: cada simulación (identificada por su archivo relativo) en exactamente un conjunto, y todas las LOCA/LOCAC de una misma severidad en el mismo conjunto. `cli.main` la ejecuta justo después de `repartir`; una violación termina con código 1 y el mensaje en la salida de error, sin publicar artefactos.
- **Razón**: FR-015 y la primera aclaración. No se toca `particion.py` de 001: el reparto y los artefactos siguen siendo los mismos.
- **Alternativas**: una verificación genérica compartida por las dos plantas (cruzaría los paquetes, decisión 1 de 002).

## 6. Rutas de los datasets reales en las pruebas

- **Decisión**: un módulo `tests/datos_reales.py` resuelve la raíz de IA-Nuclear con la variable de entorno `IANUCLEAR_DATOS` y, si no está, `../IA-Nuclear` respecto de la raíz del repositorio. Las pruebas reales nuevas se omiten si la carpeta no existe.
- **Razón**: en cada máquina del equipo el dataset está en un lugar distinto (en esta, `C:\Users\User\Desktop\IANuclear`). Las pruebas reales existentes de 001 no se cambian.

## 7. Qué queda para KAN-18

- **Decisión**: esta funcionalidad no construye arreglos, no escala conjuntos, no escribe archivos ni imprime reportes. Entrega `Reparto` (contracts/api.md) para que `salida.py`, `reporte.py` y `cli.py` de 002 lo usen.
- **Razón**: la tarea de Jira pide la división; el resto pertenece a KAN-18 (002, tareas T019–T030). El escalado PWR 3L ya lo implementó 003.
