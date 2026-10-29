# Research: Normalización solo con entrenamiento y verificación automática del paso de muestreo

**Fecha**: 2026-10-28 · **Spec**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md)

## 1. Medición empírica de `TIME` en los datasets reales

- **Hecho medido**:
  - **NPPAD** (`NuclearPowerPlantAccidentData/Operation_csv_data`): las 202 simulaciones de las cuatro clases (`Normal`, `LOCA`, `LOCAC`, `ATWS`) contienen la columna `TIME`, empiezan en `0.0` y avanzan con diferencia constante de `10.0` s en todas sus filas. Hoy `preparacion_datos` ni siquiera leía la columna `TIME` y fijaba `PASO_SEGUNDOS = 10` en `config.py`.
  - **PWR 3L** (`PWR 3L`): los 100 archivos de las cinco clases de entrenamiento (`NORM`, `LOCA`, `LOCAC`, `ATWS`, `TRIP_OK`) contienen la columna `TIME`, empiezan en `0` y avanzan con diferencia constante de `1.0` s en todas sus filas. Hoy `preparacion_pwr3l` comprobaba `tiempo != np.arange(len(tiempo))` asumiendo un paso fijo de 1 s y fijaba `PASO_SEGUNDOS = 1` en `config.py`.

## 2. Cálculo del paso de muestreo y tolerancia numérica

- **Decisión**: para cada archivo leído, tras convertir la columna `TIME` con la misma validación estricta que el resto de columnas (numérica, no vacía, finita):
  1. Verificar que tenga al menos 2 filas (`len(tiempo) >= 2`); si no, lanzar `ErrorDatos(relativo, "menos de 2 filas para calcular el paso de muestreo", VARIABLE_TIEMPO)`. (En NPPAD, además, se mantiene el requisito de al menos 150 pasos tras validar el tiempo).
  2. En PWR 3L, verificar que `tiempo[0] == 0.0` (según la aclaración Q2, regla de 002); si no, lanzar `ErrorDatos(relativo, f"el tiempo debe iniciar en 0 s (inicia en {tiempo[0]:g} s)", VARIABLE_TIEMPO)`.
  3. Calcular `diferencias = np.diff(tiempo)`.
  4. Si alguna diferencia es `<= 0`, detener en la primera fila `i` (`fila de datos i + 2`, base 1 para las filas de datos): `ErrorDatos(relativo, f"el tiempo no avanza en la fila de datos {i + 2} (paso {diferencias[i]:g} s)", VARIABLE_TIEMPO)`.
  5. Tomar `paso = float(diferencias[0])` y verificar que todas las diferencias cumplan `abs(d - paso) <= 1e-6 * paso` (tolerancia relativa `1e-6` definida en FR-002). Si alguna fila `i` se desvía más, lanzar `ErrorDatos(relativo, f"paso de muestreo no constante en la fila de datos {i + 2} (esperado {paso:g} s, encontrado {diferencias[i]:g} s)", VARIABLE_TIEMPO)`.
  6. Si `abs(paso - round(paso)) <= 1e-9 * max(1.0, abs(paso))`, normalizar `paso` a `int(round(paso))` si se requiere entero en JSON o conservar el `int`/`float` limpio (`10` o `1` cuando el paso es entero exacto, o `float` cuando tiene decimales como `0.5`), para mantener compatibilidad exacta en `metadata.json` (`"paso_segundos": 10` cuando es `10.0`).
- **Razón**: cumple FR-001 a FR-006 sin asumir ningún valor de diseño, detecta cualquier hueco, salto, repetición o retroceso en cualquier fila del archivo completo (incluso después de la fila 150 o 300), y soporta pequeñas imprecisiones de representación en texto de punto flotante (`1e-6` relativo).
- **Alternativas descartadas**: comparar contra `PASO_SEGUNDOS` fijo (viola FR-001 y aclaración Q1); validar solo las primeras 150 o 300 filas (viola FR-001 y lección F5 de 001).

## 3. Verificación de paso común entre todos los archivos del dataset

- **Decisión**: en `cargar_simulaciones` (NPPAD) y `cargar_corridas` (PWR 3L), el primer archivo leído fija el paso de referencia `(archivo_ref, paso_ref)`. Para cada archivo subsiguiente con paso `paso_i`, se comprueba `abs(paso_i - paso_ref) <= 1e-6 * paso_ref`. Si no coincide, se lanza `ErrorDatos(archivo_i, f"paso de muestreo ({paso_i:g} s) distinto al del resto del dataset ({paso_ref:g} s en {archivo_ref})", VARIABLE_TIEMPO)`. En PWR 3L se añade además la función pública `obtener_paso_comun(corridas)` que devuelve el paso común verificado (o lanza `ErrorDatos` si hay discordancia o no hay corridas leídas), dejando listo el dato para el reporte de 002.
- **Razón**: cumple FR-004 y FR-008. En PWR 3L las corridas `corta` sí se leen y también deben coincidir en paso de muestreo; las `descartada` y `ood` no se leen y no participan.

## 4. Publicación del paso medido y duración de muestra en NPPAD

- **Decisión**:
  - Eliminar `PASO_SEGUNDOS` de `src/preparacion_datos/config.py` y `src/preparacion_pwr3l/config.py` (añadiendo `VARIABLE_TIEMPO = "TIME"` en `preparacion_datos/config.py`).
  - Añadir `paso_segundos: Union[int, float]` a `Simulacion` (en `preparacion_datos/lectura.py`) y a `Corrida` (en `preparacion_pwr3l/descubrimiento.py`).
  - En `preparacion_datos/reporte.py`, `Resumen` recibe `paso_segundos` (por defecto calculado desde las simulaciones de `particion` si no se pasa explícitamente, para no romper llamadas existentes en pruebas unitarias de `construir_resumen`) y expone `paso_segundos` y `duracion_muestra_segundos = PASOS * paso_segundos`.
  - En `preparacion_datos/salida.py`, `construir_metadata(resumen)` toma `paso_segundos` y `duracion_muestra_segundos` de `resumen`.
  - En `preparacion_datos/reporte.py`, la sección 1 del reporte impreso muestra: `Semilla: {resumen.semilla} | Reparto 70/15/15 por simulación completa | {PASOS} pasos por muestra (paso medido de TIME: {resumen.paso_segundos:g} s, duración: {resumen.duracion_muestra_segundos:g} s)`.
- **Razón**: cumple FR-007 y mantiene compatibilidad con las pruebas unitarias existentes de `test_reporte.py` (donde `Simulacion` puede crearse sin `paso_segundos` en pruebas sintéticas de partición/reporte usando un valor por defecto o el medido de las simulaciones).

## 5. Normalización ajustada solo con entrenamiento y validación de forma

- **Decisión**:
  - En `src/preparacion_datos/escalado.py` y en el nuevo `src/preparacion_pwr3l/escalado.py`:
    - `ajustar_escalador(x_train)` verifica que `x_train` sea un arreglo 3D con `x_train.ndim == 3`, `x_train.shape[1:] == (PASOS, len(VARIABLES_ENTRADA))` y `x_train.shape[0] >= 1`. Si no, lanza `ValueError` con un mensaje descriptivo en español (FR-011).
    - `aplicar(escalador, x)` verifica que `x` sea un arreglo 3D con `x.ndim == 3` y `x.shape[1:] == (PASOS, len(VARIABLES_ENTRADA))`. Si `x.shape[0] == 0`, devuelve un arreglo vacío `(0, PASOS, F)` de tipo `float32` sin fallar; si la forma de pasos o variables no coincide, lanza `ValueError`.
    - El ajuste se realiza aplanando `x_train` a `(N_train * PASOS, F)` en `float64` con `StandardScaler().fit(filas)`. Las variables con `np.ptp(filas, axis=0) == 0` quedan con `escala = 1.0` (comportamiento nativo de `StandardScaler`) y sus nombres se listan en `variables_sin_varianza`.
- **Razón**: cumple FR-009, FR-010, FR-011, FR-012 y FR-013, manteniendo paquetes separados para NPPAD (12 variables, 150 pasos) y PWR 3L (26 variables, 300 pasos).

## 6. Corrección puntual de la prueba `test_libro_xlsx_con_extension_xls` en 002

- **Decisión**: en `tests/pwr3l/unit/test_pwr3l_lectura.py`, la prueba `test_libro_xlsx_con_extension_xls` comparaba `corrida.serie` con `ayudantes.datos_corrida(1)` en memoria con `np.array_equal`, fallando por 6e-14 debido a que `openpyxl` serializa números de punto flotante con 15–16 dígitos significativos al guardar el archivo `.xls` (xlsx). Se actualiza para comparar contra los valores leídos directamente de las celdas del libro con `openpyxl` (igual que la prueba de CSV compara contra `csv.DictReader`), verificando que `leer_corrida` no altera ningún valor del archivo.
- **Razón**: documentado en `ENTREGABLES-002.md` §5 y §6 (tarea T011 pendiente); dejar la suite completamente en verde permite verificar SC-005 sin falsos fallos.
