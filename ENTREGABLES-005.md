# Quinta iteración SDD: `005-clasificador-etapa1`

**Tarea de Jira**: «Entrenar el clasificador de Etapa 1 (familia del evento)» · **Responsable**: Abner Arboleda
**Rama**: `005-clasificador-etapa1` (creada desde `main` con 001–004 fusionadas) · **Fecha**: 2026-11-03
**Herramienta**: GitHub Spec Kit + Claude Code (`claude-opus-5-5`) + `speckit-metricas` · **Constitución**: v2.0.0, sin cambios

> **Estado: iteración completa y convergente (`converged` en la 2.ª pasada).** Se ejecutaron todas las fases de Spec Kit (`/speckit-specify` → `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement` → `/speckit-converge` ×2) y todos los comandos de métricas. 35/35 tareas (108 puntos), 50 pruebas nuevas. Con los datos reales: **cumple 2 de las 3 metas**. La familia LOCA se reconoce más tarde de lo que pedía la meta de detección temprana; se informa tal como sale.

---

## 1. Qué pide la tarea

> Bi-LSTM que distingue operación normal, familia LOCA y transitorio con disparo. Entrenar con prefijos cortos de la secuencia para que decida con pocos segundos de datos, y con pesos de clase para el desbalance.

| Familia (etiqueta) | Clases de PWR 3L |
|---|---|
| NORM | operación normal, y cualquier instante anterior al inicio del evento |
| LOCA | LOCA rama caliente y LOCAC rama fría |
| TRANS | ATWS y TRIP_OK (transitorio con disparo) |

- **Datos**: solo PWR 3L (un dato por segundo). NPPAD no sirve para medir segundos: tiene un dato cada 10 s y una sola simulación NORM y ATWS. Además, la constitución prohíbe mezclar plantas.
- **Reutiliza** lo construido por el equipo: la lectura de corridas (002), el reparto sin fuga y su verificación (004) y el escalado ajustado solo con entrenamiento (003).
- **Fuera de alcance**: la Etapa 2 (rama caliente o fría; ATWS o TRIP_OK), la consola del operador y el modo sombra.

---

## 2. Cómo se resolvió «prefijos cortos» (decisiones del responsable en `/speckit-clarify`)

1. **Qué ve el modelo en cada instante**: cada segundo τ, los **últimos 30 s hasta τ** (al empezar la corrida, lo que haya desde t = 0, rellenado con la primera fila). Es lo que vería en planta en tiempo real, así que lo que se mide sirve para operar.
2. **Tramo previo al evento**: los instantes anteriores al inicio se etiquetan como **operación normal**. Así el modelo aprende a no alarmar antes de tiempo y se pueden medir las falsas alarmas.
3. **Entrenamiento**: corridas NORM completas, todo el tramo previo y los **primeros 60 s de cada evento**, para que aprenda a decidir con pocos segundos.

El instante de inicio del evento se toma del validador del proyecto (`t_inicio_real` en `validacion.json` o en `validacion_corridas.csv`). Para las TRIP_OK manuales sin validación se usa el instante del nombre de su carpeta (`_t48`).

---

## 3. Lo que se hizo, fase por fase

| # | Fase | Comando | Resultado | Archivo |
|---|---|---|---|---|
| 1 | Rama | git | `005-clasificador-etapa1` desde `main` | — |
| 2 | Especificar | `/speckit-specify` | 3 historias, 15 FR, 7 SC, 2 dudas marcadas | [spec.md](specs/005-clasificador-etapa1/spec.md) |
| 3 | Aclarar | `/speckit-clarify` | 2 preguntas respondidas por el responsable (sección 2); checklist 16/16 | spec.md, [checklists/](specs/005-clasificador-etapa1/checklists/requirements.md) |
| 4 | Planificar | `/speckit-plan` | Constitution Check con todo en «cumple», 11 decisiones, modelo de datos, 2 contratos y quickstart | [plan.md](specs/005-clasificador-etapa1/plan.md), [research.md](specs/005-clasificador-etapa1/research.md), [data-model.md](specs/005-clasificador-etapa1/data-model.md), [contracts/](specs/005-clasificador-etapa1/contracts/) |
| 5 | Tareas | `/speckit-tasks` + `puntos` | 32 tareas, pruebas primero; **97 puntos** | [tasks.md](specs/005-clasificador-etapa1/tasks.md), [puntos-tarea.csv](specs/005-clasificador-etapa1/puntos-tarea.csv) |
| 6 | Analizar | `/speckit-analyze` | 6 hallazgos (**0 críticos**, 1 medio y 5 bajos); los 6 aplicados con aprobación | [analisis-inicial.md](specs/005-clasificador-etapa1/analisis-inicial.md) |
| 7 | Implementar | `/speckit-implement` | 32/32 tareas; paquete `clasificador_etapa1` y comando `entrenar-etapa1` | `src/clasificador_etapa1/`, `tests/etapa1/` |
| 8 | Converge (1.ª) | `/speckit-converge` | 3 hallazgos `partial` → T033–T035 (+11 puntos), implementados solo con inserciones | [auditoria.md](specs/005-clasificador-etapa1/auditoria.md) |
| 9 | Converge (2.ª) | `/speckit-converge` | **`converged`**, 0 hallazgos | — |

---

## 4. Qué se construyó

| Módulo (`src/clasificador_etapa1/`) | Qué hace | Líneas |
|---|---|---|
| `config.py` | Familias, ventana de 30 s, horizontes, umbral 0,80, hiperparámetros, aviso consultivo | 38 |
| `eventos.py` | Instante de inicio de cada corrida (validador → CSV → nombre de carpeta) | 66 |
| `muestras.py` | Una muestra por segundo: ventana causal de 30 s, etiqueta y k = τ − inicio | 78 |
| `modelo.py` | Bi-LSTM de 1 capa y 32 unidades por dirección (~16 000 parámetros) | 28 |
| `entrenamiento.py` | Pesos de clase N/(3·n_c), Adam, parada temprana por F1 de validación, determinismo | 97 |
| `evaluacion.py` | Métricas globales y por horizonte, tiempo de confirmación, falsas alarmas, metas y reporte | 296 |
| `prediccion.py` | `cargar(ruta).clasificar(serie)`: probabilidades, recomendación o «INCIERTO» y aviso consultivo | 59 |
| `cli.py` | `entrenar-etapa1`: reparto 004 → verificación → escalado 003 → entrenamiento → evaluación → artefactos | 195 |

Artefactos en `modelos/etapa1/` (no se versiona; se regenera con el comando): `modelo.pt`, `modelo.json`, `reporte.json` y `reporte.txt`.

---

## 5. Resultados con los datos reales (`D:\Personal\IANuclear\PWR 3L`)

**Reparto (004)**: 63 corridas de entrenamiento (8 449 muestras), 15 de validación (4 425) y 13 de prueba (3 835). **Pesos de clase**: NORM 0,52, LOCA 1,86 y TRANS 1,86. **Mejor época**: la 2.ª de 8 (F1 de validación 0,969). **Tiempo**: 16,7 s en total.

### Métricas globales en prueba

| Familia | Precisión | Exhaustividad | F1 |
|---|---|---|---|
| NORM | 0,958 | 1,000 | 0,978 |
| LOCA | 0,977 | 0,965 | 0,971 |
| TRANS | 1,000 | 0,972 | 0,986 |
| **F1 macro** | | | **0,978** |

### ¿Con cuántos segundos decide? (exhaustividad a h segundos del inicio del evento)

| Familia | 1 s | 2 s | 3 s | 5 s | 10 s | 20 s | 30 s |
|---|---|---|---|---|---|---|---|
| LOCA | 0,00 | 0,00 | 0,00 | 0,00 | 0,80 | 1,00 | 1,00 |
| TRANS | 0,50 | 0,80 | 1,00 | 1,00 | 1,00 | 1,00 | 1,00 |

### Tiempo de confirmación (≥ 0,80 dos segundos seguidos)

| Familia | Corridas de prueba | Resultado |
|---|---|---|
| TRANS | 5 (3 ATWS y 2 TRIP_OK) | **5 de 5 en 2–4 s** (mediana 3 s) |
| LOCA | 5 | 100 cm²: **19 s** (R44, R83) · 10 cm²: 120 s (R19, R88) · 5 cm²: no detectada (R46) |

### Falsas alarmas

**0** en las corridas de operación normal y **0** en los tramos previos al evento.

### Metas

| Meta | Resultado | Estado |
|---|---|---|
| SC-001: LOCA ≥ 50 cm² confirmada en ≤ 10 s | 0 de 2 (19 s) | **No cumple** |
| SC-002: 0 falsas alarmas en corridas NORM | 0 | Cumple |
| SC-003: F1 macro de los primeros 30 s ≥ 0,80 | 0,927 | Cumple |
| SC-005: reproducible | Dos ejecuciones con artefactos idénticos | Cumple |
| SC-006: < 15 min en CPU | 16,7 s | Cumple |

**Lectura honesta.** El transitorio con disparo se reconoce en pocos segundos y no hay falsas alarmas. La familia LOCA, en cambio, necesita entre 10 y 20 s, y mucho más con roturas pequeñas, así que no alcanza la meta de detección temprana del plan de referencia. No se ajustó el modelo mirando la prueba. Mejoras a evaluar solo con validación:
- elegir el modelo por el F1 de los primeros segundos en lugar del F1 global;
- usar ventanas más cortas o atención en lugar de la media;
- añadir variables de tendencia.

La prueba tiene 13 corridas, así que estas cifras tienen mucha incertidumbre.

---

## 6. Métricas (`speckit-metricas`)

### 6.1 Sesiones

| Sesión | Fase | Inicio–Fin | Horas | Commits | Código | Pruebas |
|---|---|---|---|---|---|---|
| `20261103-1259-especificar` | especificar | 12:59–13:01 | 0,25 | 1 | 0 | 0 |
| `20261103-1301-aclarar` | aclarar | 13:01–13:11 | 0,25 | 1 | 0 | 0 |
| `20261103-1311-planificar` | planificar | 13:11–13:14 | 0,25 | 1 | 0 | 0 |
| `20261103-1314-tareas` | tareas | 13:14–13:16 | 0,25 | 1 | 0 | 0 |
| `20261103-1316-analizar` | analizar | 13:16–13:20 | 0,25 | 2 | 0 | 0 |
| `20261103-1320-implementar` | implementar | 13:20–13:37 | 0,25 | 11 | +851 / −0 | +683 / −0 |
| `20261103-1337-analizar` | converge (1.ª) | 13:37–13:38 | 0,25 | 1 | 0 | 0 |
| `20261103-1339-implementar` | implementar (convergencia) | 13:39–13:41 | 0,25 | 2 | +13 / −0 | +19 / −0 |
| `20261103-1341-analizar` | converge (2.ª) | 13:41–13:42 | 0,25 | 0 | 0 | 0 |
| **Total** | **9 sesiones** | **12:59–13:42** | **2,25** | **20** | **+864 / −0** | **+702 / −0** |

⚠ Las horas son el mínimo por sesión que registra la extensión (0,25 h), no un cronómetro: el reloj marca unos 43 minutos de trabajo del agente. La instalación de PyTorch y la exploración de los datos no están registradas. No se informaron tokens ni costo.

### 6.2 Tamaño y desperdicio (`recolectar`)

| Indicador | 005 |
|---|---|
| Historias / FR / SC / escenarios | 3 / 15 / 7 / 11 |
| Tareas | **35 / 35** |
| Puntos de tarea | **108** (97 del plan + 11 de convergencia) |
| Código agregado / que sobrevive | **864 / 864** |
| Pruebas agregadas | +702 (50 pruebas) |
| Desperdicio | **0 líneas (0 %)** |
| Esfuerzo | 2,25 h = 0,0148 persona-mes |
| Modelo de IA | `claude-opus-5-5` |

Proyecto completo (001–005): 2 940 líneas entregadas y 0,0641 persona-mes.

### 6.3 Calibración, estimación y exportación

- **`calibrar`** con 5 funcionalidades (001–005): modelo exploratorio. La mejor medida ahora es **tareas** (MMRE 0,135, PRED(25) 0,8 y MMRE en validación cruzada 0,21). COCOMO II estándar sigue sin servir a esta escala (MMRE 95).
- **`estimar`** para 005: 1,8 h por requisitos, 2,1 h por puntos del plan y 2,6 h por KSLOC, frente a 2,25 h reales. 005 está dentro de la calibración, así que la comparación no es independiente.
- **`exportar`**: `metricas/salidas/dataset-IANuclear-20261103.zip`, sin anonimizar (el mismo criterio que en 004).

---

## 7. Historial de commits (rama `005-clasificador-etapa1`)

| Commit | Mensaje |
|---|---|
| `ca0018f` | docs(005): especificación del clasificador de Etapa 1 (familia del evento) |
| `cb27b6f` | docs(005): aclaraciones de la especificación |
| `0161621` | docs(005): plan, decisiones, modelo de datos y contratos |
| `c8374be` | docs(005): tareas, puntos de tarea y registro de sesión |
| `5034b80` | docs(005): informe de /speckit-analyze |
| `094e1b6` | docs(005): correcciones del análisis (U1, U2, C1, C2, A1, T1) |
| `421e2c5` | feat(005): paquete clasificador_etapa1, extra modelo (PyTorch) y guion entrenar-etapa1 |
| `e1532db` / `cb1cf79` | test / feat(005): inicios de evento y muestras con ventana causal de 30 s |
| `4e5e035` / `cb5285b` | test / feat(005): Bi-LSTM, entrenamiento con pesos de clase y comando entrenar-etapa1 |
| `e6ed60e` / `aa039d7` | test / feat(005): evaluación por horizonte, tiempo de confirmación, falsas alarmas y metas |
| `4a1e60e` / `ec59f70` | test / feat(005): clasificación consultiva con el modelo guardado |
| `ffd56c6` | test(005): entrenamiento corto con el dataset real de PWR 3L |
| `2b3422b` | docs(005): README, resultados con los datos reales y tareas completadas |
| `fb6c9cf` | docs(005): tareas de convergencia (T033–T035) |
| `4e01bb8` / `5ab93e0` | test / feat(005): métricas completas por horizonte, reparto, área y validación en el reporte |
| `18fc91b`, `d0c982e`, `7703acf`, `7fb6124` | docs(005): registros de sesión y puntos |
| *(último)* | docs(005): auditoría y documento de entregables |

---

## 8. Carpetas

```
specs/005-clasificador-etapa1/     spec, plan, research, data-model, contracts/ (cli, salidas), quickstart,
                                   tasks, puntos-tarea.csv, analisis-inicial, auditoria, checklists/
src/clasificador_etapa1/           config, eventos, muestras, modelo, entrenamiento, evaluacion, prediccion, cli
tests/etapa1/                      conftest (corridas sintéticas) · unit/ (eventos, muestras, entrenamiento,
                                   evaluacion, prediccion) · integration/ (cli, real)
modelos/etapa1/                    (no se versiona) modelo.pt, modelo.json, reporte.json, reporte.txt
metricas/sesiones/                 20261103-1259 … 1341 (9 sesiones)
```

---

## 9. Cómo verificarlo

```powershell
# Dependencias (PyTorch para CPU)
uv pip install --python .venv\Scripts\python.exe -e ".[dev]"
uv pip install --python .venv\Scripts\python.exe torch --index-url https://download.pytorch.org/whl/cpu

# Entrenar y evaluar (≈ 17 s); imprime el reporte y deja los artefactos en modelos\etapa1
.venv\Scripts\entrenar-etapa1.exe --origen "D:\Personal\IANuclear\PWR 3L" --salida modelos\etapa1

# Pruebas
$env:IANUCLEAR_DATOS = "D:\Personal\IANuclear"
.venv\Scripts\python.exe -m pytest tests/etapa1 -q      # 50 pruebas
.venv\Scripts\python.exe -m pytest -q                   # suite completa
```

---

## 10. Pendientes

| Pendiente | Detalle |
|---|---|
| Mejorar la detección temprana de LOCA (SC-001) | Selección por el F1 de los primeros segundos, ventana más corta o atención, variables de tendencia; siempre evaluado con validación |
| Etapa 2 | Distinguir rama caliente o fría y ATWS o TRIP_OK sobre los eventos que la Etapa 1 clasifique |
| PR de 005 | Subir la rama y abrir el pull request hacia `main` |
