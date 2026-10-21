# Research: Compuertas deterministas, rechazo de la IA y modo sombra

Fuentes: `IA-Nuclear/docs/planning/plan-de-trabajo1.0.md` (Fase 5), `docs/PLAN_DATASET_PWR3L_DETECCION_RAPIDA.md` §5, `RESULTADOS_IMPLEMENTACION_PWR3L.md`, `fusion_pwr3l.py`, `eop_mapper.py`.

## D1. Compuerta ATWS — ya resuelta

- **Decision**: Reutilizar `atws_gate_series` (demanda de disparo + retardo del scram + 1.5 s + PWNT > 20 %).
- **Rationale**: 20/20 ATWS y 0/20 falsos positivos; prevalece sobre el clasificador en `fuse_outputs`.
- **Alternatives considered**: Ninguna; ya validada.

## D2. Compuerta de DNBR — RESUELTA (Q1)

- **Decision**: Umbral **relativo**: caída porcentual del DNBR estimado respecto al DNBR nominal de la condición inicial, con porcentaje configurable. Solo se ordena disparo si el reactor no ha disparado (un TRIP_OK ya disparó). No se evalúa con estimaciones no fiables (ATWS). Se entrega a la experta la tabla de DNBR por clase con el 1.3 literal como referencia, y ella confirma el porcentaje.
- **Rationale**: El 1.3 literal nunca se activa (en PCTRAN el DNBR parte de ~2.3 y llega a ~141). El umbral relativo no depende de la escala de PCTRAN y es el más defendible. Dato de la clarificación: en PWR 3L el peor ATWS cae 28 % (2.29 → 1.65); se verifica al construir la tabla.
- **Alternatives considered**: 1.3 literal (cumple en el papel, no demuestra nada); umbral absoluto calibrado sobre PCTRAN (obliga a justificar el valor con los datos).

## D3. Compuerta de PCT — PENDIENTE de la experta

- **Decision**: Umbral configurable; valor y escala los fija la experta. Mientras tanto se reporta contra el 900 °C informativo y contra 1204 °C (10 CFR 50.46, 2200 °F) como referencia.
- **Rationale**: La PCT de PCTRAN no es una temperatura real de vaina: en PWR 3L parte de ~550 °C y no pasa de 606 °C, así que un límite real nunca se alcanzaría.
- **Alternatives considered**: Límite absoluto regulatorio; límite relativo (subida desde el valor inicial); valor fijado por la experta.

## D4. Rechazo por confianza

- **Decision**: Reutilizar el umbral 0.80 de `UNCERTAINTY_THRESHOLD`; añadir el evento de rechazo y el respaldo.
- **Rationale**: Hoy la baja confianza ya produce INCIERTO pero no se registra como "rechazo + respaldo".
- **Alternatives considered**: Solo mostrar INCIERTO (no cumple FR-006).

## D5. Rechazo por deriva KL

- **Decision**: Histograma de cada variable de entrada en ventana deslizante contra su distribución de entrenamiento; KL promedio (o máximo) > 0.1 → rechazo. En el canal rápido, los monitores de novedad físicos cuentan como la señal equivalente.
- **Rationale**: Es el criterio del plan; los monitores físicos ya detectan 6/6 y 0/100 falsas.
- **Alternatives considered**: Autoencoder o IsolationForest (este último dio 0–4 % de detección en OOD).

## D6. Respaldo en espera fría — RESUELTA (Q2)

- **Decision**: Algoritmos deterministas clásicos, sin IA: setpoints automáticos de la planta de la guía de la experta (disparo por presión baja 132.2 bar, HPI 118.1 bar, contención 1.30 bar, nivel bajo de GV 17 %, acumuladores 43.27 bar, RHR 11.36 bar) más el mapeo a E-0, la compuerta ATWS y los monitores de novedad (que ya son deterministas). El "< 1 s" es la latencia de conmutar del resultado de la IA al respaldo (software, medible), no el tiempo de detección.
- **Rationale**: Los setpoints están en `docs/Thresholds_EOP_Timeline_simplified.pdf`; son independientes del modelo estadístico rechazado (FR-012).
- **Alternatives considered**: Solo mostrar "IA rechazada" sin recomendar (descartada: pierde el respaldo útil).

## D7. Referencia de expertos para el modo sombra — RESUELTA (Q3)

- **Decision**: Dos niveles. (1) Referencia automática: la guía de la experta (procedimiento por clase y tiempos de referencia medidos en R03, R09 y R28, con la nota de que el detector debe compararse contra ellos). (2) Revisión real: la experta anota a ciegas unas 10 corridas con el procedimiento que esperaría.
- **Rationale**: No hay registros de operadores reales; el plan habla de "decisiones teóricas de un comité de expertos". El nivel 1 es coherente con el plan y el nivel 2 permite decir que hubo criterio experto y no solo una tabla.
- **Alternatives considered**: Solo referencia automática (menos defendible); comité formal (no disponible).

## D8. Formato del log de sombra

- **Decision**: JSON Lines, un registro por decisión; contrato en `contracts/shadow-log.md`.
- **Rationale**: Apendable, auditable, fácil de filtrar; permite generar la consola sin recalcular.
- **Alternatives considered**: CSV (pierde estructura), JSON único.

## D9. Eventos fuera de distribución del canal lento

- **Decision**: Usar como OOD las 14 categorías de NPPAD no entrenadas: FLB, LACP, LLB, LOF, LR, MD, RI, RW, SGATR, SGBTR, SLBIC, SLBOC, SP, TT.
- **Rationale**: Existen en `Operation_csv_data/` (con 1 a 110 corridas cada una) y no se usaron para entrenar; dan una prueba real para el canal lento.
- **Alternatives considered**: Probar solo el canal rápido (deja el lento sin verificación OOD).

## D10. Validación de la fusión entre canales

- **Decision**: Pruebas con datos sintéticos (coincidencia, desacuerdo, canal ausente) y declarar la limitación; opcional: probar el canal lento sobre PWR 3L con 1 dato de cada 10 y normalización relativa.
- **Rationale**: No existe el mismo transitorio en las dos plantas; PCTRAN demo no carga la configuración de NPPAD.
- **Alternatives considered**: Licencia completa de PCTRAN para generar el mismo transitorio (pregunta 7 abierta).
