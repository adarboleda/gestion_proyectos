# Segunda iteración SDD: `002-preprocesamiento-pwr3l` (KAN-18)

**Tarea de Jira**: KAN-18 «Adaptar el preprocesamiento a ventanas de 300 s y cinco clases» · **Responsable**: Marcelo Acuña
**Rama**: `002-preprocesamiento-pwr3l` (creada desde `main`) · **Fecha**: 2026-10-28
**Herramienta**: GitHub Spec Kit + Claude Code (`claude-opus-5-5`) · **Constitución**: v2.0.0, sin cambios

> **Estado: iteración a medias.** Las fases de documento de Spec Kit (especificar → aclarar → planificar → tareas → analizar) están completas. La implementación llegó hasta la fase 2 de 6 (descubrir y leer las corridas) y se detuvo a pedido del responsable. Lo que falta está en la sección 6.

---

## 1. Qué pide KAN-18 y por qué es distinta de 001

En 001, Abner preparó los datos **NPPAD**: 150 pasos de 10 s y 4 clases. KAN-18 prepara otra planta, **PWR 3L** (2705 MWt), con un dato por segundo:

- **Muestras de 300 pasos de 1 s** (los primeros 300 s de cada corrida).
- **Cinco clases**: NORM (0), LOCA rama caliente (1), LOCAC rama fría (2), ATWS (3) y TRIP_OK (4), que es un disparo correcto del reactor. LOCA y LOCAC quedan separadas.
- Las corridas **OOD** (eventos desconocidos: PORV trabada, rotura de tubos del GV, rotura de línea de vapor) **no son una clase de entrenamiento**.
- La constitución (principio IV) **prohíbe mezclar PWR 3L con NPPAD**. Por eso esta iteración tiene paquete, comando y carpeta de salida propios: `preparacion_pwr3l`, `preparar-pwr3l` y `data_processed_pwr3l/`.

---

## 2. Lo que se encontró en los datos (medido, no supuesto)

Se recorrió la carpeta `D:\Proyectos\IA-Nuclear\PWR 3L`:

| Hecho | Detalle |
|---|---|
| 109 carpetas de corrida, 110 archivos de datos | 35 manuales y 74 automáticas (`auto/R<n>_<CLASE>`); R27 tiene dos archivos |
| Las «106 simulaciones» de Jira | 109 menos las 3 que el equipo ya descartó (R07, R27 y R28) = **20 por clase × 5 + 6 OOD** |
| Dos formatos | Las manuales son `.xls`, pero en realidad son libros xlsx (hay que leerlas con openpyxl); las automáticas y las TRIP_OK manuales son `.csv` |
| Datos limpios | 93 columnas en todas, el tiempo avanza de 1 s en 1 s desde 0, sin valores faltantes |
| **9 corridas de entrenamiento tienen menos de 300 filas** | R38 (NORM, 295), R41 (295), R42 (289), R43 (294) y R82 (299) de LOCA, R91 (295) y R98 (299) de ATWS, y R55 (295) y R63 (295) de TRIP_OK |
| R47 y R48 | Tienen 301 filas y R91 tiene 295 (en el manifiesto de IA-Nuclear aparecían con 0 filas). Su estado «REVISAR» viene del validador externo y no impide usarlas |

Resultado esperado al terminar: **91 muestras** (NORM 19, LOCA 16, LOCAC 20, ATWS 18, TRIP_OK 18).

---

## 3. Lo que se hizo, fase por fase

| # | Fase | Comando | Resultado | Archivo |
|---|---|---|---|---|
| 1 | Rama | script `create-new-feature.ps1` | `002-preprocesamiento-pwr3l`. El script creó la carpeta y la rama se creó con git, porque la extensión git de Spec Kit no está instalada | — |
| 2 | Especificar | `/speckit-specify` | 3 historias, 16 requisitos (FR), 8 criterios de éxito (SC) y 2 dudas marcadas | [spec.md](specs/002-preprocesamiento-pwr3l/spec.md) |
| 3 | Aclarar | `/speckit-clarify` | 3 preguntas respondidas (sección 4); checklist de calidad 16/16 | spec.md, [checklists/requirements.md](specs/002-preprocesamiento-pwr3l/checklists/requirements.md) |
| 4 | Planificar | `/speckit-plan` | Plan con *Constitution Check* (todo «cumple»), 12 decisiones técnicas, modelo de datos, 2 contratos y quickstart | [plan.md](specs/002-preprocesamiento-pwr3l/plan.md), [research.md](specs/002-preprocesamiento-pwr3l/research.md), [data-model.md](specs/002-preprocesamiento-pwr3l/data-model.md), [contracts/](specs/002-preprocesamiento-pwr3l/contracts/), [quickstart.md](specs/002-preprocesamiento-pwr3l/quickstart.md) |
| 5 | Tareas | `/speckit-tasks` | 34 tareas en 6 fases, con las pruebas antes del código; línea base de **95 puntos de tarea** | [tasks.md](specs/002-preprocesamiento-pwr3l/tasks.md), [puntos-tarea.csv](specs/002-preprocesamiento-pwr3l/puntos-tarea.csv) |
| 6 | Analizar | `/speckit-analyze` | 8 hallazgos: **0 críticos**, 3 medios y 5 bajos; cobertura del 100 %; sin conflictos con la constitución. Las 8 correcciones se aplicaron en un commit aparte antes de programar | [analisis-inicial.md](specs/002-preprocesamiento-pwr3l/analisis-inicial.md) |
| 7 | Implementar | `/speckit-implement` | **Parcial**: fases 1 y 2 (tareas T001–T010) | `src/preparacion_pwr3l/`, `tests/pwr3l/` |
| 8 | Converge | `/speckit-converge` | **No ejecutado** | — |

### Hallazgos del análisis y cómo se resolvieron

| ID | Severidad | Problema | Solución aplicada |
|---|---|---|---|
| U1 | Media | No estaba definido qué pasa si una clase no tiene corridas | Si una clase no tiene ninguna corrida, error. Si todas sus corridas son cortas, la clase sigue con cero muestras y una advertencia |
| U2 | Media | Una pareja ATWS/TRIP_OK nueva podía quedar sin agrupar y causar fuga de datos | Se compara la gemela declarada en `config.json` con la tabla del proyecto; si no coinciden, error |
| A1 | Media | «Reparto cercano a 70/15/15» no tenía medida | Regla definida: grupos completos al conjunto con más déficit, por familia de clases; ningún conjunto supera su meta en un grupo entero |
| C1, C2 | Baja | Faltaban pruebas de los valores por defecto y de volver a ejecutar sobre una salida previa | Agregadas a la tarea T015 |
| D1 | Baja | Varias corridas NORM se parecen entre sí y no se agrupan | Declarado como limitación |
| I1, T1 | Baja | Versiones desactualizadas en el plan; «corrida» y «simulación» usadas para lo mismo | Corregido |

---

## 4. Decisiones clave (para explicar)

1. **Corridas cortas (menos de 300 filas): se excluyen con aviso.** Detenerse bloquearía siempre el dataset real, y rellenar los pasos que faltan inventaría datos (principio III).
2. **«Igual severidad» de LOCA y LOCAC = misma área de rotura (cm²).** Todas las LOCA y LOCAC con la misma área van al mismo conjunto, para que no haya fuga entre entrenamiento y prueba (principio II). El área se toma del nombre de la carpeta (`R10_LOCA_hot_50cm_t60`) o de la descripción en `config.json`. El grupo de 2000 cm² junta 8 corridas.
3. **Las gemelas ATWS/TRIP_OK van juntas.** Son el mismo escenario con y sin fallo del disparo; hay 19 pares fijos tomados del plan de corridas del proyecto.
4. **Las OOD solo se listan.** No se leen ni se guardan; quedan para el monitor de novedades.
5. **26 variables de entrada, todas medibles en sala de control.** Se excluye `WLR` (caudal de fuga): no se mide en planta y haría trivial detectar un LOCA. Los 7 márgenes térmicos (DNBR, TPCT, …) se guardan aparte y sin escalar, igual que en 001.
6. **Se valida el archivo completo**, no solo los primeros 300 pasos (lección F5 de 001). Un archivo defectuoso detiene todo y nombra el archivo y la causa.

> Las tres respuestas de `/speckit-clarify` las eligió el agente, siempre con la opción recomendada, por delegación. Están anotadas en la spec para que el responsable las revise en el PR.

---

## 5. Métricas (`speckit-metricas`)

### Tiempo por fase

| Fase | Horas registradas | Commits | Código | Pruebas |
|---|---|---|---|---|
| Especificar | 0.25 | 1 | 0 | 0 |
| Aclarar | 0.25 | 1 | 0 | 0 |
| Planificar | 0.25 | 1 | 0 | 0 |
| Tareas | 0.25 | 1 | 0 | 0 |
| Analizar | 0.25 | 2 | 0 | 0 |
| Implementar (parcial) | 0.25 | 3 | +342 / −0 | +496 / −0 |
| **Total** | **1.50** | **9** | **+342** | **+496** |

- **Las horas son el mínimo que registra la extensión por sesión (0.25 h), no un cronómetro.** El reloj marca unos 20 minutos de trabajo del agente entre la primera y la última sesión (18:43 a 19:02); la exploración de los datos previa no está registrada. No se informaron tokens ni costo.
- **Desperdicio: 0 líneas eliminadas** (tasa 0 %), porque todavía no hubo correcciones de código.
- Modelo de IA: `claude-opus-5-5` en las 6 sesiones. Desarrollador según git: `cmacuna7`.

### Puntos de tarea

| Medida | Valor |
|---|---|
| Línea base del plan | 95 puntos (34 tareas) |
| Hechos | T001–T010 = **31 puntos (33 %)** |
| Pendientes | T011–T034 = 64 puntos |

### Tamaño de lo entregado

| Parte | Líneas |
|---|---|
| Código (`src/preparacion_pwr3l/`: config 55, descubrimiento 182, lectura 97, otros 8) | 342 |
| Pruebas (`tests/pwr3l/`: árbol sintético 186, descubrimiento 180, lectura 130) | 496 |
| Documentos de Spec Kit (`specs/002-…/`) | 814 |

### Pruebas

**44 pruebas de 002: 43 pasan y 1 falla.** La que falla es un error de la prueba, no del código. Compara un libro xlsx con los valores del generador, pero openpyxl guarda 16 cifras, así que el archivo difiere en unos 6e-14. La corrección es comparar con las celdas del propio archivo; se dejó sin aplicar al detener el trabajo. Las 79 pruebas de 001 no se tocaron.

---

## 6. Qué falta para cerrar KAN-18

| Fase | Tareas | Qué es |
|---|---|---|
| 2 | T011 | Corregir la prueba del xlsx y dejar la fase en verde |
| 3, US1 (núcleo) | T012–T021 | Formar los grupos, repartir en train/val/test, escalar solo con entrenamiento y publicar `X_*`, `y_*` y `scaler_*` |
| 4, US2 | T022–T024 | Guardar los márgenes térmicos sin escalar (`margins_*`) |
| 5, US3 | T025–T030 | Reporte impreso y `metadata.json` |
| 6 | T031–T034 | Prueba con la carpeta real, README, quickstart y suite completa |
| Cierre | — | `/speckit-converge`, auditoría y puntos finales |

---

## 7. Historial de commits (rama `002-preprocesamiento-pwr3l`)

| Commit | Mensaje |
|---|---|
| `1cb0995` | docs(002): especificación del preprocesamiento PWR 3L (KAN-18) |
| `80154ec` | docs(002): aclaraciones de la especificación |
| `208a840` | docs(002): plan, decisiones, modelo de datos y contratos |
| `d72b3c1` | docs(002): tareas, puntos de tarea y registros de sesión |
| `79eab23` | docs(002): informe de /speckit-analyze |
| `73c553e` | docs(002): correcciones del análisis |
| `f521c84` | feat(002): paquete preparacion_pwr3l, openpyxl y guion preparar-pwr3l |
| `e0220ec` | test(002): árbol PWR 3L sintético y pruebas de descubrimiento y lectura |
| `8ccc7fe` | feat(002): descubrimiento, lectura y validación de las corridas PWR 3L |

---

## 8. Cómo verificarlo

```
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -e ".[dev]"
.venv/Scripts/python.exe -m pytest tests/pwr3l -q      # 43 passed, 1 failed (la del xlsx, sección 5)
```
