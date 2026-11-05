# Contrato: `informe-hito1`

```
informe-hito1 [--etapa1 DIR] [--regla DIR] [--tiempos DIR] [--etapa2 DIR] [--diagnostico DIR] [--salida DIR]
python -m informe_hito1 [mismas opciones]
```

## Opciones

| Opción | Por defecto |
|---|---|
| `--etapa1` | `modelos/etapa1` |
| `--regla` | `resultados_regla_atws` |
| `--tiempos` | `resultados_tiempo_deteccion` |
| `--etapa2` | `modelos/etapa2` |
| `--diagnostico` | `resultados_evaluacion_diagnostico` |
| `--salida` | `informe_hito1` |

## Códigos de salida

| Código | Significado |
|---|---|
| 0 | `hito1.md` y `hito1.json` publicados, todos o ninguno |
| 1 | Falta un archivo de resultados o es ilegible, o la salida no se puede escribir |
| 2 | Argumentos inválidos |

**Mensaje de error**: `ERROR: <archivo>: <causa> (genéralo con: <comando>)`.

## `hito1.md`

Secciones, en este orden:

1. Aviso consultivo
2. Metas del Hito 1
3. Matriz de confusión con abstención (prueba)
4. Abstención y errores con confianza alta
5. Validación cruzada
6. Tiempos de detección por corrida (prueba)
7. Regla de ATWS
8. Etapa 2 (rama caliente o fría)
9. Falsas alarmas
10. Lectura honesta y limitaciones
11. Fuentes y reproducción
