# Segunda iteración SDD: `002-preprocesamiento-pwr3l` (KAN-18)

**Tarea de Jira**: KAN-18 «Adaptar el preprocesamiento a ventanas de 300 s y cinco clases» · **Responsable**: Marcelo Acuña
**Rama**: `002-preprocesamiento-pwr3l` (creada desde `main`) · **Fechas**: 2026-10-28 (documentos) y 2026-11-03 (implementación)
**Herramienta**: GitHub Spec Kit + Claude Code (`claude-opus-5-5`) · **Constitución**: v2.0.0, sin cambios

> **Estado: completa.** Ciclo completo de Spec Kit (especificar → aclarar → planificar → tareas → analizar → implementar → converge): 38/38 tareas y 181 pruebas en verde (79 de 001 y 102 de 002). El comando funciona con la carpeta real.

---

## 1. Qué pide KAN-18 y por qué es distinta de 001

En 001, Abner preparó los datos **NPPAD**: 150 pasos de 10 s y 4 clases. KAN-18 prepara otra planta, **PWR 3L** (2705 MWt), con un dato por segundo:

- **Muestras de 300 pasos de 1 s** (los primeros 300 s de cada corrida).
- **Cinco clases**: NORM (0), LOCA rama caliente (1), LOCAC rama fría (2), ATWS (3) y TRIP_OK (4), que es un disparo correcto del reactor.
- Las corridas **OOD** (eventos desconocidos) **no son una clase de entrenamiento**.
- La constitución (principio IV) **prohíbe mezclar PWR 3L con NPPAD**: por eso hay paquete, comando y salida propios (`preparacion_pwr3l`, `preparar-pwr3l` y `data_processed_pwr3l/`).

---

## 2. Lo que se encontró en los datos (medido)

| Hecho | Detalle |
|---|---|
| 109 carpetas de corrida | 35 manuales y 74 automáticas; R27 tiene dos archivos de datos |
| Las «106 simulaciones» de Jira | 109 menos las 3 que el equipo ya descartó (R07, R27 y R28) = **20 por clase × 5 + 6 OOD** |
| Dos formatos | Las manuales son `.xls`, pero en realidad son libros xlsx (se leen con openpyxl); las demás son `.csv` |
| Datos limpios | 93 columnas, tiempo de 1 s en 1 s desde 0, sin valores faltantes |
| **9 corridas de clases de entrenamiento con menos de 300 filas** | R38 (295), R41 (295), R42 (289), R43 (294), R82 (299), R91 (295), R98 (299), R55 (295) y R63 (295) |

---

## 3. Resultado con la carpeta real

`preparar-pwr3l` tarda unos 30 s y termina con código 0:

| Clase | Entrenamiento | Validación | Prueba | Total |
|---|---|---|---|---|
| NORM | 13 | 3 | 3 | 19 |
| LOCA | 10 | 3 | 3 | 16 |
| LOCAC | 14 | 3 | 3 | 20 |
| ATWS | 12 | 3 | 3 | 18 |
| TRIP_OK | 13 | 3 | 2 | 18 |
| **Total** | **62** | **15** | **14** | **91** |

- Las cuentas cierran: 91 usables + 9 cortas + 3 descartadas + 6 OOD = **109 corridas encontradas**.
- Ninguna corrida ni grupo cae en dos conjuntos. Las gemelas ATWS/TRIP_OK y las LOCA/LOCAC de igual área van juntas; por ejemplo, las 8 corridas de 2000 cm² están en entrenamiento.
- El escalador se ajustó solo con entrenamiento (18 600 filas = 62 × 300).
- Salida: `X_*` (N, 300, 26), `y_*` (0–4), `margins_*` (N, 300, 7), `scaler_*` y `metadata.json`, que dice qué corrida es cada fila.

---

## 4. Lo que se hizo, fase por fase

| # | Fase | Comando | Resultado | Archivo |
|---|---|---|---|---|
| 1 | Rama | script `create-new-feature.ps1` | `002-preprocesamiento-pwr3l` | — |
| 2 | Especificar | `/speckit-specify` | 3 historias, 16 FR, 8 SC | [spec.md](specs/002-preprocesamiento-pwr3l/spec.md) |
| 3 | Aclarar | `/speckit-clarify` | 3 preguntas (sección 5); checklist 16/16 | spec.md, [checklists/requirements.md](specs/002-preprocesamiento-pwr3l/checklists/requirements.md) |
| 4 | Planificar | `/speckit-plan` | *Constitution Check* «cumple», 12 decisiones, modelo de datos, 2 contratos y quickstart | [plan.md](specs/002-preprocesamiento-pwr3l/plan.md), [research.md](specs/002-preprocesamiento-pwr3l/research.md), [data-model.md](specs/002-preprocesamiento-pwr3l/data-model.md), [contracts/](specs/002-preprocesamiento-pwr3l/contracts/), [quickstart.md](specs/002-preprocesamiento-pwr3l/quickstart.md) |
| 5 | Tareas | `/speckit-tasks` | 34 tareas en 6 fases, pruebas primero; 95 puntos de tarea | [tasks.md](specs/002-preprocesamiento-pwr3l/tasks.md) |
| 6 | Analizar | `/speckit-analyze` | 8 hallazgos (0 críticos, 3 medios, 5 bajos), corregidos antes de programar | [analisis-inicial.md](specs/002-preprocesamiento-pwr3l/analisis-inicial.md) |
| 7 | Implementar | `/speckit-implement` | 34/34 tareas; en cada historia las pruebas se commitearon **antes** que el código | `src/preparacion_pwr3l/`, `tests/pwr3l/` |
| 8 | Converge | `/speckit-converge` | 1.ª pasada: 4 hallazgos → T035–T038. 2.ª pasada: **converged** | [auditoria.md](specs/002-preprocesamiento-pwr3l/auditoria.md) |

### Código

| Módulo | Responsabilidad |
|---|---|
| `config.py` | Clases, carpetas, 26 entradas, 7 márgenes, 300 pasos, descartadas y 19 pares de gemelas |
| `descubrimiento.py` | Recorre `PWR 3L` y `auto`: clase, id, archivo, área de rotura, control de `gemelo_de` |
| `lectura.py` | Lee CSV y xlsx, valida el archivo completo y marca las corridas cortas sin rellenar |
| `grupos.py` | Grupos de gemelas y de LOCA/LOCAC de igual área |
| `particion.py` | Reparto de grupos completos por familia (regla del mayor déficit, semilla 42) |
| `escalado.py` | `StandardScaler` ajustado solo con entrenamiento |
| `salida.py` | Arreglos y `metadata.json` |
| `reporte.py` | Reporte de 9 secciones: corridas encontradas, muestras, grupos, exclusiones, advertencias y limitaciones |
| `cli.py` | Comando `preparar-pwr3l`; código 1 ante cualquier defecto, sin escribir nada |

---

## 5. Decisiones clave (para explicar)

1. **Corridas cortas: se excluyen con aviso.** Detenerse bloquearía siempre el dataset real, y rellenar inventaría datos (principio III).
2. **«Igual severidad» = misma área de rotura.** Todas las LOCA y LOCAC con la misma área van al mismo conjunto, para que no haya fuga (principio II).
3. **Las gemelas ATWS/TRIP_OK van juntas.** Son el mismo escenario con y sin fallo del disparo; si `config.json` declara otra gemela, el comando se detiene.
4. **Las OOD solo se listan.** No se preparan; quedan para el monitor de novedades.
5. **Solo 26 variables medibles en sala de control.** Se excluye `WLR` (caudal de fuga), que no se mide en planta y haría trivial detectar un LOCA. Los 7 márgenes térmicos se guardan aparte y sin escalar.
6. **Se valida el archivo completo**, no solo los 300 pasos. Un defecto detiene todo, nombra el archivo y no escribe nada.

> Las respuestas de `/speckit-clarify` las eligió el agente, con la opción recomendada, por delegación del responsable. Están anotadas en la spec para revisarlas en el PR.

---

## 6. Métricas (`speckit-metricas`)

### Tiempo por fase

| Fase | Horas registradas | Commits |
|---|---|---|
| Especificar | 0.25 | 1 |
| Aclarar | 0.25 | 1 |
| Planificar | 0.25 | 1 |
| Tareas | 0.25 | 1 |
| Analizar | 0.25 | 2 |
| Implementar (1.ª sesión, fases 1–2) | 0.25 | 3 |
| Implementar (2.ª sesión, fases 3–7) | 0.25 | 12 |
| **Total** | **1.75** | **21** (+ este documento) |

Las horas son el mínimo que registra la extensión por sesión (0.25 h), no un cronómetro. No se informaron tokens ni costo.

### Tamaño y calidad

| Medida | Valor |
|---|---|
| Código (`src/preparacion_pwr3l/`) | **771 líneas**, 0 eliminadas |
| Pruebas (`tests/pwr3l/`) | 1148 líneas; 2 eliminadas (corrección de una prueba, `Causa: defecto`) |
| Desperdicio de código | **0 %** |
| Pruebas | **102** de 002 + 79 de 001 = **181, todas verdes** (≈ 3.5 min) |
| Puntos de tarea | **99** (95 del plan + 4 de convergencia) |
| Hallazgos del análisis | 8 (0 críticos), corregidos |
| Hallazgos de converge | 4 → resueltos; 2.ª pasada sin hallazgos |

---

## 7. Limitaciones (declaradas en el reporte)

- Unas 20 corridas por clase: validación y prueba tienen ~3 muestras por clase, así que las métricas tendrán mucha incertidumbre.
- La etiqueta es una por corrida: los segundos previos al evento llevan la etiqueta del accidente. El etiquetado paso a paso queda para KAN-23.
- El grupo de 2000 cm² (8 corridas) desequilibra el reparto de LOCA/LOCAC.
- Varias corridas NORM se parecen (mismo rechazo de carga con otra condición inicial) y no se agrupan.
- Un solo simulador, sin ruido de sensores.

---

## 8. Cómo verificarlo

```
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -e ".[dev]"
.venv/Scripts/python.exe -m pytest -q                 # 181 passed
.venv/Scripts/preparar-pwr3l                          # reporte + data_processed_pwr3l/
```
