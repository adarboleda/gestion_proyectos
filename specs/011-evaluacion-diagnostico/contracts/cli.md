# Contrato de Línea de Órdenes: `evaluar-diagnostico`

## 1. Argumentos de Consola

```bash
evaluar-diagnostico [--origen CARPETA] [--salida CARPETA] [--modelo CARPETA] [--k NUM] [--semilla NUM]
```

| Argumento | Tipo | Por defecto | Descripción |
|---|---|---|---|
| `--origen` | `str` | `"PWR 3L"` / configurado | Ruta a la carpeta del dataset PWR 3L (solo lectura). |
| `--salida` | `str` | `"resultados_evaluacion_diagnostico"` | Carpeta donde se publican los artefactos. |
| `--modelo` | `str` | `None` | (Opcional) Ruta al modelo entrenado `modelos/etapa1`. Si no se pasa, entrena deterministamente. |
| `--k` | `int` | `5` | Número de particiones para la validación cruzada agrupada. |
| `--semilla` | `int` | `42` | Semilla reproducible para particiones y entrenamiento. |

---

## 2. Códigos de Salida

| Código | Significado |
|---|---|
| `0` | Éxito: evaluación completada y artefactos publicados. |
| `1` | Error en los datos de entrada o argumentos inválidos. |
| `3` | Falta dependencia requerida (PyTorch si se requiere inferencia con redes). |

---

## 3. Artefactos Producidos

1. `evaluacion_diagnostico.json`: diccionario con las secciones de `validacion`, `prueba` y `validacion_cruzada`.
2. `evaluacion_diagnostico.txt`: reporte formateado en texto legible por humanos.
