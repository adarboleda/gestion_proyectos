# Fase 1 — Preprocesamiento y Documentación del Dataset NPPAD

Documentación técnica integral del origen, modelo de planta, catálogo de variables, estrategia de partición sin fuga de información (*zero data leakage*) y limitaciones metodológicas del dataset de la **Fase 1** (preprocesamiento de simulaciones en reactores PWR para el sistema de diagnóstico y evaluación de seguridad nuclear).

Este documento consolida la arquitectura de datos del proyecto y complementa las especificaciones funcionales del repositorio `gestion_proyectos`.

---

## 1. Objetivo y Resumen Ejecutivo

El objetivo primordial de la Fase 1 es transformar los registros brutos en formato CSV generados por el simulador termohidráulico PCTRAN (`Operation_csv_data/`) en tensores tridimensionales estructurados listos para el entrenamiento y evaluación de modelos de aprendizaje profundo (clasificadores Bi-LSTM de Fase 2) y en matrices de márgenes térmicos preservadas en unidades de ingeniería para la futura calculadora de seguridad y la interfaz de operador (Fase 5 / HMI).

El pipeline garantiza:
1. **Separación estricta de 4 escenarios operativos**: Operación Normal (`NORM`), Accidente por Pérdida de Refrigerante en Rama Caliente (`LOCA`), Accidente por Pérdida de Refrigerante en Rama Fría (`LOCAC`) y Transitorio Anticipado sin Disparo Rápido del Reactor (`ATWS`).
2. **Cero fuga de información**: partición independiente por archivo de simulación completo (*group split*) en las clases donde existen múltiples corridas.
3. **Escalado determinista y causal**: normalización estándar (`StandardScaler`) ajustada exclusivamente con los datos del conjunto de entrenamiento.
4. **Conservación de márgenes térmicos**: preservación de variables clave de seguridad en sus unidades físicas originales, sin sufrir transformaciones ni normalizaciones.

---

## 2. Origen de los Datos y Licenciamiento

Los datos de origen proceden del proyecto público de investigación **NPPAD** (*Nuclear Power Plant Accident Data*), desarrollado por investigadores del **Instituto de Energía Nuclear y Nuevas Tecnologías (INET) de la Universidad Tsinghua (THU-INET)**.

* **Cita bibliográfica oficial**:
  ```bibtex
  @article{Qi2022NPPAD,
    author = {Qi, Ben and Xiao, Xingyu and Liang, Jingang and others},
    title = {An open time-series simulated dataset covering various accidents for nuclear power plants},
    journal = {Scientific Data},
    volume = {9},
    number = {766},
    year = {2022},
    doi = {10.1038/s41597-022-01879-1}
  }
  ```
* **Repositorio de origen**: `https://github.com/thu-inet/NuclearPowerPlantAccidentData`
* **Licencia de uso**: Licencia de código abierto **MIT** (`LICENSE`), permitiendo su uso, investigación, adaptación y redistribución con la debida atribución.
* **Motor de simulación**: Las series temporales fueron generadas mediante scripts de automatización interactuando con **PCTRAN** (*Personal Computer Transient Analyzer*), desarrollado por Micro-Simulation Technology (MST), un simulador de referencia en la industria y en organismos reguladores internacionales (como el OIEA / IAEA) para el análisis termohidráulico y entrenamiento de operadores en tiempo real.

---

## 3. Modelo de Planta Nuclear

El modelo físico simulado en PCTRAN corresponde a un **Reactor de Agua a Presión (PWR, *Pressurized Water Reactor*)** de dos lazos (*2-loop PWR*), representativo de plantas comerciales de diseño tipo Westinghouse o KWU de potencia media (~900 a 1000 MWe, ~2700 MWt).

### Características y Subsistemas Clave de la Planta:
1. **Condición Inicial**: En todas las simulaciones, la planta se inicializa operando en estado estacionario al **100 % de potencia nominal** antes de la introducción de cualquier evento iniciador.
2. **Circuito Primario (RCS, *Reactor Coolant System*)**:
   - Compuesto por el recipiente del reactor (*reactor vessel*), el núcleo con combustible de dióxido de uranio ($UO_2$) enriquecido y vainas de zircaloy, dos lazos de refrigeración (Lazo A y Lazo B) con sus respectivas bombas de refrigerante del reactor (RCP).
   - Presurizador conectado a la rama caliente del lazo primario, equipado con rociadores (*spray*) y calentadores eléctricos (*heaters*) proporcionales y de respaldo para el control fino de la presión del sistema (~155 bar nominales).
3. **Generadores de Vapor (SG, *Steam Generators*)**:
   - Dos generadores de vapor verticales de tubos en U que transfieren el calor del circuito primario al secundario, produciendo vapor saturado para la turbina.
4. **Sistemas de Seguridad y Salvaguardias Tecnológicas (ECCS, *Emergency Core Cooling System*)**:
   - Inyección de seguridad a alta presión (HPI / *High Pressure Injection*).
   - Inyección de seguridad a baja presión y remoción de calor residual (LPSI / RHR / *Low Pressure Safety Injection*).
   - Tanques acumuladores pasivos presurizados con nitrógeno.
5. **Alcance de los escenarios**:
   - Conforme al diseño original de NPPAD, el dataset no incluye fallas superpuestas de los sistemas de mitigación de emergencia (salvaguardias disponibles bajo diseño).

---

## 4. Catálogo de Variables de Entrada (Features del Clasificador)

Para el clasificador de transitorios (Bi-LSTM), se seleccionó un conjunto optimizado de **12 variables de planta** enfocadas estrictamente en el comportamiento termohidráulico y neutrónico del circuito primario. Cada muestra se compone de una ventana temporal de **150 pasos de tiempo a 10 segundos por paso** (duración total de $1500\text{ s} = 25\text{ min}$).

Estas 12 variables son normalizadas mediante un escalador estándar (`StandardScaler`, media cero y varianza unitaria) ajustado **únicamente sobre el conjunto de entrenamiento** (`train`):

| Variable | Nombre del Sensor / Magnitud | Unidad Física | Rol y Fenomenología |
|---|---|---|---|
| `P` | Presión del sistema de refrigeración del reactor (RCS) | `bar` | Indicador primario de pérdida de inventario o despresurización. |
| `TAVG` | Temperatura promedio del refrigerante en el RCS | `°C` | Refleja el balance térmico entre núcleo y generadores de vapor. |
| `THA` | Temperatura en la rama caliente del Lazo A | `°C` | Termohidráulica del refrigerante saliente del núcleo hacia el SG A. |
| `TCA` | Temperatura en la rama fría del Lazo A | `°C` | Termohidráulica del refrigerante entrante al núcleo tras el SG A. |
| `WRCA` | Caudal de flujo del refrigerante en el Lazo A | `t/hr` | Detección de pérdida de circulación forzada o degradación de flujo. |
| `WRCB` | Caudal de flujo del refrigerante en el Lazo B | `t/hr` | Simetría y flujo en el lazo secundario de refrigeración. |
| `LVPZ` | Nivel de líquido en el presurizador | `%` | Inventario volumétrico y comportamiento de la burbuja de vapor. |
| `LVCR` | Nivel de agua en el interior del núcleo | `m` | Estado de cobertura del núcleo y prevención del desnudamiento. |
| `PWNT` | Potencia por flujo neutrónico | `%` | Respuesta neutrónica instantánea y cinética del reactor. |
| `PWR` | Potencia térmica total del núcleo | `%` | Tasa de generación de calor transferida al refrigerante. |
| `WECS` | Caudal total de inyección de emergencia (ECCS) | `t/hr` | Respuesta automática de inyección de agua de refrigeración. |
| `WLR` | Caudal de fuga del lazo primario | `t/hr` | Magnitud directa de la tasa de rotura / pérdida de masa del RCS. |

---

## 5. Catálogo de Variables de Margen Térmico

En paralelo a las variables de entrada del modelo, el pipeline extrae **7 variables de margen térmico y degradación**, conservándolas **en sus unidades físicas originales sin normalizar**. Estas variables están alineadas paso a paso con las variables de entrada para su posterior evaluación en la calculadora de márgenes térmicos y visualización en la interfaz de operador:

| Variable | Descripción Técnica | Unidad Física | Categoría |
|---|---|---|---|
| `DNBR` | Razón de desviación del hervido nucleado (*Departure from Nucleate Boiling Ratio*) | Adimensional | Margen térmico |
| `TPCT` | Temperatura pico de vaina del combustible (*Peak Cladding Temperature*) | `°C` | Margen térmico |
| `SCMA` | Margen de subenfriamiento en el Lazo A | `°C` | Margen térmico |
| `SCMB` | Margen de subenfriamiento en el Lazo B | `°C` | Margen térmico |
| `TSAT` | Temperatura de saturación del presurizador | `°C` | Margen térmico |
| `FRCL` | Fracción de falla o daño en las vainas de combustible | `%` | Indicador de daño |
| `FRZR` | Fracción de reacción y oxidación del circonio con vapor | `%` | Indicador de daño |

---

## 6. Cobertura del Dataset frente a las 97 Variables de PCTRAN

Las simulaciones de PCTRAN en NPPAD registran un total de **97 variables termohidráulicas, neutrónicas, radiológicas y de contención**.

La selección de las 19 variables (12 de entrada + 7 de margen) obedece a un criterio de ingeniería nuclear riguroso:
* **Variables incluidas (19)**: Focalizadas en el circuito primario y la integridad de la primera y segunda barrera de contención (pastilla de combustible y vaina). Permiten un diagnóstico temprano y causal del transitorio durante los primeros 1500 segundos.
* **Variables no incluidas en la entrada (78 restantes)**: Incluyen variables del edificio de contención (`PRB`, `TRB`, `LWRB`, `CNH2`), monitores de radiación en chimeneas y efluentes (`RM1`, `RM2`, `RM3`, `RM4`, `RC87`, `RC131`), lado secundario extendido (presiones y flujos en líneas de vapor y agua de alimentación `PSGA`, `PSGB`, `WFWA`, `WFWB`, `WSTA`, `WSTB`) y parámetros de degradación severa de núcleo fundido (*corium* y hormigón). Si bien son relevantes para fases tardías de accidentes graves, no forman parte del vector de entrada del clasificador temprano de la Fase 1.

---

## 7. Conteos de Archivos y Corrección de Mapeos

### 7.1 Corrección del Mapeo de Carpetas
En el repositorio de origen NPPAD se identificó y corrigió una inconsistencia de nomenclatura:
* La carpeta en disco de la operación normal se denomina `Normal` (no `'NORM'`).
* Se separó explícitamente `LOCA` (rotura en rama caliente) de `LOCAC` (rotura en rama fría), dado que una rotura en rama caliente y una en rama fría inducen firmas termohidráulicas opuestas en la potencia previa al *scram* (sobrepotencia por enfriamiento del moderador en rama caliente vs caída suave en rama fría).

| Carpeta en origen | Clase Asignada | Etiqueta Numérica | Conteo de Archivos Base |
|---|---|---|---|
| `Normal/` | `NORM` | `0` | 1 archivo |
| `LOCA/` | `LOCA` | `1` | 100 archivos (severidades 1 % a 100 %) |
| `LOCAC/` | `LOCAC` | `2` | 100 archivos (severidades 1 % a 100 %) |
| `ATWS/` | `ATWS` | `3` | 1 archivo |
| **Total** | — | — | **202 archivos** |

---

## 8. Estrategia de Partición y Cero Fuga de Datos (*Zero Data Leakage*)

El reparto de datos sigue una proporción teórica objetivo de **70 % entrenamiento (`train`), 15 % validación (`val`) y 15 % prueba (`test`)**, implementado bajo dos estrategias según la naturaleza de la clase:

1. **LOCA y LOCAC (100 archivos por clase)**:
   - Partición por **simulación completa** (*Group Split* por archivo). Una simulación nunca se fragmenta entre dos conjuntos.
   - Enfoque pareado por severidad: la corrida de severidad $k$ de LOCA y la de severidad $k$ de LOCAC se asignan al mismo conjunto, garantizando que el conjunto de prueba evalúe severidades nunca vistas durante el entrenamiento.
   - Conteo: 70 archivos en `train`, 15 archivos en `val`, 15 archivos en `test`.
2. **NORM y ATWS (1 solo archivo por clase)**:
   - Al existir un único archivo continuo por clase, no es posible aplicar un group-split por archivo.
   - Se aplican dos modalidades documentadas:
     * *Modalidad estándar (`preparacion_datos`)*: la simulación completa se asigna al conjunto `train`, dejando `val` y `test` en 0 muestras y emitiendo una advertencia explícita en el reporte y metadatos.
     * *Modalidad de bloques disjuntos con ventaneo deslizante (referencia `IA-Nuclear`)*: el registro continuo se divide en 3 bloques de tiempo disjuntos no solapados, generando ventanas de 150 pasos (`stride = 10` pasos):
       - `NORM`: `train = 1`, `val = 1`, `test = 0` (debido a que el archivo solo contiene 302 filas y requiere al menos $3 \times 150 = 450$ filas para los 3 bloques).
       - `ATWS`: `train = 10`, `val = 3`, `test = 3`.
       - Totales de muestras en la referencia: `train = 151`, `val = 34`, `test = 33`.

---

## 9. Limitaciones Conocidas del Dataset

De acuerdo con el Principio V de la Constitución v2.0.0 (*Honestidad y transparencia en limitaciones*), se declaran formalmente las siguientes limitaciones metodológicas:

1. **Ausencia de muestras de prueba para NORM**:
   El único archivo disponible para Operación Normal posee **302 filas** (equivalentes a 3020 segundos). Para generar tres bloques disjuntos independientes de 150 pasos se requieren al menos **450 filas** ($3 \times 150$). En consecuencia, el conjunto de prueba (`test`) para NORM queda matemáticamente vacío.
2. **Autocorrelación temporal en NORM y ATWS**:
   Todas las ventanas de NORM y ATWS provienen de una única corrida continua. Aunque la partición por bloques evita que las mismas filas se repitan en entrenamiento y validación, no se elimina la autocorrelación temporal inherente a una serie física continua. Las métricas en estas dos clases deben interpretarse como orientativas y no como prueba definitiva de generalización estadística.
3. **Severo desbalance de clases**:
   Mientras LOCA y LOCAC aportan 100 simulaciones independientes con variación graduada de severidad (roturas del 1 % al 100 % de $100\text{ cm}^2$), NORM y ATWS cuentan con una sola simulación base. Se requiere el uso obligatorio de ponderación de pérdida (*class weights*) o esquemas de detección de novedades en las fases de clasificación.
4. **Variabilidad acotada en operación normal**:
   Al contar con un único perfil operativo en estado estacionario, el modelo no es expuesto a maniobras legítimas de planta (como cambios de carga, variaciones de boro o reposicionamiento de barras de control), limitando su capacidad para distinguir pequeños transitorios normales de fallas incipientes.
5. **Alcance limitado al circuito primario**:
   Las 12 variables de entrada no incorporan lecturas del lado secundario ni de contención, por lo que transitorios cuya firma inicial se concentre en el circuito secundario (rupturas de líneas de vapor SLB o agua de alimentación FLB) no pueden ser discriminados con este vector de características.
6. **Mecanismo de salvaguarda por padding**:
   El pipeline implementa una salvaguarda de repetición de la última fila (`pad_to_length`) en caso de simulaciones con longitud menor a 150 filas. Con las simulaciones completas de LOCA/LOCAC no se activa, pero queda disponible para proteger la ejecución ante archivos truncados.

---

## 10. Estructura de Metadatos y Verificación Rápida

Los metadatos se consolidan en `data_processed/metadata.json` con la siguiente estructura canónica:

```json
{
  "selected_features": ["P", "TAVG", "THA", "TCA", "WRCA", "WRCB", "LVPZ", "LVCR", "PWNT", "PWR", "WECS", "WLR"],
  "margin_features": ["DNBR", "TPCT", "SCMA", "SCMB", "TSAT", "FRCL", "FRZR"],
  "margin_feature_categories": {
    "thermal_margins": ["DNBR", "TPCT", "SCMA", "SCMB", "TSAT"],
    "damage_indicators": ["FRCL", "FRZR"]
  },
  "class_mapping": {"NORM": 0, "LOCA": 1, "LOCAC": 2, "ATWS": 3},
  "sequence_length": 150,
  "time_step_seconds": 10,
  "sequence_duration_seconds": 1500,
  "split_ratios_target": {"train": 0.7, "val": 0.15, "test": 0.15},
  "file_counts": {"NORM": 1, "LOCA": 100, "LOCAC": 100, "ATWS": 1},
  "sample_counts": {
    "NORM": {"train": 1, "val": 1, "test": 0},
    "LOCA": {"train": 70, "val": 15, "test": 15},
    "LOCAC": {"train": 70, "val": 15, "test": 15},
    "ATWS": {"train": 10, "val": 3, "test": 3}
  },
  "known_limitations": [
    "NORM proviene de un único archivo de origen (302 filas, menos de las 450 requeridas para 3 bloques disjuntos); el split 'test' de NORM queda vacío por diseño matemático.",
    "Las muestras de NORM y ATWS provienen de un único archivo cada una; existe autocorrelación temporal entre ventanas de la misma clase.",
    "Fuerte desbalance de clases: LOCA/LOCAC aportan decenas de muestras independientes por split, mientras NORM/ATWS aportan muy pocas ventanas.",
    "NORM cuenta con una sola muestra de entrenamiento en el split estándar.",
    "El conjunto de 12 entradas se enfoca en el lazo primario y neutrónico; variables de lado secundario y contención no forman parte de este vector."
  ],
  "scaler": {
    "fitted_on": "train_only",
    "mean_file": "scaler_mean.npy",
    "std_file": "scaler_std.npy"
  }
}
```

### Script de Verificación Rápida en Python:
```python
import json
from pathlib import Path

meta = json.loads(Path("data_processed/metadata.json").read_text(encoding="utf-8"))
print(f"Variables de entrada: {len(meta['selected_features'])} variables")
print(f"Variables de margen: {len(meta['margin_features'])} variables")
print(f"Conteos de archivos: {meta['file_counts']}")
print(f"Conteos de muestras: {meta['sample_counts']}")
print(f"Limitaciones declaradas: {len(meta['known_limitations'])}")
```

