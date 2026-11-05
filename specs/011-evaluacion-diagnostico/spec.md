# Feature Specification: Evaluación del diagnóstico: matriz de confusión, abstenciones y validación cruzada

**Feature Branch**: `011-evaluacion-diagnostico`  
**Created**: 2026-11-04  
**Status**: Draft  
**Jira**: KAN-26 «Evaluación del diagnóstico: matriz de confusión, abstenciones y validación cruzada»  
**Input**: User description: "Evaluación del diagnóstico: matriz de confusión, abstenciones y validación cruzada. Reportar juntas la exactitud global (contando UNCERTAIN como no acierto), la tasa de abstención y los errores con confianza alta, en prueba y en validación. Añadir validación cruzada y los intervalos de confianza."

---

## Clarifications

### Session 2026-11-04

- Q1: ¿Cómo se define formalmente la «exactitud global (contando UNCERTAIN como no acierto)»?  
  → A1: Se define como $\text{Acc}_{\text{abst}} = \frac{\sum_{i=1}^N \mathbb{I}(\hat{y}_i = y_i \land \text{conf}_i \ge \theta)}{N}$, donde $\theta = 0.80$ es el umbral de confianza y $\mathbb{I}$ es la función indicadora. Una muestra con $\text{conf}_i < 0.80$ se clasifica como `UNCERTAIN` y cuenta en el denominador $N$ pero suma 0 en el numerador, reflejando el criterio conservador exigido. Adicionalmente se reporta la exactitud sobre decididas $\text{Acc}_{\text{decididas}} = \frac{\sum_{i: \text{conf}_i \ge \theta} \mathbb{I}(\hat{y}_i = y_i)}{\sum_{i=1}^N \mathbb{I}(\text{conf}_i \ge \theta)}$ como referencia complementaria.
- Q2: ¿Qué dimensiones tiene la matriz de confusión con abstención?  
  → A2: Es una matriz rectangular de dimensiones $K \times (K+1)$, donde las $K$ filas corresponden a las clases verdaderas (para Etapa 1: `NORM`, `LOCA`, `TRANS`, $K=3$) y las $K+1$ columnas corresponden a las clases diagnosticadas con confianza más la columna de abstención `UNCERTAIN` ($K+1=4$). Cada fila suma exactamente el total de muestras verdaderas de esa clase.
- Q3: ¿Cómo se calculan los intervalos de confianza?  
  → A3: Para las proporciones (exactitud con abstención, tasa de abstención, errores con alta confianza) se utiliza el método de **Wilson score interval** al 95 % de nivel de confianza ($z = 1.95996$), el cual garantiza cobertura rigurosa y cotas válidas en $[0, 1]$ incluso con muestras reducidas. Para la validación cruzada se calcula el intervalo de confianza de la media entre folds: $\bar{x} \pm t_{\alpha/2, k-1} \frac{s}{\sqrt{k}}$.
- Q4: ¿Cómo se estructura la validación cruzada para evitar fuga de información?  
  → A4: Se realiza una validación cruzada de $k=5$ particiones agrupadas (*Group K-Fold*), garantizando que todas las corridas de una misma severidad pareada (LOCA/LOCAC) y los gemelos de ATWS permanezcan en el mismo fold, sin que ninguna corrida aparezca a la vez en entrenamiento y evaluación.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reporte conjunto de exactitud, abstenciones y errores en validación y prueba (Priority: P1)

Un analista de seguridad nuclear evalúa el rendimiento del clasificador de diagnóstico y necesita ver reportadas juntas y de forma transparente:
1. La exactitud global conservadora (contando `UNCERTAIN` como no acierto).
2. La tasa de abstención ($\text{conf} < 0.80$).
3. La tasa y conteo de errores con confianza alta ($\hat{y} \ne y \land \text{conf} \ge 0.80$).
4. La matriz de confusión rectangular $K \times (K+1)$ con la columna `UNCERTAIN`.
Y necesita comparar estas métricas en paralelo tanto en el conjunto de **validación** (`val`) como en el de **prueba** (`test`).

**Why this priority**: Permite juzgar si el modelo está calibrado y si generaliza honestamente: un modelo que no se equivoca porque se abstiene en casos dudosos es infinitamente más seguro en una central nuclear que uno que arriesga diagnósticos erróneos con alta certeza.

**Independent Test**: Evaluar un clasificador sobre validación y prueba y verificar que la suma de aciertos con confianza, abstenciones y errores con alta confianza equivale exactamente al 100 % de las muestras de cada conjunto.

**Acceptance Scenarios**:
1. **Given** predicciones probabilísticas sobre validación y prueba, **When** se calculan las métricas conjuntas, **Then** para ambos conjuntos se reportan $\text{Acc}_{\text{abst}}$, $\text{Tasa}_{\text{abst}}$ y $\text{Err}_{\text{alta\_conf}}$, cumpliéndose que $\text{Acc}_{\text{abst}} + \text{Tasa}_{\text{abst}} + \text{Err}_{\text{alta\_conf}} = 1.0$ (tolerancia $10^{-6}$).
2. **Given** las etiquetas reales y las predicciones con abstención, **When** se construye la matriz de confusión, **Then** tiene forma $(3, 4)$ con columnas `NORM`, `LOCA`, `TRANS` y `UNCERTAIN`, y cada fila suma el total real de su clase.
3. **Given** un conjunto con errores cometidos con confianza $\ge 0.80$, **When** se emite el reporte, **Then** se detalla la lista de instancias erróneas con su clase real, clase predicha y confianza obtenida.

---

### User Story 2 - Intervalos de confianza estadísticos al 95 % (Priority: P1)

Un evaluador estadístico del sistema necesita conocer los intervalos de confianza del 95 % para la exactitud con abstención, la tasa de abstención y los errores de alta confianza, tanto en validación como en prueba, para determinar el margen de incertidumbre inherente al tamaño de muestra disponible.

**Why this priority**: En ingeniería nuclear, un porcentaje puntual sin intervalo de confianza induce a falsas sensaciones de certeza, especialmente con conjuntos pequeños de evaluación.

**Independent Test**: Verificar mediante pruebas unitarias que para proporciones conocidas ($p = k/n$), la función de intervalo de Wilson devuelve cotas inferiores y superiores matemáticamente correctas y acotadas en $[0, 1]$.

**Acceptance Scenarios**:
1. **Given** $k$ aciertos en $n$ muestras, **When** se calcula el intervalo de Wilson al 95 %, **Then** se obtiene un rango $[L, U]$ tal que $0 \le L \le p \le U \le 1$.
2. **Given** las métricas conjuntas de validación y prueba, **When** se visualiza el reporte, **Then** cada métrica porcentual se acompaña de su intervalo $[L, U]$ al 95 %.

---

### User Story 3 - Validación cruzada de 5 particiones sin fuga de información (Priority: P1)

Un auditor de calidad requiere una validación cruzada de $k=5$ folds sobre las corridas disponibles para certificar que el rendimiento del clasificador no es fruto de un reparto afortunado de datos y que no existe fuga entre entrenamiento y evaluación.

**Why this priority**: Con pocas corridas por clase, una sola partición tiene alta varianza; la validación cruzada agrupada aporta solidez y representatividad estadística.

**Independent Test**: Ejecutar la validación cruzada de 5 folds sobre el dataset y verificar que ninguna corrida o par de severidad se solapa entre el entrenamiento y la evaluación de ningún fold, y que se reportan la media y desviación estándar de cada métrica.

**Acceptance Scenarios**:
1. **Given** las corridas del dataset, **When** se forman los 5 folds, **Then** la intersección de corridas entre el fold de evaluación y el conjunto de entrenamiento de ese fold es vacía.
2. **Given** los resultados de los 5 folds, **When** se consolida el reporte de validación cruzada, **Then** se calcula la media $\mu$, la desviación estándar $s$ y el intervalo de confianza al 95 % para la exactitud con abstención y para la tasa de abstención.

---

### User Story 4 - Comando de consola `evaluar-diagnostico` y artefactos JSON/TXT (Priority: P2)

El equipo de desarrollo necesita ejecutar un comando de consola que automatice toda la evaluación del diagnóstico y publique los artefactos `evaluacion_diagnostico.json` y `evaluacion_diagnostico.txt` de manera determinista con una sola orden.

**Why this priority**: Asegura la reproducibilidad completa del pipeline en entornos de integración continua y auditorías técnicas.

**Independent Test**: Ejecutar `evaluar-diagnostico --origen <ruta> --salida <carpeta>` y comprobar que retorna código 0 y escribe ambos archivos con el formato especificado.

**Acceptance Scenarios**:
1. **Given** el comando `evaluar-diagnostico`, **When** se ejecuta con origen y salida válidos, **Then** genera `evaluacion_diagnostico.json` y `evaluacion_diagnostico.txt` con código de salida 0.
2. **Given** dos ejecuciones con la misma semilla, **When** se comparan los JSON resultantes, **Then** son estrictamente idénticos.

---

### Edge Cases

- Si en el conjunto de prueba una clase no tiene muestras (p. ej., NORM en algunos splits reducidos), la fila correspondiente en la matriz debe tener suma 0 y las métricas por clase deben reportar `null` o valor no definido sin lanzar división por cero.
- Si todas las muestras caen por debajo de 0.80 de confianza, la tasa de abstención debe ser 100 %, la exactitud con abstención 0 %, y la exactitud sobre decididas `null` (sin división por cero).
- Si ninguna muestra comete error con alta confianza, la tasa de errores de alta confianza es 0 % y el intervalo de Wilson da $[0, U]$ con $U > 0$ coherente con la regla de tres / cota de Poisson.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema MUST calcular y reportar juntas para un conjunto de evaluación:
  - Exactitud global con abstención: proporción de muestras con predicción correcta y confianza $\ge 0.80$.
  - Tasa de abstención: proporción de muestras con confianza máxima $< 0.80$.
  - Tasa de errores con confianza alta: proporción de muestras con predicción incorrecta y confianza $\ge 0.80$.
  - Exactitud sobre decididas: proporción de aciertos entre las muestras no abstenidas (o `null` si todas se abstienen).
- **FR-002**: El sistema MUST generar la evaluación conjunta tanto para el conjunto de **validación** (`val`) como para el conjunto de **prueba** (`test`).
- **FR-003**: El sistema MUST calcular e incluir para cada una de las proporciones evaluadas el intervalo de confianza de Wilson al 95 % $[L, U]$ acotado en $[0, 1]$.
- **FR-004**: El sistema MUST construir la matriz de confusión rectangular $K \times (K+1)$ (para Etapa 1: $3 \times 4$ con filas `NORM`, `LOCA`, `TRANS` y columnas `NORM`, `LOCA`, `TRANS`, `UNCERTAIN`), verificando que cada fila sume el total verdadero de la clase.
- **FR-005**: El sistema MUST listar detalladamente cada muestra errónea con confianza $\ge 0.80$, indicando índice/corrida, clase verdadera, clase predicha y confianza obtenida.
- **FR-006**: El sistema MUST implementar validación cruzada agrupada de $k$ folds (por defecto $k=5$) que no permita fuga de información entre corridas ni severidades pareadas.
- **FR-007**: El sistema MUST calcular en cada fold de validación cruzada la exactitud con abstención, la tasa de abstención y los errores de alta confianza, y reportar la media, desviación estándar e intervalo de confianza al 95 % a través de los $k$ folds.
- **FR-008**: El sistema MUST proveer el comando de consola `evaluar-diagnostico` accesible desde el entorno del proyecto.
- **FR-009**: `evaluar-diagnostico` MUST aceptar los argumentos `--origen`, `--salida`, `--modelo`, `--k` y `--semilla`.
- **FR-010**: `evaluar-diagnostico` MUST publicar atómicamente los artefactos `evaluacion_diagnostico.json` y `evaluacion_diagnostico.txt` en la carpeta de salida.
- **FR-011**: El sistema MUST ser determinista: dos ejecuciones con la misma semilla y datos de origen MUST producir resultados numéricos idénticos.
- **FR-012**: El sistema MUST incluir un aviso consultivo explícito en el reporte: «Recomendación consultiva: el operador valida y decide; el sistema no actúa sobre la planta».
- **FR-013**: El sistema MUST proveer una suite completa de pruebas unitarias y de integración en `tests/evaluacion_diagnostico/`.
- **FR-014**: El sistema MUST NOT modificar los datos de origen ni romper el funcionamiento de los paquetes previos.

### Key Entities

- **Evaluación Diagnóstica**: Estructura consolidada que contiene las métricas conjuntas con abstención, matrices de confusión e intervalos de confianza para validación, prueba y validación cruzada.
- **Matriz de Confusión Rectangular**: Matriz de $K$ filas por $K+1$ columnas que incorpora la categoría `UNCERTAIN`.
- **Intervalo de Wilson**: Intervalo de confianza binomial asimétrico para proporciones.
- **K-Fold Agrupado**: Validación cruzada con partición disjunta a nivel de corrida y severidad.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El reporte muestra juntas la exactitud con abstención, la tasa de abstención y los errores de alta confianza en prueba y en validación.
- **SC-002**: Las matrices de confusión de validación y prueba tienen 4 columnas (`NORM`, `LOCA`, `TRANS`, `UNCERTAIN`) y cuadran exactamente con la suma de muestras reales.
- **SC-003**: Todas las métricas de proporción incluyen su intervalo de confianza de Wilson al 95 %.
- **SC-004**: La validación cruzada de 5 folds reporta la media, desviación estándar e intervalo de confianza de cada métrica sin solapamiento entre folds.
- **SC-005**: 100 % de las pruebas en `tests/evaluacion_diagnostico/` en verde y 0 regresiones en el repositorio global.
