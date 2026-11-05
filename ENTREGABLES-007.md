# Séptima iteración SDD: `007-hito1-resultados` (KAN-27, Hito 1)

**Tarea de Jira**: KAN-27 «HITO 1 — Presentación de resultados preliminares» · **Responsable**: Marcelo Acuña (con Abner Arboleda y Christian Bonifaz) · Fase 2 · vence el 19/nov
**Ramas**: `007-hito1-resultados` (spec, PR #6) y `007-hito1-resultados-cierre` (resto, desde `main` con 008–011) · **Fecha**: 2026-11-04
**Herramienta**: GitHub Spec Kit + Claude Code (`claude-opus-5-5`) + `speckit-metricas` · **Constitución**: v2.0.0, sin cambios

> **Estado: completa y `converged`.** 16/16 tareas y 31 pruebas nuevas (suite completa del proyecto: 489, todas verdes). El comando `informe-hito1` genera el informe del Hito 1 con los resultados reales. **Copia del informe**: [specs/007-hito1-resultados/hito1-2026-11-04.md](specs/007-hito1-resultados/hito1-2026-11-04.md).

---

## 1. Qué pide KAN-27

> Demostración del diagnóstico: matriz de confusión, tiempos de detección frente a las metas (10 s y 3 s) y tasa de abstención.

El Hito no hace un modelo nuevo: **reúne lo que hizo cada uno** en la Fase 2 en un informe reproducible para la presentación.

| Tarea | Responsable | Qué aporta al Hito |
|---|---|---|
| KAN-23 (005) Etapa 1 | Abner | F1 por familia y falsas alarmas en NORM |
| KAN-22 (006) Regla de ATWS | Marcelo | ATWS detectados, falsas alarmas y umbral |
| KAN-25 (008) Tiempo desde la falla | Abner | **Metas de 10 s y 3 s** |
| KAN-24 (009) Etapa 2 | Christian | Rama caliente o fría |
| KAN-26 (011) Evaluación | Christian | **Matriz con abstención**, **tasa de abstención** y validación cruzada |

---

## 2. Cómo funciona (para explicar)

```
entrenar-etapa1 → evaluar-regla-atws → medir-tiempo-deteccion → entrenar-etapa2 → evaluar-diagnostico
        │                 │                     │                      │                  │
        └─────────────────┴─────────── archivos de resultados ─────────┴──────────────────┘
                                              │
                                        informe-hito1  →  hito1.md (presentación) + hito1.json
```

- **No reentrena ni recalcula**: copia cada cifra del archivo de su responsable y guarda su **SHA-256**, para que se pueda comprobar de dónde sale.
- Si falta un archivo, se detiene y dice **qué comando** hay que ejecutar.
- Cada sección dice de qué tarea (KAN) sale. Las metas que no se cumplen se muestran tal cual, con su definición.

---

## 3. Resultados del Hito 1 (datos reales, esta máquina)

| Meta | Valor | Estado |
|---|---|---|
| **Diagnóstico ≤ 10 s desde la falla** (prueba) | 10 de 10 | **cumple** |
| **ATWS ≤ 3 s desde la demanda** (validación y prueba) | 6 de 6 | **cumple** |
| LOCA ≥ 50 cm² en ≤ 10 s (Etapa 1) | 2 de 2 | cumple |
| F1 de los primeros 30 s ≥ 0.80 (Etapa 1) | 0.948 | cumple |
| 0 falsas alarmas en NORM (Etapa 1) | 3 (R33, R36, R40) | no cumple |
| Etapa 2 sin errores con confianza | 0 errores, **cobertura 0 %** | cumple sin decisiones |
| Etapa 2: LOCA ≥ 50 cm² con su rama en ≤ 10 s | 0 de 2 | no cumple |
| Regla de ATWS sin falsas alarmas | 1 (R54, validación) | no cumple |

**Matriz de confusión con abstención (Etapa 1, prueba, 3 835 segundos)**:

| Verdadera \ Recomendada | NORM | LOCA | TRANS | UNCERTAIN |
|---|---|---|---|---|
| NORM | 1107 | 0 | 12 | 74 |
| LOCA | 12 | 1285 | 0 | 2 |
| TRANS | 0 | 92 | 1250 | 1 |

**Tasa de abstención: 2.0 %** (IC 95 %: 1.6–2.5 %) · errores con confianza alta: 3.0 % · exactitud con abstención: 95.0 %. Validación cruzada (k = 5): exactitud estándar 95.6 % (IC 91.1–100 %).

---

## 4. Lectura honesta (para la presentación)

1. **Las dos metas del Hito (10 s y 3 s) se cumplen** con esta ejecución.
2. **La Etapa 2 no decide**: se abstiene siempre. No se equivoca, pero tampoco distingue la rama caliente de la fría.
3. **Falsas alarmas**: la Etapa 1 da 3 en NORM de prueba, y la regla de ATWS 1 en validación (R54, explicada en ENTREGABLES-006).
4. **Las cifras cambian de una máquina a otra.** Abner informó 5 de 10 en el diagnóstico ≤ 10 s y 0 falsas alarmas; aquí salen 10 de 10 y 3. El reentrenamiento en CPU no es idéntico entre máquinas. **Antes del 19/nov el equipo debe acordar una sola ejecución** (o versionar el modelo de Etapa 1 que se presenta) para citar las mismas cifras.

---

## 5. Fases de Spec Kit

| # | Fase | Resultado | Archivo |
|---|---|---|---|
| 1 | Especificar + aclarar | 2 historias, 9 FR, 4 SC, 3 aclaraciones (actualizada al llegar 008–011) | [spec.md](specs/007-hito1-resultados/spec.md) |
| 2 | Planificar | 6 decisiones, modelo de datos, contrato | [plan.md](specs/007-hito1-resultados/plan.md), [research.md](specs/007-hito1-resultados/research.md) |
| 3 | Tareas | 14 tareas, 31 puntos | [tasks.md](specs/007-hito1-resultados/tasks.md) |
| 4 | Analizar | 3 hallazgos (0 críticos) | [analisis-inicial.md](specs/007-hito1-resultados/analisis-inicial.md) |
| 5 | Implementar | 14/14; paquete `informe_hito1`, comando `informe-hito1` | `src/informe_hito1/`, `tests/hito1/` |
| 6 | Converge | 1.ª pasada: 2 hallazgos (T015–T016); 2.ª pasada: **converged** | [auditoria.md](specs/007-hito1-resultados/auditoria.md) |

---

## 6. Métricas

| Medida | Valor |
|---|---|
| Sesiones | especificar, aclarar, planificar, tareas, analizar e implementar (0.25 h cada una, el mínimo de la extensión) |
| Código | `src/informe_hito1/` 384 líneas |
| Pruebas | 31 nuevas; 1 corrección con `Causa: defecto` (legibilidad) |
| Puntos de tarea | 37 (31 del plan + 6 de las 2 tareas de convergencia) |

---

## 7. Cómo verificarlo

```
.venv/Scripts/python.exe -m pytest tests/hito1 -q    # 31 passed
# regenerar: los cinco comandos del quickstart y después
.venv/Scripts/informe-hito1                         # → informe_hito1/hito1.md
```
