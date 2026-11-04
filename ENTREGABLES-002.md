# Segunda iteración SDD: `002-preprocesamiento-pwr3l` (KAN-18)

**Tarea de Jira**: KAN-18 «Adaptar el preprocesamiento a ventanas de 300 s y cinco clases» · **Responsable**: Marcelo Acuña
**Ramas**: `002-preprocesamiento-pwr3l` (documentos y fases 1–2, PR #2) y `002-preprocesamiento-pwr3l-cierre` (cierre sobre `main`)
**Fechas**: 2026-10-28 (documentos y fases 1–2) y 2026-11-04 (cierre) · **Herramienta**: GitHub Spec Kit + Claude Code (`claude-opus-5-5`) · **Constitución**: v2.0.0, sin cambios

> **Estado: completa.** Ciclo completo de Spec Kit, 38/38 tareas, `converged`. El comando `preparar-pwr3l` funciona con la carpeta real y la suite completa del proyecto (001–005 + este cierre) pasa: **293 pruebas**.

---

## 1. Qué pide KAN-18

Preparar las corridas de la planta **PWR 3L** (2705 MWt, un dato por segundo) para el canal rápido:

- **Muestras de 300 pasos de 1 s** (los primeros 300 s de cada corrida).
- **Cinco clases**: NORM (0), LOCA rama caliente (1), LOCAC rama fría (2), ATWS (3) y TRIP_OK (4), que es un disparo correcto.
- Las corridas **OOD** (eventos desconocidos) no son clase de entrenamiento.
- No se mezcla con NPPAD (principio IV): paquete, comando y salida propios.

---

## 2. Cómo se hizo en dos tramos (para explicar)

1. **28/10, rama `002-preprocesamiento-pwr3l`**: especificar, aclarar, planificar, tareas y analizar completos, más las fases 1–2 (descubrir y leer las corridas). Se fusionó en `main` con el PR #2.
2. **Mientras tanto**, el equipo construyó sobre `main`:
   - **003 (Christian)**: escalado solo con entrenamiento y paso de muestreo medido desde `TIME`.
   - **004 (Abner)**: grupos, reparto 70/15/15 sin fuga y verificación independiente.
3. **04/11, rama `002-preprocesamiento-pwr3l-cierre` desde `main`**: lo que faltaba de KAN-18 (salida, márgenes, reporte y comando `preparar-pwr3l`), **usando los módulos de 003 y 004**, no reemplazándolos. La rama 002 original había avanzado con versiones propias de grupos, reparto y escalado; esas versiones no se llevaron a `main`, para no pisar el trabajo del equipo.

---

## 3. Resultado con la carpeta real

`preparar-pwr3l` tarda unos 30 s y termina con código 0. Paso medido: 1 s en todas las corridas.

| Clase | Entrenamiento | Validación | Prueba | Total |
|---|---|---|---|---|
| NORM | 13 | 3 | 3 | 19 |
| LOCA | 11 | 4 | 1 | 16 |
| LOCAC | 14 | 2 | 4 | 20 |
| ATWS | 12 | 3 | 3 | 18 |
| TRIP_OK | 13 | 3 | 2 | 18 |
| **Total** | **63** | **15** | **13** | **91** |

- Las cuentas cierran: 91 usables + 9 cortas + 3 descartadas (R07, R27, R28) + 6 OOD = **109 corridas encontradas**.
- La verificación de 004 da 0 violaciones: ninguna corrida, área de rotura ni par de gemelas en dos conjuntos.
- Salida en `data_processed_pwr3l/`: `X_*` (N, 300, 26) escalado solo con entrenamiento, `y_*` (0–4), `margins_*` (N, 300, 7) sin escalar, `scaler_*` y `metadata.json`, que dice qué corrida es cada fila, sus grupos, las exclusiones con su motivo y las limitaciones.

---

## 4. Fases de Spec Kit

| # | Fase | Resultado | Archivo |
|---|---|---|---|
| 1 | Especificar | 3 historias, 16 FR, 8 SC | [spec.md](specs/002-preprocesamiento-pwr3l/spec.md) |
| 2 | Aclarar | 3 preguntas: cortas excluidas con aviso, igual severidad = área, OOD solo listadas | spec.md |
| 3 | Planificar | 12 decisiones, modelo de datos, 2 contratos, quickstart | [plan.md](specs/002-preprocesamiento-pwr3l/plan.md), [research.md](specs/002-preprocesamiento-pwr3l/research.md) |
| 4 | Tareas | 34 tareas, pruebas primero, 95 puntos | [tasks.md](specs/002-preprocesamiento-pwr3l/tasks.md) |
| 5 | Analizar | 8 hallazgos (0 críticos), corregidos antes de programar | [analisis-inicial.md](specs/002-preprocesamiento-pwr3l/analisis-inicial.md) |
| 6 | Implementar | T001–T011 (002), T012–T018 (003 y 004), T015 y T019–T034 (cierre) | `src/preparacion_pwr3l/`, `tests/pwr3l/` |
| 7 | Converge | 1.ª pasada: 4 hallazgos (T035–T038). 2.ª: **converged** | [auditoria.md](specs/002-preprocesamiento-pwr3l/auditoria.md) |

### Módulos de KAN-18 (de Marcelo)

| Módulo | Qué hace |
|---|---|
| `config.py`, `descubrimiento.py`, `lectura.py` | Clases, variables, descartadas y gemelas; recorrer `PWR 3L` y `auto`; leer CSV y xlsx validando todo el archivo |
| `salida.py` | Arreglos `X`, `y` y márgenes; `metadata.json` |
| `reporte.py` | Reporte de 9 secciones: corridas encontradas, muestras, grupos, exclusiones, escalador, advertencias y limitaciones |
| `cli.py` | `preparar-pwr3l`: lectura (002) → grupos y reparto con verificación de fuga (004) → escalado (003) → publicación todos o ninguno |

---

## 5. Decisiones clave

1. **Corridas cortas: se excluyen con aviso.** Rellenar inventaría datos.
2. **Igual severidad = misma área de rotura**: LOCA y LOCAC de igual área van juntas.
3. **Las gemelas ATWS/TRIP_OK van juntas**; si `config.json` declara otra gemela, el comando se detiene.
4. **26 variables medibles en sala de control**, sin `WLR` (caudal de fuga, no medible). Los 7 márgenes térmicos van aparte y sin escalar.
5. **El paso de muestreo se mide y se publica** (003), no se supone.

> Las respuestas de `/speckit-clarify` las eligió el agente con la opción recomendada, por delegación del responsable.

---

## 6. Métricas (`speckit-metricas`)

| Sesión | Fase | Horas | Commits | Código | Pruebas |
|---|---|---|---|---|---|
| 20261028-1843 … 1852 | especificar, aclarar, planificar, tareas, analizar | 1.25 | 6 | 0 | 0 |
| 20261028-1856 | implementar (fases 1–2) | 0.25 | 3 | +342 | +496 |
| 20261104-1317 | implementar (cierre sobre `main`) | 0.25 | 3 | +315 | +461 |
| **Total en `main`** | | **1.75** | **12** + docs | **+657** | **+957** |

- Las horas son el mínimo por sesión que registra la extensión (0.25 h), no un cronómetro.
- **Desperdicio: 0 líneas** en `main`. El código de la rama 002 original que no se llevó a `main` (grupos, reparto y escalado propios) no se cuenta como entregado.
- **Puntos de tarea: 99** (95 del plan + 4 de convergencia).
- **Pruebas**: 133 en `tests/pwr3l` (descubrimiento, lectura, grupos, reparto, verificación, escalado, reporte, comando, márgenes y carpeta real). Suite completa: **293, todas verdes**.

---

## 7. Limitaciones (declaradas en el reporte)

- Unas 20 corridas por clase: validación y prueba tienen ~3 por clase, así que las métricas tendrán mucha incertidumbre.
- Una etiqueta por corrida: los segundos previos al evento llevan la etiqueta del accidente. 005 resuelve el etiquetado por segundo.
- El grupo de 2000 cm² reúne 8 corridas y desequilibra el reparto de LOCA/LOCAC.
- Las NORM parecidas entre sí no se agrupan.
- Un solo simulador, sin ruido de sensores.

---

## 8. Cómo verificarlo

```
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -e ".[dev]"
.venv/Scripts/python.exe -m pytest tests/pwr3l -q    # 133 passed (con IANUCLEAR_DATOS o ../IA-Nuclear)
.venv/Scripts/preparar-pwr3l                         # reporte + data_processed_pwr3l/
```
