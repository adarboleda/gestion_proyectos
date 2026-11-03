# Research: Clasificador de Etapa 1 (familia del evento) para PWR 3L

## 1. Datos y familias

- **Decisión**: corridas usables de PWR 3L (002) con el reparto de 004 (`formar_grupos` → `repartir` → `verificar_reparto` con todas las corridas). Familias: NORM ← NORM; LOCA ← LOCA y LOCAC; TRANS ← ATWS y TRIP_OK. Etiquetas 0, 1 y 2.
- **Razón**: FR-001 y FR-002. El reparto de 004 ya junta las LOCA/LOCAC de igual área y las gemelas ATWS/TRIP_OK, así que la evaluación no ve escenarios ya vistos.
- **Alternativas**: NPPAD (un dato cada 10 s y una sola simulación NORM y ATWS: no permite medir segundos); validación cruzada de 5 particiones (más robusta, pero cambia el reparto acordado en 004; queda como mejora).

## 2. Instante de inicio del evento

- **Decisión**: `eventos.inicio_evento(origen, corrida)`: (1) `validacion.json` de la carpeta de la corrida (automáticas) → `t_inicio_real`; (2) `validacion_corridas.csv` de la raíz del origen (manuales), fila cuyo nombre empieza por el identificador, ignorando las filas `[mitigation]`; (3) número tras `_t` en el nombre de la carpeta (instante planificado) para las manuales sin validación (TRIP_OK R59–R62); NORM → sin inicio. Una corrida de evento usable sin inicio → `ErrorDatos` (FR-014).
- **Medición con los datos reales**: los tres caminos cubren las 72 corridas de evento usables. En R59, R61 y R62 el instante planificado coincide con el inicio real de su gemela ATWS (25, 62 y 21 s); en R60 no (48 s frente a 13 s de R22). Se documenta como limitación.
- **Razón**: el validador del proyecto detecta el primer cambio real (variable de inicio), más fiable que el instante planificado (en R22 el evento empezó en 13 s y no en 45 s).

## 3. Muestras: ventana causal de 30 s

- **Decisión**: para cada segundo τ = 5…299 (fila τ de la serie, paso de 1 s medido por 003), la muestra son las filas [τ − 29, τ] de las 26 variables escaladas; si τ < 29, las filas que faltan al principio se rellenan repitiendo la fila 0. El inicio se redondea hacia arriba al segundo entero (`ceil`), porque τ es entero (hallazgo U1). Etiqueta: NORM si τ < inicio; si no, la familia de la corrida. Se guardan τ y k = τ − inicio (sin valor en las corridas NORM).
- **Entrenamiento**: todas las muestras de las corridas NORM, todas las de τ < inicio y las de 0 ≤ k ≤ 60 de cada evento (primera aclaración). Validación y prueba: todas las muestras.
- **Razón**: FR-004 y FR-005. Es exactamente lo que el modelo vería en tiempo real cada segundo. Repetir la primera fila es un dato pasado (estado inicial estable), no información futura, y evita máscaras de longitud variable.
- **Alternativas**: relleno con ceros (en datos escalados, cero es la media de entrenamiento, no el estado de la planta); secuencias de longitud variable empaquetadas (más complejo, sin ganancia para ventanas de 30 s).

## 4. Modelo

- **Decisión**: Bi-LSTM de una capa, 32 unidades por dirección, entrada de 26 variables; la salida concatena el último estado hacia delante, el último estado hacia atrás y la media temporal de las salidas (192 valores); dropout 0,3 y una capa lineal a 3 clases. Unos 16 000 parámetros.
- **Razón**: el modelo de referencia de NPPAD (`model_fase2.py` de IA-Nuclear) usa la misma idea (red pequeña, bidireccional, último estado más media) porque hay pocos datos; una red grande memorizaría las 63 corridas de entrenamiento.
- **Causalidad**: la dirección hacia atrás recorre solo la ventana [τ − 29, τ]; no hay datos posteriores a τ (principio II).

## 5. Entrenamiento

- **Decisión**: pérdida de entropía cruzada con pesos de clase `w_c = N / (3 · n_c)` sobre las muestras de entrenamiento (FR-006); Adam (lr 1e-3, weight decay 1e-4); lotes de 256; hasta 40 épocas; parada temprana con paciencia 6 sobre el F1 macro de validación, conservando el mejor estado (FR-008).
- **Determinismo (FR-007)**: `torch.manual_seed(semilla)`, `torch.use_deterministic_algorithms(True)`, un `torch.Generator` con la semilla para barajar y `numpy` con la semilla; CPU. Dos ejecuciones con la misma semilla dan los mismos pesos y métricas en la misma máquina, con la misma versión de PyTorch y el mismo número de hilos (hallazgo A1); la versión de PyTorch y los hilos se registran en `modelo.json`.
- **Alternativas**: sobremuestreo (duplica muestras casi idénticas de pocas corridas); focal loss (otro hiperparámetro sin datos para ajustarlo).

## 6. Métricas por familia y por horizonte

- **Decisión**: sobre todas las muestras de prueba, matriz de confusión, precisión, exhaustividad y F1 por familia y F1 macro. **Horizonte h** (1, 2, 3, 5, 10, 20, 30 s): muestras de evento con k = h (una por corrida de evento) más todas las muestras de operación normal de prueba; se informan la exhaustividad de cada familia de evento en k = h y el F1 macro. **Primeros 30 s** (SC-003): muestras de evento con 0 ≤ k ≤ 30 más todas las de operación normal.
- **Metas sin datos (U2)**: si ninguna corrida de prueba permite evaluar una meta, se informa «sin datos», ni cumple ni falla.
- **Razón**: FR-009. La exhaustividad en k = h responde a la pregunta de la tarea («¿acierta con h segundos de datos?»); sumar las muestras NORM evita un F1 que ignore las falsas alarmas.

## 7. Confirmación y tiempo de detección

- **Decisión**: una familia se **confirma** en τ si en τ − 1 y en τ el modelo da esa familia con probabilidad ≥ 0,80. Tiempo de confirmación de una corrida de evento: el menor k = τ − inicio con τ − 1 ≥ inicio en que se confirma la familia correcta; si no ocurre, «no detectada». Para LOCA se agrupa por área de rotura (002).
- **Razón**: FR-010; regla del plan de detección rápida de IA-Nuclear (k = 2 confirmaciones, umbral 0,80 de la abstención «UNCERTAIN»).

## 8. Falsas alarmas

- **Decisión**: sobre las muestras etiquetadas NORM de prueba (corridas NORM y τ < inicio), una falsa alarma es cada confirmación de LOCA o TRANS con ambas muestras etiquetadas NORM; se cuentan los instantes confirmados, los episodios (bloques consecutivos) y las corridas con al menos una.
- **Razón**: FR-011 y SC-002.

## 9. Artefactos y reemplazo

- **Decisión**: `modelo.pt` (estado de la red), `modelo.json` (familias, variables, ventana, hiperparámetros, semilla, pesos de clase, media y escala del escalador, historial, versión), `reporte.json` y `reporte.txt` (el mismo contenido, legible). Se escriben en una carpeta temporal junto a la salida y se publican reemplazando solo esos cuatro archivos.
- **Razón**: FR-012 y el caso límite de reentrenar sobre una salida previa (mismo criterio que 001).

## 10. Clasificación consultiva

- **Decisión**: `prediccion.cargar(ruta)` y `Clasificador.clasificar(serie)` con la serie sin escalar (T, 26), T ≥ 5, de una corrida hasta τ: escala con los parámetros guardados, toma la ventana de los últimos 30 s y devuelve `{"probabilidades": {NORM, LOCA, TRANS}, "recomendacion": familia o "INCIERTO", "aviso": "Recomendación consultiva: …"}`.
- **Razón**: FR-013 y principio I.

## 11. Dependencia de PyTorch

- **Decisión**: extra opcional `modelo = ["torch>=2.2"]` en `pyproject.toml`; instalación CPU (`--index-url https://download.pytorch.org/whl/cpu`). Las pruebas de `tests/etapa1` usan `pytest.importorskip("torch")`.
- **Razón**: la preparación de datos (001–004) no debe exigir PyTorch.
