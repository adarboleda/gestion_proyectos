# Cuarta iteración SDD: `004-division-sin-fuga`

**Tarea de Jira**: «División en entrenamiento, validación y prueba sin fuga de datos» · **Responsable**: Abner Arboleda
**Rama**: `004-division-sin-fuga` (creada desde `main` con 001, 002 y 003 fusionadas) · **Fecha**: 2026-10-28
**Herramienta**: GitHub Spec Kit + Claude Code (`claude-opus-5-5`) + `speckit-metricas` · **Constitución**: v2.0.0, sin cambios

> **Estado: iteración completa y convergente (`converged`).** Se ejecutaron todas las fases de Spec Kit (`/speckit-specify` → `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement` → `/speckit-converge`) y todos los comandos de métricas (`sesion`, `cerrar`, `puntos`, `recolectar`, `calibrar`, `estimar`, `exportar`). Las 25 tareas (54 puntos) están hechas, las 44 pruebas nuevas pasan y la suite completa con los datos reales da 210 pasadas y 1 omitida.

---

## 1. Qué pide la tarea y cuál es su alcance

> Dividir por simulación completa. En LOCA y LOCAC, el mismo tamaño de rotura debe caer en el mismo conjunto para ambas ramas (división pareada por severidad).

- **NPPAD** ya cumplía esto desde 001: el reparto de severidades se hace una sola vez y se aplica a LOCA y LOCAC.
- **PWR 3L** no lo tenía. En la iteración 002 (KAN-18), la agrupación y el reparto eran las tareas T012, T013, T016 y T017, y quedaron sin hacer. La iteración 003 las dejó explícitamente para otros integrantes.

Por eso esta iteración:

1. **Construye la división sin fuga de PWR 3L**:
   - `grupos.py`: LOCA y LOCAC de igual área de rotura juntas, y cada ATWS con su gemela TRIP_OK.
   - `particion.py`: reparto 70/15/15 por familia sin partir grupos.
   - `verificacion.py`: comprobación independiente de que no hay fuga.
2. **Añade la misma verificación a NPPAD** sin cambiar su reparto. Lo decidió el responsable en `/speckit-clarify`.
3. **No construye** la salida, el reporte ni el comando de PWR 3L, que siguen en KAN-18. Tampoco toca el escalado, que ya hizo 003.

---

## 2. Lo que se midió en los datos reales (`C:\Users\User\Desktop\IANuclear`)

| Hecho | Detalle |
|---|---|
| 109 corridas PWR 3L | 91 usables (NORM 19, LOCA 16, LOCAC 20, ATWS 18, TRIP_OK 18), 9 cortas, 3 descartadas y 6 OOD |
| 14 áreas de rotura LOCA/LOCAC | De 2 a 8500 cm². La de **2000 cm² reúne 8 corridas** (3 LOCA y 5 LOCAC); 4 áreas tienen una sola corrida (5, 3000, 7700 y 8500 cm²) |
| 15 parejas de gemelas completas | Otras 4 gemelas quedan solas porque su pareja es corta: R29 (R63), R48 (R55), R99 (R91) y R106 (R98) |
| **Fuga en el proyecto de referencia** | `split_groups` de IA-Nuclear (`pwr3l_rapid_detector.py`) agrupa solo las gemelas: cada LOCA y cada LOCAC es su propio grupo. Replicado con estas 91 corridas y su semilla 42, deja **6 de las 10 áreas con más de una corrida partidas entre entrenamiento y prueba** (2, 50, 200, 500, 2000 y 4000 cm²). Con otras semillas son entre 4 y 6 |

---

## 3. Lo que se hizo, fase por fase

| # | Fase | Comando | Resultado | Archivo |
|---|---|---|---|---|
| 1 | Rama | git | `004-division-sin-fuga` desde `main`. La extensión git de Spec Kit no está instalada | — |
| 2 | Especificar | `/speckit-specify` | 3 historias, 15 FR, 6 SC y 1 duda marcada (alcance NPPAD); checklist 15/16 | [spec.md](specs/004-division-sin-fuga/spec.md) |
| 3 | Aclarar | `/speckit-clarify` | 2 preguntas **respondidas por el responsable** (sección 4); +1 SC; checklist 16/16 | spec.md, [checklists/requirements.md](specs/004-division-sin-fuga/checklists/requirements.md) |
| 4 | Planificar | `/speckit-plan` | *Constitution Check* con todo en «cumple», 7 decisiones (incluida la prueba de la cota del desvío), modelo de datos, contrato y quickstart | [plan.md](specs/004-division-sin-fuga/plan.md), [research.md](specs/004-division-sin-fuga/research.md), [data-model.md](specs/004-division-sin-fuga/data-model.md), [contracts/api.md](specs/004-division-sin-fuga/contracts/api.md), [quickstart.md](specs/004-division-sin-fuga/quickstart.md) |
| 5 | Tareas | `/speckit-tasks` + `/speckit-metricas-puntos` | 25 tareas en 6 fases, pruebas primero; **54 puntos de tarea**, las 25 clasificadas a mano | [tasks.md](specs/004-division-sin-fuga/tasks.md), [puntos-tarea.csv](specs/004-division-sin-fuga/puntos-tarea.csv) |
| 6 | Analizar | `/speckit-analyze` | 7 hallazgos: **0 críticos**, 1 medio y 6 bajos; cobertura del 100 %. El responsable aprobó 5 correcciones, aplicadas en un commit aparte | [analisis-inicial.md](specs/004-division-sin-fuga/analisis-inicial.md) |
| 7 | Implementar | `/speckit-implement` | 25/25 tareas; 4 módulos nuevos y 1 cambio en `preparar-datos`; 44 pruebas nuevas | `src/preparacion_pwr3l/`, `src/preparacion_datos/`, `tests/` |
| 8 | Converge | `/speckit-converge` | **`converged`** en la primera pasada: 0 hallazgos, `tasks.md` sin cambios | [auditoria.md](specs/004-division-sin-fuga/auditoria.md) |

### Hallazgos del análisis y cómo se resolvieron

| ID | Severidad | Problema | Solución aplicada (`a149615`) |
|---|---|---|---|
| U1 | Media | `repartir` solo conoce las corridas usables, así que no puede detectar una excluida dentro de un conjunto | El contrato exige que KAN-18 llame a `verificar_reparto(corridas, reparto)` con **todas** las corridas; la prueba real lo hace con las 109 |
| C1 | Baja | El objetivo de rendimiento no se medía | La prueba real mide el tiempo (0,0015 s; objetivo: menos de 1 s) |
| C2 | Baja | Faltaban casos de familia con menos de 3 grupos y de clase sin corridas usables | Dos pruebas nuevas |
| C3 | Baja | No se probaba que agrupar y repartir no modifican las corridas | Dos pruebas nuevas |
| T1 | Baja | «Severidad» significaba dos cosas | En PWR 3L es el área en cm²; en NPPAD, el número de severidad del archivo |
| D1, I1 | Baja | SC-002 repite FR-008; 002 sigue mostrando T012/T013/T016/T017 sin marcar | Sin cambio (aceptados) |

---

## 4. Decisiones clave (para explicar)

1. **«Mismo tamaño de rotura» = misma área exacta en cm².** Todas las LOCA y LOCAC usables con la misma área forman un grupo `AREA-<cm2>`, también las repeticiones dentro de una rama. 7700 y 8500 cm² son grupos distintos.
2. **Las gemelas ATWS/TRIP_OK van juntas** (`GEMELAS-<a>-<b>`). Si la pareja es corta, la otra queda sola: no hay fuga posible porque la corta no está en ningún conjunto.
3. **Reparto por familia, de mayor a menor tamaño** (respuesta del responsable en `/speckit-clarify`). Las familias son NORM, LOCA+LOCAC y ATWS+TRIP_OK. Cada grupo va al conjunto con más déficit respecto de 70/15/15, y los empates se sortean con la semilla 42. El grupo de 8 corridas va primero y cae en entrenamiento.
4. **Desvío acotado y demostrado.** En cada familia y conjunto, `|asignadas − meta| <` tamaño del grupo más grande (research §3). Se comprueba con 200 repartos aleatorios y con los datos reales.
5. **Verificación independiente.** `verificar_reparto` revisa el reparto a partir de los atributos de cada corrida (estado, área, gemela) y no de los grupos, así que también detecta un error al agrupar. `repartir` la ejecuta antes de devolver: nunca sale un reparto con fuga.
6. **NPPAD también se verifica** (respuesta del responsable). `preparar-datos` llama a `verificar_particion` después de repartir. Si hubiera fuga, termina con código 1 y el mensaje `FUGA DE DATOS`, sin publicar nada. El reparto de 001 no cambia.
7. **Rutas de datos reales configurables.** Las pruebas nuevas usan la variable `IANUCLEAR_DATOS`, porque el dataset está en un lugar distinto en cada máquina del equipo.

---

## 5. Resultado con los datos reales

### PWR 3L

| Familia | Entrenamiento (meta) | Validación (meta) | Prueba (meta) | Grupo mayor |
|---|---|---|---|---|
| NORM (19) | 13 (13,3) | 3 (2,85) | 3 (2,85) | 1 |
| LOCA + LOCAC (36) | 25 (25,2) | 6 (5,4) | 5 (5,4) | 8 |
| ATWS + TRIP_OK (36) | 25 (25,2) | 6 (5,4) | 5 (5,4) | 2 |
| **Total (91)** | **63** | **15** | **13** | |

- **Por clase** (entrenamiento / validación / prueba): NORM 13/3/3 · LOCA 11/4/1 · LOCAC 14/2/4 · ATWS 12/3/3 · TRIP_OK 13/3/2.
- **Áreas:** las 14 en un solo conjunto. Por ejemplo, 2000 cm² en entrenamiento, 20 cm² en validación, y 10 y 100 cm² en prueba.
- **Gemelas:** las 15 parejas juntas (11 en entrenamiento, 2 en validación y 2 en prueba).
- **Verificación:** 0 violaciones con las 109 corridas; ninguna de las 18 excluidas aparece en un conjunto.
- **Tiempo:** 0,0015 s para agrupar, repartir y verificar.

### NPPAD

Ejecuté `preparar-datos` con el dataset real y la referencia de IA-Nuclear:
- Código 0 y reparto 142 / 30 / 30.
- La comparación con la referencia da **`COINCIDE`**.
- La verificación de fuga no encuentra violaciones: cada una de las 100 severidades está en un solo conjunto.

---

## 6. Métricas (`speckit-metricas`)

### 6.1 Sesiones

| Archivo de sesión | Fase | Inicio–Fin | Horas | Commits | Código | Pruebas |
|---|---|---|---|---|---|---|
| `20261028-2148-especificar-143a.csv` | especificar | 21:48–21:50 | 0,25 | 1 | 0 | 0 |
| `20261028-2150-aclarar-ea6a.csv` | aclarar | 21:50–21:52 | 0,25 | 1 | 0 | 0 |
| `20261028-2152-planificar-4960.csv` | planificar | 21:52–21:55 | 0,25 | 1 | 0 | 0 |
| `20261028-2155-tareas-82c7.csv` | tareas | 21:55–21:57 | 0,25 | 1 | 0 | 0 |
| `20261028-2157-analizar-01be.csv` | analizar | 21:57–21:59 | 0,25 | 2 | 0 | 0 |
| `20261028-2159-implementar-58e8.csv` | implementar | 21:59–22:14 | 0,25 | 9 | +276 / −2 | +568 / −0 |
| `20261028-2214-analizar-f870.csv` | analizar (converge) | 22:14–22:15 | 0,25 | 0 | 0 | 0 |
| **Total** | **7 sesiones** | **21:48–22:15** | **1,75** | **15** | **+276 / −2** | **+568 / −0** |

- **Las horas son el mínimo por sesión que registra la extensión (0,25 h), no un cronómetro.** El reloj marca unos 27 minutos de trabajo del agente. La exploración previa del dataset y del proyecto de referencia no está registrada. No se informaron tokens ni costo.
- Las horas de inicio y fin de cada sesión son las del registro.
- Modelo de IA: `claude-opus-5-5` en las 7 sesiones.

### 6.2 Tamaño, puntos y desperdicio (`recolectar`)

| Indicador | 004 | Acumulado del proyecto |
|---|---|---|
| Historias / FR / SC / escenarios | 3 / 15 / 7 / 15 | — |
| Tareas completadas | **25 / 25** | — |
| Puntos de tarea | **54** (sin agregados ni eliminados) | 300 (001: 103, 002: 95, 003: 48, 004: 54) |
| Código agregado / que sobrevive | **276 / 275** | 1461 líneas entregadas |
| Pruebas agregadas | +568 | — |
| Eliminado | 1 por requisito y 1 sin clasificar (ver 6.4) | — |
| Desperdicio | **1 línea (0,36 %)** | 3,44 % global |
| Esfuerzo | 1,75 h = 0,0115 persona-mes | 0,0493 persona-mes |

Desglose del código: `grupos.py` 52, `particion.py` 88, `verificacion.py` (PWR 3L) 86, `verificacion.py` (NPPAD) 46 y 4 líneas en `cli.py`. Desglose de las pruebas: 7 archivos nuevos y 1 ampliado (44 pruebas).

### 6.3 Calibración, estimación y exportación

- **`calibrar`**: 4 puntos de datos (001–004), así que **el modelo es exploratorio**.
  - La mejor medida de tamaño es KSLOC: `PM = 0,0253 · KSLOC^0,706`, R² 0,84, MMRE 0,08, PRED(25) 1,0 y MMRE en validación cruzada 0,24.
  - COCOMO II estándar da un MMRE de 76: no sirve para iteraciones de horas.
  - La ecuación de tiempo sale degenerada (`TDEV = 0 · PM^−2,2`) por los pocos puntos.
  - Esfuerzo por fase en el proyecto: analizar e implementar 20 % cada una; especificar, aclarar, planificar y tareas 13,3 % cada una.
- **`estimar`** para 004:
  - Con 15 requisitos: 1,7 h (rango 1,2–2,1).
  - Con 54 puntos de tarea: 1,6 h (1,1–2,2).
  - Con 0,276 KSLOC: 1,6 h (1,2–1,9).
  - El real fue 1,75 h. *Advertencia: 004 forma parte de los 4 puntos de la calibración, así que la comparación no es independiente.*
- **`exportar`**: `metricas/salidas/dataset-IANuclear-20261028.zip`, sin anonimizar (decisión del responsable; la carpeta no se versiona).

### 6.4 Observaciones de la medición

- **Una línea «sin clasificar».** El commit `53069a5` reescribió 2 líneas de `particion.py` (de `return Reparto(…)` a `reparto = Reparto(…)`, para verificar antes de devolver, tarea T018) sin el trailer `Causa:`. Su causa real es `requisito`. No se reescribió el historial.
- **Fechas del resumen.** `recolectar` informa como primer commit el 2026-10-18 y 11 días de calendario, porque toma commits anteriores a la rama. La iteración se hizo entera el 2026-10-28.

---

## 7. Historial de commits (rama `004-division-sin-fuga`)

| Commit | Mensaje |
|---|---|
| `0ba68e7` | docs(004): especificación de la división sin fuga de datos (PWR 3L) |
| `121de18` | docs(004): aclaraciones de la especificación |
| `dd8e411` | docs(004): plan, decisiones, modelo de datos y contrato |
| `0a62d1c` | docs(004): tareas, puntos de tarea y registro de sesión |
| `3385ab5` | docs(004): informe de /speckit-analyze |
| `a149615` | docs(004): correcciones del análisis (U1, C1, C2, C3, T1) |
| `30e1b77` | test(004): rutas de datos reales, fábrica de corridas y pruebas de agrupación |
| `9dc7d57` | feat(004): grupos de corridas PWR 3L por área de rotura y por gemelas |
| `3eb8f37` | test(004): pruebas del reparto por familia, cota del desvío y reproducibilidad |
| `6f116e4` | feat(004): reparto de grupos PWR 3L hacia 70/15/15, de mayor a menor tamaño |
| `70befcc` | test(004): pruebas de la verificación de fuga en PWR 3L, NPPAD y preparar-datos |
| `53069a5` | feat(004): verificación independiente de fuga del reparto PWR 3L |
| `6adaec5` | feat(004): verificación de fuga de la partición NPPAD en preparar-datos (`Causa: requisito`) |
| `6ae9389` | test(004): división sin fuga con los datasets reales de PWR 3L y NPPAD |
| `dcf28d0` | docs(004): README, resultados del quickstart y tareas completadas |
| `8b548e3` | docs(004): registro de la sesión de implementación |
| *(último)* | docs(004): auditoría, documento de entregables y registro de la sesión de converge |

---

## 8. Qué queda para otras tareas

| Tarea | Qué falta |
|---|---|
| **KAN-18 (002)** | Usar `formar_grupos`, `repartir` y `verificar_reparto(corridas, reparto)` con **todas** las corridas al construir `X_*`, `y_*`, `margins_*`, el reporte, `metadata.json` y el comando `preparar-pwr3l` (T019–T030 de 002). Las tareas T012, T013, T016 y T017 de 002 quedan cubiertas por 004 |
| Limitación heredada | Las corridas NORM parecidas no se agrupan (D1 de 002) |

---

## 9. Cómo verificarlo

```powershell
# Pruebas de 004 (sintéticas)
.venv\Scripts\python.exe -m pytest tests/pwr3l/unit/test_pwr3l_grupos.py tests/pwr3l/unit/test_pwr3l_particion.py tests/pwr3l/unit/test_pwr3l_verificacion.py tests/unit/test_verificacion.py -q

# Suite completa con los datos reales
$env:IANUCLEAR_DATOS = "C:\Users\User\Desktop\IANuclear"
.venv\Scripts\python.exe -m pytest -q          # 210 passed, 1 skipped

# Ver el reparto real de PWR 3L
.venv\Scripts\python.exe -c "from preparacion_pwr3l.lectura import cargar_corridas; from preparacion_pwr3l.grupos import formar_grupos; from preparacion_pwr3l.particion import repartir; from preparacion_pwr3l.verificacion import verificar_reparto; c = cargar_corridas(r'C:\Users\User\Desktop\IANuclear\PWR 3L'); r = repartir(formar_grupos(c)); verificar_reparto(c, r); print(r.conteos)"
```
