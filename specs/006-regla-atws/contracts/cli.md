# Contrato: `evaluar-regla-atws`

```
evaluar-regla-atws [--origen RUTA] [--salida RUTA] [--semilla N]
python -m regla_atws [mismas opciones]
```

| Opción | Por defecto | Descripción |
|---|---|---|
| `--origen` | `../IA-Nuclear/PWR 3L` | Carpeta PWR 3L (solo lectura) |
| `--salida` | `resultados_regla_atws` | Carpeta de resultados |
| `--semilla` | `42` | Semilla del reparto (la de 004) |

**Códigos de salida**:

| Código | Significado |
|---|---|
| 0 | Éxito |
| 1 | Error de datos (de 002, del reparto de 004 o del registro de eventos) o de escritura; no se publica nada |
| 2 | Argumentos inválidos |

**Errores propios**:
- `ERROR: <carpeta>: no hay registro de eventos (.dat)`
- `ERROR: <carpeta>: hay más de un registro de eventos (.dat)`
- `ERROR: <archivo .dat>: registro ilegible (<tipo>)`

## Reporte

```
REPORTE DE LA REGLA DE ATWS (PWR 3L)
RECOMENDACIÓN PARA EL OPERADOR: la regla no actúa sobre la planta ni sustituye la protección.
== 1. Configuración ==          origen, semilla, espera 2 s, alto flujo 118 %, meta 3 s desde la demanda
== 2. Regla calibrada ==        umbral, retardos por tipo, margen (mín ATWS, máx no-ATWS), con entrenamiento
== 3. Resultados por conjunto == tabla train/val/test: detectados, omitidos, falsas alarmas, rechazos correctos
== 4. Tiempos de detección ==   cada ATWS: conjunto, señal, demanda, decisión, tiempo desde demanda y desde señal
== 5. Errores ==                omisiones y falsas alarmas nombradas, o «Ninguno»
== 6. Advertencias ==
== 7. Limitaciones ==
== 8. Artefactos escritos ==
```
