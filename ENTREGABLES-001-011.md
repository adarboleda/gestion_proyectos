# Iteraciones SDD 001 a 011: resumen unificado hasta el Hito 1

**Proyecto**: IANuclear, sistema consultivo para detectar accidentes LOCA y ATWS en reactores PWR con datos simulados
**Equipo**: Marcelo Acuña, Abner Arboleda y Christian Bonifaz
**Metodología**: Desarrollo Guiado por Especificaciones con GitHub Spec Kit y la extensión `speckit-metricas` · **Constitución**: v2.0.0, sin cambios en ninguna iteración
**Periodo**: 2026-10-18 a 2026-11-04 (Fase 1 y Fase 2 hasta el Hito 1, KAN-27)
**Documentos detallados**: `ENTREGABLES.md` (001), [ENTREGABLES-002.md](ENTREGABLES-002.md) … [ENTREGABLES-011.md](ENTREGABLES-011.md) y [ENTREGABLES-002-003-004.md](ENTREGABLES-002-003-004.md)

---

## 1. Visión de conjunto

Las once iteraciones construyen el **diagnóstico rápido** de la planta PWR 3L (un dato por segundo) y preparan los datos de NPPAD:

```
FASE 1 · Datos
NPPAD:   lectura y reparto (001, Abner)  +  paso medido (003)  +  verificación de fuga (004)
PWR 3L:  leer corridas → medir paso → agrupar y repartir sin fuga → escalar → salida, reporte y comando → documentación
         (002, Marcelo)  (003, Christian)    (004, Abner)        (003)       (002, Marcelo)          (010, Christian)

FASE 2 · Diagnóstico rápido
         Etapa 1: NORM / LOCA / TRANS (005, Abner) ──┐
         Regla de ATWS (006, Marcelo) ───────────────┼─► tiempo desde la falla (008, Abner)
         Etapa 2: rama caliente o fría (009, Christian)│
         Evaluación: abstención y validación cruzada (011, Christian)
                                                     └─► HITO 1: informe consolidado (007, Marcelo)
```

| Iteración | Tarea de Jira | Responsable | Rama | Estado | En `main` |
|---|---|---|---|---|---|
| **001** Preparación NPPAD | Fase 1 (base de KAN-19) | Abner Arboleda | `001-preparacion-datos` | Completa, `converged` | Sí (PR #1) |
| **002** Preprocesamiento PWR 3L | KAN-18 | Marcelo Acuña | `002-preprocesamiento-pwr3l` y `-cierre` | Completa, `converged` | Sí (PR #2 y #5) |
| **003** Normalización y paso de muestreo | KAN-20 | Christian Bonifaz | `003-normalizacion-paso-muestreo` | Completa, `converged` | Sí |
| **004** División sin fuga | KAN-19 | Abner Arboleda | `004-division-sin-fuga` | Completa, `converged` | Sí (PR #3) |
| **005** Clasificador de Etapa 1 | KAN-23 | Abner Arboleda | `005-clasificador-etapa1` | Completa, `converged` | Sí (PR #4) |
| **006** Regla de ATWS | KAN-22 | Marcelo Acuña | `006-regla-atws` | Completa, `converged` | Sí (PR #7) |
| **007** Hito 1 | KAN-27 | Marcelo Acuña (con los tres) | `007-hito1-resultados` y `-cierre` | Completa, `converged` | Spec sí (PR #6); cierre pendiente de PR |
| **008** Tiempo desde la falla | KAN-25 | Abner Arboleda | `008-tiempo-desde-falla` | Completa, `converged` | Sí (PR #8) |
| **009** Clasificador de Etapa 2 | KAN-24 | Christian Bonifaz | `009-clasificador-etapa2` | Completa, `converged` | Sí (fusión directa) |
| **010** Documentación del dataset | KAN-21 | Christian Bonifaz | `010-documentacion-dataset` | Completa, `converged` | Sí (fusión directa) |
| **011** Evaluación del diagnóstico | KAN-26 | Christian Bonifaz | `011-evaluacion-diagnostico` | Completa, `converged` | Sí (fusión directa) |

---

## 2. Resumen corto de cada iteración (para exponer)

### 001 · Preparación de datos NPPAD (Abner Arboleda)

- **Qué se hizo**: comando `preparar-datos`. Lee las 202 simulaciones NPPAD, toma 150 pasos de 10 s, reparte por simulación completa con LOCA y LOCAC de igual severidad juntas (70/15/15), escala solo con entrenamiento y publica los artefactos todos o ninguno.
- **Resultado**: 142 / 30 / 30 muestras; la comparación con el proyecto previo da `COINCIDE`. 39/39 tareas y 79 pruebas.

### 002 · Preprocesamiento PWR 3L (Marcelo Acuña, KAN-18)

- **Problema**: PWR 3L es otra planta (2705 MWt, 1 s) y no puede mezclarse con NPPAD.
- **Qué se hizo**:
  - Descubrimiento y lectura de 109 corridas en dos formatos (los `.xls` son libros xlsx).
  - Cinco clases (NORM, LOCA, LOCAC, ATWS, TRIP_OK) y muestras de 300 s.
  - Corridas cortas excluidas con aviso, sin inventar datos.
  - Salida, márgenes térmicos, reporte y comando `preparar-pwr3l`, integrados con 003 y 004.
- **Resultado**: 91 muestras (63 / 15 / 13), 0 violaciones de fuga. 38/38 tareas.

### 003 · Normalización y paso de muestreo (Christian Bonifaz, KAN-20)

- **Qué se hizo**: el paso de tiempo se **mide** en cada archivo en lugar de suponerse, y el escalado de PWR 3L se ajusta solo con entrenamiento.
- **Resultado**: NPPAD 10 s y PWR 3L 1 s exactos y constantes. 22/22 tareas.

### 004 · División sin fuga (Abner Arboleda, KAN-19)

- **Qué se hizo**: grupos (LOCA/LOCAC por área de rotura, gemelas ATWS/TRIP_OK), reparto 70/15/15 por familia y verificación independiente de fuga.
- **Hallazgo**: el método del proyecto anterior dejaba 6 de 10 áreas partidas entre entrenamiento y prueba; con 004 son 0. 25/25 tareas.

### 005 · Clasificador de Etapa 1 (Abner Arboleda, KAN-23)

- **Qué se hizo**: Bi-LSTM que cada segundo mira los últimos 30 s y recomienda la familia del evento (NORM, LOCA o TRANS), o «INCIERTO» si no llega a 0.80 de confianza.
- **Resultado (su entregable)**: F1 macro 0.978. Los transitorios con disparo se confirman en 2–4 s; la familia LOCA tarda 19 s o más, así que no cumple su meta de detección temprana. 35/35 tareas.

### 006 · Regla de ATWS (Marcelo Acuña, KAN-22)

- **Qué se hizo**: regla fija y explicable. Si hay demanda de disparo y 2 s después el flujo neutrónico sigue alto, recomienda «posible ATWS». La demanda es la señal del sistema de protección más el retardo de su lógica. El umbral se calibra solo con entrenamiento (19.3 % del flujo inicial).
- **Resultado**: **18 de 18 ATWS en ≤ 3 s** desde la demanda. Hay 1 falsa alarma en validación (R54, disparo de turbina), cuyo tipo de señal no aparece en entrenamiento; no se corrigió mirando validación. 25/25 tareas.

### 007 · Informe del Hito 1 (Marcelo Acuña, KAN-27)

- **Qué se hizo**: comando `informe-hito1`. Consolida los resultados de 005, 006, 008, 009 y 011 **sin recalcular**, con el SHA-256 de cada archivo de origen, y genera `hito1.md` para la presentación.
- **Resultado**: informe con los datos reales en [specs/007-hito1-resultados/hito1-2026-11-04.md](specs/007-hito1-resultados/hito1-2026-11-04.md). 16/16 tareas.

### 008 · Tiempo de detección desde la falla (Abner Arboleda, KAN-25)

- **Qué se hizo**: localiza el instante real de la falla (registro, programado o carpeta) y mide desde ahí el diagnóstico de la Etapa 1 y la regla de ATWS frente a las metas de 10 s y 3 s.
- **Resultado (su entregable)**: ATWS ≤ 3 s cumple (6 de 6). Diagnóstico ≤ 10 s **no cumple** (5 de 10), porque los LOCA pequeños tardan. 31/31 tareas.

### 009 · Clasificador de Etapa 2 (Christian Bonifaz, KAN-24)

- **Qué se hizo**: red que distingue la rama caliente (LOCA) de la fría (LOCAC) tras reconocer la familia LOCA.
- **Resultado**: 0 errores con confianza alta, pero **se abstiene en todas las muestras** de prueba: no decide la rama. La meta de confirmar roturas ≥ 50 cm² en ≤ 10 s no se cumple (0 de 2). 18/18 tareas.

### 010 · Documentación del dataset (Christian Bonifaz, KAN-21)

- **Qué se hizo**: README de la Fase 1 con el origen de los datos, el modelo de planta, las variables, los conteos por clase y conjunto y las limitaciones; versiona los `metadata.json`.
- **Resultado**: 12/12 tareas (es una iteración de documentación, sin código de producción).

### 011 · Evaluación del diagnóstico (Christian Bonifaz, KAN-26)

- **Qué se hizo**: matriz de confusión 3 × 4 con la columna «UNCERTAIN». Tres tasas que suman 1: exactitud con abstención, abstención y errores con confianza alta. Intervalos de Wilson y validación cruzada agrupada (k = 5) sin fuga.
- **Resultado (ejecución del Hito)**: abstención del 2.0 % en prueba, exactitud con abstención del 95 %. 12/12 tareas.

---

## 3. Fases de Spec Kit en cada iteración

Todas pasaron por `/speckit-specify` → `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement` → `/speckit-converge`.

| Iteración | Historias / FR / SC | Tareas | Puntos (plan + agregados) | Hallazgos del análisis | Converge |
|---|---|---|---|---|---|
| 001 | 3 / 13 / 8 | 39 | 103 (82 + 21) | 9 (0 críticos) | 2 pasadas, `converged` |
| 002 | 3 / 16 / 8 | 38 | 99 (95 + 4) | 8 (0 críticos) | 2 pasadas, `converged` |
| 003 | 3 / 14 / 6 | 22 | 48 | 3 bajos | `converged` |
| 004 | 3 / 15 / 7 | 25 | 54 | 7 (0 críticos) | `converged` |
| 005 | 3 / 15 / 7 | 35 | 108 (97 + 11) | 6 (0 críticos) | 2 pasadas, `converged` |
| 006 | 3 / 10 / 6 | 25 | 59 (55 + 4) | 5 (0 críticos) | 2 pasadas, `converged` |
| 007 | 2 / 9 / 4 | 16 | 37 (31 + 6) | 3 (0 críticos) | 2 pasadas, `converged` |
| 008 | 3 / 15 / 7 | 31 | 86 (73 + 13) | 6 (0 críticos, 2 altos) | 2 pasadas, `converged` |
| 009 | 3 / 15 / 6 | 18 | 67 | 3 bajos | `converged` |
| 010 | 3 / 14 / 5 | 12 | 25 | 3 bajos | `converged` |
| 011 | 4 / 14 / 5 | 12 | 43 | 0 inconsistencias | `converged` |

---

## 4. Métricas unificadas (`speckit-metricas`, `recolectar` del 2026-11-05)

Todas las cifras salen del mismo cálculo (`metricas/salidas/resumen-funcionalidades.csv`), así que son comparables entre iteraciones. Pueden diferir un poco de los documentos individuales; las notas explican por qué.

### 4.1 Tamaño de la especificación

| Medida | 001 | 002 | 003 | 004 | 005 | 006 | 007 | 008 | 009 | 010 | 011 | **Total** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Historias de usuario | 3 | 3 | 3 | 3 | 3 | 3 | 2 | 3 | 3 | 3 | 4 | **33** |
| Requisitos funcionales | 13 | 16 | 14 | 15 | 15 | 10 | 9 | 15 | 15 | 14 | 14 | **150** |
| Criterios de éxito | 8 | 8 | 6 | 7 | 7 | 6 | 4 | 7 | 6 | 5 | 5 | **69** |
| Escenarios de aceptación | 9 | 10 | 13 | 15 | 11 | 9 | 6 | 11 | 12 | 8 | 9 | **113** |
| Tareas (todas hechas) | 39 | 38 | 22 | 25 | 35 | 25 | 16 | 31 | 18 | 12 | 12 | **273** |
| Puntos de tarea | 103 | 99 | 48 | 54 | 108 | 59 | 37 | 86 | 67 | 25 | 43 | **729** |

### 4.2 Esfuerzo

| Medida | 001 | 002 | 003 | 004 | 005 | 006 | 007 | 008 | 009 | 010 | 011 | **Total** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Horas registradas | 2.75 | 1.75 | 1.50 | 1.75 | 2.50 | 1.75 | 1.50 | 2.50 | 1.50 | 1.50 | 1.50 | **20.5 h** |
| Sesiones | 10 | 7 | 6 | 7 | 10 | 6 | 6 | 9 | 6 | 6 | 6 | **79** |
| Persona-mes | 0.0181 | 0.0115 | 0.0099 | 0.0115 | 0.0164 | 0.0115 | 0.0099 | 0.0164 | 0.0099 | 0.0099 | 0.0099 | **0.1349** |

Por fase (proyecto): constitución 0.5 h, especificar 2.75 h, aclarar 2.75 h, planificar 2.75 h, tareas 2.75 h, analizar 4.25 h, implementar 4.5 h y gestión 0.25 h.

Modelos de IA: `claude-sonnet-5-5` (001), `claude-opus-5-5` (002, 004–008), `claude-opus-5-5:medium` + `gemini-4-argon:low` (003) y `claude-opus-5-5:low` (009–011).

⚠ Las horas son el **mínimo que la extensión registra por sesión (0.25 h)**, no un cronómetro. No se informaron tokens ni costo; la tarifa humana configurada es 0, por eso el costo sale en 0.

### 4.3 Código, pruebas y desperdicio

| Medida | 001 | 002 | 003 | 004 | 005 | 006 | 007 | 008 | 009 | 010 | 011 | **Total** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Commits | 16 | 28 | 12 | 17 | 27 | 19 | 15 | 22 | 9 | 8 | 7 | **186** |
| Código agregado | 629 | 1086 | 266 | 276 | 864 | 504 | 386 | 857 | 941 | 0 | 665 | **7089** |
| Código que sobrevive | 591 | 644 | 266 | 275 | 864 | 504 | 384 | 842 | 941 | 0 | 665 | **6591** |
| Desperdicio | 38 | 442 ⁽¹⁾ | 0 | 1 | 0 | 0 | 2 | 15 | 0 | 0 | 0 | **498 (7.0 %)** |
| Pruebas agregadas | 1009 | 1611 | 376 | 568 | 702 | 652 | 405 | 835 | 664 | 165 | 376 | **8365** |

**Notas**

1. **Las 442 líneas de 002** son código que se escribió en la rama `002-preprocesamiento-pwr3l` y nunca llegó a `main`. Esa rama siguió avanzando con versiones propias de grupos, reparto y escalado mientras 003 y 004 hacían las suyas en `main`. El cierre de KAN-18 se hizo sobre `main`, usando los módulos de 003 y 004, y las versiones duplicadas quedaron fuera. Es trabajo duplicado entre personas, **no** un error del código: la lección es coordinar quién hace cada módulo antes de empezar.
2. Las eliminaciones de 003 (36 líneas) son «por requisito» (el paso fijo se reemplazó por el paso medido) y no cuentan como desperdicio de 003.
3. 008 tiene 7 líneas eliminadas sin el trailer `Causa:`.

### 4.4 Proyecto completo (001–011)

| Medida | Valor |
|---|---|
| Funcionalidades | 11 |
| Historias / FR / SC / escenarios | 33 / 150 / 69 / 113 |
| Tareas | **273 de 273 hechas** |
| Puntos de tarea | 729 (670 del plan + 59 agregados por convergencia) |
| Código | 7089 líneas agregadas; **6591 sobreviven** |
| Pruebas | +8365 líneas; **489 pruebas automáticas en verde** (con los datos reales) |
| Desperdicio | 498 líneas (7.0 %): 45 por requisito, 16 por defecto, 8 sin clasificar, y el resto por el trabajo duplicado de la nota 1 |
| Esfuerzo | 20.5 h en 79 sesiones (0.1349 persona-mes); calendario de 22 días |
| Commits | 186 |

---

## 5. Lo que hizo cada uno

| | Marcelo Acuña | Abner Arboleda | Christian Bonifaz |
|---|---|---|---|
| **Tareas** | KAN-18, KAN-22, KAN-27 | 001, KAN-19, KAN-23, KAN-25 | KAN-20, KAN-21, KAN-24, KAN-26 |
| **Iteraciones** | 002, 006, 007 | 001, 004, 005, 008 | 003, 009, 010, 011 |
| **Aporte principal** | Datos PWR 3L de 5 clases, regla de ATWS, informe del Hito 1 | Datos NPPAD, reparto sin fuga, Etapa 1, tiempos desde la falla | Paso medido y escalado, Etapa 2, documentación, evaluación con abstención |
| **Puntos de tarea** | 195 | 351 | 183 |
| **Código que sobrevive** | 1532 | 2572 | 1872 |
| **Comandos** | `preparar-pwr3l`, `evaluar-regla-atws`, `informe-hito1` | `preparar-datos`, `entrenar-etapa1`, `medir-tiempo-deteccion` | `entrenar-etapa2`, `evaluar-diagnostico` |

---

## 6. Resultado del Hito 1 (KAN-27)

Cifras de la ejecución consolidada del 2026-11-04 ([hito1-2026-11-04.md](specs/007-hito1-resultados/hito1-2026-11-04.md)):

| Meta | Valor | Estado |
|---|---|---|
| Diagnóstico ≤ 10 s desde la falla (prueba) | 10 de 10 | cumple |
| ATWS ≤ 3 s desde la demanda (validación y prueba) | 6 de 6 | cumple |
| 0 falsas alarmas de la Etapa 1 en NORM | 3 | no cumple |
| Etapa 2: rama confirmada en ≤ 10 s | 0 de 2 (se abstiene siempre) | no cumple |
| Regla de ATWS sin falsas alarmas | 1 (R54) | no cumple |
| Tasa de abstención de la Etapa 1 (prueba) | 2.0 % (IC 1.6–2.5 %) | — |

⚠ **Las cifras cambian de una máquina a otra.** El reentrenamiento en CPU no es idéntico entre computadoras. Abner midió el diagnóstico ≤ 10 s en 5 de 10 y 0 falsas alarmas; la ejecución del Hito da 10 de 10 y 3. Antes de la presentación hay que acordar una sola ejecución o versionar el modelo de Etapa 1.

---

## 7. Carpetas: dónde está cada cosa

```
gestion_proyectos/
├── ENTREGABLES.md, ENTREGABLES-002.md … ENTREGABLES-011.md   ← detalle de cada iteración
├── ENTREGABLES-002-003-004.md          ← resumen de la Fase 1 (PWR 3L)
├── ENTREGABLES-001-011.md              ← este documento
├── specs/NNN-…/                        spec, plan, research, data-model, contracts/, quickstart,
│                                       tasks, puntos-tarea.csv, analisis-inicial, auditoria, checklists/
├── src/
│   ├── preparacion_datos/              001 (+ 003, 004)
│   ├── preparacion_pwr3l/              002 (+ 003, 004)
│   ├── clasificador_etapa1/            005
│   ├── regla_atws/                     006
│   ├── informe_hito1/                  007
│   ├── tiempo_deteccion/               008
│   ├── clasificador_etapa2/            009
│   └── evaluacion_diagnostico/         011
├── tests/                              una carpeta por funcionalidad; datos_reales.py (IANUCLEAR_DATOS)
└── metricas/sesiones/                  79 sesiones (un archivo por sesión)
```

---

## 8. Pendientes del equipo

| Pendiente | Responsable previsto | Detalle |
|---|---|---|
| PR de `007-hito1-resultados-cierre` | Marcelo Acuña | Subir la rama y abrir el pull request hacia `main` |
| Acordar una sola ejecución para la presentación | Los tres | Las cifras de la Etapa 1, 008 y 011 cambian entre máquinas (sección 6) |
| Validar la señal de demanda de disparo con la experta | Marcelo Acuña | KAN-22 lo pide; propuesta: retardos de diseño de la lógica (quitaría R54) |
| Mejorar la Etapa 2 | Christian Bonifaz | Hoy no decide ninguna rama |
| `resultados_evaluacion_diagnostico/` en `.gitignore` | Christian Bonifaz | Salida regenerable que hoy no está ignorada |
| Trailer `Causa:` en 7 líneas de 008 | Abner Arboleda | Solo para que las métricas clasifiquen bien el desperdicio |
| Diapositivas del Hito 1 (19/nov) | Los tres | A partir de `hito1.md` |
