# Contrato: comando `medir-tiempo-deteccion`

```text
medir-tiempo-deteccion [--origen RUTA] [--modelo RUTA] [--salida RUTA] [--semilla N]
python -m tiempo_deteccion [mismas opciones]
```

| Opción | Por defecto | Significado |
|---|---|---|
| `--origen` | `../IA-Nuclear/PWR 3L` | Carpeta PWR 3L (solo lectura) |
| `--modelo` | `modelos/etapa1` | Clasificador de Etapa 1 publicado por `entrenar-etapa1` (005) |
| `--salida` | `resultados_tiempo_deteccion` | Carpeta de resultados |
| `--semilla` | `42` | Semilla del reparto (004); debe ser la del modelo |

## Flujo

cargar corridas → reparto + verificación de fuga (004) → verificar el modelo contra el reparto → instante de la falla de cada corrida → Etapa 1 segundo a segundo en validación y prueba → regla de ATWS (calibrada con entrenamiento) → tiempos, metas y falsas alarmas → publicar → imprimir el reporte.

## Códigos de salida

| Código | Significado | Efecto en `--salida` |
|---|---|---|
| 0 | Evaluación completa (se cumplan o no las metas) | Resultados publicados |
| 1 | Error de datos, fuga en el reparto, o modelo inexistente o que no corresponde al reparto | Sin cambios |
| 3 | PyTorch no está instalado | Sin cambios |

## Salida estándar

`reporte.txt`: aviso consultivo, instante de la falla por corrida (con fuente) e inciertas, tiempos de diagnóstico (desde la falla y desde el validador), tiempos de ATWS (desde la demanda y desde la falla), metas y falsas alarmas.
