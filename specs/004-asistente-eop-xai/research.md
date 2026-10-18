# Research: Asistente EOP y explicabilidad

Fuentes: `IA-Nuclear/NuclearPowerPlantAccidentData/pipeline/README_FASE4.md`, `RESULTADOS_IMPLEMENTACION_PWR3L.md` §4.1, `docs/Thresholds_EOP_Timeline_simplified.pdf`.

## D1. Mapeo EOP como lógica determinista pura

- **Decision**: `EOP_TREE` fijo, sin IA ni dependencias.
- **Rationale**: El plan lo exige (sección 4.1) y la trazabilidad regulatoria necesita reglas auditables.
- **Alternatives considered**: Recomendación aprendida (no auditable).

## D2. Alertas térmicas informativas, no compuertas

- **Decision**: `DNBR_ADVISORY_THRESHOLD = 2.5` (escala PCTRAN) y `PCT_ADVISORY_THRESHOLD = 900 °C`.
- **Rationale**: En esta escala el DNBR real de LOCA/LOCAC parte de ~2.3; el límite de diseño 1.3 no es aplicable directamente. Las compuertas reales son de la feature 005.
- **Alternatives considered**: Usar 1.3 (nunca se alcanzaría en el dataset).

## D3. Caveat térmico de ATWS

- **Decision**: Reemplazar el número por una advertencia textual.
- **Rationale**: La FNN predice DNBR −11.31 (imposible) en ATWS; mostrarlo engañaría al operador.
- **Alternatives considered**: Ocultar la alerta (pierde información).

## D4. SHAP GradientExplainer con fallback

- **Decision**: `shap.GradientExplainer` sobre el modelo con softmax; agregación de `|SHAP|` sobre el eje temporal; fallback por oclusión (poner la variable en su media z-scored) declarado en el campo `method`.
- **Rationale**: Funciona sobre LSTM bidireccional + pooling + MLP; el fallback evita depender de la versión de la librería.
- **Alternatives considered**: LIME (no probado).

## D5. Variable estable → frase "se mantuvo estable"

- **Decision**: Si la diferencia en z-score es menor a 0.05, no se dice "cambió de X a X".
- **Rationale**: En ATWS lo relevante es que PWR y WECS no cambian, que es la definición de ATWS.
- **Alternatives considered**: Forzar frase de cambio.

## D6. Contrafácticos por interpolación

- **Decision**: Interpolar hacia el perfil medio de train de la segunda clase más probable, empezando por las variables de mayor SHAP en pasos de 10 %; probar 1 variable y luego las 2 principales.
- **Rationale**: Algoritmo determinista y sin dependencias; "no encontrado" es un resultado honesto para diagnósticos muy seguros.
- **Alternatives considered**: Optimización por gradiente (no probada).

## D7. Selección determinista de muestras representativas

- **Decision**: Primera muestra de test de cada clase presente, los 4 casos límite, la muestra NORM de validación y la primera LOCA y LOCAC correctas con confianza ≥ 80 %.
- **Rationale**: Sin las dos correctas, las únicas muestras LOCA/LOCAC mostradas eran los 4 casos INCIERTO y daban la impresión de que el modelo "siempre duda" (en realidad 26 de 30 superan 80 %).
- **Alternatives considered**: Elegir las más favorables (sesgo).

## D8. Consolas precalculadas y reproducción causal

- **Decision**: JSON embebido; reproducción con `predict_hierarchical` sobre prefijos crecientes; EOP y alertas recalculados en el navegador por un puerto de `eop_mapper.py`.
- **Rationale**: Se abren con `file:///`; se muestra lo mismo que mediría el sistema en vivo.
- **Alternatives considered**: Servidor con el modelo cargado.

## D9. Importancia por permutación en el canal rápido

- **Decision**: `explain_pwr3l.py` calcula la importancia por permutación; variables de mayor peso: RM1, demanda de disparo, PWNT y nivel del GV B (ninguna es `WLR`).
- **Rationale**: Es la medida natural del modelo elegido y se traduce en la línea "Por qué".
- **Alternatives considered**: SHAP del plan; no se consideró necesario.

## D10. Pendientes

- Calcular la alerta térmica solo sobre la porción posterior al disparo.
- Explicabilidad de la FNN (qué variables mueven DNBR/PCT).
- Árbol de enfriamiento del núcleo (FR-C.1/C.2/C.3) si se obtienen termopares de núcleo y nivel de vasija.
- Mitigar el diagnóstico ATWS temprano en LOCA (ver `specs/001-diagnostico-lento-nppad/tasks.md` T043).
