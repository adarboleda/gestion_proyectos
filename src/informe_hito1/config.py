"""Fuentes del Hito 1 (KAN-27): qué tarea publica cada archivo y con qué comando."""

# clave -> datos de la tarea y archivos que se leen: alias -> (nombre del archivo, claves requeridas)
FUENTES = {
    "etapa1": {
        "kan": "KAN-23", "responsable": "Abner Arboleda", "funcionalidad": "005",
        "comando": "entrenar-etapa1", "carpeta": "modelos/etapa1",
        "archivos": {"reporte": ("reporte.json", ("global", "metas", "falsas_alarmas", "primeros_30s", "entrenamiento"))},
    },
    "regla": {
        "kan": "KAN-22", "responsable": "Marcelo Acuña", "funcionalidad": "006",
        "comando": "evaluar-regla-atws", "carpeta": "resultados_regla_atws",
        "archivos": {"resumen": ("resumen.json", ("por_conjunto", "errores", "tiempos")),
                     "regla": ("regla.json", ("umbral_pwnt_pct", "margen"))},
    },
    "tiempos": {
        "kan": "KAN-25", "responsable": "Abner Arboleda", "funcionalidad": "008",
        "comando": "medir-tiempo-deteccion", "carpeta": "resultados_tiempo_deteccion",
        "archivos": {"tiempos": ("tiempos.json", ("corridas", "metas", "falsas_alarmas"))},
    },
    "etapa2": {
        "kan": "KAN-24", "responsable": "Christian Bonifaz", "funcionalidad": "009",
        "comando": "entrenar-etapa2", "carpeta": "modelos/etapa2",
        "archivos": {"reporte": ("reporte.json", ("global", "metas", "corridas"))},
    },
    "diagnostico": {
        "kan": "KAN-26", "responsable": "Christian Bonifaz", "funcionalidad": "011",
        "comando": "evaluar-diagnostico --modelo modelos/etapa1", "carpeta": "resultados_evaluacion_diagnostico",
        "archivos": {"evaluacion": ("evaluacion_diagnostico.json", ("prueba", "validacion", "validacion_cruzada"))},
    },
}

SALIDA_POR_DEFECTO = "informe_hito1"

AVISO = (
    "Sistema consultivo: todas las salidas son recomendaciones para el operador; el sistema no actúa sobre "
    "la planta ni sustituye la lógica de protección."
)

LIMITACIONES = [
    "Pocas corridas: 13 de prueba y 15 de validación (unas 3 por clase): las cifras tienen mucha incertidumbre; "
    "por eso se informan intervalos y validación cruzada.",
    "Un solo simulador (PCTran) y una sola planta (PWR 3L), sin ruido de sensores ni datos de planta real.",
    "La Etapa 1 y la Etapa 2 se reentrenan en CPU: algunas cifras cambian de una máquina a otra (mejor época, "
    "falsas alarmas). Las de este informe son las de los archivos de la ejecución citada en «Fuentes».",
    "La señal de demanda de disparo y los retardos de la regla de ATWS están pendientes de validar con la experta.",
]
