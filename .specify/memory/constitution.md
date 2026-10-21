# IANuclear Constitution
<!-- Sistema consultivo de apoyo al operador para detectar accidentes LOCA y ATWS en reactores PWR con datos simulados -->

## Core Principles

### I. IA estrictamente consultiva (NON-NEGOTIABLE)
La IA solo aconseja: MUST NOT actuar sobre la planta, sustituir la lógica de protección existente ni
tener autoridad de control. El operador valida y ejecuta cualquier acción. Toda salida del sistema
(diagnóstico, procedimiento, alerta) MUST presentarse como recomendación, y toda interfaz o reporte
MUST decirlo de forma visible.

### II. Cero fuga de datos (NON-NEGOTIABLE)
Las particiones entrenamiento/validación/prueba MUST hacerse por simulación completa, nunca por fila;
las simulaciones emparejadas (mismo escenario con y sin accidente, o de igual severidad) MUST ir al
mismo grupo. Los escaladores y cualquier transformación aprendida MUST ajustarse solo con
entrenamiento. Una predicción en el instante `t` MUST NOT usar información posterior a `t`.

### III. Honestidad y reproducibilidad
Se MUST reportar lo que salió, incluidos los resultados negativos, las metas no cumplidas y las
limitaciones. Toda meta MUST enunciarse con su definición exacta (qué se mide, sobre qué conjunto).
Todo resultado MUST poder regenerarse con un comando documentado; los artefactos generados MUST NOT
editarse a mano.

### IV. Procedencia de datos
El dataset original MUST conservarse sin modificar; todo dato derivado se genera aparte y de forma
reproducible. Datos de plantas o configuraciones distintas (p. ej. NPPAD y PWR 3L) MUST NOT mezclarse:
cada modelo se entrena y evalúa con datos de una sola planta.

### V. Alcance acotado a LOCA y ATWS
El alcance es la detección de accidentes LOCA y ATWS en reactores PWR con datos simulados. Otros
accidentes, ciberataques y datos de planta real quedan fuera; cualquier ampliación MUST pasar por
una enmienda de esta constitución. Las estimaciones del sistema MUST NOT presentarse como reemplazo
del cálculo termohidráulico del simulador.

## Restricciones Adicionales

- **Lenguaje**: Python.
- **Estructura**: el código MUST vivir en `src/` y las pruebas en `tests/`.
- **Idioma**: la documentación MUST estar en español.

## Flujo de Desarrollo

- **Spec Kit completo**: cada funcionalidad MUST seguir `specify → clarify → plan → tasks → analyze →
  implement` y vivir en `specs/NNN-nombre/`.
- **Pruebas**: todo comportamiento crítico MUST tener pruebas automáticas en `tests/`, escritas antes
  de dar la tarea por terminada.
- **Commits**: el mensaje MUST tener la forma `feat(NNN): descripción`, donde `NNN` es el número de la
  funcionalidad (p. ej. `feat(001): descripción`). Cuando el commit elimine o reescriba código
  existente MUST incluir el trailer `Causa: requisito|defecto|refactor`, con exactamente uno de esos
  tres valores. El historial publicado MUST NOT reescribirse.
- **Métricas SDD**: cada fase Spec Kit MUST registrarse como sesión con la extensión `metricas`
  (se abre por hook; se cierra con `/speckit-metricas-cerrar`); el trailer `Causa:` alimenta la
  clasificación del código eliminado.

## Governance

Esta constitución prevalece sobre cualquier otra práctica del proyecto. Una enmienda requiere:
descripción del cambio, motivo, impacto sobre las especificaciones existentes y actualización de
`Version`/`Last Amended`. El versionado es semántico: MAJOR por eliminar o redefinir un principio de
forma incompatible, MINOR por añadir un principio o sección o ampliar materialmente su guía, PATCH por
aclaraciones de redacción. Los principios I y II no admiten excepciones. Toda revisión de
especificación, plan o tarea MUST verificar el cumplimiento de estos principios (sección
*Constitution Check* de cada `plan.md`); cualquier desviación MUST justificarse en *Complexity
Tracking*. La guía operativa diaria está en `README.md`.

**Version**: 2.0.0 | **Ratified**: 2026-10-20 | **Last Amended**: 2026-10-20
