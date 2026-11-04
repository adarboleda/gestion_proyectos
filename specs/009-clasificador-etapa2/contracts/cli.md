# Contrato: comando `entrenar-etapa2`

```
entrenar-etapa2 [--origen RUTA] [--salida RUTA] [--semilla N] [--epocas N]
```

| Opción | Por defecto | Significado |
|---|---|---|
| `--origen` | `../IA-Nuclear/PWR 3L` | carpeta PWR 3L (solo lectura) |
| `--salida` | `modelos/etapa2` | carpeta de artefactos |
| `--semilla` | 42 | reparto y entrenamiento |
| `--epocas` | 40 | máximo de épocas |

| Código | Caso |
|---|---|
| 0 | entrenado, evaluado y publicado; imprime el reporte |
| 1 | error de datos (`ErrorDatos`), fuga (`ErrorFuga`), `ValueError` (sin corridas de una rama, sin inicio) o escritura |
| 3 | falta PyTorch |

Publica solo `modelo.pt`, `modelo.json`, `reporte.json`, `reporte.txt` en `--salida`, reemplazándolos de forma atómica; no toca otros archivos.
