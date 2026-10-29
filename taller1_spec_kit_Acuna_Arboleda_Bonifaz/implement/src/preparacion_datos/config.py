"""Constantes de la preparación de datos NPPAD."""

# Carpeta de origen -> (clase, etiqueta numérica)
CLASES_POR_CARPETA = {
    "Normal": ("NORM", 0),
    "LOCA": ("LOCA", 1),
    "LOCAC": ("LOCAC", 2),
    "ATWS": ("ATWS", 3),
}
CLASES = {clase: etiqueta for clase, etiqueta in CLASES_POR_CARPETA.values()}
# Clases cuyas simulaciones no tienen severidad (una sola corrida en el dataset)
CLASES_SIN_SEVERIDAD = ("NORM", "ATWS")

VARIABLES_PLANTA = ["P", "TAVG", "THA", "TCA", "WRCA", "WRCB", "LVPZ", "LVCR", "PWNT", "PWR", "WECS", "WLR"]
VARIABLES_MARGEN = ["DNBR", "TPCT", "SCMA", "SCMB", "TSAT", "FRCL", "FRZR"]
VARIABLES = VARIABLES_PLANTA + VARIABLES_MARGEN

PASOS = 150
PASO_SEGUNDOS = 10

CONJUNTOS = ("train", "val", "test")
PROPORCION_TRAIN = 0.70
PROPORCION_VAL = 0.15
PROPORCION_TEST = 0.15
SEMILLA = 42

ORIGEN_POR_DEFECTO = "../IA-Nuclear/NuclearPowerPlantAccidentData/Operation_csv_data"
SALIDA_POR_DEFECTO = "data_processed"
REFERENCIA_POR_DEFECTO = "../IA-Nuclear/data_processed/metadata.json"
