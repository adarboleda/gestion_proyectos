# Entregables de la primera iteración SDD — `001-preparacion-datos`

**Proyecto**: IANuclear — sistema consultivo de apoyo al operador para detectar accidentes LOCA y ATWS en reactores PWR con datos simulados.
**Iteración documentada**: `001-preparacion-datos` — preparación de los datos de simulación NPPAD sin fuga de información.
**Metodología**: Desarrollo Guiado por Especificaciones (SDD) con [GitHub Spec Kit](https://github.com/github/spec-kit) y Claude Code.
**Fecha de la revisión**: 2026-10-20 · **Rama**: `001-preparacion-datos`

Este documento explica, para cada uno de los seis entregables pedidos, qué es, qué comando lo genera, dónde está, qué contiene en este proyecto, cómo se produjo y cómo se verifica. Al final hay un resumen de estado y las limitaciones que se conocen.

---

## 1. Qué es SDD y cómo se encadenan los entregables

En SDD **primero se define qué se quiere y por qué, después cómo, y al final se programa**. Cada fase produce un documento que alimenta la siguiente:

```
constitución → especificación → aclaración → plan → tareas → análisis → implementación → convergencia
 (reglas)         (qué y por qué)  (dudas)    (cómo) (lista)  (revisar)    (código)        (auditar)
```

| # | Entregable pedido | Comando | Archivo principal |
|---|---|---|---|
| 1 | Documento de constitución | `/speckit-constitution` | `.specify/memory/constitution.md` |
| 2 | Documento de especificación | `/speckit-specify` (+ `/speckit-clarify`) | `specs/001-preparacion-datos/spec.md` |
| 3 | Documento de planificación | `/speckit-plan` | `specs/001-preparacion-datos/plan.md` |
| 4 | Documento de tareas | `/speckit-tasks` | `specs/001-preparacion-datos/tasks.md` |
| 5 | Implementación de una iteración | `/speckit-implement` | `src/preparacion_datos/` y `tests/` |
| 6 | Documento de auditoría | `/speckit-analyze` + `/speckit-converge` | `specs/001-preparacion-datos/auditoria.md` |

Además, la extensión `speckit-metricas` registró el tiempo y el código de cada fase (sección 8).

> **Nota sobre el sexto entregable.** El enunciado lo llama «Speckit-coverage». Ese nombre no es un comando de Spec Kit. Lo que audita la cobertura son `/speckit-analyze` (cobertura de requisitos por tareas, antes de implementar) y `/speckit-converge` (cobertura de la spec por el código, después de implementar). El documento de auditoría de este proyecto reúne ambos.

---

## 2. Documento de constitución (`/speckit-constitution`)

**Archivo**: [.specify/memory/constitution.md](.specify/memory/constitution.md) — versión **2.0.0**, ratificada el 2026-10-20.

### Qué es
La constitución es el conjunto de **reglas permanentes del proyecto**. No describe una funcionalidad concreta: fija los principios que toda especificación, plan y tarea debe respetar. Es la autoridad más alta: si una tarea la contradice, el análisis lo marca como crítico.

### Qué contiene

| Sección | Contenido |
|---|---|
| **Principio I — IA estrictamente consultiva** (no negociable) | La IA solo aconseja; no actúa sobre la planta ni sustituye la protección existente. Toda salida se presenta como recomendación. |
| **Principio II — Cero fuga de datos** (no negociable) | Particiones por simulación completa, nunca por fila; simulaciones emparejadas en el mismo grupo; escaladores ajustados solo con entrenamiento; nada posterior al instante `t`. |
| **Principio III — Honestidad y reproducibilidad** | Se reporta lo que salió, incluidos los resultados negativos; toda meta con su definición exacta; todo resultado se regenera con un comando; los artefactos generados no se editan a mano. |
| **Principio IV — Procedencia de datos** | El dataset original no se modifica; no se mezclan plantas distintas (NPPAD y PWR 3L). |
| **Principio V — Alcance acotado a LOCA y ATWS** | Otros accidentes, ciberataques y datos de planta real quedan fuera salvo enmienda. |
| **Restricciones adicionales** | Python; código en `src/`, pruebas en `tests/`; documentación en español. |
| **Flujo de desarrollo** | Ciclo Spec Kit completo; pruebas automáticas antes de dar una tarea por terminada; commits `feat(NNN): descripción` con trailer `Causa: requisito\|defecto\|refactor` cuando se elimina o reescribe código; cada fase registrada con la extensión de métricas. |
| **Governance** | La constitución prevalece sobre otras prácticas; enmiendas con versión semántica (MAJOR/MINOR/PATCH); los principios I y II no admiten excepciones; cada `plan.md` debe incluir un *Constitution Check*. |

### Cómo se produjo
Se partió de la plantilla vacía de Spec Kit y se ejecutó `/speckit-constitution` con las reglas del proyecto. Se archivó una versión anterior escrita a mano en `specs-referencia/constitution-anterior.md`, que no forma parte de la entrega.

### Cómo se usa en esta iteración
El `plan.md` contiene una tabla *Constitution Check* que evalúa cada principio contra el diseño (los cinco dan «cumple»; el I es «no aplica» porque esta funcionalidad no emite diagnósticos). El análisis inicial y la auditoría también contrastan contra la constitución: **no se encontraron conflictos**.

---

## 3. Documento de especificación (`/speckit-specify` y `/speckit-clarify`)

**Archivo**: [specs/001-preparacion-datos/spec.md](specs/001-preparacion-datos/spec.md) · **Checklist**: [checklists/requirements.md](specs/001-preparacion-datos/checklists/requirements.md)

### Qué es
La especificación describe **qué** debe hacer la funcionalidad y **por qué**, sin hablar de tecnología. Está escrita para que la entienda alguien que no programa y es el contrato contra el que se mide todo lo demás.

### Qué contiene

**Funcionalidad especificada**: un analista necesita preparar los datos de simulación de accidentes del dataset NPPAD (Universidad Tsinghua, simulador PCTRAN) para entrenar y evaluar después un clasificador. Las clases son operación normal, LOCA de rama caliente, LOCA de rama fría (LOCAC) y ATWS.

| Parte | Contenido |
|---|---|
| **3 historias de usuario** | **US1 (P1)** conjuntos de entrenamiento/validación/prueba sin fuga, con 12 variables escaladas solo con entrenamiento. **US2 (P2)** 7 variables de margen térmico conservadas aparte, sin escalar y alineadas. **US3 (P2)** reporte de conteos por clase y conjunto con las limitaciones. |
| **9 escenarios de aceptación** | Formato *Given / When / Then*, 4 en US1, 2 en US2 y 3 en US3. |
| **7 casos límite** | Normal y ATWS con una sola simulación; simulación con menos de 150 pasos; archivo con variables ausentes o valores no numéricos; variable con desviación cero; LOCA y LOCAC sin pareja; desbalance de clases; re-ejecución sobre una salida previa. |
| **13 requisitos funcionales (FR-001…FR-013)** | Por ejemplo FR-003 (cada simulación en un solo conjunto), FR-004 (LOCA y LOCAC de igual severidad juntas), FR-006 (escalado solo con entrenamiento), FR-007 (Normal y ATWS completas a entrenamiento), FR-012 (archivo defectuoso detiene la preparación). |
| **8 criterios de éxito (SC-001…SC-008)** | Medibles y sin tecnología: 100 % de las simulaciones en exactamente un conjunto, parámetros de escala idénticos a los calculados solo con entrenamiento, márgenes idénticos al CSV, reporte con totales que cuadran, ejecuciones idénticas, origen sin cambios. |
| **Entidades clave** | Simulación, Muestra, Variables de planta (12), Márgenes térmicos (7), Conjunto, Parámetros de escala, Reporte de preparación. |
| **Supuestos** | Reparto 70/15/15 con semilla fija; los primeros 150 pasos bastan; Normal y ATWS no tendrán métricas sobre datos no vistos. |

### Cómo se produjo
1. `/speckit-specify` generó la spec desde una descripción en lenguaje natural, sin tecnología. Dejó **un** marcador `[NEEDS CLARIFICATION]` (FR-007).
2. `/speckit-clarify` hizo **3 preguntas** y se respondió **A** en todas. Quedaron registradas en la sección *Clarifications*:

| Pregunta | Decisión | Por qué |
|---|---|---|
| ¿Cómo se tratan las clases con una sola simulación? | Van completas a entrenamiento; sin validación ni prueba; el reporte lo advierte. | Cumple «una simulación nunca en dos conjuntos» y el principio II. Partirlas daría métricas infladas. |
| ¿Cómo se extraen las muestras de 150 pasos? | Una muestra por simulación: los primeros 150 pasos. | El propósito es la detección temprana. Con ventanas adicionales (se midió: 212 de LOCA y 251 de LOCAC) se mezclan regímenes distintos y se desbalancean las clases. |
| ¿Qué pasa con un archivo defectuoso? | Detener con un error que nombre el archivo y la causa; no escribir ningún conjunto. | Excluir en silencio cambiaría los conteos sin que el analista lo note. |

3. El checklist de calidad pasó a 16/16 (sin marcadores pendientes, requisitos testeables, criterios medibles y sin detalles de implementación).

### Cómo se verifica
Abrir `spec.md` y comprobar que cada requisito tiene al menos una tarea y una prueba (tabla de cobertura en la auditoría, sección 7).

---

## 4. Documento de planificación (`/speckit-plan`)

**Archivo**: [specs/001-preparacion-datos/plan.md](specs/001-preparacion-datos/plan.md), con los documentos de apoyo `research.md`, `data-model.md`, `quickstart.md` y `contracts/` en la misma carpeta.

### Qué es
El plan define **cómo** se construye lo que la spec describe: tecnologías, estructura del código, decisiones de diseño y contratos. Aquí sí se habla de tecnología.

### Qué contiene

| Archivo | Contenido |
|---|---|
| **plan.md** | Resumen; contexto técnico (Python ≥ 3.11, pandas, numpy, scikit-learn, pytest, Windows 11); **Constitution Check** (tabla de cumplimiento de cada principio); estructura de documentos y de código; *Complexity Tracking* (sin violaciones). |
| **research.md** | 12 decisiones con su justificación (ver abajo). |
| **data-model.md** | Entidades con campos y formas (`X` de `(N,150,12)` float32, `y` int64, `margins` de `(N,150,7)`), relaciones, reglas de validación y transiciones. |
| **contracts/cli.md** | Contrato de la línea de órdenes: invocación `preparar-datos` / `python -m preparacion_datos`, opciones (`--origen`, `--salida`, `--semilla`, `--referencia`, `--sin-referencia`), códigos de salida y formato del reporte (8 secciones). |
| **contracts/salidas.md** | Contrato de los 12 artefactos de `data_processed/` y de `metadata.json`. |
| **quickstart.md** | Guía de instalación, ejecución y las validaciones que prueban que funciona. |

**Estructura de código planificada**: `src/preparacion_datos/` con un módulo por responsabilidad (`config`, `lectura`, `particion`, `escalado`, `salida`, `reporte`, `cli`), pruebas en `tests/unit/` y `tests/integration/`, y la salida generada en `data_processed/`.

**Decisiones de diseño principales (`research.md`)**:
- **LOCA y LOCAC comparten asignación por severidad.** Se reparten las 100 severidades una sola vez (70/15/15, semilla 42) y se aplica a ambas clases; cada clase conserva sus conteos 70/15/15 y se respeta la regla de no compartir conjunto. *El plan pedido decía «se reparten por separado», lo que contradecía el FR-004 y el principio II; el plan lo detectó y lo resolvió, y lo declara en una nota.*
- Normal y ATWS completas a entrenamiento.
- Validación del archivo completo antes de escribir cualquier cosa.
- Escalado con `StandardScaler` ajustado solo con entrenamiento.
- Publicación de los artefactos «todos o ninguno».
- Comparación opcional con la referencia del proyecto previo (solo LOCA y LOCAC).

### Cómo se produjo
`/speckit-plan` con las tecnologías y los conteos esperados (142 / 30 / 30). Se evaluó la constitución antes y después del diseño.

---

## 5. Documento de tareas (`/speckit-tasks`)

**Archivo**: [specs/001-preparacion-datos/tasks.md](specs/001-preparacion-datos/tasks.md) · **Puntos de tarea**: `specs/001-preparacion-datos/puntos-tarea.csv`

### Qué es
Es la lista ordenada de trabajo, derivada del plan y la spec. Cada tarea es lo bastante concreta para ejecutarse sin más contexto, con su ruta de archivo.

### Qué contiene
- **Formato estricto**: `- [X] T### [P] [US#] descripción con ruta`. `[P]` marca tareas paralelizables; `[US#]` las asocia a una historia.
- **39 tareas en 7 fases**:

| Fase | Tareas | Contenido |
|---|---|---|
| 1 Setup | T001–T004 | `pyproject.toml`, estructura del paquete, `data_processed/` en `.gitignore`, instalación en modo editable |
| 2 Foundational | T005–T009 | Dataset sintético de pruebas, pruebas de lectura primero, configuración y lectura/validación de CSV |
| 3 US1 (MVP) | T010–T018 | Pruebas de partición, escalado y comando (que deben fallar primero); luego `particion`, `escalado`, `salida` y `cli` |
| 4 US2 | T019–T022 | Pruebas de márgenes sin escalar y alineados; ampliación de `salida` |
| 5 US3 | T023–T029 | Pruebas del reporte; `reporte.py`, `metadata.json`, opciones de referencia y código de salida 2 |
| 6 Polish | T030–T034 | Prueba contra el dataset real, sección del README, revisión del principio IV (origen solo lectura), validaciones del quickstart y suite completa |
| 7 Convergence | T035–T039 | Añadidas por `/speckit-converge` tras implementar |

- **Pruebas primero**: en cada historia, las pruebas se escriben y se comprueba que fallan antes de implementar (lo exige la constitución).
- 13 tareas paralelizables; dependencias entre fases, estrategia MVP (solo la US1) y entrega incremental.
- Las 5 tareas de la fase 7 llevan una referencia a qué parte de la spec o del plan cubren y su tipo (`partial`, `unrequested`).

### Cómo se produjo
`/speckit-tasks` con la instrucción de incluir pruebas para la no-fuga, el escalado, el archivo defectuoso y Normal/ATWS solo en entrenamiento. Al terminar, el hook `after_tasks` fijó la línea base de **82 puntos de tarea**.

---

## 6. Implementación de una iteración (`/speckit-implement`)

**Código**: [src/preparacion_datos/](src/preparacion_datos/) · **Pruebas**: [tests/](tests/) · **Configuración**: [pyproject.toml](pyproject.toml)

### Qué es
La ejecución real de las tareas: se escribe el código y las pruebas que satisfacen la spec.

### Qué se construyó
Un comando, `preparar-datos` (o `python -m preparacion_datos`), que:
1. Lee las **202 simulaciones** NPPAD (1 Normal, 100 LOCA, 100 LOCAC, 1 ATWS) en solo lectura y valida **cada archivo completo**: falta de variables, valores no numéricos o faltantes, menos de 150 pasos.
2. Toma los primeros 150 pasos de cada una como una muestra.
3. Reparte las simulaciones completas en entrenamiento, validación y prueba (70/15/15, semilla 42), con LOCA y LOCAC de igual severidad en el mismo conjunto, y Normal y ATWS completas a entrenamiento.
4. Escala las 12 variables de planta con un escalador ajustado solo con entrenamiento y conserva sin escalar las 7 variables de margen térmico.
5. Escribe los 12 artefactos en `data_processed/` (publicación «todos o ninguno») y un `metadata.json`.
6. Imprime un reporte de 8 secciones con conteos, simulaciones por conjunto, advertencias y limitaciones.

| Módulo | Responsabilidad | Líneas |
|---|---|---|
| `config.py` | Clases, variables, 150 pasos, proporciones, semilla | 29 |
| `lectura.py` | Descubrir simulaciones, leer y validar CSV | 120 |
| `particion.py` | Reparto por simulación completa | 56 |
| `escalado.py` | Escalado solo con entrenamiento | 40 |
| `salida.py` | Armado de arreglos y publicación de artefactos | 120 |
| `reporte.py` | Reporte impreso y comparación con la referencia | 166 |
| `cli.py`, `__main__.py` | Argumentos, orquestación y códigos de salida | 76 + 7 |

### Resultado con el dataset real
- **142** muestras de entrenamiento (70 LOCA, 70 LOCAC, 1 Normal, 1 ATWS), **30** de validación y **30** de prueba.
- La comparación con la referencia del proyecto previo da **COINCIDE** para LOCA y LOCAC.
- Los 202 archivos pasan la validación completa; el origen queda sin cambios.
- Un CSV al que se le quita `DNBR` hace terminar el comando con código 1, nombra el archivo y no crea la salida.
- **79 pruebas, todas verdes** (verificado de nuevo en esta revisión: `79 passed in 152.77s`), incluida una contra el dataset real.

### Cómo se produjo y su historial
`/speckit-implement` ejecutó las 34 tareas originales; las 5 de convergencia (T035–T039) se implementaron después. El historial de commits de la funcionalidad:

| Commit | Contenido |
|---|---|
| `4fee101` | `docs(001)`: constitución, spec, plan, tareas, análisis y configuración de métricas |
| `1b67f1e` | `feat(001)`: lectura y validación de las simulaciones |
| `c20d17a` | `feat(001)`: partición por simulación y escalado solo con entrenamiento |
| `5ef3383` | `feat(001)`: salida, reporte y comando `preparar-datos` |
| `96ca897`, `ec7ae0c`, `23e6580` | `feat(001)`: publicación todos o ninguno, nombres libres para Normal y ATWS, validación del archivo completo (tareas de convergencia; con `Causa: defecto`) |
| `1620545`, `eaf0627` | `test(001)`: prueba de `python -m`, salida tolerante a consolas limitadas |
| `5a828a3`, `1ea8c82`, `28d41d8`, `42e1baa` | `docs(001)`: registros de sesión, tareas completadas y auditoría |

### Cómo se verifica
```bash
pip install -e ".[dev]"
python -m pytest -q                 # 79 pruebas (≈ 2 min 30 s; incluye el dataset real)
preparar-datos                      # genera data_processed/ y imprime el reporte (≈ 12 s)
```

---

## 7. Documento de auditoría (`/speckit-analyze` + `/speckit-converge`)

**Archivos**: [auditoria.md](specs/001-preparacion-datos/auditoria.md) (documento principal) y [analisis-inicial.md](specs/001-preparacion-datos/analisis-inicial.md) (informe del `analyze`).

### Qué es
La auditoría comprueba que lo especificado, lo planificado y lo construido **coinciden**. Se hace en dos momentos:
- **Antes de implementar** (`/speckit-analyze`, solo lectura): busca duplicaciones, ambigüedades, huecos de cobertura e incoherencias entre `spec.md`, `plan.md` y `tasks.md`, y los contrasta con la constitución.
- **Después de implementar** (`/speckit-converge`): compara el código con la spec y el plan y **añade a `tasks.md` lo que falte o sobre**, hasta que no encuentre diferencias.

### Qué contiene `auditoria.md`

| Sección | Contenido |
|---|---|
| 1 Resumen | Cifras globales del análisis y la convergencia |
| 2 Cobertura de requisitos | Tabla de los 13 FR y 8 SC con sus tareas y las pruebas que los verifican (79 en total, por archivo) |
| 3 Hallazgos del análisis inicial | Los 9 hallazgos y cómo se resolvió cada uno |
| 4 Decisiones sin aprobación explícita | Qué se aplicó sin consultar y qué se hizo distinto de lo propuesto |
| 5 Hallazgos de converge | Las dos pasadas, con tarea y commit |
| 6 Resolución de las tareas de convergencia | Cómo se resolvió T035–T039 |
| 7 Estado final de tareas | 39/39 por fase |
| 8 Pendientes y aceptados | Lo que queda abierto |

### Resultados de la auditoría
- **Análisis inicial**: 9 hallazgos, **0 críticos** (3 medios, 6 bajos), cobertura 100 % de requisitos, sin conflictos con la constitución.
- **Converge, 1.ª pasada**: 5 hallazgos (1 medio, 4 bajos) → se añadieron las tareas T035–T039 y se implementaron:

| Hallazgo | Qué se detectó | Resolución |
|---|---|---|
| F1 (medio) | La publicación archivo por archivo podía dejar la salida mezclada si fallaba a mitad | Publicación con respaldo y restauración (T035) |
| F2 | La lectura exigía nombre numérico también a Normal y ATWS | Solo se exige a LOCA y LOCAC (T036) |
| F3 | `python -m preparacion_datos` sin prueba | Prueba con `subprocess` (T037) |
| F4 | Tolerancia de consola sin justificar | Justificada en `research.md` §12 y probada (T038) |
| F5 | Solo se validaban las primeras 150 filas, la spec pedía el archivo completo | Validación del archivo completo (T039) |

- **Converge, 2.ª pasada**: **«converged»**, 0 hallazgos y `tasks.md` sin cambios.
- **Estado final**: 39/39 tareas, 79 pruebas verdes.

La auditoría es honesta con lo que no salió limpio: registra que varias correcciones del análisis (U1, I1, C1, C2, A1, I2, U2) se **aplicaron durante la implementación sin aprobación explícita**, y que I1 y C1 se resolvieron de forma distinta a la propuesta.

---

## 8. Medición de tiempo y esfuerzo (`speckit-metricas`)

**Archivos**: `metricas/` (configuración, un archivo por sesión en `metricas/sesiones/`, resúmenes en `metricas/salidas/`).

La extensión registra, mediante *hooks* de Spec Kit, una sesión por fase (modelo de IA, horas, líneas de código generadas y eliminadas).

| Medida | Valor |
|---|---|
| Esfuerzo total | **2.75 h** (0.0181 persona-mes) |
| Calendario | 3 días (2026-10-18 a 10-20) |
| Código entregado | 629 líneas agregadas, 14 eliminadas, **615 sobrevivientes** |
| Pruebas | +1005 / −3 líneas |
| Desperdicio | 14 líneas, todas por defecto; **tasa 2.23 %** |
| Commits | 12 en la funcionalidad |
| Modelo de IA | `claude-sonnet-5-5` (10 sesiones) |
| Puntos de tarea | 96 (82 del plan + 14 añadidos por converge) |

| Fase | Horas |
|---|---|
| Constitución | 0.50 |
| Especificar | 0.25 |
| Aclarar | 0.25 |
| Planificar | 0.25 |
| Tareas | 0.25 |
| Analizar | 0.50 |
| Implementar | 0.75 |

Estas horas son **estimaciones automáticas** de Claude Code, no un cronómetro. No se informaron tokens ni costo de IA, y la tarifa por hora humana está en 0, por eso el costo sale en 0.

---

## 9. Estado de los entregables

| Entregable | Estado | Evidencia |
|---|---|---|
| Constitución | Completo | v2.0.0, 5 principios, sin placeholders |
| Especificación | Completo | 3 historias, 13 FR, 8 SC, 3 aclaraciones, checklist 16/16 |
| Planificación | Completo | `plan.md`, `research.md` (12 decisiones), `data-model.md`, 2 contratos, `quickstart.md` |
| Tareas | Completo | 39/39 completadas, pruebas primero |
| Implementación | Completo | Comando funcional, 79 pruebas verdes, dataset real validado |
| Auditoría | Completo, con matices | `analyze` + 2 pasadas de `converge`; ver sección 10 |

---

## 10. Limitaciones y detalles que conviene conocer

**Pendientes menores (no cambian el resultado)**
1. **La sección 8 de `auditoria.md` está desactualizada en dos puntos**: dice que la sesión de métricas de implementación sigue abierta (ya se cerró) y que las tareas de convergencia no están en `puntos-tarea.csv` (esto último sí sigue siendo cierto: falta ejecutar `/speckit-metricas-puntos`; hoy esos 14 puntos están clasificados por heurística).
2. `spec.md` conserva el campo `Status: Draft`.
3. El checklist `requirements.md` conserva una nota obsoleta («Pendiente: FR-007») que ya se resolvió.
4. `plan.md` no lista `tests/unit/test_salida.py` en el árbol de pruebas, y `contracts/cli.md` enumera menos causas de error de las que el código produce.
5. Algunas frases de `tasks.md` y del quickstart siguen diciendo «cercana a 0/1» aunque las pruebas usan tolerancias numéricas explícitas (1e-5).

**Limitaciones de método**
- **Solo se ejecutó un `/speckit-analyze`, antes de implementar.** La verificación posterior la hicieron las dos pasadas de `converge`; no se repitió el `analyze`.
- **Los commits de código se hicieron por tramos después de implementar en bloque** (los cuatro primeros llevan la misma hora). Los defectos corregidos antes del primer commit no figuran como desperdicio, así que la tasa de 2.23 % es probablemente optimista.
- **Las horas no incluyen un material anterior** escrito a mano para las seis funcionalidades de todo el proyecto IANuclear. Ese material está archivado en `specs-referencia/` y **no forma parte de esta entrega**.

**Limitaciones del producto (declaradas en la propia spec y el reporte)**
- Normal y ATWS tienen **una sola simulación cada una** y van a entrenamiento: no tendrán métricas sobre datos no vistos. Cualquier conclusión sobre esas clases queda sin verificar.
- Esta iteración solo prepara datos; **no entrena ningún clasificador**. Las fases de diagnóstico, margen térmico, recomendación de procedimientos y compuertas de seguridad quedan para iteraciones siguientes.

---

## 11. Mapa de archivos

```
gestion_proyectos/
├── ENTREGABLES.md                       ← este documento
├── README.md                            guía de uso de Spec Kit y del comando preparar-datos
├── .specify/
│   ├── memory/constitution.md           ← 1. Constitución
│   ├── templates/, scripts/             plantillas y scripts de Spec Kit
│   └── extensions/metricas/             extensión de métricas
├── specs/001-preparacion-datos/
│   ├── spec.md                          ← 2. Especificación
│   ├── checklists/requirements.md       calidad de la especificación
│   ├── plan.md                          ← 3. Planificación
│   ├── research.md, data-model.md, quickstart.md, contracts/
│   ├── tasks.md                         ← 4. Tareas
│   ├── puntos-tarea.csv                 puntos de tarea (métricas)
│   ├── analisis-inicial.md              informe de /speckit-analyze
│   └── auditoria.md                     ← 6. Auditoría
├── src/preparacion_datos/               ← 5. Implementación
├── tests/                               ← 5. Pruebas (79)
├── pyproject.toml                       paquete e instalación
├── data_processed/                      salida generada (no se versiona)
├── metricas/                            sesiones y resúmenes de tiempo
└── specs-referencia/                    material previo archivado (no es entrega)
```
