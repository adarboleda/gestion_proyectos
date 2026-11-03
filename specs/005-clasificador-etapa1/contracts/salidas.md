# Contrato: artefactos y clasificación

## Archivos en `--salida`

| Archivo | Contenido |
|---|---|
| `modelo.pt` | Pesos de la Bi-LSTM (estado de PyTorch) |
| `modelo.json` | Configuración completa para reutilizar el modelo (data-model.md, «Modelo entrenado») |
| `reporte.json` | Evaluación en prueba (data-model.md, «Reporte de evaluación») |
| `reporte.txt` | El mismo reporte, legible; es lo que imprime el comando |

Se publican los cuatro juntos; otros archivos de la carpeta no se tocan. No se editan a mano: se regeneran con el comando.

## Invariantes

- `modelo.json["corridas"]` reparte las 91 corridas usables en 63 / 15 / 13 con los datos reales (reparto de 004) y ninguna aparece en dos conjuntos.
- `modelo.json["escalador"]` coincide con el ajuste sobre las series de entrenamiento.
- `reporte.json["deteccion"]` tiene una entrada por cada corrida de evento de prueba.
- La suma de la matriz de confusión global es el número de muestras de prueba.

## Clasificación (`clasificador_etapa1.prediccion`)

```text
clasificador = cargar(ruta_salida)
resultado = clasificador.clasificar(serie)   # serie: (T, 26) sin escalar, T ≥ 5, filas hasta el instante actual
```

- `resultado["probabilidades"]`: `{"NORM", "LOCA", "TRANS"}` → probabilidades que suman 1.
- `resultado["recomendacion"]`: la familia más probable si su probabilidad es ≥ 0,80; si no, `"INCIERTO"`.
- `resultado["aviso"]`: `"Recomendación consultiva: el operador valida y decide; el sistema no actúa sobre la planta."`
- Errores: `ValueError` si la serie no es (T, 26) o T < 5.
