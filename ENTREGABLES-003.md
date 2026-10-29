# Tercera iteración SDD: `003-normalizacion-paso-muestreo`

**Actividad**: «Normalización y verificación automática del paso de muestreo» · **Desarrollador**: `cmbonifaz`
**Rama**: `003-normalizacion-paso-muestreo` (creada desde `main`) · **Fecha**: 2026-10-28
**Herramienta**: GitHub Spec Kit + `speckit-metricas` (`claude-opus-5-5` / `gemini-4-argon`) · **Constitución**: v2.0.0, sin cambios

> **Estado: iteración completa y convergente (`converged`).** Se ejecutaron todas las fases de Spec Kit (`/speckit-specify` → `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement` → `/speckit-converge`) y todos los comandos de métricas (`iniciar`, `cerrar`, `puntos`, `recolectar`, `calibrar`, `estimar`, `exportar`). Las 22 tareas (`T001`–`T022`, 48 puntos de tarea) y las 166 pruebas automatizadas están en verde.

---

## 1. Qué pide la actividad y cuál es su alcance

La actividad solicita dos garantías de integridad de datos y cero fuga de información:

1. **Normalizar las variables de entrada usando solo el conjunto de entrenamiento**:
   - Ajustar `StandardScaler` exclusivamente sobre las observaciones del conjunto `train` aplanando eje de muestras y eje temporal (`(N_train * T, F)`), y reutilizar los estadísticos `scaler_mean` y `scaler_scale` de entrenamiento para transformar `train`, `val` y `test` sin reajustar.
   - Rechazar entradas vacías o con dimensionalidad distinta a 3D `(N, T, F)` con un `ValueError` descriptivo.
2. **Calcular el paso de muestreo a partir de la columna `TIME` y detener el proceso si no es constante, en lugar de asumirlo**:
   - Eliminar las constantes fijas `PASO_SEGUNDOS = 10` (en `preparacion_datos`) y `PASO_SEGUNDOS = 1` (en `preparacion_pwr3l`).
   - Medir `Δt = TIME[i] - TIME[i-1]` en **todas las filas** de cada archivo (no solo dentro de la ventana recortada de `150` o `300` pasos), verificando que `Δt > 0`, que sea constante dentro del archivo (tolerancia relativa `1e-6`) y que coincida entre todos los archivos del mismo dataset.
   - Propagar el paso medido a las estructuras `Simulacion` / `Corrida`, al resumen de ejecución, a `metadata.json` (`paso_segundos` y `duracion_muestra_segundos = PASOS * paso_segundos`) y al reporte en consola.

### Delimitación del alcance en equipo

- Se aplicó en **ambas** tuberías del repositorio (`src/preparacion_datos/` para **NPPAD** y `src/preparacion_pwr3l/` para **PWR 3L**), manteniendo su separación estricta (Principio IV de la Constitución).
- En `preparacion_pwr3l` (funcionalidad `002`), el trabajo se limitó estrictamente a `config.py`, `descubrimiento.py`, `lectura.py` y `escalado.py` (junto con sus pruebas unitarias), **sin implementar ni modificar** `grupos.py`, `particion.py`, `salida.py`, `reporte.py` ni `cli.py`, que corresponden a otros integrantes del equipo.

---

## 2. Lo que se midió en los datos reales (referencia `IA-Nuclear`)

Se inspeccionaron los datasets reales en `C:\Users\Administrador\Desktop\Nuecleare\IA-Nuclear`:

| Planta / Dataset | Archivos inspeccionados | Columna de tiempo | Paso medido (`Δt`) | Constancia en todo el archivo |
|---|---|---|---|---|
| **NPPAD** (`NuclearPowerPlantAccidentData/Operation_csv_data`) | 202 CSV (`Normal`, `LOCA`, `LOCAC`, `ATWS`) | `TIME` (inicia en `0.0`) | `10` s (`10.0` s exactos) | 100 % constante en las 202 simulaciones; `199` usables (`>= 150` pasos), `3` cortas descartadas (`LOCAC/15.csv`, `LOCAC/44.csv`, `LOCA/24.csv`) |
| **PWR 3L** (`PWR 3L`) | 100 archivos de las 5 clases (`NORM`, `LOCA`, `LOCAC`, `ATWS`, `TRIP_OK`) | `TIME` (inicia en `0`) | `1` s (`1.0` s exactos) | 100 % constante en todas las corridas (`91` usables `>= 300` pasos y `9` cortas `< 300` pasos) |

---

## 3. Lo que se hizo, fase por fase (Spec Kit)

| # | Fase | Comando | Resultado | Artefactos principales |
|---|---|---|---|---|
| 1 | Rama y Especificar | `/speckit-specify` | Rama `003-normalizacion-paso-muestreo` creada desde `main`. Especificación con 3 historias de usuario (US1, US2, US3), 14 requisitos funcionales (`FR-001`–`FR-014`), 6 criterios de éxito (`SC-001`–`SC-006`) y checklist 16/16 PASS | [spec.md](specs/003-normalizacion-paso-muestreo/spec.md), [checklists/requirements.md](specs/003-normalizacion-paso-muestreo/checklists/requirements.md) |
| 2 | Aclarar | `/speckit-clarify` | 2 preguntas respondidas con el usuario (Q1: aceptar cualquier paso común constante `> 0` y publicarlo en metadatos; Q2: conservar `TIME[0] == 0` solo en PWR 3L y no exigirlo en NPPAD) | [spec.md](specs/003-normalizacion-paso-muestreo/spec.md) |
| 3 | Planificar | `/speckit-plan` | Plan técnico con *Constitution Check* (6 principios en cumplimiento), 6 decisiones de diseño en `research.md`, modelo de datos y contratos de CLI y salidas | [plan.md](specs/003-normalizacion-paso-muestreo/plan.md), [research.md](specs/003-normalizacion-paso-muestreo/research.md), [data-model.md](specs/003-normalizacion-paso-muestreo/data-model.md), [contracts/cli.md](specs/003-normalizacion-paso-muestreo/contracts/cli.md), [contracts/salidas.md](specs/003-normalizacion-paso-muestreo/contracts/salidas.md), [quickstart.md](specs/003-normalizacion-paso-muestreo/quickstart.md) |
| 4 | Tareas y Puntos | `/speckit-tasks` + `/speckit-metricas-puntos` | 22 tareas (`T001`–`T022`) organizadas en 6 fases con enfoque TDD; línea base de **48 puntos de tarea** | [tasks.md](specs/003-normalizacion-paso-muestreo/tasks.md), [puntos-tarea.csv](specs/003-normalizacion-paso-muestreo/puntos-tarea.csv) |
| 5 | Analizar | `/speckit-analyze` | 0 hallazgos críticos/altos/medios y 3 hallazgos bajos (`I1`, `U1`, `C1`); cobertura del 100 % de los 14 FR y 6 SC. Las 3 correcciones se aplicaron antes de implementar | [analisis-inicial.md](specs/003-normalizacion-paso-muestreo/analisis-inicial.md) |
| 6 | Implementar | `/speckit-implement` | Implementación completa de las 22 tareas (`T001`–`T022`), 166 pruebas en verde (`1 skipped`) y validación contra el dataset NPPAD real | `src/preparacion_datos/`, `src/preparacion_pwr3l/`, `tests/` |
| 7 | Convergencia | `/speckit-converge` | Estado **`converged`**: 22/22 tareas `[X]`, 14/14 FR verificados, 6/6 SC cumplidos, 0 brechas pendientes | [tasks.md](specs/003-normalizacion-paso-muestreo/tasks.md) |

### Hallazgos de `/speckit-analyze` y cómo se resolvieron

| ID | Severidad | Hallazgo | Corrección aplicada (`da818dc`) |
|---|---|---|---|
| `I1` | Baja | `spec.md` mencionaba `test_cli_reporte.py` y `tasks.md` referenciaba `test_cli.py` para las pruebas de integración de fallo de `TIME` | Se incluyeron ambos archivos en `T005` (`tests/integration/test_cli.py` y `tests/integration/test_cli_reporte.py`) |
| `U1` | Baja | `T019` no detallaba el nombre de la función ni la firma para verificar el paso común entre corridas de PWR 3L | Se especificó `obtener_paso_comun(corridas)` en `src/preparacion_pwr3l/lectura.py` y su invocación desde `cargar_corridas` |
| `C1` | Baja | `FR-006` exigía verificar también los archivos cortos descartados en `cargar_simulaciones`, pero no tenía caso explícito en `T003` | Se añadió en `T003` el caso de archivo corto (`< 150` filas) con `TIME` válido pero paso distinto al del resto del dataset |

---

## 4. Cambios técnicos implementados

### 4.1 Tubería NPPAD (`src/preparacion_datos/`)

- **`src/preparacion_datos/config.py`**:
  - Se eliminó `PASO_SEGUNDOS = 10` y se añadió `VARIABLE_TIEMPO = "TIME"`.
- **`src/preparacion_datos/lectura.py`**:
  - Se añadió el campo `paso_segundos: int | float` al dataclass `Simulacion`.
  - Se implementaron `_calcular_paso_tiempo(df, ruta)` y `_normalizar_paso(valor)` con tolerancia relativa `TOLERANCIA_RELATIVA_PASO = 1e-6`:
    - Verifica presencia y tipo numérico sin `NaN`/`inf` de `TIME`, al menos 2 filas (`ValueError` si tiene `< 2` filas), avance estrictamente positivo (`Δt > 0`) y paso constante en **todas las filas del CSV** (incluso más allá de la fila 150).
  - En `cargar_simulaciones`, se verifica el paso de **todos** los archivos (tanto usables `>= 150` pasos como cortos `< 150` pasos) y se detiene con `ValueError` nombrando los dos archivos y sus pasos si alguno difiere del primer archivo válido.
- **`src/preparacion_datos/escalado.py`**:
  - Se añadieron validaciones explícitas en `ajustar_escalador(x_train)` y `aplicar(escalador, x)` para exigir arreglos 3D con ` shape[1:] == (150, 12)` y rechazar `x_train` vacío (`N == 0`), soportando `N == 0` en `aplicar` sin error.
- **`src/preparacion_datos/reporte.py`, `src/preparacion_datos/salida.py` y `src/preparacion_datos/cli.py`**:
  - `Resumen`, `construir_resumen`, `formatear_reporte` y `guardar_artefactos` reciben `paso_segundos` medido desde las simulaciones cargadas y calculan dinámicamente `duracion_muestra_segundos = PASOS * paso_segundos` tanto en `metadata.json` como en la sección `1. CONFIGURACIÓN DE VENTANA` del reporte en consola.

### 4.2 Tubería PWR 3L (`src/preparacion_pwr3l/`)

- **`src/preparacion_pwr3l/config.py`**:
  - Se eliminó `PASO_SEGUNDOS = 1`.
- **`src/preparacion_pwr3l/descubrimiento.py`**:
  - Se añadió `paso_segundos: int | float | None = None` al dataclass `Corrida`.
- **`src/preparacion_pwr3l/lectura.py`**:
  - En `_validar_tabla`, se mantuvo la regla `TIME[0] == 0` propia de PWR 3L y se reemplazó la comparación contra `1.0` fijo por el cálculo de `Δt = TIME[1] - TIME[0]` (> 0) y su verificación con tolerancia relativa `1e-6` sobre todas las filas del archivo.
  - Se asigna `corrida.paso_segundos` tanto en corridas usables (`>= 300` filas) como en corridas cortas (`< 300` filas).
  - Se implementó `obtener_paso_comun(corridas)` y se integró al final de `cargar_corridas` para detener el proceso si una corrida usable o corta tiene un paso distinto al del resto del dataset.
- **`src/preparacion_pwr3l/escalado.py` (nuevo módulo)**:
  - Implementa `Escalador`, `ajustar_escalador(x_train)` y `aplicar(escalador, x)` para tensores `(N, 300, 26)` en `float64`, ajustando `StandardScaler` exclusivamente con `x_train` y manejando `scale_ == 0` sin producir `NaN`/`inf`.
- **Corrección de prueba previa en `tests/pwr3l/unit/test_pwr3l_lectura.py`**:
  - Se corrigió `test_libro_xlsx_con_extension_xls` leyendo el archivo `.xls` en modo binario con `openpyxl.load_workbook`, dejando el 100 % de la suite de `tests/pwr3l` en verde.

---

## 5. Métricas registradas (`speckit-metricas`)

### 5.1 Sesiones de trabajo de `003-normalizacion-paso-muestreo`

| Archivo de sesión | Fase | Inicio–Fin | Horas (mín. sesión) | Modelo IA | Commits | LOC Código | LOC Pruebas |
|---|---|---|---|---|---|---|---|
| `20261028-2008-especificar-deb2.csv` | `especificar` | 20:08–20:12 | 0.25 h | `claude-opus-5-5` | 1 | +0 / −0 | +0 / −0 |
| `20261028-2012-aclarar-4055.csv` | `aclarar` | 20:12–20:14 | 0.25 h | `claude-opus-5-5` | 1 | +0 / −0 | +0 / −0 |
| `20261028-2014-planificar-ccba.csv` | `planificar` | 20:14–20:24 | 0.25 h | `claude-opus-5-5` | 1 | +0 / −0 | +0 / −0 |
| `20261028-2024-tareas-2510.csv` | `tareas` | 20:24–20:28 | 0.25 h | `gemini-4-argon` | 1 | +0 / −0 | +0 / −0 |
| `20261028-2028-analizar-c997.csv` | `analizar` | 20:28–20:30 | 0.25 h | `gemini-4-argon` | 2 | +0 / −0 | +0 / −0 |
| `20261028-2030-implementar-2d92.csv` | `implementar` | 20:30–20:42 | 0.25 h | `gemini-4-argon` | 3 | +266 / −36 | +376 / −31 |
| **Total `003`** | **6 fases** | **20:08–20:42** | **1.50 h** | — | **9** | **+266 / −36** | **+376 / −31** |

### 5.2 Resumen de tamaño, puntos de tarea y desperdicio (`metricas/salidas/`)

| Indicador | Valor en `003-normalizacion-paso-muestreo` | Acumulado del proyecto (`IANuclear`) |
|---|---|---|
| Historias de usuario | 3 | 9 |
| Requisitos funcionales (FR) | 14 | 43 |
| Criterios de éxito (SC) | 6 | 22 |
| Escenarios de aceptación | 13 | 32 |
| Tareas completadas / planeadas | **22 / 22 (100 %)** | 61 / 95 |
| Puntos de tarea completados / plan | **48 / 48 puntos (100 %)** | 246 puntos totales |
| Líneas de código productivo (`loc_agregadas` / `loc_sobrevivientes`) | **+266 agregadas / 266 sobrevivientes** | 1237 agregadas / 1187 sobrevivientes |
| Líneas eliminadas por cambio de requisito (`loc_elim_requisito`) | 36 (reemplazo de `PASO_SEGUNDOS` fijo) | 36 |
| Desperdicio neto en `003` (`loc_desperdicio_total`) | **0 líneas (0 %)** | 50 líneas (4.04 % global) |
| Líneas de pruebas automatizadas (`loc_pruebas_agregadas`) | **+376 / −31** | +1877 / −34 |

---

## 6. Historial de commits en `003-normalizacion-paso-muestreo`

| Commit | Mensaje |
|---|---|
| `f9832dd` | `docs(003): especificación de normalización solo con entrenamiento y verificación del paso de muestreo` |
| `a1ec10c` | `docs(003): aclaraciones de la especificación` |
| `e2a06a3` | `docs(003): plan, decisiones, modelo de datos y contratos` |
| `83e9e78` | `docs(003): tareas, puntos de tarea y registros de sesión` |
| `bac04f4` | `docs(003): informe de /speckit-analyze` |
| `da818dc` | `docs(003): correcciones del análisis` |
| `928af38` | `test(003): pruebas de medición del paso desde TIME y normalización con entrenamiento` |
| `48046b3` | `feat(003): verificación automática del paso desde TIME y normalización solo con entrenamiento` |
| `9ca35da` | `docs(003): marcar tareas completadas y actualizar puntos de tarea` |

---

## 7. Cómo verificar la entrega

```powershell
# 1. Ejecutar la suite completa de pruebas (NPPAD + PWR 3L)
.venv\Scripts\python.exe -m pytest -q
# Resultado esperado: 166 passed, 1 skipped

# 2. Ejecutar solo las pruebas nuevas/actualizadas de 003
.venv\Scripts\python.exe -m pytest tests/unit/test_lectura.py tests/unit/test_escalado.py tests/unit/test_reporte.py tests/integration/test_cli.py tests/integration/test_cli_reporte.py tests/pwr3l/unit/test_pwr3l_lectura.py tests/pwr3l/unit/test_pwr3l_escalado.py -v

# 3. Probar extremo a extremo con el dataset NPPAD real de IA-Nuclear
.venv\Scripts\preparar-datos.exe --data-dir "C:\Users\Administrador\Desktop\Nuecleare\IA-Nuclear\NuclearPowerPlantAccidentData\Operation_csv_data" --output-dir "$env:TEMP\nppad_003_check"
```
