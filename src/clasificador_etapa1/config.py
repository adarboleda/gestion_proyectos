"""Constantes del clasificador de Etapa 1 (familia del evento) de PWR 3L."""

# Familias que distingue la Etapa 1 y su etiqueta (índice)
FAMILIAS = ("NORM", "LOCA", "TRANS")
FAMILIA_DE_CLASE = {"NORM": "NORM", "LOCA": "LOCA", "LOCAC": "LOCA", "ATWS": "TRANS", "TRIP_OK": "TRANS"}
ETIQUETA = {familia: i for i, familia in enumerate(FAMILIAS)}

# Muestras: en cada segundo τ el modelo ve los últimos VENTANA_S segundos hasta τ
VENTANA_S = 30
TAU_MIN_S = 5
HORIZONTE_ENTRENAMIENTO_S = 60  # en entrenamiento, solo los primeros 60 s de cada evento

# Decisión y evaluación
UMBRAL = 0.80
CONFIRMACION_S = 2
HORIZONTES_S = (1, 2, 3, 5, 10, 20, 30)
PRIMEROS_S = 30
AREA_META_CM2 = 50  # SC-001: LOCA de 50 cm² o más
LATENCIA_META_S = 10
F1_META = 0.80

HIPERPARAMETROS = {
    "unidades": 32,
    "capas": 1,
    "dropout": 0.3,
    "lr": 1e-3,
    "weight_decay": 1e-4,
    "lote": 256,
    "epocas": 40,
    "paciencia": 6,
}
SEMILLA = 42

SALIDA_POR_DEFECTO = "modelos/etapa1"
ARTEFACTOS = ("modelo.pt", "modelo.json", "reporte.json", "reporte.txt")

AVISO = "Recomendación consultiva: el operador valida y decide; el sistema no actúa sobre la planta."
AVISO_REPORTE = "Clasificador consultivo: las salidas son recomendaciones; el operador decide."
