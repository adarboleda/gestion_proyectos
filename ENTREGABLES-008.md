# Octava iteración SDD: `008-tiempo-desde-falla`

**Tarea de Jira**: KAN-25, «Medir el tiempo de detección desde la falla»
**Responsable**: Abner Arboleda
**Rama**: `008-tiempo-desde-falla`, creada desde `main` con 001–007 fusionadas
**Fecha**: 2026-11-04
**Herramientas**: GitHub Spec Kit, Claude Code (`claude-opus-5-5`) y `speckit-metricas`
**Constitución**: v2.0.0, sin cambios

> **Estado: iteración completa y convergente** (`converged` en la 2.ª pasada).
> - Se ejecutaron todas las fases de Spec Kit: `/speckit-specify` → `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement` → `/speckit-converge` ×2. También se ejecutaron todos los comandos de métricas.
> - 31/31 tareas (86 puntos) y 61 pruebas nuevas. Suite completa con los datos reales: 405 pasadas.
> - Con los datos reales, la meta de **ATWS en ≤ 3 s se cumple (6 de 6)**. La de **diagnóstico en ≤ 10 s no se cumple (5 de 10)**: los transitorios con disparo se reconocen en 2–5 s, pero las LOCA de prueba tardan 19 s o más. Se informa tal como sale.

---

## 1. Qué pide la tarea

> Evaluación causal segundo a segundo con la regla de confianza sostenida. Contar el tiempo desde el instante de la falla (tomado del Transient Report), no desde el inicio de la ventana. Metas: diagnóstico en 10 s o menos; ATWS en 3 s o menos.

- **Qué se mide**:
  - el clasificador de Etapa 1 de 005 (familia NORM, LOCA o TRANS), confirmado con probabilidad ≥ 0,80 dos segundos seguidos;
  - la regla de ATWS de 006 (KAN-22, de Marcelo).
- **Cómo**: se reproducen las corridas de validación y de prueba **segundo a segundo**. En cada segundo solo se usan los datos recibidos hasta ese momento, como en planta. No se reentrena ni se ajusta nada.
- **Desde cuándo se cuenta el tiempo**: desde el **instante de la falla**. En 005 se medía desde el inicio que detectaba el validador.

---

## 2. De dónde sale el instante de la falla

Se revisaron los Transient Report (`*.dat`) de las 109 corridas:
- **ATWS y TRIP_OK**: el registro anota la acción que inicia la falla. Puede ser el cierre de las válvulas FWIV (pérdida de agua de alimentación), «RCP-A trip» (bomba), «Turbine Trip Control Change: True» (turbina) o la válvula de la turbina del AFW al 100 % (pérdida de energía exterior). Se toma la **primera de esas líneas con t > 0**.
- **LOCA**: el registro solo anota «Malfunction # 1» en t = 0, con un retardo que no muestra.
- **Extracción de barras**: la primera línea es «Scram High Flux», que es la consecuencia, no la causa.

**Decisiones del responsable en `/speckit-clarify`**:
1. **Cuando el registro no tiene el instante** (LOCA y otras fallas) se usa el **instante programado**: el retardo de la falla en `config.json` (sin contar la falla 8, «fallo del disparo», que siempre está en 0) o el `_t<n>` del nombre de la carpeta. Si el validador ve cambios **más de 2 s antes**, la corrida queda **«incierta»**: se informa aparte y no cuenta para la meta de diagnóstico.
2. **La meta de 3 s del ATWS se mide desde la demanda de disparo**: la señal del registro más el retardo de la lógica de protección, como en 006. Es el instante en que el reactor debía dispararse y no lo hizo. El tiempo desde la falla se informa aparte, como dato.

**Correcciones aprobadas en `/speckit-analyze`**:
- **I1**: la meta de ATWS se mide sobre validación + prueba, porque la regla no usó validación para calibrarse. La cifra solo de prueba se da aparte.
- **I2**: las inciertas se excluyen solo de la meta de diagnóstico. La de ATWS no depende del instante de la falla, así que las incluye.
- **U1**: el registro solo se busca en ATWS y TRIP_OK.
- **U2**: se informan las confusiones, es decir, cuando la primera familia confirmada tras la falla es la equivocada.

---

## 3. Lo que se hizo, fase por fase

| # | Fase | Comando | Resultado | Archivo |
|---|---|---|---|---|
| 1 | Rama | git | `008-tiempo-desde-falla` desde `main` | — |
| 2 | Especificar | `/speckit-specify` | 3 historias, 15 FR, 7 SC | [spec.md](specs/008-tiempo-desde-falla/spec.md) |
| 3 | Aclarar | `/speckit-clarify` | 2 preguntas respondidas por el responsable (sección 2); checklist 16/16 | spec.md, [checklists/](specs/008-tiempo-desde-falla/checklists/requirements.md) |
| 4 | Planificar | `/speckit-plan` | Constitution Check con todo en «cumple»; decisiones medidas sobre los datos reales; modelo de datos, 2 contratos y quickstart | [plan.md](specs/008-tiempo-desde-falla/plan.md), [research.md](specs/008-tiempo-desde-falla/research.md), [data-model.md](specs/008-tiempo-desde-falla/data-model.md), [contracts/](specs/008-tiempo-desde-falla/contracts/) |
| 5 | Tareas | `/speckit-tasks` + `puntos` | 26 tareas, con las pruebas primero; **73 puntos** | [tasks.md](specs/008-tiempo-desde-falla/tasks.md), [puntos-tarea.csv](specs/008-tiempo-desde-falla/puntos-tarea.csv) |
| 6 | Analizar | `/speckit-analyze` | 6 hallazgos (**0 críticos**, 2 altos, 2 medios y 2 bajos); los 4 altos y medios se aplicaron con aprobación | [analisis-inicial.md](specs/008-tiempo-desde-falla/analisis-inicial.md) |
| 7 | Implementar | `/speckit-implement` | 26/26 tareas; paquete `tiempo_deteccion` y comando `medir-tiempo-deteccion` | `src/tiempo_deteccion/`, `tests/tiempo/` |
| 8 | Converge (1.ª) | `/speckit-converge` | 5 hallazgos, convertidos en T027–T031 (+13 puntos) | [auditoria.md](specs/008-tiempo-desde-falla/auditoria.md) |
| 9 | Converge (2.ª) | `/speckit-converge` | **`converged`**, 0 hallazgos | — |

---

## 4. Qué se construyó

| Módulo (`src/tiempo_deteccion/`) | Qué hace | Líneas |
|---|---|---|
| `config.py` | Metas (10 s y 3 s), tolerancia de 2 s, patrones del iniciador y aviso consultivo | 34 |
| `falla.py` | Instante de la falla: registro (ATWS/TRIP_OK) → `config.json` → carpeta; marca las inciertas | 106 |
| `reproduccion.py` | Verifica que el modelo de 005 corresponda al reparto; probabilidades segundo a segundo con ventana causal; confirmación sostenida | 70 |
| `atws.py` | Regla de 006 calibrada con entrenamiento; tiempo desde la demanda y desde la falla; falsas alarmas | 48 |
| `evaluacion.py` | Tiempos de diagnóstico, comparación con el validador, falsas alarmas, confusiones, metas, archivos y reporte | 451 |
| `cli.py` | `medir-tiempo-deteccion`: orquestación y publicación de todos los archivos o de ninguno | 123 |

El comando escribe en `resultados_tiempo_deteccion/`, que no se versiona y se regenera con el comando:
- `tiempos.json`;
- `tiempos.csv`: una fila por corrida;
- `lineas_tiempo.csv`: una fila por corrida y segundo;
- `reporte.txt`.

---

## 5. Resultados con los datos reales (`D:\Personal\IANuclear\PWR 3L`)

**Ejecución**: 56 s. Dos ejecuciones dieron los cuatro archivos idénticos. Con otra semilla, el comando se detiene porque el modelo no corresponde al reparto.

### Instante de la falla

- **72 corridas de evento**: 29 con el instante del registro y 43 con el programado (26 de `config.json` y 17 de la carpeta).
- **5 inciertas**, ninguna en prueba:
  - **R22**: las FWIV se cierran a 47,5 s, pero la planta cambia desde 13 s.
  - **R47, R48, R54 y R99**: falla 9; PCTran no respetó el retardo programado y la planta cambia desde 1 s.

### Diagnóstico ≤ 10 s desde la falla (prueba)

| Corrida | Clase | Área | Falla (s) | Fuente | Desde la falla | Desde el validador (005) |
|---|---|---|---|---|---|---|
| R95, R103 | ATWS, TRIP_OK | — | 50 | registro | **2 s** | 2 s |
| R96, R104 | ATWS, TRIP_OK | — | 26 | registro | **3 s** | 3 s |
| R29 | ATWS | — | 2 | registro | **5 s** | 4 s |
| R44, R83 | LOCA, LOCAC | 100 cm² | 50 / 35 | programado | 19 s | 19 s |
| R19, R88 | LOCAC | 10 cm² | 30 / 45 | programado | 121 / 120 s | 120 / 120 s |
| R46 | LOCAC | 5 cm² | 40 | programado | no detectado | no detectado |

- **TRANS: 5 de 5 en ≤ 10 s** (mediana 3 s).
- **LOCA: 0 de 5**.
- Validación, como referencia: las LOCA grandes (3 000–8 500 cm²) tardan 10–16 s y las de 20 cm² 55–56 s; TRANS, 4 de 4 en 3 s.

### ATWS ≤ 3 s desde la demanda

- **6 de 6 en validación + prueba** (solo prueba: 3 de 3), en 2–2,5 s.
- Desde la falla, como dato: 5 s en R25, R49, R95 y R96. En R29 son 35 s, porque la demanda de disparo llega 33 s después del iniciador.

### Falsas alarmas

- **Prueba**: 0 de la Etapa 1 y 0 de la regla.
- **Validación**: 1 de la regla (R54, la misma que informó 006).
- **Confusiones**: ninguna.

### Metas

| Meta | Definición | Resultado | Estado |
|---|---|---|---|
| Diagnóstico ≤ 10 s | familia confirmada en ≤ 10 s desde la falla en el 100 % de las corridas de evento de prueba no inciertas | 5 de 10 (50 %) | **No cumple** |
| ATWS ≤ 3 s | ATWS reconocido en ≤ 3 s desde la demanda en el 100 % de los ATWS de validación y prueba | 6 de 6 (100 %) | **Cumple** |
| SC-004 (sin falsas alarmas en prueba) | 0 de la Etapa 1 en corridas NORM, y 0 «posible ATWS» sin ATWS | 0 y 0 | Cumple |
| SC-005 (reproducible) | dos ejecuciones idénticas | idénticas | Cumple |
| SC-006 (< 5 min) | evaluación completa en CPU | 56 s | Cumple |

**Lectura honesta**:
- Medir desde la falla cambia poco en prueba: entre −1 y 0 s frente a 005, porque ahí el validador y la falla casi coinciden. Donde sí cambia es en las corridas de falla 9 y en R22, que ahora se marcan como inciertas en vez de dar tiempos engañosos.
- La regla de ATWS cumple su meta.
- El diagnóstico rápido cumple en los transitorios con disparo, pero no en las LOCA de 100 cm² o menos. Es la misma limitación que mostró 005.
- No se ajustó nada mirando la prueba.
- Con 13 corridas de prueba, las cifras tienen mucha incertidumbre.

---

## 6. Métricas (`speckit-metricas`)

### 6.1 Sesiones

| Sesión | Fase | Inicio–Fin | Horas | Commits | Código | Pruebas |
|---|---|---|---|---|---|---|
| `20261104-1614-especificar` | especificar | 16:14–16:16 | 0,25 | 1 | 0 | 0 |
| `20261104-1616-aclarar` | aclarar | 16:16–16:18 | 0,25 | 1 | 0 | 0 |
| `20261104-1618-planificar` | planificar | 16:18–16:20 | 0,25 | 1 | 0 | 0 |
| `20261104-1620-tareas` | tareas | 16:20–16:24 | 0,25 | 1 | 0 | 0 |
| `20261104-1624-analizar` | analizar | 16:24–16:30 | 0,25 | 2 | 0 | 0 |
| `20261104-1630-implementar` | implementar | 16:30–16:58 | 0,5 | 9 | +839 / −7 | +797 / −0 |
| `20261104-1659-analizar` | converge (1.ª) | 16:59–17:00 | 0,25 | 1 | 0 | 0 |
| `20261104-1700-implementar` | implementar (convergencia) | 17:00–17:05 | 0,25 | 3 | +18 / −8 | +38 / −2 |
| `20261104-1705-analizar` | converge (2.ª) | 17:05–17:06 | 0,25 | 0 | 0 | 0 |
| **Total** | **9 sesiones** | **16:14–17:06** | **2,5** | **19** | **+857 / −15** | **+835 / −2** |

⚠ Las horas son el mínimo por sesión que registra la extensión (0,25 h), no un cronómetro: el reloj marca unos 52 minutos de trabajo del agente.
- No está registrada la exploración previa de los Transient Report, hecha en la sesión de especificación para decidir de dónde sale el instante de la falla.
- No se informaron tokens ni costo.

### 6.2 Tamaño y desperdicio (`recolectar`)

| Indicador | 008 |
|---|---|
| Historias / FR / SC | 3 / 15 / 7 |
| Tareas | **31 / 31** |
| Puntos de tarea | **86** (73 del plan y 13 de convergencia) |
| Código agregado / que sobrevive | **857 / 842** |
| Pruebas agregadas | +835 (61 pruebas) |
| Desperdicio | **15 líneas (1,75 %)**, todas reescrituras por requisito. 7 figuran «sin clasificar» porque al commit 2363b19 le faltó el trailer; ver la [auditoría](specs/008-tiempo-desde-falla/auditoria.md) |
| Esfuerzo | 2,5 h = 0,0164 persona-mes |
| Modelo de IA | `claude-opus-5-5` |

Proyecto completo (000–008): 4 601 líneas entregadas, 0,097 persona-mes.

### 6.3 Calibración, estimación y exportación

- **`calibrar`** con 7 funcionalidades: el modelo sigue siendo exploratorio. La mejor medida es ahora **puntos de tarea** (MMRE 0,10, PRED(25) 0,86 y MMRE en validación cruzada 0,14). COCOMO II estándar no sirve a esta escala (MMRE 113).
- **`estimar`** para 008: 2,3 h por requisitos (15), 2,1 h por puntos del plan (73; rango 1,7–2,5 h) y 2,4 h por KSLOC (0,857), frente a 2,5 h reales. Las tres quedan un 4–16 % por debajo. 008 está incluida en la calibración, así que la comparación no es independiente.
- **`exportar`**: `metricas/salidas/dataset-IANuclear-20261104.zip`, sin anonimizar (el mismo criterio que en 004 y 005).

---

## 7. Historial de commits (rama `008-tiempo-desde-falla`)

| Commit | Mensaje |
|---|---|
| `50d938f` | docs(008): especificación del tiempo de detección desde la falla (KAN-25) |
| `c7ee0ae` | docs(008): aclaraciones de la especificación |
| `f20a298` | docs(008): plan, decisiones, modelo de datos y contratos |
| `91d7fb1` | docs(008): tareas, puntos de tarea y registro de sesión |
| `a8c5062` / `51f9247` | docs(008): análisis inicial de consistencia / correcciones del análisis |
| `6eab831` | feat(008): paquete tiempo_deteccion, guion medir-tiempo-deteccion y constantes |
| `acaf6dd` / `6871d74` | test / feat(008): instante de la falla desde el Transient Report (US1) |
| `4e41a72` / `59d14e8` | test / feat(008): reproducción causal, ATWS, tiempos, metas y comando (US2) |
| `e8f98f1` / `2363b19` | test / feat(008): comparación con el validador y líneas de tiempo (US3) |
| `5e5b477` | test(008): medición con el dataset real de PWR 3L |
| `2adf55d` | docs(008): README, resultados con los datos reales y tareas completadas |
| `fd20869` | docs(008): tareas de convergencia T027–T031 y sus puntos |
| `494529f` / `117aac9` | test / feat(008): diferencia validador−falla, CSV consultivos y motivo de la regla |
| `62fe1bf` | docs(008): causa de las eliminaciones de 2363b19, modelo de datos y contrato |
| `2b21ba4`, `5021b4c` | docs(008): registros de sesión |
| *(último)* | docs(008): auditoría y documento de entregables |

---

## 8. Carpetas

```
specs/008-tiempo-desde-falla/      spec, plan, research, data-model, contracts/ (cli, salidas), quickstart,
                                   tasks, puntos-tarea.csv, analisis-inicial, auditoria, checklists/
src/tiempo_deteccion/              config, falla, reproduccion, atws, evaluacion, cli
tests/tiempo/                      conftest y ayudas_tiempo (árbol de fallas y modelo de 005 sintéticos)
                                   · unit/ (falla, reproduccion, atws, evaluacion) · integration/ (cli, real)
resultados_tiempo_deteccion/       (no se versiona) tiempos.json, tiempos.csv, lineas_tiempo.csv, reporte.txt
metricas/sesiones/                 20261104-1614 … 1705 (9 sesiones)
```

---

## 9. Cómo verificarlo

```powershell
# Requisito: el modelo de Etapa 1 publicado por 005 (≈ 17 s)
.venv\Scripts\entrenar-etapa1.exe --origen "D:\Personal\IANuclear\PWR 3L" --salida modelos\etapa1

# Medir (≈ 1 min): imprime el reporte y deja los cuatro archivos en resultados_tiempo_deteccion\
.venv\Scripts\medir-tiempo-deteccion.exe --origen "D:\Personal\IANuclear\PWR 3L" --modelo modelos\etapa1

# Pruebas
$env:IANUCLEAR_DATOS = "D:\Personal\IANuclear"
.venv\Scripts\python.exe -m pytest tests/tiempo -q      # 61 pruebas
.venv\Scripts\python.exe -m pytest -q                   # suite completa: 405 passed (8 min)
```

---

## 10. Pendientes

| Pendiente | Detalle |
|---|---|
| Detección temprana de LOCA | Es lo que impide la meta de 10 s: LOCA de ≤ 100 cm² en 19 s o más. Mejoras de 005: elegir el modelo por el F1 de los primeros segundos, ventana más corta o atención, variables de tendencia; siempre evaluadas con validación |
| Falsa alarma R54 de la regla (006) | Disparo por turbina sin ejemplo de ese retardo en entrenamiento |
| Corridas de falla 9 | PCTran no respetó el retardo programado: conviene regenerarlas o excluirlas del dataset |
| Informe del Hito 1 (007, KAN-27) | Puede leer `tiempos.json` para las cifras medidas desde la falla |
