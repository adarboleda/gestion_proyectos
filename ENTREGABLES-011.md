# Undécima iteración SDD: `011-evaluacion-diagnostico`

**Actividad**: «Evaluación del diagnóstico: matriz de confusión, abstenciones y validación cruzada»  
**Rama**: `011-evaluacion-diagnostico` (creada desde `main`) · **Fecha**: 2026-11-04  
**Herramienta**: GitHub Spec Kit + `speckit-metricas` (`antigravity` / `claude-opus-5-5`) · **Constitución**: v2.0.0, sin cambios  

> **Estado: iteración completa y convergente (`converged`).**  
> Se ejecutaron rigurosamente todas las fases del ciclo Spec Kit (`/speckit-specify` → `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → `/speckit-implement` → `/speckit-converge`) y todos los scripts de métricas (`sesion`, `puntos`, `recolectar`, `calibrar`, `estimar`). Las 12 tareas (`T001`–`T012`, 43 puntos de tarea) y las 10 pruebas del subsistema están en verde (suite global del proyecto: **439 pasadas, 19 omitidas, 0 fallos**).

---

## 1. Qué pide la tarea y alcance

> **Descripción**:  
> Reportar juntas la exactitud global (contando UNCERTAIN como no acierto), la tasa de abstención y los errores con confianza alta, en prueba y en validación. Añadir validación cruzada y los intervalos de confianza.

- **Métricas conjuntas y transparencia muestral**:
  - Exactitud global con abstención ($\text{Acc}_{\text{abst}}$): aciertos con confianza divididos entre el total de muestras ($n$). Las muestras con abstención (`UNCERTAIN`) penalizan como no aciertos.
  - Tasa de abstención ($\text{Tasa}_{\text{abst}}$): proporción de instantes donde la confianza softmax máxima es inferior a 0,80.
  - Tasa de errores con confianza alta ($\text{Tasa}_{\text{err}}$): proporción de clasificaciones donde el modelo se equivocó de clase teniendo una confianza $\ge 0,80$.
  - **Partición exhaustiva**: $\text{Acc}_{\text{abst}} + \text{Tasa}_{\text{abst}} + \text{Tasa}_{\text{err}} = 1.0$.
- **Matriz de confusión rectangular $3 \times 4$**:
  - 3 clases verdaderas (`NORM`, `LOCA`, `TRANS`) en las filas.
  - 4 columnas en las predicciones: `NORM`, `LOCA`, `TRANS` y la columna consultiva `UNCERTAIN`.
- **Intervalos de confianza al 95 %**:
  - Para proporciones binomiales: método de Wilson score interval (resistente a muestras reducidas, asimetría y casos en los extremos 0 y 1 sin colapsar a ancho cero).
  - Para medias entre particiones de validación cruzada: distribución $t$-Student con $k-1$ grados de libertad ($\mu \pm t_{\alpha/2, k-1} \cdot s/\sqrt{k}$).
- **Validación cruzada agrupada (*Group K-Fold*, $k=5$)**:
  - Agrupamiento estricto por pares de severidad (roturas LOCA y LOCAC de la misma área) y gemelos ATWS/TRIP_OK.
  - Garantía de **cero fuga de información** (*Principio II de la Constitución*): ningún grupo se divide entre entrenamiento y prueba de un mismo fold.
- **Línea de órdenes y artefactos**:
  - Comando `evaluar-diagnostico` con parámetros `--origen`, `--salida`, `--modelo`, `--k`, `--semilla`, `--epocas`, `--umbral`.
  - Publicación atómica de `evaluacion_diagnostico.json` y `evaluacion_diagnostico.txt`.
  - Retorno de códigos de estado normalizados: 0 (éxito), 1 (error de datos), 3 (falta PyTorch).

---

## 2. Decisiones de diseño y formulación estadística

1. **Partición exhaustiva de las muestras**:
   Cada instante evaluado cae en una y solo una de las siguientes tres categorías mutuamente excluyentes:
   $$\text{Acierto con confianza} \quad (\hat{y} = y \land \max p \ge \theta)$$
   $$\text{Abstención / Incertidumbre} \quad (\max p < \theta \rightarrow \text{UNCERTAIN})$$
   $$\text{Error con confianza alta} \quad (\hat{y} \ne y \land \max p \ge \theta)$$
   Al dividir por el total de muestras $n$, se cumple idénticamente:
   $$\text{Acc}_{\text{abst}} + \text{Tasa}_{\text{abst}} + \text{Tasa}_{\text{err}} = 1.0$$
   Esto impide cualquier manipulación o maquillaje de métricas por descarte selectivo de predicciones difíciles.

2. **Intervalo de Wilson al 95 %**:
   Para una proporción $\hat{p} = k/n$ y nivel de significancia $z = 1.95996$:
   $$IC = \frac{\hat{p} + \frac{z^2}{2n} \pm z\sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$
   Si $n = 0$, el intervalo devuelve `[None, None]`. Si $k = 0$, el extremo inferior es estrictamente 0.0 y el superior es $z^2 / (n + z^2) > 0$.

3. **Validación cruzada sin fuga**:
   La función `particionar_kfold_por_grupos` agrupa las corridas usables en función de su identificador de severidad pareada (`AREA-<area>`) o gemelos ATWS (`GEMELAS-<id1>-<id2>`). Un algoritmo voraz con barajado determinista equilibra el volumen de corridas por fold mientras mantiene los grupos íntegros.

4. **Publicación atómica**:
   Los archivos `evaluacion_diagnostico.json` y `evaluacion_diagnostico.txt` se escriben primero en un directorio temporal del mismo volumen (`.salida-temp/`) y se reemplazan atómicamente con `os.replace` / `Path.replace`, evitando estados corruptos o bloqueos por lectura concurrente.

---

## 3. Fases completadas con GitHub Spec Kit

| # | Fase | Comando Spec Kit | Entregables y Estado |
|---|---|---|---|
| 1 | Especificación | `/speckit-specify` | [spec.md](specs/011-evaluacion-diagnostico/spec.md): 4 historias de usuario (`US1`–`US4`), 14 requisitos funcionales (`FR-001`–`FR-014`), 5 criterios de éxito (`SC-001`–`SC-005`). [requirements.md](specs/011-evaluacion-diagnostico/checklists/requirements.md): 16/16 PASS. |
| 2 | Aclaración | `/speckit-clarify` | Integradas respuestas y precisiones sobre la identidad muestral de 1.0 y la columna `UNCERTAIN` en la matriz $3 \times 4$. |
| 3 | Planificación | `/speckit-plan` | [plan.md](specs/011-evaluacion-diagnostico/plan.md), [research.md](specs/011-evaluacion-diagnostico/research.md), [data-model.md](specs/011-evaluacion-diagnostico/data-model.md), [contracts/cli.md](specs/011-evaluacion-diagnostico/contracts/cli.md), [quickstart.md](specs/011-evaluacion-diagnostico/quickstart.md). |
| 4 | Tareas y Puntos | `/speckit-tasks` + `puntos.ps1` | [tasks.md](specs/011-evaluacion-diagnostico/tasks.md): 12 tareas desglosadas en 5 fases TDD. [puntos-tarea.csv](specs/011-evaluacion-diagnostico/puntos-tarea.csv): **43 puntos de tarea**. |
| 5 | Análisis | `/speckit-analyze` | [analisis-inicial.md](specs/011-evaluacion-diagnostico/analisis-inicial.md): Cobertura 100 %, 0 inconsistencias o brechas. |
| 6 | Implementación | `/speckit-implement` | Paquete `src/evaluacion_diagnostico/`, suite `tests/evaluacion_diagnostico/` y script `evaluar-diagnostico`. |
| 7 | Convergencia | `/speckit-converge` | [auditoria.md](specs/011-evaluacion-diagnostico/auditoria.md): Veredicto **`converged`** (12/12 tareas completadas, 439 pruebas globales en verde). |

---

## 4. Qué se construyó

### Paquete `src/evaluacion_diagnostico/`
- [`config.py`](file:///C:/Users/Administrador/Desktop/gestion/gestion_proyectos/src/evaluacion_diagnostico/config.py): Definición de clases (`NORM`, `LOCA`, `TRANS`), etiquetas numéricas, columna de abstención `UNCERTAIN`, hiperparámetros por defecto (`umbral=0.80`, `k=5`, `semilla=42`), nombres de artefactos y aviso consultivo institucional.
- [`metricas.py`](file:///C:/Users/Administrador/Desktop/gestion/gestion_proyectos/src/evaluacion_diagnostico/metricas.py):
  - `intervalo_wilson(k, n, confianza=0.95)`: Cálculo analítico de intervalos score de Wilson.
  - `matriz_confusion_con_abstencion(y_true, y_pred, is_uncertain)`: Construcción de la matriz rectangular $3 \times 4$.
  - `metricas_conjuntas(y_true, probabilidades, umbral=0.80)`: Evaluación conjunta y cálculo de la partición exhaustiva, detalle de errores con confianza alta y exactitud sobre decididas.
- [`validacion_cruzada.py`](file:///C:/Users/Administrador/Desktop/gestion/gestion_proyectos/src/evaluacion_diagnostico/validacion_cruzada.py):
  - `obtener_clave_grupo(c)`: Mapeo de corridas a grupos pareados por área, gemelas ATWS o identificador.
  - `particionar_kfold_por_grupos(corridas, k, semilla)`: Particionado determinista sin fuga de datos.
  - `agregar_metricas_folds(resultados_folds)`: Agregación de medias, varianzas e intervalos $t$-Student al 95 %.
  - `ejecutar_kfold(...)`: Bucle completo de reentrenamiento y prueba con escaladores ajustados solo con el entrenamiento de cada fold.
- [`reporte.py`](file:///C:/Users/Administrador/Desktop/gestion/gestion_proyectos/src/evaluacion_diagnostico/reporte.py):
  - `construir_reporte_json(...)`: Estructuración del diccionario canónico.
  - `formatear_reporte_texto(...)`: Generación del reporte en texto tabular legible para operadores y auditores.
- [`cli.py`](file:///C:/Users/Administrador/Desktop/gestion/gestion_proyectos/src/evaluacion_diagnostico/cli.py):
  - `ejecutar_evaluacion_completa(...)`: Pipeline integrado de validación, prueba y validación cruzada.
  - `publicar(...)`: Escritura atómica mediante carpetas temporales.
  - `main(argv)`: Punto de entrada con control de excepciones y códigos de salida 0, 1 y 3.
- [`__init__.py`](file:///C:/Users/Administrador/Desktop/gestion/gestion_proyectos/src/evaluacion_diagnostico/__init__.py) y [`__main__.py`](file:///C:/Users/Administrador/Desktop/gestion/gestion_proyectos/src/evaluacion_diagnostico/__main__.py).

### Pruebas y Cobertura
- [`tests/evaluacion_diagnostico/conftest.py`](file:///C:/Users/Administrador/Desktop/gestion/gestion_proyectos/tests/evaluacion_diagnostico/conftest.py): Fixtures de probabilidades sintéticas, etiquetas de eventos y corridas pareadas de prueba.
- [`tests/evaluacion_diagnostico/test_metricas.py`](file:///C:/Users/Administrador/Desktop/gestion/gestion_proyectos/tests/evaluacion_diagnostico/test_metricas.py): Pruebas del intervalo de Wilson, consistencia de la matriz $3 \times 4$ y verificación de que las tres métricas sumen exactamente 1.0.
- [`tests/evaluacion_diagnostico/test_validacion_cruzada.py`](file:///C:/Users/Administrador/Desktop/gestion/gestion_proyectos/tests/evaluacion_diagnostico/test_validacion_cruzada.py): Pruebas de no fuga en particiones agrupadas y agregación estadística $t$-Student.
- [`tests/evaluacion_diagnostico/test_evaluacion_cli.py`](file:///C:/Users/Administrador/Desktop/gestion/gestion_proyectos/tests/evaluacion_diagnostico/test_evaluacion_cli.py): Pruebas de formateo de texto, serialización JSON, publicación atómica y códigos de salida 0, 1 y 3.

### Integración y Configuración
- [`pyproject.toml`](file:///C:/Users/Administrador/Desktop/gestion/gestion_proyectos/pyproject.toml): Registro del ejecutable de consola `evaluar-diagnostico = "evaluacion_diagnostico.cli:main"`.
- [`src/clasificador_etapa1/cli.py`](file:///C:/Users/Administrador/Desktop/gestion/gestion_proyectos/src/clasificador_etapa1/cli.py): Incorporación de la función auxiliar desacoplada `agregar_metricas_diagnostico_opcional` para interoperabilidad sin modificar los esquemas existentes.
- [`README.md`](file:///C:/Users/Administrador/Desktop/gestion/gestion_proyectos/README.md): Documentación completa de la funcionalidad 011, instrucciones de ejecución y descripción matemática.

---

## 5. Verificación de Metas de Éxito

| Criterio | Requisito | Estado | Evidencia |
|---|---|---|---|
| **SC-001** | Reporte simultáneo de $\text{Acc}_{\text{abst}}$, $\text{Tasa}_{\text{abst}}$ y $\text{Tasa}_{\text{err}}$ sumando exactamente 1.0 en validación y prueba | **CUMPLE** | Verificado en `test_metricas_conjuntas_suma_uno_y_valores_exactos`. |
| **SC-002** | Matriz de confusión rectangular $3 \times 4$ con desglose por filas (`NORM`, `LOCA`, `TRANS`) y columna de abstención `UNCERTAIN` | **CUMPLE** | Verificado en `test_matriz_confusion_con_abstencion`. |
| **SC-003** | Intervalos de confianza de Wilson al 95 % para todas las proporciones binomiales | **CUMPLE** | Verificado en `test_intervalo_wilson_propiedades_basicas`. |
| **SC-004** | Validación cruzada agrupada ($k=5$) sin fuga de severidad ni gemelos ATWS, con media, std e IC $t$-Student | **CUMPLE** | Verificado en `test_particionar_kfold_por_grupos_sin_fuga` y `test_agregar_metricas_folds`. |
| **SC-005** | Publicación atómica de `evaluacion_diagnostico.json` y `evaluacion_diagnostico.txt` con códigos 0/1/3 | **CUMPLE** | Verificado en `test_evaluacion_cli.py` (5 pruebas pasando). |

---

## 6. Métricas registradas (`speckit-metricas`)

### 6.1 Sesiones de trabajo
| Sesión | Fase | Duración | Commits | Código | Pruebas |
|---|---|---|---|---|---|
| `20261104-1936-especificar-b733.csv` | `especificar` | 0,25 h | 1 | +0 / −0 | +0 / −0 |
| `20261104-1938-aclarar-13ca.csv` | `aclarar` | 0,25 h | 1 | +0 / −0 | +0 / −0 |
| `20261104-1939-planificar-cdbd.csv` | `planificar` | 0,25 h | 1 | +0 / −0 | +0 / −0 |
| `20261104-1941-tareas-62d3.csv` | `tareas` | 0,25 h | 1 | +0 / −0 | +0 / −0 |
| `20261104-1944-analizar-d830.csv` | `analizar` | 0,25 h | 1 | +0 / −0 | +0 / −0 |
| `20261104-1945-implementar-f5e4.csv` | `implementar` | 0,25 h | 1 | +665 / −0 | +376 / −0 |

### 6.2 Resumen de esfuerzo y estimación (`recolectar.ps1`, `calibrar.ps1`, `estimar.ps1`)
- **Puntos de tarea**: 43 PTS (12 tareas completadas al 100 %).
- **Líneas de código agregadas**: +665 líneas de producción, +376 líneas de pruebas.
- **Desperdicio**: 0 líneas (0 % de desperdicio).
- **Esfuerzo total estimado**: 0.010 PM (~1.6 horas).
- **Pruebas globales del repositorio**: **439 pasadas, 19 omitidas, 0 fallos**.

---

## 7. Instrucciones para Ejecución Manual

Para ejecutar la evaluación diagnóstica sobre el dataset de PWR 3L:

```powershell
.venv\Scripts\evaluar-diagnostico.exe --origen "C:\Users\Administrador\Desktop\Nuecleare\IA-Nuclear\PWR 3L" --salida resultados_evaluacion_diagnostico
```

Para correr las pruebas del subsistema:

```powershell
.venv\Scripts\python.exe -m pytest tests/evaluacion_diagnostico -v
```

---

## 8. Estado Git y Siguientes Pasos

- **Rama actual**: `011-evaluacion-diagnostico`.
- **Compromiso con el usuario**: Conforme a la instrucción *"y luego te doy luz verde para hacer push de la rama y despues merge a main"*, **NO** se ha realizado push al repositorio remoto ni merge a la rama `main`.
- La rama queda lista para que el usuario examine este documento `ENTREGABLES-011.md` y dé la luz verde cuando considere oportuno.
