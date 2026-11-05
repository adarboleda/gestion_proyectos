# Décima iteración SDD: `010-documentacion-dataset`

**Actividad**: «Documentar el dataset (README de la Fase 1 y metadatos)» · **Desarrollador**: `cmbonifaz`  
**Rama**: `010-documentacion-dataset` (creada desde `main`) · **Fecha**: 2026-11-04  
**Herramienta**: GitHub Spec Kit + `speckit-metricas` (`antigravity` / `claude-opus-5-5:low`) · **Constitución**: v2.0.0, sin cambios  

> **Estado: iteración completa y convergente (`converged`).** Se ejecutaron todas las fases de Spec Kit (`/speckit-specify` → `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement` → `/speckit-converge`) y todos los comandos de métricas (`sesion`, `puntos`, `recolectar`, `calibrar`, `estimar`). Las 12 tareas (`T001`–`T012`, 25 puntos de tarea) y las 13 pruebas automatizadas de documentación están en verde (suite global del proyecto: 429 pasadas, 19 omitidas, 0 fallos).

---

## 1. Qué pide la actividad y alcance delimitado

La actividad solicita:
> Documentar el dataset (README de la Fase 1 y metadatos): Describir origen de los datos, modelo de planta, variables, conteo por clase y conjunto, y limitaciones conocidas.

### Delimitación estricta del alcance
- **Foco exclusivo en Fase 1 (NPPAD / PCTRAN)**: No se alteró el código ni los clasificadores de otras fases (`preparacion_pwr3l`, `clasificador_etapa1`, `clasificador_etapa2`, `regla_atws`, `tiempo_deteccion`).
- **Respeto a la Constitución v2.0.0**: Separación categórica entre dominios de planta (NPPAD a 10 s/muestra vs PWR 3L a 1 s/muestra; Principio IV) y declaración transparente y honesta de todas las limitaciones de los datos sin maquillar (Principio V).
- **Control de versiones**: Rama `010-documentacion-dataset` creada desde `main`. Todo probado y comprometido localmente, **a la espera de la luz verde del usuario antes de realizar el push y el merge a `main`**.

---

## 2. Lo que se documentó de los datos reales (referencia `IA-Nuclear`)

Se tomó como referencia la carpeta `C:\Users\Administrador\Desktop\Nuecleare\IA-Nuclear` y el repositorio oficial `https://github.com/adarboleda/IA-Nuclear.git`:

| Elemento | Fuente en Referencia | Documentación Implementada |
|---|---|---|
| **Origen** | `NuclearPowerPlantAccidentData/README_ES.md` | `docs/README_FASE1.md` §2: Cita oficial a Qi et al. (Sci Data 9, 766, 2022), Universidad Tsinghua (THU-INET), software PCTRAN (Micro-Simulation Technology) y licencia MIT. |
| **Modelo de planta** | PCTRAN / `README_ES.md` | `docs/README_FASE1.md` §3: Reactor PWR comercial de 2 lazos (~900-1000 MWe, ~2700 MWt), condición inicial al 100 % de potencia nominal, lazo primario RCS con presurizador (rociadores y calentadores), 2 generadores de vapor y salvaguardias ECCS (HPI, LPSI y acumuladores). |
| **Variables de entrada (12)** | `pipeline/README_FASE1.md` §4.2 | `docs/README_FASE1.md` §4 y `data_processed/metadata.json`: 12 variables termohidráulicas y neutrónicas (`P`, `TAVG`, `THA`, `TCA`, `WRCA`, `WRCB`, `LVPZ`, `LVCR`, `PWNT`, `PWR`, `WECS`, `WLR`), escaladas mediante `StandardScaler` ajustado exclusivamente en `train`. |
| **Variables de margen (7)** | `pipeline/README_FASE1.md` §4.3 | `docs/README_FASE1.md` §5 y `data_processed/metadata.json`: 7 variables de margen térmico e indicadores de daño (`DNBR`, `TPCT`, `SCMA`, `SCMB`, `TSAT`, `FRCL`, `FRZR`), conservadas en **unidades físicas reales sin normalizar**. |
| **Catálogo de 97 variables** | `README_ES.md` Tabla 2 | `docs/README_FASE1.md` §6: Contextualización de por qué se aislaron 19 variables y se excluyeron de la entrada temprana los monitores radiológicos, contención y lado secundario extendido. |
| **Conteos y Partición** | `pipeline/README_FASE1.md` §4.1, §4.4 | `docs/README_FASE1.md` §7, §8 y `metadata.json`: Corrección de carpeta `Normal` $\to$ NORM, separación `LOCA` / `LOCAC`. Conteo base de 202 archivos (1 NORM, 100 LOCA, 100 LOCAC, 1 ATWS). Partición sin fuga (70/15/15) por simulación completa (group split) y detalle de la modalidad de ventaneo ($151/34/33$). |
| **Limitaciones conocidas** | `data_processed/metadata.json` | `docs/README_FASE1.md` §9 y `metadata.json`: 6 limitaciones críticas detalladas matemáticamente (NORM sin test por $302 < 450$ filas, autocorrelación temporal, severo desbalance, generalización acotada de operación normal, padding y alcance de 12 canales). |

---

## 3. Lo que se hizo, fase por fase (Spec Kit)

| # | Fase | Comando | Resultado | Artefactos generados |
|---|---|---|---|---|
| 1 | Rama y Especificar | `/speckit-specify` | Rama `010-documentacion-dataset` creada desde `main`. Especificación con 3 historias de usuario (US1: Origen y planta, US2: Catálogo de variables, US3: Conteos y limitaciones), 14 requisitos funcionales (`FR-001`–`FR-014`), 5 criterios de éxito (`SC-001`–`SC-005`) y checklist 16/16 PASS. | [spec.md](specs/010-documentacion-dataset/spec.md), [requirements.md](specs/010-documentacion-dataset/checklists/requirements.md) |
| 2 | Aclarar | `/speckit-clarify` | 3 aclaraciones registradas: ubicación modular (`docs/README_FASE1.md` y `data_processed/metadata.json`), nivel de detalle exigido en tablas y limitaciones, y validación mediante suite de pruebas automatizadas. | [spec.md](specs/010-documentacion-dataset/spec.md) |
| 3 | Planificar | `/speckit-plan` | Plan técnico con Constitution Check en «cumple», decisiones de diseño en `research.md`, modelo de datos de `metadata.json` y contratos de documentación. | [plan.md](specs/010-documentacion-dataset/plan.md), [research.md](specs/010-documentacion-dataset/research.md), [data-model.md](specs/010-documentacion-dataset/data-model.md), [contracts/documentacion.md](specs/010-documentacion-dataset/contracts/documentacion.md), [quickstart.md](specs/010-documentacion-dataset/quickstart.md) |
| 4 | Tareas y Puntos | `/speckit-tasks` + `puntos.ps1` | 12 tareas (`T001`–`T012`) organizadas en 5 fases bajo ciclo TDD; línea base de **25 puntos de tarea**. | [tasks.md](specs/010-documentacion-dataset/tasks.md), [puntos-tarea.csv](specs/010-documentacion-dataset/puntos-tarea.csv) |
| 5 | Analizar | `/speckit-analyze` | 0 hallazgos críticos/altos/medios y 3 hallazgos menores resueltos; 100 % de cobertura de FR y SC. | [analisis-inicial.md](specs/010-documentacion-dataset/analisis-inicial.md) |
| 6 | Implementar (TDD) | `/speckit-implement` | Creación de suite `tests/documentacion/` (comprobada en rojo inicialmente: 13 fallos); redacción de `docs/README_FASE1.md`, creación de `data_processed/metadata.json` y `docs/metadata.json`, actualización de `README.md` y suite en verde (13/13 pasadas). | `docs/README_FASE1.md`, `data_processed/metadata.json`, `tests/documentacion/`, `README.md` |
| 7 | Convergencia | `/speckit-converge` | Estado **`converged`** (1.ª pasada): 12/12 tareas completadas `[x]`, 25/25 puntos, 14/14 FR verificados, 0 brechas, 429 pruebas globales en verde. | [auditoria.md](specs/010-documentacion-dataset/auditoria.md), [tasks.md](specs/010-documentacion-dataset/tasks.md) |

---

## 4. Qué se construyó

1. **Documento Maestro [`docs/README_FASE1.md`](file:///c:/Users/Administrador/Desktop/gestion/gestion_proyectos/docs/README_FASE1.md)**:
   - 218 líneas de documentación técnica de alta calidad.
   - 10 secciones completas: Resumen, Origen y Licenciamiento, Modelo de Planta PWR 2 lazos, Diccionario de 12 Variables de Entrada, Diccionario de 7 Variables de Margen, Cobertura frente a 97 variables de PCTRAN, Conteos y Mapeo de Carpetas, Partición de Datos sin Fuga, Limitaciones Conocidas y Script de Verificación Rápida.
2. **Metadatos Canónicos [`data_processed/metadata.json`](file:///c:/Users/Administrador/Desktop/gestion/gestion_proyectos/data_processed/metadata.json)**:
   - Estructura JSON válida codificada en UTF-8 conteniendo todas las claves canónicas exigidas por los clasificadores y la calculadora de márgenes.
   - Réplica de seguridad en [`docs/metadata.json`](file:///c:/Users/Administrador/Desktop/gestion/gestion_proyectos/docs/metadata.json) y actualización de `.gitignore` para versionar los metadatos sin incorporar archivos `.npy` masivos.
3. **Suite de Pruebas Automatizadas [`tests/documentacion/`](file:///c:/Users/Administrador/Desktop/gestion/gestion_proyectos/tests/documentacion/)**:
   - [`conftest.py`](file:///c:/Users/Administrador/Desktop/gestion/gestion_proyectos/tests/documentacion/conftest.py): Fixtures de rutas del proyecto.
   - [`test_metadata_json.py`](file:///c:/Users/Administrador/Desktop/gestion/gestion_proyectos/tests/documentacion/test_metadata_json.py): 6 pruebas que validan esquema, tipos, presencia de las 12 variables, 7 márgenes categorizados, parámetros temporales, conteos por clase y limitaciones.
   - [`test_readme_fase1.py`](file:///c:/Users/Administrador/Desktop/gestion/gestion_proyectos/tests/documentacion/test_readme_fase1.py): 7 pruebas que validan longitud (>=120 líneas), origen PCTRAN/Tsinghua/MIT, modelo PWR, catálogos completos de variables, conteos y enlace en el `README.md` principal.
4. **Actualización de [`README.md`](file:///c:/Users/Administrador/Desktop/gestion/gestion_proyectos/README.md)**:
   - Nueva sección formal «Documentación del Dataset — Fase 1 (funcionalidad 010)» con enlaces directos a la documentación y metadatos.

---

## 5. Resultados de Verificación y Métricas

### Verificación de Pruebas
```
tests/documentacion/test_metadata_json.py::test_metadata_json_existe_y_es_json_valido PASSED [  7%]
tests/documentacion/test_metadata_json.py::test_metadata_json_contiene_12_variables_de_entrada PASSED [ 15%]
tests/documentacion/test_metadata_json.py::test_metadata_json_contiene_7_variables_de_margen_con_categorias PASSED [ 23%]
tests/documentacion/test_metadata_json.py::test_metadata_json_parametros_temporales_y_clases PASSED [ 30%]
tests/documentacion/test_metadata_json.py::test_metadata_json_conteos_de_archivos_y_muestras PASSED [ 38%]
tests/documentacion/test_metadata_json.py::test_metadata_json_declara_limitaciones_conocidas_y_escalador PASSED [ 46%]
tests/documentacion/test_readme_fase1.py::test_readme_fase1_existe_y_longitud PASSED [ 53%]
tests/documentacion/test_readme_fase1.py::test_readme_fase1_contiene_origen_y_licencia PASSED [ 61%]
tests/documentacion/test_readme_fase1.py::test_readme_fase1_contiene_modelo_de_planta PASSED [ 69%]
tests/documentacion/test_readme_fase1.py::test_readme_fase1_contiene_catalogo_de_12_variables_y_escalador PASSED [ 76%]
tests/documentacion/test_readme_fase1.py::test_readme_fase1_contiene_catalogo_de_7_margenes_termicos PASSED [ 84%]
tests/documentacion/test_readme_fase1.py::test_readme_fase1_contiene_conteos_y_limitaciones PASSED [ 92%]
tests/documentacion/test_readme_fase1.py::test_readme_principal_enlaza_fase1 PASSED [100%]

============================= 13 passed in 0.05s ==============================
Suite global: 429 passed, 19 skipped in 126.43s (0 regresiones).
```

### Métricas de Esfuerzo y Calibración
- **Sesiones registradas**: 6 sesiones cerradas en `metricas/sesiones/` (fases `especificar`, `aclarar`, `planificar`, `tareas`, `analizar`, `implementar`).
- **Puntos de tarea**: 25 puntos de tarea completados.
- **Modelo de calibración**: recalibrado con éxito en `metricas/salidas/modelo-estimacion.json` y `reporte-calibracion.md` ($n = 9$, MMRE 0.1863 sobre puntos de tarea).
- **Esfuerzo**: 0.009 PM (~1.3 h estimadas).

---

## 6. Estado en Git y Próximos Pasos

- **Rama activa**: `010-documentacion-dataset`
- **Árbol de trabajo**: Limpio.
- **Condición**: Siguiendo las instrucciones del usuario (*"y luego te doy luz verde para hacer push de la rama y despues merge a main"*), **no** se ha realizado el push a remoto ni el merge a `main`. Todo está listo en la rama local para que el usuario revise y confirme la luz verde.
