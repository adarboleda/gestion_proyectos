# Research: Informe técnico final y documentación consolidada

## D1. Estructura del informe

- **Decision**: 8 capítulos + anexo de reproducción (ver `plan.md`).
- **Rationale**: Sigue el orden del plan de trabajo (datos → modelos → EOP/XAI → compuertas/sombra) y separa resultados, cumplimiento y limitaciones para que el jurado vea cada uno.
- **Alternatives considered**: Un capítulo por fase (repite contenido entre canales); un solo documento sin separar limitaciones.

## D2. Tabla de cumplimiento generada

- **Decision**: `build_tabla_cumplimiento.py` lee `fase2_output/metrics_fase2.json`, `fase3_output/metrics_fase3.json`, `pwr3l_output/acceptance/acceptance.json`, `fase4_output/metrics_fase4.json` y `fase5_output/shadow_summary.json` y escribe la tabla.
- **Rationale**: Hay cifras con versiones distintas en documentos antiguos (12 vs 17 pruebas; ATWS 2.0 vs 2.25 s). Generarla evita transcribir mal.
- **Alternatives considered**: Tabla a mano.

## D3. Cómo presentar la comparación de tiempos

- **Decision**: Mostrar las tres columnas (Fase 2 sobre NPPAD, control con la regla de la Fase 2, canal rápido), destacar el control (24.5 s → 1.0 s, ×24) y avisar de que 200 s → 1 s mezcla dos plantas.
- **Rationale**: Es la comparación limpia; la otra solo da el orden de magnitud.
- **Alternatives considered**: Presentar solo 200 s → 1 s (engañoso).

## D4. Tratamiento de las metas no cumplidas

- **Decision**: Estados explícitos: cumple, parcial, no cumple, no alcanzable en este canal. Ejemplos: tiempo < 3 s del canal lento (no alcanzable a 10 s); ATWS en DNBR (no resuelto); rama caliente/fría en PWR 3L (parcial, 25/28); exactitud estricta del canal lento (87.9 %, 100 % excluyendo INCIERTO).
- **Rationale**: Principio III de la constitución.
- **Alternatives considered**: Omitirlas o reformular la meta.

## D5. Correcciones de documentos

- **Decision**: Aplicar la tabla de `docs/PLAN_DATASET_PWR3L_DETECCION_RAPIDA.md` §3.7.
- **Rationale**: Son errores identificados: Δt = 0.05 s (es 10 s en NPPAD y 1 s en PWR 3L), tiempo de detección sin definición, "AP1000" (NPPAD no lo es), ejemplo de XAI con `WLR` (no medible).
- **Alternatives considered**: Dejarlos y aclararlos en el informe (los documentos seguirían contradiciéndolo).

## D6. Bibliografía

- **Decision**: Capítulo 2 desde `docs/RSL.docx` y los 12 artículos de `Articulos/`; buscar referencias para el ruido de sensores y las compuertas.
- **Rationale**: El ruido de sensores y los umbrales son supuestos que el jurado cuestionará; la bibliografía los respalda.
- **Alternatives considered**: Declarar el ruido como supuesto sin referencia (debilidad abierta).

## D7. Orden de redacción

- **Decision**: Cerrar la feature 005 (23 oct), congelar los resultados, generar la tabla, escribir limitaciones al final (resumen de las 001–005).
- **Rationale**: Evita reescribir cifras.
- **Alternatives considered**: Redactar en paralelo (riesgo de cifras desactualizadas).
