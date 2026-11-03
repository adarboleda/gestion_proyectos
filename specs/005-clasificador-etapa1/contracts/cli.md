# Contrato: comando `entrenar-etapa1`

## Invocación

```text
entrenar-etapa1 [--origen RUTA] [--salida RUTA] [--semilla N] [--epocas N]
python -m clasificador_etapa1 [mismas opciones]
```

| Opción | Por defecto | Significado |
|---|---|---|
| `--origen` | `../IA-Nuclear/PWR 3L` | Carpeta PWR 3L (solo lectura) |
| `--salida` | `modelos/etapa1` | Carpeta donde se publican los artefactos |
| `--semilla` | `42` | Semilla del reparto (004) y del entrenamiento |
| `--epocas` | `40` | Máximo de épocas (la parada temprana puede terminar antes) |

## Flujo

`cargar_corridas` (002) → `formar_grupos` + `repartir` + `verificar_reparto(corridas, reparto)` (004) → inicios de evento → escalador ajustado con las series de entrenamiento (003) → muestras → entrenamiento con parada por validación → evaluación en prueba → publicación → reporte impreso.

## Códigos de salida

| Código | Significado | Efecto en `--salida` |
|---|---|---|
| 0 | Entrenamiento y evaluación completos (se cumplan o no las metas; el reporte lo dice) | Artefactos publicados |
| 1 | Error de datos: origen inexistente, archivo defectuoso, corrida de evento sin inicio, fuga en el reparto | Sin cambios |
| 3 | PyTorch no está instalado | Sin cambios |

## Salida estándar

El reporte de `reporte.txt` (ver [salidas.md](salidas.md)): aviso consultivo, datos y reparto, pesos de clase, historial resumido, métricas globales, tabla por horizonte, tiempos de confirmación por corrida y por área, falsas alarmas, metas y advertencias.

## Salida de error

`ERROR: <archivo>: <causa>` (datos), `FUGA DE DATOS: …` (reparto) o `ERROR: falta PyTorch: pip install -e ".[modelo]" …`.
