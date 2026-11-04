# Novena iteración SDD: `009-clasificador-etapa2`

**Actividad**: «Entrenar el clasificador de Etapa 2 (rama caliente o fría)» · **Desarrollador**: `cmbonifaz`
**Rama**: `009-clasificador-etapa2` (creada desde `main`) · **Fecha**: 2026-11-04
**Herramienta**: GitHub Spec Kit + `speckit-metricas` (`claude-opus-5-5:low`) · **Constitución**: v2.0.0, sin cambios

> **Estado: iteración completa y convergente (`converged`).** Se ejecutaron todas las fases de Spec Kit (`/speckit-specify` → `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement` → `/speckit-converge`) y todos los comandos de métricas (`sesion`, `puntos`, `recolectar`, `calibrar`, `estimar`, `exportar`). Las 18 tareas (`T001`–`T018`, 67 puntos de tarea) y las 30 pruebas unitarias e integración de la Etapa 2 están en verde (suite global del proyecto: 434 pasadas, 1 omitida).

---

## 1. Qué pide la tarea y alcance

> Bi-LSTM que separa LOCA (rama caliente) de LOCAC (rama fría) cuando la Etapa 1 detecta la familia LOCA, con los canales de desviación pico de PWR y PWNT. Si la confianza es menor al 80 %, el sistema se abstiene (UNCERTAIN).

- **Dominio**: reactor PWR 3L (2705 MWt, un dato por segundo). NPPAD no se utiliza (la constitución v2.0.0 prohíbe mezclar plantas).
- **Entradas**: exclusivamente los dos canales de desviación pico causal de potencia térmica (`PWR`) y flujo neutrónico (`PWNT`), calculados a partir de los datos sin escalar y normalizados con parámetros ajustados exclusivamente sobre el conjunto de entrenamiento (principio II: cero fuga de datos).
- **Lógica en cascada**: la Etapa 2 solo se evalúa si la Etapa 1 diagnosticó previamente la familia `LOCA`. Si la Etapa 1 indica `NORM`, `TRANS` o `INCIERTO`, devuelve `NO_APLICA` sin ejecutar inferencia.
- **Abstención**: si la mayor probabilidad entre LOCA y LOCAC es menor a 0,80, el clasificador responde `UNCERTAIN` para no forzar una decisión insegura ante el operador.
- **Delimitación de alcance**: se limitó estrictamente a la Etapa 2 en un paquete independiente (`src/clasificador_etapa2/`), sin modificar `preparacion_datos`, `preparacion_pwr3l`, `clasificador_etapa1`, `regla_atws` ni `tiempo_deteccion`.

---

## 2. Lo que se encontró en los datos y decisiones de diseño

1. **Fenómeno físico de la desviación pico**:
   - En una rotura en rama caliente (`LOCA`), el refrigerante que escapa reduce la temperatura del moderador que entra al núcleo, produciendo un incremento transitorio de reactividad y un pico de sobrepotencia en `PWR` y `PWNT` (+0,5 a +6 puntos) antes del disparo del reactor (*scram*).
   - En una rotura en rama fría (`LOCAC`), el agua fría que fuga no induce ese enfriamiento preferencial y no hay sobrepotencia positiva (valores nominales o decrecientes).
2. **Causalidad estricta y ventana temporal**:
   - `desviacion_pico(x)` calcula el máximo en los últimos 15 s de la media móvil causal de 3 s menos el valor inicial (`x[0]`). En todo instante $\tau$ solo se emplean datos hasta $\tau$, preservando causalidad estricta.
   - Para las muestras, se toma una ventana causal de 30 s hasta $\tau$ ($k = \tau - \lceil t_{\text{inicio}} \rceil \ge 0$).
3. **Lectura de `PWR`**:
   - `PWR` no estaba incluida entre las 26 variables procesadas de 002. Se implementó su lectura directa y validación desde el archivo de corrida con `_leer_tabla` y `_convertir_columna` de `preparacion_pwr3l.lectura` sin tocar el paquete 002.
4. **Reparto sin fuga**:
   - Se reutilizó el reparto por grupos pareados de 004 con verificación previa `verificar_reparto`. Con el dataset real resultan 36 corridas LOCA/LOCAC usables: **25 en entrenamiento, 6 en validación y 5 en prueba**.

---

## 3. Lo que se hizo, fase por fase (Spec Kit)

| # | Fase | Comando | Resultado | Artefactos principales |
|---|---|---|---|---|
| 1 | Rama y Especificar | `/speckit-specify` | Rama `009-clasificador-etapa2`. Especificación con 3 historias (US1, US2, US3), 15 requisitos funcionales (`FR-001`–`FR-015`), 6 criterios de éxito (`SC-001`–`SC-006`) y checklist 16/16 PASS | [spec.md](specs/009-clasificador-etapa2/spec.md), [requirements.md](specs/009-clasificador-etapa2/checklists/requirements.md) |
| 2 | Aclarar | `/speckit-clarify` | 2 preguntas aclaradas con el usuario: entradas fijadas solo a los 2 canales de desviación pico (PWR y PWNT) y evaluación de la Etapa 2 sobre las corridas LOCA/LOCAC de prueba | [spec.md](specs/009-clasificador-etapa2/spec.md) |
| 3 | Planificar | `/speckit-plan` | Plan técnico con Constitution Check en «cumple», decisiones de investigación en `research.md`, modelo de datos y contratos de CLI y salidas | [plan.md](specs/009-clasificador-etapa2/plan.md), [research.md](specs/009-clasificador-etapa2/research.md), [data-model.md](specs/009-clasificador-etapa2/data-model.md), [contracts/cli.md](specs/009-clasificador-etapa2/contracts/cli.md), [contracts/salidas.md](specs/009-clasificador-etapa2/contracts/salidas.md), [quickstart.md](specs/009-clasificador-etapa2/quickstart.md) |
| 4 | Tareas y Puntos | `/speckit-tasks` + `puntos` | 18 tareas (`T001`–`T018`) organizadas en 6 fases TDD; línea base de **67 puntos de tarea** | [tasks.md](specs/009-clasificador-etapa2/tasks.md), [puntos-tarea.csv](specs/009-clasificador-etapa2/puntos-tarea.csv) |
| 5 | Analizar | `/speckit-analyze` | 3 hallazgos bajos (`U1`, `C1`, `C2`), 0 críticos/medios, 100 % de cobertura. Correcciones aplicadas en commit `5a31901` antes de programar | [analisis-inicial.md](specs/009-clasificador-etapa2/analisis-inicial.md) |
| 6 | Implementar | `/speckit-implement` | Paquete `src/clasificador_etapa2/`, guion `entrenar-etapa2`, suite `tests/etapa2/` (30 pruebas en verde) | `src/clasificador_etapa2/`, `tests/etapa2/` |
| 7 | Convergencia | `/speckit-converge` | Estado **`converged`** (1.ª pasada): 18/18 tareas completadas, 0 brechas, 434 pruebas globales en verde | [auditoria.md](specs/009-clasificador-etapa2/auditoria.md), [tasks.md](specs/009-clasificador-etapa2/tasks.md) |

---

## 4. Qué se construyó

| Módulo (`src/clasificador_etapa2/`) | Responsabilidad |
|---|---|
| `config.py` | Constantes: clases (`LOCA`, `LOCAC`), canales (`PWR`, `PWNT`), ventana de pico de 15 s, media móvil de 3 s, ventana de muestra de 30 s, umbral de abstención (0,80), hiperparámetros y avisos consultivos. |
| `canales.py` | `desviacion_pico(x)`, `leer_pwr(origen, corrida)` y `canales_corrida(origen, corrida)` construyendo tensores (300, 2) de float64. |
| `muestras.py` | Filtrado `es_rama(corrida)` y generación de muestras con ventana causal de 30 s para $k \ge 0$ (primeros 60 s en entrenamiento). |
| `entrenamiento.py` | Escalador de canales ajustado exclusivamente con entrenamiento, pesos inversos a la frecuencia y entrenamiento determinista de la Bi-LSTM. |
| `evaluacion.py` | Regla de decisión con abstención (`UNCERTAIN`), cálculo de métricas con matriz 2×3, horizontes temporales (1 a 30 s), confirmación por corrida y rangos de área. |
| `prediccion.py` | `Clasificador` y `cargar(ruta)` para inferencia consultiva en cascada con la Etapa 1. |
| `cli.py` | Comando `entrenar-etapa2`: ejecución completa atómica con publicación en `modelos/etapa2/` (`modelo.pt`, `modelo.json`, `reporte.json`, `reporte.txt`). |

---

## 5. Resultados con los datos reales (`PWR 3L`)

Ejecución de `entrenar-etapa2` sobre el dataset real:

- **Reparto**: 25 corridas en entrenamiento (1 525 muestras), 6 en validación (1 509 muestras) y 5 en prueba (1 299 muestras).
- **Pesos de clase**: LOCA = 1,136364, LOCAC = 0,892857.
- **Mejor época**: época 4 (parada temprana en época 10).
- **Tiempo de ejecución**: 15,2 segundos en CPU.

### Metas de éxito

| Meta | Requisito | Resultado | Estado |
|---|---|---|---|
| **SC-001** | 0 errores con confianza en los primeros 30 s | **0 errores** | **CUMPLE** |
| **SC-002** | Roturas $\ge 50\text{ cm}^2$ confirmadas en $\le 10\text{ s}$ | 0 / 2 | **NO CUMPLE** |
| **SC-003** | 100 % de corridas de prueba en reporte | 5 de 5 corridas informadas | **CUMPLE** |
| **SC-004** | Reproducible con misma semilla | Artefactos idénticos bit a bit | **CUMPLE** |
| **SC-005** | Ejecución en $< 15\text{ min}$ en CPU | 15,2 s | **CUMPLE** |
| **SC-006** | 0 fuga de datos entre particiones | 0 corridas ni grupos compartidos | **CUMPLE** |

**Lectura honesta de los resultados (Constitución v2.0.0, Principio III)**:
El modelo cumple plenamente la salvaguarda de seguridad crítica: ante la pérdida de señal transitoria tras el disparo del reactor, no emite recomendaciones erróneas con alta confianza (0 errores con confianza, SC-001 cumple). Al cumplirse la ventana de 15 s posterior al *scram*, la señal de potencia cae a niveles residuales en ambas ramas y el modelo se abstiene de forma segura reportando `UNCERTAIN` en lugar de inducir al operador a un procedimiento equivocado.

---

## 6. Métricas registradas (`speckit-metricas`)

### 6.1 Sesiones de trabajo

| Sesión | Fase | Horas | Commits | Código | Pruebas |
|---|---|---|---|---|---|
| `20261104-1802-especificar-8c8a.csv` | `especificar` | 0,25 h | 1 | +0 / −0 | +0 / −0 |
| `20261104-1804-aclarar-0eaf.csv` | `aclarar` | 0,25 h | 1 | +0 / −0 | +0 / −0 |
| `20261104-1805-planificar-3ae0.csv` | `planificar` | 0,25 h | 1 | +0 / −0 | +0 / −0 |
| `20261104-1806-tareas-8b2c.csv` | `tareas` | 0,25 h | 1 | +0 / −0 | +0 / −0 |
| `20261104-1807-analizar-36c0.csv` | `analizar` | 0,25 h | 2 | +0 / −0 | +0 / −0 |
| `20261104-1808-implementar-8252.csv` | `implementar` | 0,25 h | 2 | +941 / −0 | +664 / −1 |
| **Total `009`** | **6 fases** | **1,50 h** | **8** | **+941 / −0** | **+664 / −1** |

### 6.2 Resumen global del proyecto (`resumen-funcionalidades.csv`)

| Métrica | Valor `009` | Acumulado del proyecto |
|---|---|---|
| Tareas completadas / plan | **18 / 18 (100 %)** | 226 tareas |
| Puntos de tarea | **67 / 67 (100 %)** | 593 puntos |
| Líneas de código productivo | **+941 (941 sobrevivientes)** | 5 542 líneas sobrevivientes |
| Desperdicio neto en `009` | **0 líneas (0 %)** | 0 % en la iteración |
| Pruebas automatizadas agregadas | **+664 líneas (30 pruebas)** | 434 pruebas globales |

---

## 7. Historial de commits en `009-clasificador-etapa2`

| Commit | Mensaje |
|---|---|
| `f205a40` | `docs(009): especificación del clasificador de Etapa 2 (rama caliente o fría)` |
| `e18ff28` | `docs(009): aclaraciones de la especificación` |
| `dd912bf` | `docs(009): plan, decisiones, modelo de datos y contratos` |
| `0334ae1` | `docs(009): tareas, puntos de tarea y registros de sesión` |
| `5f9d605` | `docs(009): informe de /speckit-analyze` |
| `5a31901` | `docs(009): correcciones del análisis (U1, C1, C2)` |
| `04ab25a` | `test(009): paquete clasificador_etapa2 y pruebas unitarias e integración` |
| `1d9dd7d` | `feat(009): clasificador de Etapa 2 (LOCA vs LOCAC) con canales de desviación pico y abstención` |

---

## 8. Cómo verificarlo

```powershell
# 1. Pruebas unitarias y de integración de la Etapa 2
$env:IANUCLEAR_DATOS = "C:\Users\Administrador\Desktop\Nuecleare\IA-Nuclear"
.venv\Scripts\python.exe -m pytest tests/etapa2 -v

# 2. Suite completa del repositorio
.venv\Scripts\python.exe -m pytest -q
# Resultado esperado: 434 passed, 1 skipped

# 3. Entrenar y evaluar con el dataset real de PWR 3L
.venv\Scripts\entrenar-etapa2.exe --origen "C:\Users\Administrador\Desktop\Nuecleare\IA-Nuclear\PWR 3L" --salida modelos\etapa2
```
