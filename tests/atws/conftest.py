"""Árbol PWR 3L sintético para la regla de ATWS (006).

Solo corridas automáticas (`auto/R<n>_<CLASE>`), aceptadas por `preparacion_pwr3l`: las cinco
clases, `config.json` coherentes con la tabla de gemelas y un `transientlist.dat` por corrida.
Perfiles de PWNT (% del nominal):
- TRIP_OK: 100 hasta el scram (señal + retardo de su tipo) y 6 después.
- ATWS: 100 hasta la señal y luego baja en 3 s a un nivel que se mantiene (sin scram).
- ATWS por extracción de barras (R96): sin señal en el registro; PWNT sube a 120 en t = 50.
- LOCA/LOCAC: «Scram Lo RX Press» a los 40 s, scram a los 40.5 s y PWNT a 6.
- NORM: sin señales; PWNT 100.
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
COLUMNAS = ["TIME", "WLR"] + VARIABLES_ENTRADA + VARIABLES_MARGEN
FILAS = 301

RETARDO = {"Turbine trip": 5.0, "RCP-A trip": 2.5, "Low SG Level 17.0 %": 1.0, "Scram High Flux 118.0 %": 0.5}
NIVEL_ATWS = {"Turbine trip": 55.0, "RCP-A trip": 40.0, "Low SG Level 17.0 %": 85.0}

# (ATWS, TRIP_OK, señal, instante de la señal); R96/R104 es la extracción de barras
PARES = [
    ("R47", "R54", "Turbine trip", 45.5), ("R48", "R55", "Turbine trip", 20.5),
    ("R49", "R56", "RCP-A trip", 31.5), ("R50", "R57", "RCP-A trip", 61.5),
    ("R51", "R58", "Low SG Level 17.0 %", 40.0), ("R91", "R99", "Low SG Level 17.0 %", 33.0),
    ("R92", "R100", "RCP-A trip", 45.0), ("R93", "R101", "Turbine trip", 21.5),
    ("R94", "R102", "Low SG Level 17.0 %", 30.0), ("R95", "R103", "RCP-A trip", 50.0),
    ("R96", "R104", "Scram High Flux 118.0 %", 50.0),
]
LOCAS = [("R41", "LOCA", 5), ("R42", "LOCA", 10), ("R43", "LOCA", 20), ("R44", "LOCA", 100), ("R45", "LOCA", 1000),
         ("R46", "LOCAC", 5), ("R83", "LOCAC", 10), ("R84", "LOCAC", 20), ("R85", "LOCAC", 100), ("R86", "LOCAC", 1000)]
NORMS = [f"R{n}" for n in range(31, 41)]
IDS_ATWS = {a for a, _, _, _ in PARES}
NUMERO_CORRIDAS = len(NORMS) + len(LOCAS) + 2 * len(PARES)


def _tabla(semilla: int, pwnt: np.ndarray) -> pd.DataFrame:
    tiempo = np.arange(FILAS)
    datos = {"TIME": tiempo}
    for j, nombre in enumerate(COLUMNAS[1:]):
        datos[nombre] = 50.0 + 7.0 * j + 0.37 * semilla + 0.01 * (j + 1) * np.sin(tiempo / 10.0 + semilla)
    datos["PWNT"] = pwnt
    return pd.DataFrame(datos, columns=COLUMNAS)


def _dat(lineas) -> str:
    cuerpo = "".join(f"{t:08.1f} sec, {texto}\n" for t, texto in lineas)
    return "Basic Data Set #1 W 3-Loop TPC #3\nReset to IC #1 100% POWER EOC\n000000.0 sec, HPI Pump #3 Position Change: 100%\n" + cuerpo


def _escribir(raiz: Path, rid: str, clase: str, pwnt, lineas, gemela="", descripcion="x", semilla=0):
    carpeta = raiz / "auto" / f"{rid}_{clase}"
    carpeta.mkdir(parents=True, exist_ok=True)
    _tabla(semilla, np.asarray(pwnt, dtype=float)).to_csv(carpeta / "plotdata.csv", index=False)
    (carpeta / "transientlist.dat").write_text(_dat(lineas), encoding="latin-1")
    configuracion = {"id": rid, "clase": clase, "gemelo_de": gemela, "descripcion": descripcion}
    (carpeta / "config.json").write_text(json.dumps(configuracion, ensure_ascii=False), encoding="utf-8")


def perfil_trip_ok(t_senal: float, retardo: float) -> np.ndarray:
    pwnt = np.full(FILAS, 100.0)
    pwnt[np.arange(FILAS) > t_senal + retardo] = 6.0
    return pwnt


def perfil_atws(t_senal: float, nivel: float) -> np.ndarray:
    t = np.arange(FILAS, dtype=float)
    rampa = np.clip((t - t_senal) / 3.0, 0.0, 1.0)
    return 100.0 - (100.0 - nivel) * rampa


def construir_arbol(raiz: Path) -> Path:
    raiz.mkdir(parents=True, exist_ok=True)
    semilla = 0
    for rid in NORMS:
        semilla += 1
        _escribir(raiz, rid, "NORM", np.full(FILAS, 100.0), [(30.0, "TBV Valve #1 Position Change: 100%")], semilla=semilla)
    for rid, clase, area in LOCAS:
        semilla += 1
        rama = "caliente" if clase == "LOCA" else "fría"
        _escribir(raiz, rid, clase, perfil_trip_ok(40.0, 0.5),
                  [(40.0, "Scram Lo RX Press  1890.0 psia"), (40.5, "Reactor Scram")],
                  descripcion=f"LOCA rama {rama} {area} cm2", semilla=semilla)
    for atws, trip, senal, t in PARES:
        semilla += 1
        retardo = RETARDO[senal]
        if senal.startswith("Scram High Flux"):  # extracción de barras: sin anunciador en el ATWS
            pwnt = np.where(np.arange(FILAS) >= t, 120.0, 100.0)
            _escribir(raiz, atws, "ATWS", pwnt, [], semilla=semilla)
            trip_pwnt = np.where(np.arange(FILAS) >= t, 120.0, 100.0)
            trip_pwnt[np.arange(FILAS) > t + retardo] = 6.0
            _escribir(raiz, trip, "TRIP_OK", trip_pwnt, [(t - 0.5, senal), (t, "Reactor Scram")], gemela=atws, semilla=semilla + 100)
            continue
        _escribir(raiz, atws, "ATWS", perfil_atws(t, NIVEL_ATWS[senal]), [(t, senal)], semilla=semilla)
        _escribir(raiz, trip, "TRIP_OK", perfil_trip_ok(t, retardo), [(t, senal), (t + retardo, "Reactor Scram")],
                  gemela=atws, semilla=semilla + 100)
    return raiz


def hash_arbol(raiz: Path) -> str:
    resumen = hashlib.sha256()
    for ruta in sorted(Path(raiz).rglob("*")):
        if ruta.is_file():
            resumen.update(ruta.relative_to(raiz).as_posix().encode())
            resumen.update(ruta.read_bytes())
    return resumen.hexdigest()


def cambiar_pwnt(raiz: Path, carpeta: str, valores) -> None:
    ruta = Path(raiz) / "auto" / carpeta / "plotdata.csv"
    tabla = pd.read_csv(ruta)
    tabla["PWNT"] = np.asarray(valores, dtype=float)
    tabla.to_csv(ruta, index=False)


@pytest.fixture(scope="session")
def arbol_atws(tmp_path_factory) -> Path:
    """Árbol de solo lectura compartido: no modificarlo."""
    return construir_arbol(tmp_path_factory.mktemp("atws") / "PWR 3L")


@pytest.fixture
def copia_atws(arbol_atws, tmp_path) -> Path:
    destino = tmp_path / "PWR 3L"
    shutil.copytree(arbol_atws, destino)
    return destino


@pytest.fixture
def ayudantes_atws():
    return SimpleNamespace(
        hash_arbol=hash_arbol, cambiar_pwnt=cambiar_pwnt, perfil_atws=perfil_atws, perfil_trip_ok=perfil_trip_ok,
        dat=_dat, FILAS=FILAS, IDS_ATWS=IDS_ATWS, NUMERO_CORRIDAS=NUMERO_CORRIDAS, PARES=PARES,
    )
