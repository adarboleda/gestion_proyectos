# Data Model: Normalización solo con entrenamiento y verificación automática del paso de muestreo

**Fecha**: 2026-10-28 · **Plan**: [plan.md](plan.md)

## Entidades modificadas y nuevas

### 1. `Simulacion` (`preparacion_datos.lectura.Simulacion`) — NPPAD

| Campo | Tipo | Descripción |
|---|---|---|
| `clase` | `str` | `NORM`, `LOCA`, `LOCAC` o `ATWS` |
| `etiqueta` | `int` | `0`, `1`, `2` o `3` |
| `severidad` | `int` o `None` | Número del archivo para `LOCA`/`LOCAC`; `None` para `NORM`/`ATWS` |
| `archivo` | `str` | Ruta relativa al origen (p. ej. `LOCA/7.csv`) |
| `serie` | `np.ndarray` o `None` | `(150, 19)` `float64`: 12 variables de planta + 7 márgenes |
| `paso_segundos` | `int \| float` o `None` | **Nuevo**: paso de muestreo medido de `TIME` en el archivo completo (`None` antes de leer) |

**Invariantes de lectura (NPPAD)**:
- El archivo debe contener `TIME` y las 19 variables de `VARIABLES`.
- Todos los valores de `TIME` y de `VARIABLES` en **todas** las filas del archivo son numéricos, no vacíos y finitos.
- El archivo tiene al menos 2 filas para medir el paso y al menos `PASOS = 150` filas en total.
- `diferencias = np.diff(tiempo)`: todas las diferencias son `> 0` y cumplen `|d - diferencias[0]| <= 1e-6 * diferencias[0]`.
- En `cargar_simulaciones(origen)`, todas las simulaciones leídas tienen el mismo `paso_segundos` dentro de la tolerancia `1e-6` relativa.

---

### 2. `Corrida` (`preparacion_pwr3l.descubrimiento.Corrida`) — PWR 3L

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | `str` | Identificador `R<n>[letra]` (p. ej. `R07b`) |
| `clase` | `str` | `NORM`, `LOCA`, `LOCAC`, `ATWS`, `TRIP_OK` u `OOD` |
| `origen` | `str` | `manual` o `auto` |
| `archivo` | `str` | Ruta relativa al origen con `/` |
| `area` | `int` o `None` | Área de rotura en cm² (`LOCA` y `LOCAC`) |
| `gemela` | `str` o `None` | Id de la gemela `ATWS`/`TRIP_OK` |
| `estado` | `str` | `pendiente`, `usable`, `corta`, `descartada` u `ood` |
| `filas` | `int` o `None` | Número total de filas del archivo leído |
| `serie` | `np.ndarray` o `None` | `(300, 33)` `float64`: 26 entradas + 7 márgenes (solo `usable`) |
| `paso_segundos` | `int \| float` o `None` | **Nuevo**: paso de muestreo medido de `TIME` en el archivo completo (para corridas `usable` y `corta`; `None` para `descartada` y `ood`) |

**Invariantes de lectura (PWR 3L)**:
- El archivo tiene al menos 2 filas; `TIME[0] == 0.0`.
- `diferencias = np.diff(tiempo)`: todas son `> 0` y cumplen `|d - diferencias[0]| <= 1e-6 * diferencias[0]`.
- En `cargar_corridas(origen)` y en `obtener_paso_comun(corridas)`, todas las corridas leídas (`usable` y `corta`) comparten el mismo `paso_segundos` dentro de `1e-6` relativo.

---

### 3. `Escalador` (`preparacion_datos.escalado.Escalador` y `preparacion_pwr3l.escalado.Escalador`)

| Campo | Tipo (NPPAD) | Tipo (PWR 3L) | Descripción |
|---|---|---|---|
| `scaler` | `StandardScaler` | `StandardScaler` | Objeto ajustado exclusivamente con `x_train` |
| `media` | `ndarray (12,) float64` | `ndarray (26,) float64` | Media por variable de entrada en entrenamiento |
| `escala` | `ndarray (12,) float64` | `ndarray (26,) float64` | Desviación estándar por variable en entrenamiento (`1.0` si no tiene varianza) |
| `variables_sin_varianza` | ` list[str]` | `list[str]` | Nombres de las variables de entrada con varianza cero en entrenamiento |
| `filas_ajuste` | `int` | `int` | `N_train * 150` (NPPAD) o `N_train * 300` (PWR 3L) |

**Reglas de validación**:
- `ajustar_escalador(x_train)`: exige `x_train.ndim == 3`, `x_train.shape[0] >= 1` y `x_train.shape[1:] == (PASOS, F)` (`(150, 12)` en NPPAD; `(300, 26)` en PWR 3L). En caso contrario lanza `ValueError`.
- `aplicar(escalador, x)`: exige `x.ndim == 3` y `x.shape[1:] == (PASOS, F)`. Devuelve `ndarray` de la misma forma y tipo `float32`.

---

### 4. `Resumen` (`preparacion_datos.reporte.Resumen`) — NPPAD

Se añaden los campos:
- `paso_segundos: int | float`: paso común medido del dataset.
- `duracion_muestra_segundos: int | float`: `PASOS * paso_segundos` (p. ej. `150 * 10 = 1500`).
