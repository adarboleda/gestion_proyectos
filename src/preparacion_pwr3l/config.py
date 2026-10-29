"""Constantes de la preparación de datos PWR 3L (planta de 2705 MWt, un dato por segundo)."""

# Clases de entrenamiento y su etiqueta numérica
CLASES = {"NORM": 0, "LOCA": 1, "LOCAC": 2, "ATWS": 3, "TRIP_OK": 4}
CLASE_OOD = "OOD"  # eventos fuera de distribución: se listan, no se entrenan

# Carpetas de clase de las corridas manuales -> clase
CARPETAS_MANUALES = {
    "NORM": "NORM",
    "LOCA HOT": "LOCA",
    "LOCA COLD": "LOCAC",
    "ATWS": "ATWS",
    "TRIP_OK": "TRIP_OK",
    "LOCA PORV": CLASE_OOD,
}
CARPETA_AUTO = "auto"  # corridas automáticas R<n>_<CLASE>
CLASES_AUTO = tuple(CLASES) + (CLASE_OOD,)

# Familias para el reparto: las clases que comparten grupos van juntas
FAMILIAS = {"NORM": "NORM", "LOCA": "LOCA", "LOCAC": "LOCA", "ATWS": "ATWS", "TRIP_OK": "ATWS"}
CLASES_CON_AREA = ("LOCA", "LOCAC")  # se agrupan por área de rotura (cm²)

# 26 variables medibles en sala de control (research.md §6); sin WLR ni PWR
VARIABLES_ENTRADA = [
    "P", "TAVG", "THA", "THB", "TCA", "TCB", "WRCA", "WRCB", "LVPZ", "LVCR", "PWNT", "PSGA", "PSGB",
    "NSGA", "NSGB", "WFWA", "WFWB", "WSTA", "WSTB", "TBLD", "WHPI", "WCHG", "WECS", "PRB", "TRB", "RM1",
]
VARIABLES_MARGEN = ["DNBR", "TPCT", "SCMA", "SCMB", "TSAT", "FRCL", "FRZR"]
VARIABLES = VARIABLES_ENTRADA + VARIABLES_MARGEN
VARIABLE_TIEMPO = "TIME"

PASOS = 300
PASO_SEGUNDOS = 1

CONJUNTOS = ("train", "val", "test")
PROPORCIONES = {"train": 0.70, "val": 0.15, "test": 0.15}
SEMILLA = 42

# Corridas descartadas por el equipo (docs/PLAN_DATASET_PWR3L_DETECCION_RAPIDA.md §3.1 de IA-Nuclear)
DESCARTADAS = {
    "R07": "estado inicial inestable (el validador la marcó REPETIR); se repitió como R07b",
    "R27": "intento de mitigación manual (dos tramos, FAILED y mitigation); descartada por el equipo",
    "R28": "intento de boración; descartada por el equipo",
}

# Gemelas ATWS/TRIP_OK: mismo escenario con y sin fallo del disparo (plan_corridas_pwr3l.csv)
GEMELAS = (
    ("R21", "R59"), ("R22", "R60"), ("R23", "R61"), ("R24", "R62"), ("R29", "R63"), ("R26", "R53"),
    ("R47", "R54"), ("R48", "R55"), ("R49", "R56"), ("R50", "R57"), ("R51", "R58"),
    ("R91", "R99"), ("R92", "R100"), ("R93", "R101"), ("R94", "R102"), ("R95", "R103"),
    ("R96", "R104"), ("R97", "R105"), ("R98", "R106"),
)

ORIGEN_POR_DEFECTO = "../IA-Nuclear/PWR 3L"
SALIDA_POR_DEFECTO = "data_processed_pwr3l"
