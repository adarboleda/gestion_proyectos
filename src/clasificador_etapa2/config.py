"""Constantes del clasificador de Etapa 2 (rama caliente o fría) de PWR 3L."""

# Ramas que distingue la Etapa 2 y su etiqueta (índice)
CLASES = ("LOCA", "LOCAC")  # LOCA = rotura en rama caliente; LOCAC = rotura en rama fría
ETIQUETA = {clase: i for i, clase in enumerate(CLASES)}
FAMILIA_ACTIVADORA = "LOCA"  # la Etapa 2 solo se aplica si la Etapa 1 recomienda esta familia

# Canales de entrada: desviación pico causal de la potencia térmica y del flujo neutrónico
CANALES = ("PWR", "PWNT")
VENTANA_PICO_S = 15  # máximo en [τ − 14, τ]
MEDIA_MOVIL_S = 3  # media móvil causal previa al máximo

# Muestras: en cada segundo τ del evento el modelo ve los últimos VENTANA_S segundos de los canales
VENTANA_S = 30
HORIZONTE_ENTRENAMIENTO_S = 60  # en entrenamiento, solo los primeros 60 s de cada evento

# Decisión y evaluación
UMBRAL = 0.80
INCIERTO = "UNCERTAIN"
NO_APLICA = "NO_APLICA"
CONFIRMACION_S = 2
HORIZONTES_S = (1, 2, 3, 5, 10, 20, 30)
PRIMEROS_S = 30
AREA_META_CM2 = 50  # SC-002: roturas de 50 cm² o más
LATENCIA_META_S = 10
RANGOS_AREA = (("< 50 cm²", 0, 50), ("50–499 cm²", 50, 500), (">= 500 cm²", 500, None))
MIN_CORRIDAS_PRUEBA = 10  # por debajo se advierte la incertidumbre

HIPERPARAMETROS = {
    "unidades": 8,
    "capas": 1,
    "dropout": 0.2,
    "lr": 3e-3,
    "weight_decay": 1e-4,
    "lote": 128,
    "epocas": 40,
    "paciencia": 6,
}
SEMILLA = 42

SALIDA_POR_DEFECTO = "modelos/etapa2"
ARTEFACTOS = ("modelo.pt", "modelo.json", "reporte.json", "reporte.txt")

AVISO = "Recomendación consultiva: el operador valida y decide; el sistema no actúa sobre la planta."
AVISO_REPORTE = "Clasificador consultivo de Etapa 2: las salidas son recomendaciones; el operador decide."

