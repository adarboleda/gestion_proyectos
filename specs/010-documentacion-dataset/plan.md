# Implementation Plan: Documentación del dataset (README de la Fase 1 y metadatos)

**Branch**: `010-documentacion-dataset` | **Fecha**: 2026-11-04 | **Spec**: [spec.md](spec.md)

---

## 1. Technical Context & Approach

El objetivo es documentar de forma exhaustiva, física y matemáticamente rigurosa el dataset de la Fase 1 (NPPAD / PCTRAN), consolidando tanto la documentación en prosa técnica (`docs/README_FASE1.md`) como los metadatos procesables por máquina (`data_processed/metadata.json`), y asegurando su consistencia mediante una suite de pruebas automatizadas.

### Constitution Check (Constitución v2.0.0)

| Principio | Estado | Justificación |
|---|---|---|
| I. Sin dependencias externas pesadas innecesarias | CUMPLE | Se utilizan exclusivamente Markdown estándar, JSON y utilidades estándar de Python/pytest para verificación. |
| II. Cero fuga de datos (*data leakage*) | CUMPLE | La documentación ratifica la partición estricta por simulación completa (group split 70/15/15) y explica la causa matemática de la limitación en NORM. |
| III. Causalidad estricta | CUMPLE | Se documenta la naturaleza temporal del dataset (secuencias de 150 pasos de 10 s = 1500 s). |
| IV. Separación estricta de dominios de planta | CUMPLE | Se delimita con total claridad que la Fase 1 corresponde a NPPAD (PCTRAN, PWR de 2 lazos, 10 s/muestra), sin confundirlo con PWR 3L (1 s/muestra). |
| V. Honestidad y transparencia en limitaciones | CUMPLE | Es el núcleo de esta actividad: documentar sin maquillar la ausencia de test en NORM, la autocorrelación en NORM/ATWS y el severo desbalance de clases. |
| VI. Trazabilidad y reproducibilidad con Spec Kit | CUMPLE | Todo el ciclo SDD se registra con Spec Kit y sus sesiones de métricas. |

---

## 2. Architecture & File Locations

```
gestion_proyectos/
├── docs/
│   └── README_FASE1.md                 # Documento técnico maestro de la Fase 1
├── data_processed/
│   └── metadata.json                   # Metadatos estructurados canónicos de Fase 1
├── tests/
│   └── documentacion/
│       ├── __init__.py
│       ├── test_readme_fase1.py        # Pruebas de contenido, estructura y secciones de README_FASE1.md
│       └── test_metadata_json.py       # Pruebas de esquema JSON, tipos, variables y limitaciones
└── README.md                           # Actualización de la sección del dataset en la raíz
```

---

## 3. Plan de Fases de Tareas

1. **Fase 1: Configuración de pruebas (TDD Red)**:
   - Crear suite `tests/documentacion/` con pruebas que verifiquen las secciones obligatorias de `docs/README_FASE1.md` y las claves/valores canónicos de `data_processed/metadata.json`.
2. **Fase 2: Redacción técnica de `docs/README_FASE1.md`**:
   - Sección 1: Objetivo y contexto de la Fase 1.
   - Sección 2: Origen de los datos (PCTRAN, Tsinghua, Sci Data 2022, licencia MIT).
   - Sección 3: Modelo de planta (PWR de 2 lazos, parámetros nominales al 100 % de potencia, lazo primario RCS, generadores de vapor y ECCS).
   - Sección 4: Catálogo de las 12 variables de entrada (sensores primarios y neutrónicos con descripción física y unidades) y notas sobre normalización (`StandardScaler` en train).
   - Sección 5: Catálogo de las 7 variables de margen térmico (unidades físicas directas, no normalizadas).
   - Sección 6: Contextualización de las 97 variables de PCTRAN y justificación de selección.
   - Sección 7: Conteo de archivos base por clase y corrección de mapeos (`Normal` $\to$ NORM).
   - Sección 8: Partición de datos sin fuga (70/15/15, group split vs bloques temporales).
   - Sección 9: Declaración explícita de limitaciones conocidas (NORM sin test, autocorrelación, desbalance, muestra única en train, alcance de 12 canales).
   - Sección 10: Verificación rápida con Python.
3. **Fase 3: Publicación de `data_processed/metadata.json`**:
   - Esquema JSON canónico con `selected_features`, `margin_features`, `margin_feature_categories`, `class_mapping`, `sequence_length` (150), `time_step_seconds` (10), `sequence_duration_seconds` (1500), `split_ratios_target`, `file_counts`, `sample_counts`, `known_limitations` y `scaler`.
4. **Fase 4: Integración y documentación general**:
   - Actualizar `README.md` principal en la raíz con enlace y síntesis de la Fase 1.
   - Ejecutar la suite de pruebas unitarias y verificar 0 regresiones globales.

