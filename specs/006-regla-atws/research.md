# Research: Regla determinista de ATWS

**Fecha**: 2026-11-04 · **Spec**: [spec.md](spec.md)

Medición previa sobre las corridas ATWS y TRIP_OK reales (script de exploración, no versionado):

- Tras un scram correcto, PWNT cae a ~5.7 % del nominal en 1 s, en todos los TRIP_OK.
- En los ATWS, PWNT queda entre ~33 % y ~117 % varios segundos después de la demanda. Los más bajos son los ATWS por pérdida de caudal (RCP-A trip): la realimentación de reactividad baja la potencia aunque no haya scram.
- El scram llega tras la señal del anunciador con un retardo que depende de la señal:

  | Señal | Retardo hasta el scram |
  |---|---|
  | `Scram …` | 0.5 s |
  | Low SG Level | 1.0 s |
  | RCP-A trip | 2.5 s con pérdida de red; 1.0 s con rotor bloqueado |
  | Turbine trip | 5.0 s |

- R97 y R98 (ATWS por extracción de barras) no registran ninguna señal en el `.dat`: su demanda real es el alto flujo (PWNT ≥ 118 %).
- Prototipo con el reparto de la rama 002: en entrenamiento, el ATWS con menor flujo se queda en 37 % y el no-ATWS con mayor flujo en 5.7 %. Umbral ≈ 21 %. En validación y prueba detecta 3/3 y 3/3 ATWS, sin falsas alarmas.

## 1. Señal de disparo

- **Decisión**: la primera línea del registro de eventos que contenga una señal del sistema de protección (`Scram `, `Low SG Level`, `Turbine trip`/`Turbine Trip`, `RCP-A trip`, `Hi RX`, `High RX`, `Lo RX`, `low RX`, `OTDT`, `OPDT`, `Hi Flux`, `High Flux`), excluida `Reactor Scram`, o el primer segundo con PWNT ≥ 118 %, lo que ocurra antes. El tipo se normaliza: se quitan el valor final (`17.0 %`, `93.4 %`) y `Control Change…`, y se pasa a minúsculas (`turbine trip`).
- **Razón**: FR-002 y la primera aclaración. Son las mismas señales que usa el validador de corridas del proyecto; el alto flujo cubre los ATWS sin anunciador.
- **Pendiente**: validar con la experta, como pide KAN-22.

## 2. Retardo de la lógica de protección

- **Decisión**: por tipo de señal, el mayor `t(Reactor Scram) − t(señal)` observado en las corridas de entrenamiento que tienen ambas (TRIP_OK, LOCA, LOCAC). A un tipo no visto se le asigna el mayor de todos (aclaración 1).
- **Razón**: medir «2 s desde la señal» daría falsas alarmas en los TRIP_OK por turbina, cuyo scram llega a los 5 s. Tomar el mayor es conservador: espera más antes de declarar ATWS. Se mide en entrenamiento para no usar validación ni prueba (principio II).

## 3. Decisión

- **Decisión**:
  - Demanda: `t_d = t_señal + retardo`.
  - Instante de decisión: `k = ⌈t_d + 2⌉`, el primer segundo de la muestra a ≥ 2 s de la demanda.
  - Flujo relativo: `PWNT[k] / PWNT[0] · 100`. Si supera el umbral, «posible ATWS».
  - Si `k > 299`, «sin ATWS» con motivo «decisión fuera de la ventana».
  - Tiempo de detección desde la demanda: `k − t_d`. Por el muestreo de 1 s queda entre 2 y 3 s por construcción.
- **Razón**: es la regla de KAN-22. Usar el valor relativo al inicial hace la regla independiente de la condición inicial (todas arrancan a ~100 %).

## 4. Umbral

- **Decisión**: se usan los flujos en el instante de decisión de las corridas de entrenamiento con demanda.
  - Si `min(ATWS) > max(no-ATWS)`: umbral = punto medio entre ambos.
  - Si se solapan: umbral = `min(ATWS)` menos un épsilon, el mayor que no omite ningún ATWS, y se cuentan las falsas alarmas de entrenamiento (aclaración 2).
  - Se informan mínimo, máximo y separación.
  - Solo entran las corridas con demanda. Un ATWS sin demanda se cuenta como omisión, también en entrenamiento, y se advierte (análisis U1).
  - Si `PWNT[0]` ≤ 0, la evaluación se detiene con un error que nombra la corrida (análisis A1).

## 5. Datos y reparto

- **Decisión**: se llama a `preparacion_pwr3l.lectura.cargar_corridas`, `grupos.formar_grupos` y `particion.repartir` (004) con la misma semilla, y se verifica con `verificar_reparto(corridas, reparto)`. La serie de PWNT es la columna `PWNT` de los 300 s de cada corrida usable. No se lee `data_processed_pwr3l/`.
- **Razón**: el mismo reparto que el resto del canal rápido (005 también usa 004), sin depender de que alguien haya ejecutado `preparar-pwr3l` antes.

## 6. Registro de eventos

- **Decisión**: el único `*.dat` de la carpeta de la corrida (en `auto`, `transientlist.dat`), leído como latin-1 porque PCTran escribe en ANSI. Formato de línea: `NNNNNN.N sec, texto`. Si hay cero o más de un `.dat`, error que nombra la carpeta.

## 7. Salida

- **Decisión**: `regla.json` (regla calibrada), `evaluacion.csv` (una fila por corrida) y `resumen.json` (tablas por conjunto, tiempos, meta, advertencias y limitaciones), publicados todos o ninguno en `resultados_regla_atws/`, que se añade a `.gitignore`.
