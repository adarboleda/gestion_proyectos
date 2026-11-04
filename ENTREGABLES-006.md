# Sexta iteración SDD: `006-regla-atws` (KAN-22)

**Tarea de Jira**: KAN-22 «Regla determinista de ATWS (demanda de disparo sin caída de flujo)» · **Responsable**: Marcelo Acuña · Fase 2
**Rama**: `006-regla-atws` (desde `002-preprocesamiento-pwr3l-cierre`) · **Fecha**: 2026-11-03 (spec) y 2026-11-04 (resto)
**Herramienta**: GitHub Spec Kit + Claude Code (`claude-opus-5-5`) + `speckit-metricas` · **Constitución**: v2.0.0, sin cambios

> **Estado: completa y `converged`.** 25/25 tareas y 51 pruebas nuevas (suite completa del proyecto: 344, todas verdes). Con la carpeta real detecta **18 de 18 ATWS en ≤ 3 s** desde la demanda de disparo, con **1 falsa alarma en validación** (R54). Esa falsa alarma tiene una causa conocida y se informa tal como sale (sección 4).

---

## 1. Qué pide KAN-22

> Regla fija: si hay demanda de disparo y el flujo neutrónico (PWNT) sigue por encima de un umbral pasados 2 s, es ATWS. Definir la señal de demanda con la experta y calibrar el umbral con las corridas de ATWS y de disparo correcto. **Meta: detectar ATWS en 3 s o menos.**

Un ATWS es un accidente en el que el reactor debía apagarse y no se apagó. Tras un disparo correcto, el flujo neutrónico cae a ~6 % en 1 s; en un ATWS sigue alto. La regla es la primera barrera del diagnóstico rápido: es explicable, no necesita entrenamiento y es **consultiva** (recomienda; no actúa sobre la planta).

---

## 2. Cómo funciona la regla (para explicar)

```
señal de disparo ──► + retardo de la lógica ──► demanda ──► +2 s ──► ¿PWNT > umbral? ──► «posible ATWS»
(registro .dat o           (por tipo de señal,                      (% del PWNT inicial)     (recomendación)
 PWNT ≥ 118 %)              medido en entrenamiento)
```

1. **Señal de disparo**: la primera señal del sistema de protección en el registro de eventos de PCTran (Low SG Level, Turbine trip, RCP-A trip, Scram …), sin contar «Reactor Scram», que es el resultado. Si antes el flujo llega a 118 % (alto flujo), cuenta eso: así se cubren los ATWS por extracción de barras, que no registran señal (R97).
2. **Retardo de la lógica de protección**: no todas las señales disparan al instante. Por ejemplo, en un disparo de turbina el scram llega 5 s después. Si se mide «2 s desde la señal», los TRIP_OK de turbina parecerían ATWS. Por eso, para cada tipo de señal se usa el mayor tiempo señal → scram observado **en entrenamiento**.
3. **Decisión**: en el primer segundo a ≥ 2 s de la demanda, si PWNT / PWNT inicial supera el umbral, la regla recomienda «posible ATWS».
4. **Umbral**: punto medio entre el ATWS con menor flujo y el no-ATWS con mayor flujo, **solo con entrenamiento** (reparto sin fuga de 004).

---

## 3. Resultado con la carpeta real

**Regla calibrada (63 corridas de entrenamiento)**:
- Umbral: **PWNT > 19.3 %** del inicial.
- Margen: el ATWS con menor flujo queda en 32.9 % (R26, pérdida de red) y el no-ATWS con mayor flujo en 5.7 %. Separación de 27 puntos, sin solape.
- Retardos medidos: Low SG Level 1 s, RCP-A trip 2.5 s y señales «Scram …» 0.5 s.

| Conjunto | ATWS detectados | Omitidos | Falsas alarmas | Rechazos correctos | Total |
|---|---|---|---|---|---|
| Entrenamiento | 12 | 0 | 0 | 51 | 63 |
| Validación | 3 | 0 | **1** (R54) | 11 | 15 |
| Prueba | 3 | 0 | 0 | 10 | 13 |

**Meta de 3 s: cumplida en 18 de 18 ATWS** (2–2.5 s desde la demanda). Desde la señal del anunciador: 3 a 5 s.

---

## 4. La falsa alarma de R54 (lectura honesta)

- **R54** es un TRIP_OK por **disparo de turbina** (scram 5 s después de la señal).
- Con el reparto de 004, la única TRIP_OK de turbina usable cae en **validación**; su gemela R55 es corta. En entrenamiento no hay ningún disparo de turbina con scram, así que no hay retardo medido para ese tipo.
- La regla le asigna el mayor retardo de entrenamiento (2.5 s), mira el flujo antes de que llegue el scram y recomienda «posible ATWS».
- **No se ajustó la regla para quitarla**: cambiarla después de ver validación sería fuga de datos (principio II).
- **Propuesta para revisar con la experta**: tomar los retardos de la documentación de diseño de la lógica de protección (turbina 5 s, como `TRXT` de PCTran). Al ser datos de diseño y no aprendidos, no generan fuga.

En el prototipo con el reparto de la rama 002 esta corrida estaba en entrenamiento y no había falsas alarmas: el resultado depende de qué corridas caen en entrenamiento, algo esperable con tan pocas corridas.

---

## 5. Fases de Spec Kit

| # | Fase | Resultado | Archivo |
|---|---|---|---|
| 1 | Especificar | 3 historias, 10 FR, 6 SC | [spec.md](specs/006-regla-atws/spec.md) |
| 2 | Aclarar | 3 preguntas: retardo de un tipo no visto, elección del umbral, meta desde la demanda | spec.md |
| 3 | Planificar | 7 decisiones, modelo de datos, 2 contratos | [plan.md](specs/006-regla-atws/plan.md), [research.md](specs/006-regla-atws/research.md) |
| 4 | Tareas | 21 tareas, pruebas primero; 55 puntos | [tasks.md](specs/006-regla-atws/tasks.md) |
| 5 | Analizar | 5 hallazgos (0 críticos), corregidos antes de programar | [analisis-inicial.md](specs/006-regla-atws/analisis-inicial.md) |
| 6 | Implementar | 21/21 | `src/regla_atws/`, `tests/atws/` |
| 7 | Converge | 1.ª pasada: 4 hallazgos (T022–T025); 2.ª pasada: **converged** | [auditoria.md](specs/006-regla-atws/auditoria.md) |

### Código

| Módulo | Qué hace |
|---|---|
| `config.py` | Señales del sistema de protección, alto flujo 118 %, espera 2 s, meta 3 s, aviso consultivo |
| `eventos.py` | Lee el `.dat`, normaliza el tipo de señal, primera señal o alto flujo, instante del scram |
| `regla.py` | Calibra retardos y umbral solo con entrenamiento; evalúa una corrida |
| `reporte.py` | Tabla por conjunto, errores, tiempos frente a la meta, advertencias y limitaciones |
| `cli.py` | `evaluar-regla-atws`: corridas (002) → reparto verificado (004) → calibración → evaluación → `regla.json`, `evaluacion.csv`, `resumen.json` |

---

## 6. Métricas (`speckit-metricas`)

| Medida | Valor |
|---|---|
| Sesiones | especificar, aclarar, planificar, tareas, analizar e implementar: 0.25 h cada una (mínimo de la extensión) |
| Código | `src/regla_atws/` 504 líneas, 0 eliminadas |
| Pruebas | 51 nuevas; 3 correcciones de pruebas con `Causa: defecto` |
| Puntos de tarea | 55 del plan + 4 de convergencia |
| Desperdicio de código | 0 % |

---

## 7. Limitaciones

- **La señal de demanda y los retardos salen del simulador** y están pendientes de validar con la experta, como pide KAN-22.
- En los ATWS el registro de eventos puede omitir la señal real de disparo. R91 no registra «Scram High Prz Level», que sí aparece en su gemela R99.
- El tiempo de detección desde la demanda queda entre 2 y 3 s **por construcción** (espera de 2 s y muestreo de 1 s). El dato informativo es el tiempo desde el anunciador.
- Hay ~3 ATWS por conjunto de validación y prueba, sin ruido de sensores.

---

## 8. Cómo verificarlo

```
.venv/Scripts/python.exe -m pytest tests/atws -q     # 51 passed
.venv/Scripts/evaluar-regla-atws                     # reporte + resultados_regla_atws/
```
