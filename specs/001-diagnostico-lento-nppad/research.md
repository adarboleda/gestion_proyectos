# Research: Diagnóstico de accidentes sobre NPPAD

Decisiones tomadas durante las cuatro iteraciones de la Fase 2. Fuente: `IA-Nuclear/NuclearPowerPlantAccidentData/pipeline/README_FASE2.md`.

## D1. Esquema jerárquico de dos etapas

- **Decision**: Etapa 1 (NORM / familia LOCA / ATWS) y Etapa 2 (hot / cold leg), cada una con su Bi-LSTM.
- **Rationale**: Responde literalmente a la nota de clarificación funcional: clasificar primero NORM/LOCA/ATWS y, solo si es LOCA, caracterizar la rama. Permite hiperparámetros propios (Etapa 1: hidden 32, pooling `last_and_mean`; Etapa 2: hidden 48, pooling `attention`).
- **Alternatives considered**: Clasificador plano de 4 clases (iteración 1: 60.6 % en 4 clases; archivado).

## D2. Partición pareada por severidad para LOCA/LOCAC

- **Decision**: la severidad N de LOCA y la de LOCAC van siempre al mismo conjunto (70/15/15).
- **Rationale**: El split independiente dejaba severidades de prueba casi disjuntas entre clases; la Etapa 2 daba 43.3 %.
- **Alternatives considered**: Split independiente por archivo (Fase 1): insuficiente por sí solo para la rama, pero se mantiene para NORM/ATWS.

## D3. Canal de "desviación pico" de `PWR`/`PWNT`

- **Decision**: `peak_dev(t) = running_max(raw(0..t)) − raw(0)`, causal, sin dividir por el máximo, re-escalado con escalador propio (solo train). Etapa 2 pasa a 14 entradas (12 + 2).
- **Rationale**: Al escanear las 96 variables, el pico de sobrepotencia previo al disparo separa LOCA de LOCAC (99 de 100 severidades; d de Cohen ≈ 4.7). La Bi-LSTM no lo veía porque el rango de `PWR` tras el disparo domina el escalado global. Confirmado con regresión logística independiente: 99.0 % ± 2.0 %.
- **Alternatives considered**: Canal de "forma" auto-normalizado de `WECS`/`WLR`/`LVCR` (iteración 3): 48.0 % ± 4.85 %. El "d de Cohen ≈ 2" original era un artefacto de calcularlo contra la variabilidad intra-curva.

## D4. Criterio de selección de checkpoint

- **Decision**: mejora = `val_macro_f1` mayor, o igual con `val_loss` menor.
- **Rationale**: Con F1 saturado desde la época 1 el checkpoint quedaba fijo en la época menos entrenada (confianza media 0.57); con el nuevo criterio sube a 0.895 y la tasa de INCIERTO baja de 90.9 % a 12.1 %. Exactitud y confianza son cosas distintas.
- **Alternatives considered**: Seleccionar solo por F1 estricto.

## D5. Umbral de incertidumbre y confirmación sostenida

- **Decision**: UNCERTAIN si confianza < 0.80; diagnóstico confirmado tras 3 evaluaciones seguidas (`sustain_count = 3`).
- **Rationale**: Definido en el plan y en la nota funcional ("first correct diagnosis that satisfies the stability criterion").
- **Alternatives considered**: k = 1 (más rápido, más falsas alarmas). Con datos a 1 s esta regla cambia a k = 2 (feature 003).

## D6. Meta de < 3 s en el canal lento

- **Decision**: Declararla no alcanzable con datos a 10 s y reportar el tiempo como "confirmación" (minutos).
- **Rationale**: Con 3 evaluaciones seguidas a 10 s, el mínimo teórico ya es ~30 s.
- **Alternatives considered**: Re-muestrear NPPAD: imposible, el dato ya está a 10 s. Se creó el canal rápido con PWR 3L (feature 003).

## D7. Pendiente: ablación sin `WLR`

- **Decision**: Reentrenar el canal lento sin `WLR` en `fase2_output_sinWLR/` y reportar ambas versiones.
- **Rationale**: `WLR` no es medible en una planta real; si la exactitud se mantiene, el resultado gana credibilidad; si baja, se declara.
- **Alternatives considered**: Dejarlo como está y declarar la limitación (menos defendible ante jurado).
