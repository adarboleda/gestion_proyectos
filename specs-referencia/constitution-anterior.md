# IANuclear Constitution
<!-- Sistema de Asistencia Inteligente (IDSS) para detección y diagnóstico de LOCA/ATWS en reactores PWR -->

## Core Principles

### I. IA estrictamente consultiva (NON-NEGOTIABLE)
El sistema es un copiloto consultivo (Human-in-the-Loop / IDSS). NUNCA actúa sobre la planta, no sustituye la lógica de protección existente y no tiene autoridad de control. El operador valida y ejecuta los procedimientos de emergencia (EOP). Toda salida del sistema (diagnóstico, EOP, alerta térmica) se presenta como recomendación, y toda consola o reporte debe decirlo de forma visible.

### II. Causalidad y cero fuga de datos (NON-NEGOTIABLE)
Ninguna predicción en el instante `t` puede usar información posterior a `t` (estadísticos acumulados, picos enclavados, ventanas pasadas). Las particiones train/val/test se hacen **por corrida o por severidad pareada**, nunca por fila; los gemelos (ATWS/TRIP_OK, LOCA/LOCAC de igual severidad) van siempre al mismo grupo. Los escaladores se ajustan **solo con train**. Las corridas fuera de distribución (OOD) nunca se usan para entrenar.

### III. Honestidad científica y reproducibilidad
Se reporta lo que salió, incluidos los resultados negativos y las metas no cumplidas. Las iteraciones fallidas se archivan para comparar (`fase2_output/baseline_flat_4class_archive/`, `fase3_output_v1_archive/`), no se borran. Cada fase documenta objetivo, resultado real, limitaciones y cómo regenerarla (`README_FASEn.md`). Las cifras se miden fuera de muestra, con ruido de sensores y en el peor caso. Toda meta se enuncia con su definición exacta (desde cuándo se mide el tiempo, sobre qué conjunto).

### IV. Abstención y compuertas deterministas por encima de la IA
Si la confianza es menor a 0.80, o el evento es desconocido (monitores de novedad), el sistema responde `UNCERTAIN` en vez de forzar un diagnóstico. Las compuertas deterministas (p. ej. ATWS = demanda de disparo + retardo del scram + 1.5 s + PWNT alto) prevalecen sobre el clasificador estadístico. Una lectura temprana y confiada no es definitiva: el diagnóstico se confirma con una regla de estabilidad (k segundos/evaluaciones seguidas).

### V. Procedencia de datos: dos plantas, dos canales, no se mezclan
NPPAD (2895 MWt, 10 s/paso, canal lento) y PWR 3L (2705 MWt, 1 s/paso, canal rápido) son configuraciones de planta distintas; cada canal se entrena solo con sus datos. El canal rápido usa **solo variables medibles en sala de control** (sin `WLR`, `DNBR`, `TPCT`, reactividades ni `FRCL` como entrada). `WLR` solo sirve como etiqueta. El dataset original `NuclearPowerPlantAccidentData/` se conserva intacto: el código propio vive solo en `pipeline/`.

### VI. Alcance acotado
El alcance es LOCA (rama caliente/fría) y ATWS (con su contraste TRIP_OK) en PWR; ciberataques y otros accidentes quedan fuera. Los eventos fuera de alcance se detectan como `UNCERTAIN`, no se clasifican. El simulador (PCTRAN) es la referencia física; DNBR y PCT de la FNN son estimaciones sustitutas, no reemplazan el cálculo termohidráulico.

## Restricciones Adicionales

- **Lenguaje y pila**: Python con PyTorch (Bi-LSTM, FNN-SELU), scikit-learn (HistGradientBoosting, baselines), pandas/numpy, SHAP, matplotlib. Consolas del operador como HTML autosuficiente (sin servidor), con botón ES/EN (clave `idss_lang`).
- **Plataforma**: Windows 11; PCTRAN PWR 3LP demo (300 s por corrida, 1 s de muestreo) para la generación de corridas.
- **Artefactos generados** (`data_processed*/`, `fase*_output/`, `pwr3l_output/`, consolas HTML) no se editan a mano: se regeneran ejecutando el pipeline.
- **Rendimiento**: inferencia < 10 ms por paso. Detección: LOCA/LOCAC ≤ 10 s (≤ 3 s en roturas ≥ 10 cm²); ATWS ≤ 3 s o dentro de su mínimo físico por iniciador.
- **Seguridad de métricas**: cero falsos negativos en accidentes simulados y cero falsas alarmas en operación normal son metas duras; se reportan también las horas de operación normal evaluadas y la cota de la regla del tres.
- **Idioma**: documentación y mensajes al operador en español, con versión en inglés de la consola y del resumen para el jurado.

## Flujo de Desarrollo

- **Spec Kit**: cada bloque funcional sigue `specify → clarify → plan → tasks → analyze → implement` y vive en `specs/NNN-nombre/`. La constitución se enmienda solo con registro de cambio.
- **Pruebas**: los comportamientos críticos (compuerta ATWS, causalidad de características, prioridades de fusión, mapeo EOP, veredictos de aceptación) deben tener pruebas automáticas (`python -m unittest test_pwr3l -v`, hoy 17). Las fases NPPAD se verifican con los scripts de "verificación rápida" de cada README.
- **Documentación por fase**: ningún cambio de resultados se entrega sin actualizar el README de la fase y las tablas de cumplimiento correspondientes.
- **Control de calidad de datos**: toda corrida nueva pasa el checklist de `validar_corridas.py` (inicio real vs. plan, ausencia de contaminación inicial, IC válida 1–3) antes de entrar al dataset.
- **Control de versiones**: commits pequeños y descriptivos; no se reescribe historial publicado.

## Governance

Esta constitución prevalece sobre cualquier otra práctica del proyecto. Una enmienda requiere: descripción del cambio, motivo, impacto sobre las especificaciones existentes y actualización de `Version`/`Last Amended`. Los principios I y II no admiten excepciones. Toda revisión de especificación, plan o tarea debe verificar el cumplimiento de estos principios (sección *Constitution Check* de cada `plan.md`); cualquier desviación se justifica en *Complexity Tracking*. La guía operativa diaria está en `README.md` (flujo Spec Kit) y en `IA-Nuclear/README.md` (pipeline).

**Version**: 1.0.0 | **Ratified**: 2026-10-18 | **Last Amended**: 2026-10-18
