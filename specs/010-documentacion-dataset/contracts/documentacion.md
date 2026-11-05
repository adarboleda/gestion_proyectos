# Contrato de Documentación y Metadatos de Fase 1

## 1. Contrato de `docs/README_FASE1.md`

El documento `docs/README_FASE1.md` debe contener las siguientes secciones estructuradas con títulos explícitos:

1. **Objetivo**: Propósito de la Fase 1 en el flujo del sistema.
2. **Origen de los datos**: Cita académica a NPPAD (Qi et al., Sci Data 2022), PCTRAN, Universidad Tsinghua y licencia MIT.
3. **Modelo de planta**: Descripción técnica del reactor PWR de 2 lazos, circuito primario RCS, presurizador, generadores de vapor y sistemas ECCS (inyección de emergencia y acumuladores).
4. **Variables de entrada**: Tabla con las 12 variables (`P`, `TAVG`, `THA`, `TCA`, `WRCA`, `WRCB`, `LVPZ`, `LVCR`, `PWNT`, `PWR`, `WECS`, `WLR`), descripción física, unidades e indicación de normalización con `StandardScaler` ajustado solo en `train`.
5. **Variables de margen térmico**: Tabla con las 7 variables (`DNBR`, `TPCT`, `SCMA`, `SCMB`, `TSAT`, `FRCL`, `FRZR`), descripción física, unidades, categoría y declaración de que se conservan en unidades físicas reales.
6. **Conteos de archivos**: Conteo base de 202 archivos (1 NORM, 100 LOCA, 100 LOCAC, 1 ATWS).
7. **Partición de datos**: Detalle de proporciones (70 % train, 15 % val, 15 % test) y partición por simulación completa (group split).
8. **Limitaciones conocidas**: Declaración detallada de las 5 limitaciones críticas requeridas.

---

## 2. Contrato de `data_processed/metadata.json`

El archivo `data_processed/metadata.json` debe cumplir estrictamente con:
- Archivo en formato JSON válido codificado en UTF-8.
- Clave `selected_features` con lista ordenada de 12 nombres de variables.
- Clave `margin_features` con lista ordenada de 7 nombres de variables.
- Clave `margin_feature_categories` con diccionarios `thermal_margins` y `damage_indicators`.
- Clave `class_mapping` con las 4 clases (`NORM: 0`, `LOCA: 1`, `LOCAC: 2`, `ATWS: 3`).
- Claves `sequence_length: 150`, `time_step_seconds: 10`, `sequence_duration_seconds: 1500`.
- Clave `known_limitations` con al menos 4 declaraciones explícitas en texto.
