# Research: Preparación de datos NPPAD sin fuga de información

No quedaban marcadores `NEEDS CLARIFICATION`; este documento registra las decisiones de diseño que el plan pedido dejaba abiertas o que entran en tensión con la spec.

## 1. LOCA y LOCAC: reparto por severidad compartida

- **Decision**: se reparten las severidades (los 100 nombres de archivo `1.csv`…`100.csv`) una sola vez con la semilla 42 en 70 / 15 / 15, y la misma asignación se aplica a LOCA y a LOCAC. Si una severidad existiera en una sola clase, se reparte igual dentro de la unión de severidades.
- **Rationale**: la spec (FR-004) y el principio II de la constitución exigen que la simulación de LOCA y la de LOCAC de igual severidad vayan al mismo conjunto. Repartir cada clase "por separado" con barajados independientes rompe esa regla y, en la documentación del proyecto previo, dejó severidades de prueba disjuntas entre clases. El reparto compartido da exactamente los conteos esperados por clase (70/15/15).
- **Alternatives considered**: barajar LOCA y LOCAC de forma independiente (cumple los conteos pero viola FR-004 y el principio II).

## 2. Cálculo del reparto 70/15/15

- **Decision**: con `n` severidades, `n_train = round(0.70·n)`, `n_val = round(0.15·n)`, `n_test = n − n_train − n_val`; el orden sale de una permutación con `numpy.random.default_rng(42)` sobre las severidades ordenadas numéricamente.
- **Rationale**: para `n = 100` da 70/15/15; es determinista y no depende del orden en que el sistema de archivos liste los CSV.
- **Alternatives considered**: `sklearn.model_selection.train_test_split` en dos pasos (válido, pero el redondeo depende de las fracciones intermedias y es menos legible).

## 3. Normal y ATWS

- **Decision**: la única simulación de cada una va a entrenamiento (FR-007); validación y prueba quedan con cero muestras de esas clases y el reporte y `metadata.json` lo declaran como advertencia.
- **Rationale**: es la respuesta aclarada del usuario; evita que una misma simulación aparezca en dos conjuntos.
- **Alternatives considered**: partir en bloques de tiempo (rechazado en la aclaración por reutilizar una simulación entre conjuntos).

## 4. Qué se valida en cada archivo

- **Decision**: se lee solo la cabecera y las primeras 150 filas (`pandas.read_csv(..., usecols=<19 variables>, nrows=150, dtype=str)`) y cada valor se convierte con `float()` de Python, para que la conversión del texto sea exacta (SC-003). Es defectuoso, y detiene toda la preparación, un archivo al que le falta alguna de las 19 variables, que tiene menos de 150 filas o que en esas 150 filas tiene valores no numéricos, vacíos, `NaN` o infinitos. El error nombra el archivo, la variable y la causa.
- **Rationale**: solo esas filas entran en la salida (FR-002); validar el resto del archivo detendría la preparación por datos que no se usan. Las 202 simulaciones del dataset actual pasan esta validación.
- **Alternatives considered**: validar el archivo completo (más estricto, pero sin efecto sobre la salida).

## 5. Tipos y forma de los arreglos

- **Decision**: `X_*` float32 `(N,150,12)`, `y_*` int64 `(N,)`, `margins_*` **float64** `(N,150,7)`, `scaler_mean.npy` y `scaler_std.npy` float64 `(12,)`.
- **Rationale**: `X` e `y` siguen el tipo pedido. Los márgenes se guardan en float64 para que sus valores coincidan exactamente con los del CSV (SC-003); convertirlos a float32 los redondearía y obligaría a comparar con tolerancia. El tamaño es despreciable (202×150×7).
- **Alternatives considered**: margins en float32 como `X` (menor tamaño, pero SC-003 pasaría a ser una comparación aproximada).

## 6. Escalado

- **Decision**: `StandardScaler` ajustado con `fit` sobre las filas de entrenamiento aplanadas `(N_train·150, 12)`; se transforma cada conjunto con el mismo objeto. Se guardan `mean_` y `scale_` como `scaler_mean.npy` y `scaler_std.npy`. Si alguna variable tiene desviación cero en entrenamiento, scikit-learn deja su escala en 1.0; el reporte y `metadata.json` la listan en `variables_sin_varianza`.
- **Rationale**: es el escalado por variable que pide la spec, calculado solo con entrenamiento (principio II). Entrenamiento incluye las muestras únicas de Normal y ATWS, por lo que sus propias estadísticas participan en el ajuste.
- **Alternatives considered**: escalado por muestra (rompe la comparabilidad entre muestras); ajustar con los tres conjuntos (fuga de datos, prohibido).

## 7. Orden de las muestras

- **Decision**: dentro de cada conjunto, ordenadas por clase (NORM, LOCA, LOCAC, ATWS) y por severidad numérica; `metadata.json` lista las simulaciones de cada conjunto en el mismo orden que las filas de los arreglos.
- **Rationale**: salida determinista y verificable, e identificación de la simulación de origen de cada muestra (FR-002).
- **Alternatives considered**: mezclar las muestras (aporta aleatoriedad que el entrenamiento posterior puede añadir por su cuenta).

## 8. Escritura sin dejar conjuntos parciales

- **Decision**: leer y validar todas las simulaciones en memoria; construir los arreglos; escribir los archivos en un directorio temporal hermano de la salida y moverlos uno a uno (`os.replace`) a la carpeta de salida. Solo se reemplazan los archivos publicados: cualquier otro archivo que ya esté en la salida no se toca. Cualquier error anterior al movimiento deja la salida como estaba, y el directorio temporal se elimina siempre.
- **Rationale**: garantiza "sin escribir ningún conjunto" ante un archivo defectuoso (FR-012) y evita destruir archivos ajenos si `--salida` apunta a una carpeta con contenido (`os.replace` de un directorio sobre uno no vacío no es posible). Una repetición reemplaza los artefactos obsoletos por los nuevos.
- **Alternatives considered**: reemplazar la carpeta completa (destructivo e inviable si no está vacía); escribir archivos uno a uno directamente en la salida (deja estados intermedios ante un fallo).

## 9. Comparación con la referencia

- **Decision**: la ruta `../IA-Nuclear/data_processed/metadata.json` es un parámetro opcional (`--referencia`). Se comparan solo los conteos `sample_counts` de LOCA y LOCAC (train/val/test) con los obtenidos. Si coinciden, el reporte lo indica; si difieren, el reporte marca la diferencia y el comando termina con código de salida 2 después de haber escrito la salida; si el archivo no existe, el reporte indica "referencia no disponible" sin fallar. Normal y ATWS no se comparan (el proyecto previo las partió en ventanas deslizantes, así que sus conteos no son comparables).
- **Rationale**: es la validación pedida, sin convertir una referencia externa en dependencia obligatoria. Los valores de los arreglos no se comparan: la referencia escala con estadísticas de entrenamiento distintas.
- **Alternatives considered**: comparar también los identificadores de las simulaciones (la referencia no los guarda).

## 10. Dependencias y empaquetado

- **Decision**: `pyproject.toml` con diseño `src/`, dependencias `pandas`, `numpy`, `scikit-learn`, extra `dev` con `pytest`, y el guion `preparar-datos`; también se puede ejecutar con `python -m preparacion_datos`. La ruta de origen es el argumento `--origen`, con valor por defecto `../IA-Nuclear/NuclearPowerPlantAccidentData/Operation_csv_data` respecto del directorio desde el que se ejecuta (la raíz del repositorio).
- **Rationale**: una instalación editable deja un solo comando documentado (FR-013) y evita manipular `sys.path` en las pruebas.
- **Alternatives considered**: un script suelto con `PYTHONPATH=src` (menos portable y sin dependencias declaradas).

## 11. Artefactos generados

- **Decision**: `data_processed/` es salida regenerable; se recomienda añadirla a `.gitignore` en las tareas, de modo que los conjuntos se regeneren con el comando en vez de versionarse.
- **Rationale**: principio III (los artefactos generados no se editan a mano y se regeneran).
- **Alternatives considered**: versionar los `.npy` (tamaño pequeño, pero puede desincronizarse del código).
