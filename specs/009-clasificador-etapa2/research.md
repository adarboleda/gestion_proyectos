# Research: Clasificador de Etapa 2 (rama caliente o fría)

## 1. Señal física que separa las ramas

- **Decision**: usar la desviación pico de PWR (potencia térmica) y PWNT (flujo neutrónico).
- **Rationale**: en una rotura de rama caliente el refrigerante que sale reduce la temperatura del moderador vista por el núcleo y aumenta la reactividad: hay un pequeño pico de sobrepotencia antes del disparo. En rama fría no. Medido con los datos reales (reparto de 004): pico de PWR a 10 s del inicio de 0,44–2,13 % en LOCA y ≤ 0,32 % en LOCAC (salvo R85, 0,42 % a 3 s); ver `scratch` de exploración. Es la misma conclusión de NPPAD (README_FASE2 §5e de IA-Nuclear).
- **Alternatives**: 26 variables + canales (rechazado por el responsable en `/speckit-clarify`: más parámetros con 24 corridas y menos explicable).

## 2. Definición del canal

- **Decision**: `d(τ) = max_{t ∈ [τ−14, τ]} MM3(x)(t) − x(0)`, con `MM3` la media móvil causal de 3 s (`min_periods=1`).
- **Rationale**: idéntico a `prueba_rama_caliente_fria_pwr3l.py` (ventana 15, `rolling(3)`); la media móvil filtra ruido de un segundo; restar x(0) lo hace independiente de la potencia nominal.
- **Alternatives**: restar un nominal fijo (100 %): rechazado, depende de la planta.

## 3. Fuente de PWR

- **Decision**: leer la columna `PWR` del archivo de la corrida con `_leer_tabla` y `_convertir_columna` de `preparacion_pwr3l.lectura` (solo importados); PWNT se toma de `corrida.serie`.
- **Rationale**: 002 excluyó PWR de las 26 entradas; no se modifica 002. Las filas 0–299 bastan.

## 4. Escalado

- **Decision**: `StandardScaler` propio sobre las filas (N·300, 2) de los canales de las corridas LOCA/LOCAC de entrenamiento.
- **Rationale**: `preparacion_pwr3l.escalado` valida la forma (N, 300, 26) y no admite 2 canales; se respeta el mismo principio de 003 (ajuste solo con entrenamiento) sin tocar su código.

## 5. Muestras y modelo

- **Decision**: muestras τ ≥ inicio (redondeado hacia arriba), ventana de 30 s (`ventanas` de 005); entrenamiento k ≤ 60 s. Modelo `BiLSTMEtapa1(entradas=2, unidades=8, clases=2)`; pesos `pesos_clase(y, 2)`; parada por F1 macro de validación con paciencia 6, máx. 40 épocas; semilla 42; `fijar_semilla` de 005.
- **Rationale**: reutilizar la arquitectura ya revisada; 8 unidades (≈ 1 000 parámetros) por los pocos datos.

## 6. Métricas con abstención

- **Decision**: predicción = clase argmax si p ≥ 0,80, si no UNCERTAIN (−1). Matriz 2 × 3 (real × {LOCA, LOCAC, UNCERTAIN}). Precisión de una rama = aciertos / decisiones de esa rama; exhaustividad = aciertos / muestras reales de esa rama (UNCERTAIN cuenta como no acierto); F1 y F1 macro sobre ellas. Cobertura = decisiones / muestras; exactitud de decisiones = aciertos / decisiones; errores con confianza = decisiones equivocadas. Por horizonte h: muestras con k == h.
- **Confirmación por corrida**: primer k con la misma rama ≥ 0,80 dos segundos seguidos; se informa la rama confirmada, si es correcta, y si alguna vez se confirmó la rama equivocada; «sin decisión» si nunca.
- **Áreas**: < 50, 50–499, ≥ 500 cm² (como la referencia).

## 7. Integración con la Etapa 1

- **Decision**: `Clasificador.clasificar(serie, familia_etapa1)` con `serie` (T, 2) de PWR y PWNT sin escalar desde t = 0; si `familia_etapa1 != "LOCA"` devuelve `NO_APLICA` sin ejecutar el modelo.
- **Rationale**: no se modifica la Etapa 1; la cascada real queda para quien integre la consola.
