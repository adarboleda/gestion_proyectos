# Auditoría de la funcionalidad `006-regla-atws` (KAN-22)

**Fecha**: 2026-11-04 · **Rama**: `006-regla-atws` (desde `002-preprocesamiento-pwr3l-cierre`) · **Constitución**: v2.0.0

## 1. Resumen

| Momento | Resultado |
|---|---|
| `/speckit-analyze` | 5 hallazgos: 0 críticos, 2 medios, 3 bajos; cobertura 100 %; sin conflictos con la constitución ([analisis-inicial.md](analisis-inicial.md)) |
| Correcciones del análisis | Las 5 aplicadas antes de programar (`f1ec46f`) |
| Implementación | T001–T021, con las pruebas commiteadas antes que el código en cada historia |
| `/speckit-converge`, 1.ª pasada | 4 hallazgos → T022–T025 (`0e596e5`) |
| `/speckit-converge`, 2.ª pasada | **converged**: 0 hallazgos |
| Tareas | 25/25 |
| Pruebas de 006 | 51, todas verdes (incluye la carpeta real) |

## 2. Cobertura de requisitos

| Requisito | Pruebas |
|---|---|
| FR-001 corridas de 002 y reparto de 004 | cli (una fila por corrida usable con su conjunto), real (91 = 63/15/13) |
| FR-002 señal de disparo | eventos (registro, tipos, alto flujo antes o sin señal), cli y real (R97/R96 por alto flujo) |
| FR-003 retardos por tipo | regla (mayor de entrenamiento, tipo no visto), real |
| FR-004 decisión a 2 s | regla (⌈t_d + 2⌉, flujo caído/alto, sin demanda, fuera de ventana, relativo al inicial) |
| FR-005 umbral solo con entrenamiento | regla (punto medio, solape, ATWS sin demanda), cli (cambiar val/test no cambia `regla.json`), real (sin solape) |
| FR-006, FR-007 evaluación y tiempos | reporte (tabla, errores, tiempos y meta), real (18/18 ATWS en ≤ 3 s) |
| FR-008 recomendación consultiva | cli (`regla.json`, `resumen.json`), reporte (segunda línea del reporte) |
| FR-009 registro faltante o ilegible | eventos (sin `.dat`, dos `.dat`, ilegible), cli (código 1 sin salida) |
| FR-010 reproducible, un comando | cli (byte a byte, `python -m`, valores por defecto) |

## 3. Hallazgos de converge

| ID | Tipo | Hallazgo | Tarea |
|---|---|---|---|
| G1 | partial | research §2 afirmaba que el mayor retardo de entrenamiento siempre es conservador; con la carpeta real, «turbine trip» (5 s) recibe 2.5 s y da la falsa alarma R54 | T022 |
| G2 | partial | La aclaración 1 de la spec repetía esa afirmación; se añade una nota (la decisión no se cambia) | T023 |
| G3 | partial | La validación 2 del quickstart no admitía la excepción R54 | T024 |
| G4 | unrequested | Faltaba una coma en `description` de `pyproject.toml` | T025 |

## 4. Resultado que no salió como se esperaba (principio III)

El prototipo, hecho con el reparto de la rama 002, no daba falsas alarmas. Con el reparto de 004 (el de `main`), la única TRIP_OK de turbina usable (R54) cae en validación, porque su gemela R55 es corta. Su tipo de señal no tiene retardo medido en entrenamiento y la regla da **una falsa alarma en validación**.

- **No se ajustó la regla para eliminarla**: hacerlo después de ver validación sería fuga (principio II).
- **Propuesta para la experta**: tomar los retardos de la lógica de protección de su documentación de diseño. Esos valores no se aprenden de los datos, así que no son fuga.

## 5. Decisiones sin aprobación explícita

- Las tres respuestas de `/speckit-clarify` las eligió el agente, con la opción recomendada, por delegación del responsable.
- La renumeración de 003 a 006 (rama local no publicada) y empezar desde la rama de cierre de 002.

## 6. Pendientes

- Validar con la experta la señal de demanda y los retardos (KAN-22 lo pide).
- La rama depende de `002-preprocesamiento-pwr3l-cierre`: fusionar primero esa.
