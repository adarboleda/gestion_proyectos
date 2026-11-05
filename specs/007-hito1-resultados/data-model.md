# Data Model: Hito 1

## Fuente (`config.FUENTES`)

| Clave | KAN | Responsable | Comando | Archivo por defecto |
|---|---|---|---|---|
| `etapa1` | KAN-23 | Abner Arboleda | `entrenar-etapa1` | `modelos/etapa1/reporte.json` |
| `regla` | KAN-22 | Marcelo Acuña | `evaluar-regla-atws` | `resultados_regla_atws/resumen.json` (+ `regla.json`) |
| `tiempos` | KAN-25 | Abner Arboleda | `medir-tiempo-deteccion` | `resultados_tiempo_deteccion/tiempos.json` |
| `etapa2` | KAN-24 | Christian Bonifaz | `entrenar-etapa2` | `modelos/etapa2/reporte.json` |
| `diagnostico` | KAN-26 | Christian Bonifaz | `evaluar-diagnostico --modelo modelos/etapa1` | `resultados_evaluacion_diagnostico/evaluacion_diagnostico.json` |

## Meta

`{id, fuente, definicion, valor, conjunto, estado}`. El estado es `cumple`, `no cumple` o `sin datos`.

## Hito (`hito1.json`)

| Clave | Contenido |
|---|---|
| `version_formato`, `aviso` | Versión y aviso consultivo |
| `fuentes` | Por fuente: `{kan, responsable, comando, archivo, sha256}` |
| `metas` | Lista de metas |
| `diagnostico` | `{prueba, validacion}`, cada uno con la matriz 3 × 4, las tasas y sus IC; y `validacion_cruzada` |
| `tiempos` | Corridas de prueba (008): corrida, clase, área, falla, tiempo de diagnóstico, ATWS |
| `regla` | Tabla por conjunto, umbral y errores (006) |
| `etapa2` | Global, metas y corridas (009) |
| `falsas_alarmas` | De 005, 006 y 008 |
| `etapa1` | F1 global, por familia y de los primeros 30 s; reparto; mejor época |
| `limitaciones` | Lista de texto |
