# Research: Canal rápido de detección a 1 s con PWR 3L

Fuentes: `IA-Nuclear/RESULTADOS_IMPLEMENTACION_PWR3L.md`, `docs/PLAN_DATASET_PWR3L_DETECCION_RAPIDA.md`, `docs/RESUMEN_PWR3L.md`, `NuclearPowerPlantAccidentData/pctran_auto/README_AUTOMATIZACION.md`.

## D1. Dos canales, no un modelo único

- **Decision**: Canal lento (NPPAD, 10 s) y canal rápido (PWR 3L, 1 s); se juntan al final en el mapeo a procedimientos y en la fusión.
- **Rationale**: Son plantas distintas (2895 frente a 2705 MWt) y el PCTRAN demo no permite cargar la configuración del NPPAD; la demo dura 300 s.
- **Alternatives considered**: Mezclar datos con normalización relativa (descartado: no se puede validar el mismo transitorio en las dos plantas).

## D2. Quitar `WLR` y usar solo variables medibles

- **Decision**: 26 entradas medibles; `WLR`, `WBK`, `TPCT`, `DNBR`, reactividades y `FRCL` solo como etiqueta u objetivo.
- **Rationale**: `WLR` salta a ~64 000 t/h en el primer segundo de cualquier LOCA y no existe un medidor de caudal de fuga en planta; con ella la detección sería trivial.
- **Alternatives considered**: Conservarla (resultado inflado e indefendible).

## D3. Clase TRIP_OK y clase TRANS

- **Decision**: Gemelo de cada ATWS con el mismo evento y el disparo funcionando (TRIP_OK), y TRANS entre el evento y el disparo requerido.
- **Rationale**: Antes del retardo del scram, un ATWS y un disparo normal son físicamente iguales; sin ejemplos de disparo normal el detector aprende "pérdida de agua = ATWS".
- **Alternatives considered**: Solo clase ATWS (falsas alarmas de boración de emergencia).

## D4. Definición del tiempo de detección

- **Decision**: LOCA/LOCAC desde el inicio real de la fuga; ATWS/TRIP_OK desde el disparo requerido (o el más temprano entre el ATWS y su gemelo si son idénticos hasta ese instante: R91 = 33.0 s); el mínimo físico de ATWS es retardo del scram + 1.5 s.
- **Rationale**: Una meta de 3 s sin definir desde cuándo se mide no es verificable.
- **Alternatives considered**: Medir todo desde el inicio del evento (ATWS por turbina quedaría imposible).

## D5. Regla de confirmación a 1 s

- **Decision**: Clase correcta con confianza ≥ 0.80 durante 2 s seguidos (k = 2).
- **Rationale**: Con 1 dato por segundo, 3 evaluaciones gastarían todo el presupuesto de 3 s. k = 1 deja 14 de 40 casos TRIP_OK mal etiquetados en algún momento; k = 3 sube las medianas a 3.0 s.
- **Alternatives considered**: k = 1 y k = 3 (análisis de sensibilidad).

## D6. Modelo del clasificador

- **Decision**: HistGradientBoosting (exactitud balanceada 0.972).
- **Rationale**: Supera a Random Forest (0.964), GRU causal estandarizada (0.922) y regresión logística (0.899). Ablaciones: sin demanda de disparo 0.922 (necesaria); sin `P` 0.972 (no es atajo); sin picos enclavados 0.972.
- **Alternatives considered**: Bi-LSTM rápida del plan 5.2b; CNN 1D (no probada).

## D7. Compuerta ATWS determinista

- **Decision**: demanda de disparo + retardo del scram de esa señal + 1.5 s + PWNT > 20 % del nominal → ATWS confirmado; antes, "ATWS posible".
- **Rationale**: 20/20 ATWS y 0/20 falsos positivos. La versión anterior (PWNT > 90 %) marcaba 1 de 5 ATWS.
- **Alternatives considered**: Dejar la decisión solo al clasificador.

## D8. Novedad con monitores físicos

- **Decision**: Radiación (RM2, RM3, RM4), asimetría de presión entre GV, PORV abierta con presión baja, presión de contención sin radiación; umbral = 1.5 × envolvente de lo conocido.
- **Rationale**: IsolationForest dio 0–4 % de detección en OOD; los monitores dan 6/6 y 0/100 falsas.
- **Alternatives considered**: Autoencoder o divergencia KL (siguen siendo opciones para la feature 005).

## D9. Rama caliente/fría

- **Decision**: Excursión de PWR/PWNT previa al scram, enclavada.
- **Rationale**: Mismo fenómeno que en NPPAD (hot sube 0.6–5.7 puntos, cold 0.30–0.59). El primer intento falló (5–19 %) por no retener el pico.
- **Alternatives considered**: Solo ventanas de 10 s (olvidan el pico).

## D10. Ruido de sensores

- **Decision**: σ fijo por instrumento, aplicado en entrenamiento y en evaluación; peor caso de 3 realizaciones.
- **Rationale**: El simulador es determinista (en R01 la presión varía ~0.05 bar en 300 s) y los tiempos sin ruido son optimistas.
- **Alternatives considered**: Ruido proporcional al rango de cada corrida (fue el error previo).

## D11. Automatización de PCTRAN

- **Decision**: Escribir la falla directo en la base `.mdb` de PCTRAN, correr a ×16 (~1.5 min por corrida) y validar automáticamente.
- **Rationale**: Se evita depender de clics en coordenadas fijas y se manejan el fin de la demo y la revisión de calidad.
- **Alternatives considered**: Macro QuickMacro del NPPAD.

## D12. Pendientes de investigación

- Justificar con bibliografía los σ de ruido.
- Probar los monitores de novedad con eventos desconocidos distintos de los 6 usados al diseñarlos.
- Validar la regla de desacuerdo con el canal lento con datos reales (hoy solo sintéticos).
