# Research: Tiempo de detección desde la falla (PWR 3L)

## 1. Instante de la falla

- **Decisión**: `falla.instante_falla(origen, corrida)` → `InstanteFalla(t, fuente, detalle)`:
  1. **Solo ATWS y TRIP_OK** (en LOCA y NORM el registro solo trae consecuencias, como el disparo de turbina tras el scram, y no se busca): primera línea del Transient Report con t > 0 que sea el iniciador: `FWIV #<n> Position Change: 0%` (pérdida de agua de alimentación), `RCP-A trip` (bomba del refrigerante), `Turbine Trip Control Change: True` (disparo de turbina) o `AFW Turbine Valve #1 Position Change: 100%` (pérdida de energía exterior). Fuente «registro».
  2. **Si no hay esa línea** (LOCA, extracción de barras y fallas sin iniciador registrado): el instante programado. En las automáticas es el retardo (tercer campo) de la primera falla de `config.json["fallas"]` distinta de la 8, que es el «fallo del disparo» y siempre está en 0. En las manuales es el número tras `_t` en el nombre de la carpeta. Fuente «programado».
  3. Ninguna fuente → `t = None`, «incierta».
- **Por qué no se usan otras líneas**: en las LOCA el registro solo anota `Malfunction # 1/2` en t ≈ 0, con un retardo oculto (es la inserción, no la rotura). En la extracción de barras (falla 12), la primera línea es `Scram High Flux`, que es la consecuencia (el disparo), no la falla. Las líneas en t = 0 son la configuración inicial (por ejemplo, el abrir y cerrar de la FWIV #4 en R21).
- **Medición real**: 29 corridas con instante del registro y 43 programado (26 de `config.json` y 17 del nombre de carpeta). En las manuales LOFW el registro corrige el nombre de carpeta: R21 `_t30` → 23,0 s y R22 `_t45` → 47,5 s.

## 2. Corridas inciertas

- **Decisión**: incierta si `t` es `None` o si el inicio del validador (`clasificador_etapa1.eventos.inicios_evento`, el mismo de 005) es menor que `t − 2 s`. Se informa con su motivo y no cuenta para la meta de diagnóstico. Sí cuenta para la meta de ATWS, que se mide desde la demanda (su `tiempo_desde_falla_s` queda vacío).
- **Datos reales**: 5 inciertas.
  - **R47, R48 (ATWS) y R54, R99 (TRIP_OK)**: la falla 9 tenía programados 45, 20, 45 y 60 s, pero la planta cambia desde 1 s; PCTran no respetó el retardo.
  - **R22 (ATWS)**: las válvulas FWIV se cierran a los 47,5 s, pero el validador ve cambios desde 13 s.
  - Ninguna está en prueba; R47 y R54 están en validación.
- **Razón**: FR-003. Medir desde un instante posterior a cambios reales daría tiempos negativos o engañosos.

## 3. Reproducción causal de la Etapa 1

- **Decisión**: cargar `modelos/etapa1` con `clasificador_etapa1.prediccion.cargar` y escalar con la media y la escala de `modelo.json`. Después, `construir_muestras(..., entrenamiento=False)` de 005 (τ = 5…299, ventana [τ − 29, τ]) y `entrenamiento.predecir` dan las probabilidades de cada τ. La confirmación usa `clasificador_etapa1.evaluacion.confirmadas` (≥ 0,80 en τ − 1 y τ).
- **Tiempo de diagnóstico**: el menor τ con confirmación de la familia correcta y τ − 1 ≥ t_falla; tiempo = τ − t_falla (puede tener medio segundo cuando t_falla es fraccionario, por ejemplo 47,5).
- **Comparación (FR-011)**: el mismo cálculo con el inicio del validador redondeado hacia arriba, como en 005.
- **Verificación del modelo (FR-007)**: `modelo.json["corridas"]` debe coincidir, conjunto por conjunto, con el reparto de 004 para la semilla dada; si no, `ErrorModelo` y código 1.

## 4. Tiempo de ATWS

- **Decisión**: `regla_atws.cli.construir_casos(origen, semilla)` → `regla.calibrar` con los casos de entrenamiento → `regla.evaluar` con los de validación y prueba. Para cada ATWS detectado: tiempo desde la demanda = `t_decision − t_demanda` (meta de 3 s, FR-006) y tiempo desde la falla = `t_decision − t_falla`, como dato.
- **Causalidad**: la regla decide en `t_decision` con la señal del registro y el flujo de ese segundo.

## 5. Falsas alarmas

- **Etapa 1**: confirmaciones de LOCA o TRANS en corridas NORM, o en corridas de evento no inciertas con τ < t_falla (τ − 1 y τ antes de la falla). Se cuentan los episodios y las corridas. En las inciertas no se cuentan (el instante no es fiable) y se informan aparte. Una confirmación con τ − 1 < t_falla ≤ τ no es detección ni falsa alarma.
- **Confusión**: primera familia confirmada con τ − 1 ≥ t_falla distinta de la correcta. Se informa por corrida (`primera_familia`) y se cuenta en el resumen; no cambia el tiempo de diagnóstico.
- **Regla**: «posible ATWS» en corridas que no son ATWS, inciertas incluidas.
- Solo en validación y prueba.

## 6. Metas

- **Diagnóstico ≤ 10 s**: fracción de corridas de evento no inciertas de prueba con tiempo ≤ 10 s, en total, por familia y para LOCA por área. «Sin datos» si no hay corridas.
- **ATWS ≤ 3 s desde la demanda**: fracción de todos los ATWS de validación y prueba (inciertos incluidos: la demanda no depende del instante de la falla) con tiempo ≤ 3 s, más la cifra solo de prueba. Un ATWS no detectado cuenta como incumplimiento. Validación es válida para esta meta porque la regla se calibra solo con entrenamiento.
- Se informa también la versión con validación del diagnóstico, marcada como referencia (FR-014).

## 7. Salidas

- `tiempos.json`: aviso, configuración, por corrida, resumen, metas y falsas alarmas. `tiempos.csv`: una fila por corrida. `lineas_tiempo.csv`: una fila por corrida y segundo con `p_norm`, `p_loca`, `p_trans`, la familia confirmada y la decisión de ATWS. `reporte.txt`: el reporte legible.
- Publicación en una carpeta temporal, reemplazando solo esos cuatro archivos (patrón de 005).

## 8. Alternativas descartadas

- **Medir desde el inicio del validador** (005): la tarea lo excluye, y en R22 o en la falla 9 el validador no marca la falla.
- **Primer caudal de fuga para las LOCA**: equivalente (≤ 1 s) pero es el efecto, no el registro de la falla. Respuesta del responsable: instante programado.
- **Reentrenar el modelo dentro del comando**: duplicaría 005 y podría usar otra configuración; se verifica el modelo guardado.
