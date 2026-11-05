# Research: Hito 1

**Fecha**: 2026-11-04

Medición previa: se ejecutaron con la carpeta real los cinco comandos de la Fase 2 en este orden, con sus valores por defecto y todos con código 0, en unos 4 min:

| Orden | Comando | Tiempo |
|---|---|---|
| 1 | `entrenar-etapa1` | 131 s |
| 2 | `medir-tiempo-deteccion` | 33 s |
| 3 | `entrenar-etapa2` | 24 s |
| 4 | `evaluar-diagnostico --modelo modelos/etapa1` | 44 s |
| 5 | `evaluar-regla-atws` | 8 s |

## 1. Consolidar, no recalcular

- **Decisión**: el Hito lee los archivos publicados (`modelos/etapa1/reporte.json`, `resultados_regla_atws/resumen.json` y `regla.json`, `resultados_tiempo_deteccion/tiempos.json`, `modelos/etapa2/reporte.json` y `resultados_evaluacion_diagnostico/evaluacion_diagnostico.json`).
- **Razón**: cada cifra queda bajo la responsabilidad de su tarea. Recalcular duplicaría código y podría dar otro número.

## 2. Trazabilidad

- **Decisión**: `hito1.json → fuentes` lista, por fuente, la tarea, el responsable, el comando, la ruta relativa y el SHA-256 del archivo. No se guarda fecha ni ruta absoluta, para que la salida sea determinista.

## 3. Metas

- **Decisión**: se copian tal cual las metas que publica cada tarea (definición, valor y estado):
  - 008: `diagnostico_10s` y `atws_3s`;
  - 005: SC-001 a SC-003;
  - 009: SC-001 y SC-002.

  A esas se suma una meta derivada de 006: 0 falsas alarmas de la regla en validación y prueba.
- **Razón**: el Hito no redefine metas. Las dos de KAN-27 (10 s y 3 s) las mide 008 desde la falla.

## 4. Abstención y matriz

- **Decisión**: de 011, la matriz 3 × 4 de prueba y de validación, las tasas de exactitud con abstención, abstención y errores con confianza alta, sus intervalos de Wilson, y el resumen de la validación cruzada (media e IC). Se comprueba que las tres tasas suman 1, como garantiza 011.

## 5. Variación entre máquinas

- **Decisión**: el informe indica que la Etapa 1 y la Etapa 2 se reentrenan en CPU y sus cifras pueden variar un poco de una máquina a otra (por ejemplo, la mejor época de la Etapa 1: 2 en el entregable de 005, 7 en esta máquina). Las cifras del Hito son las de los archivos de la ejecución actual.

## 6. Formato

- **Decisión**: Markdown con tablas, listo para copiar a las diapositivas.
- **Secciones**: aviso, metas, matriz con abstención, validación cruzada, tiempos por corrida, regla de ATWS, Etapa 2, falsas alarmas, limitaciones y lectura honesta, fuentes y reproducción.
