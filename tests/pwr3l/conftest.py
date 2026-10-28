"""Árbol PWR 3L sintético para las pruebas de 002.

Reproduce la estructura de la carpeta real: carpetas de clase manuales (CSV y libros xlsx con
extensión `.xls`) y `auto/R<n>_<CLASE>` con `plotdata.csv` y `config.json`, más corridas
descartadas, OOD, una corrida corta y carpetas o archivos que deben ignorarse.
"""
import hashlib
import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

VARIABLES_ENTRADA = [
    "P", "TAVG", "THA", "THB", "TCA", "TCB", "WRCA", "WRCB", "LVPZ", "LVCR", "PWNT", "PSGA", "PSGB",
    "NSGA", "NSGB", "WFWA", "WFWB", "WSTA", "WSTB", "TBLD", "WHPI", "WCHG", "WECS", "PRB", "TRB", "RM1",
]
VARIABLES_MARGEN = ["DNBR", "TPCT", "SCMA", "SCMB", "TSAT", "FRCL", "FRZR"]
# Columnas del archivo: tiempo, una variable no usada entre medias y las 33 requeridas
COLUMNAS = ["TIME", "WLR"] + VARIABLES_ENTRADA + ["PWR"] + VARIABLES_MARGEN

# Corridas manuales: (carpeta de clase, carpeta de corrida, archivos de datos, formato)
MANUALES = [
    ("NORM", "R01_NORM", ["R01_plotdata_NORM.xls"], "xlsx"),
    ("NORM", "R02_NORM PD 100-90%", ["R02_plotdata_NORM_t30.csv"], "csv"),
    ("LOCA HOT", "R09_LOCA_hot_2000cm2_t0", ["R09_plotdata_LOCAH2000_t0.xls"], "xlsx"),
    ("LOCA HOT", "R10_LOCA_hot_50cm_t60", ["R10_plotdata_LOCAH50_t60.csv"], "csv"),
    ("LOCA COLD", "R03_LOCA_cold_2000cm2_t0", ["R03_plotdata_LOCAC2000_t0.csv"], "csv"),
    ("LOCA COLD", "R07_LOCA_cold_2000cm2_t30", ["R07_plotdata_LOCAC2000_t30.csv"], "csv"),
    ("ATWS", "R21_ATWS_LOFW_t30", ["R21_plotdata_ATWS LOFW_t30.csv"], "csv"),
    ("ATWS", "R27_ATWS_LOFW_tripman_FAILED_t30_op90",
     ["R27_plotdata_ATWSLOFW_FAILED_t30_op90.csv", "R27_plotdata_ATWSLOFW_mitigation_t30_op90.csv"], "csv"),
    ("TRIP_OK", "R59_TRIP_OK_LOFW_t25", ["R59_plotdata_TRIP_OK_LOFW_t25.csv"], "csv"),
    ("LOCA PORV", "R20_LOCA_PORV_t32.5", ["R20_plotdata_LOCAPORV_t32.5.csv"], "csv"),
]

# Corridas automáticas: (id, clase, gemelo_de en config.json, descripción, filas)
AUTOMATICAS = [
    *[(f"R{n}", "NORM", "", "Rechazo de carga", 301) for n in range(31, 39)],
    ("R41", "LOCA", "", "LOCA rama caliente 5 cm2", 301),
    ("R42", "LOCA", "", "LOCA rama caliente 10 cm2", 301),
    ("R43", "LOCA", "", "LOCA rama caliente 20 cm2", 301),
    ("R44", "LOCA", "", "LOCA rama caliente 100 cm2", 301),
    ("R45", "LOCA", "", "LOCA rama caliente 1000 cm2", 301),
    ("R75", "LOCA", "", "LOCA rama caliente 2 cm2", 301),
    ("R76", "LOCA", "", "LOCA rama caliente 50 cm2", 300),
    ("R77", "LOCA", "", "LOCA rama caliente 2000 cm2", 301),
    ("R07b", "LOCAC", "", "Repetición de R07: LOCA rama fría 2000 cm2", 300),
    ("R46", "LOCAC", "", "LOCA rama fría 5 cm2", 301),
    ("R83", "LOCAC", "", "LOCA rama fría 10 cm2", 301),
    ("R84", "LOCAC", "", "LOCA rama fría 20 cm2", 301),
    ("R85", "LOCAC", "", "LOCA rama fría 100 cm2", 301),
    ("R86", "LOCAC", "", "LOCA rama fría 1000 cm2 + pérdida de energía AC", 301),
    ("R87", "LOCAC", "", "LOCA rama fría 2 cm2", 301),
    ("R88", "LOCAC", "", "LOCA rama fría 7700 cm2", 301),
    *[(f"R{n}", "ATWS", "", "ATWS", 301) for n in (47, 48, 49, 50, 51, 91, 92)],
    ("R54", "TRIP_OK", "R47", "Gemelo de R47", 301),
    ("R55", "TRIP_OK", "R48", "Gemelo de R48", 295),  # corta
    ("R56", "TRIP_OK", "R49", "Gemelo de R49", 301),
    ("R57", "TRIP_OK", "R50", "Gemelo de R50", 301),
    ("R58", "TRIP_OK", "R51", "Gemelo de R51", 301),
    ("R99", "TRIP_OK", "R91", "Gemelo de R91", 301),
    ("R100", "TRIP_OK", "R92", "Gemelo de R92", 301),
    ("R52", "TRIP_OK", "", "LOOP con scram", 301),
    ("R64", "OOD", "", "Rotura de 1 tubo del GV A (SGTR)", 301),
]

IDS_DESCARTADAS = {"R07", "R27"}
IDS_OOD = {"R20", "R64"}
IDS_CORTAS = {"R55"}
NUMERO_CORRIDAS = len(MANUALES) + len(AUTOMATICAS)


def datos_corrida(semilla: int, filas: int = 301) -> pd.DataFrame:
    """Tabla determinista y distinta por corrida, con decimales que no son exactos en binario."""
    tiempo = np.arange(filas)
    datos = {"TIME": tiempo}
    for j, nombre in enumerate(COLUMNAS[1:]):
        base = 50.0 + 7.0 * j + 0.37 * semilla
        datos[nombre] = base + 0.01 * (j + 1) * np.sin(tiempo / 10.0 + semilla) + tiempo / 3.0
    return pd.DataFrame(datos, columns=COLUMNAS)


def escribir_tabla(ruta: Path, tabla: pd.DataFrame, formato: str) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    if formato == "csv":
        tabla.to_csv(ruta, index=False)
    else:
        # pandas no escribe xlsx con extensión .xls: se escribe .xlsx y se renombra, como PCTran
        temporal = ruta.with_suffix(".xlsx")
        tabla.to_excel(temporal, index=False, engine="openpyxl")
        temporal.replace(ruta)


def construir_arbol(raiz: Path) -> Path:
    raiz.mkdir(parents=True, exist_ok=True)
    (raiz / "BasicDataInitialCondition.txt").write_text("archivo suelto\n", encoding="utf-8")
    (raiz / "_notas").mkdir()
    semilla = 0
    for clase, corrida, archivos, formato in MANUALES:
        carpeta = raiz / clase / corrida
        for archivo in archivos:
            semilla += 1
            escribir_tabla(carpeta / archivo, datos_corrida(semilla), formato)
        (carpeta / f"{corrida[:3]}_transientlist.dat").write_text("0.0 sec, inicio\n", encoding="utf-8")
    (raiz / "ATWS" / "R21_ATWS_LOFW_t30" / "PLOT").mkdir()
    auto = raiz / "auto"
    for rid, clase, gemela, descripcion, filas in AUTOMATICAS:
        semilla += 1
        carpeta = auto / f"{rid}_{clase}"
        escribir_tabla(carpeta / "plotdata.csv", datos_corrida(semilla, filas), "csv")
        configuracion = {"id": rid, "clase": clase, "gemelo_de": gemela, "descripcion": descripcion}
        (carpeta / "config.json").write_text(json.dumps(configuracion, ensure_ascii=False), encoding="utf-8")
    escribir_tabla(auto / "_respaldos" / "X01_NORM" / "plotdata.csv", datos_corrida(999), "csv")
    (auto / "manifest_auto.csv").write_text("id,clase\n", encoding="utf-8")
    return raiz


def hash_arbol(raiz: Path) -> str:
    resumen = hashlib.sha256()
    for ruta in sorted(Path(raiz).rglob("*")):
        if ruta.is_file():
            resumen.update(ruta.relative_to(raiz).as_posix().encode())
            resumen.update(ruta.read_bytes())
    return resumen.hexdigest()


def corromper_csv(ruta: Path, modo: str, variable: str = "P", fila: int = 5) -> None:
    """Modifica un CSV: quitar una columna, poner texto, vaciar, poner inf o romper el tiempo."""
    tabla = pd.read_csv(ruta, dtype=str, keep_default_na=False)
    if modo == "quitar":
        tabla = tabla.drop(columns=[variable])
    elif modo == "texto":
        tabla.loc[fila, variable] = "abc"
    elif modo == "vacio":
        tabla.loc[fila, variable] = ""
    elif modo == "inf":
        tabla.loc[fila, variable] = "inf"
    elif modo == "salto":
        tabla.loc[fila:, "TIME"] = [str(int(t) + 1) for t in tabla.loc[fila:, "TIME"]]
    else:
        raise ValueError(modo)
    tabla.to_csv(ruta, index=False)


def escribir_corrida_auto(raiz: Path, rid: str, clase: str, gemela: str = "", descripcion: str = "x",
                          filas: int = 301) -> Path:
    carpeta = Path(raiz) / "auto" / f"{rid}_{clase}"
    escribir_tabla(carpeta / "plotdata.csv", datos_corrida(500, filas), "csv")
    configuracion = {"id": rid, "clase": clase, "gemelo_de": gemela, "descripcion": descripcion}
    (carpeta / "config.json").write_text(json.dumps(configuracion, ensure_ascii=False), encoding="utf-8")
    return carpeta


@pytest.fixture(scope="session")
def arbol_pwr3l(tmp_path_factory) -> Path:
    """Árbol de solo lectura compartido por todas las pruebas: no modificarlo."""
    return construir_arbol(tmp_path_factory.mktemp("origen") / "PWR 3L")


@pytest.fixture
def copia_pwr3l(arbol_pwr3l, tmp_path) -> Path:
    """Copia propia del árbol para las pruebas que lo modifican."""
    destino = tmp_path / "PWR 3L"
    shutil.copytree(arbol_pwr3l, destino)
    return destino


@pytest.fixture
def ayudantes():
    return SimpleNamespace(
        hash_arbol=hash_arbol,
        corromper_csv=corromper_csv,
        escribir_corrida_auto=escribir_corrida_auto,
        escribir_tabla=escribir_tabla,
        datos_corrida=datos_corrida,
        NUMERO_CORRIDAS=NUMERO_CORRIDAS,
        IDS_DESCARTADAS=IDS_DESCARTADAS,
        IDS_OOD=IDS_OOD,
        IDS_CORTAS=IDS_CORTAS,
        VARIABLES_ENTRADA=VARIABLES_ENTRADA,
        VARIABLES_MARGEN=VARIABLES_MARGEN,
    )
