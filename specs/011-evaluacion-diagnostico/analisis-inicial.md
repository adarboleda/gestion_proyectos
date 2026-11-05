# Análisis de Especificación y Cobertura: 011-evaluacion-diagnostico

**Fecha**: 2026-11-04 | **Herramienta**: Spec Kit Analyzer

---

## 1. Cobertura de Requisitos Funcionales vs Tareas

| Requisito | Descripción | Tareas Asociadas | Cobertura |
|---|---|---|---|
| FR-001 | Exactitud con abstención, tasa de abstención, errores alta confianza y exactitud decididas | T003, T004 | 100 % |
| FR-002 | Evaluación conjunta en validación y prueba | T004, T008, T009 | 100 % |
| FR-003 | Intervalos de Wilson al 95 % para proporciones | T003, T004 | 100 % |
| FR-004 | Matriz de confusión rectangular 3x4 (NORM, LOCA, TRANS, UNCERTAIN) | T003, T004 | 100 % |
| FR-005 | Detalle de instancias erróneas con alta confianza | T003, T004, T008 | 100 % |
| FR-006 | Validación cruzada agrupada de k=5 folds sin fuga de datos | T005, T006 | 100 % |
| FR-007 | Métricas con abstención por fold, media, std e IC del 95 % en CV | T005, T006, T008 | 100 % |
| FR-008 | Comando de consola `evaluar-diagnostico` | T001, T007, T009 | 100 % |
| FR-009 | Argumentos `--origen`, `--salida`, `--modelo`, `--k`, `--semilla` | T007, T009 | 100 % |
| FR-010 | Publicación atómica de `evaluacion_diagnostico.json` y `evaluacion_diagnostico.txt` | T007, T009 | 100 % |
| FR-011 | Determinismo estricto con semilla fijada | T006, T007, T009 | 100 % |
| FR-012 | Aviso consultivo de planta obligatorio en reportes | T008, T009 | 100 % |
| FR-013 | Suite de pruebas automatizadas en `tests/evaluacion_diagnostico/` | T002, T003, T005, T007, T012 | 100 % |
| FR-014 | No modificar datos de origen ni romper interfaces existentes | T010, T012 | 100 % |

---

## 2. Cobertura de Criterios de Éxito (Success Criteria)

| Criterio | Meta | Verificación |
|---|---|---|
| SC-001 | Reporte muestra juntas exactitud con abstención, tasa abstención y errores alta confianza | T004, T008, `test_metricas.py` |
| SC-002 | Matrices 3x4 cuadran con los totales reales por clase | T004, `test_metricas.py` |
| SC-003 | Todas las métricas de proporción incluyen intervalos de Wilson al 95 % | T004, `test_metricas.py` |
| SC-004 | Validación cruzada de 5 folds sin solape reporta medias y desviaciones estándar | T006, `test_validacion_cruzada.py` |
| SC-005 | 100 % de pruebas en verde y 0 regresiones globales | T012, suite global de pruebas |

---

## 3. Hallazgos Identificados y Resoluciones

- **Hallazgo 1 (Bajo - Rendimiento en validación cruzada)**:
  - *Detalle*: Entrenar 5 modelos Bi-LSTM completos desde cero en k-fold con 40 épocas podría tomar varios minutos en CPU si se reentrena por completo en cada invocación de prueba.
  - *Resolución*: Se implementará un mecanismo ágil: en el CLI y en las funciones de entrenamiento por fold se permitirá parametrizar épocas (p. ej. `--epocas 5` para pruebas rápidas y deterministas) y evaluar sobre los modelos ligeros o checkpoints existentes.
- **Hallazgo 2 (Bajo - Tolerancia a clases sin muestras)**:
  - *Detalle*: Si un fold de validación o prueba no tiene muestras de alguna clase, la matriz y métricas deben manejar `0` muestras sin divisiones por cero.
  - *Resolución*: Se incluye explícitamente la salvaguarda de división cero devolviendo `None` o `0.0` según corresponda.
- **Hallazgo 3 (Bajo - Registro en pyproject.toml)**:
  - *Detalle*: Para que el comando `evaluar-diagnostico` esté disponible en el entorno virtual, debe agregarse a `[project.scripts]` en `pyproject.toml` y reinstalarse en modo editable (`-e .`).
  - *Resolución*: T001 actualiza `pyproject.toml` y se reinstala en editable con `--no-build-isolation --no-deps`.

**Conclusión del análisis**: No se detectan brechas bloqueantes. Plan aprobado para implementación.
