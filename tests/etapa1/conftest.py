"""Corridas PWR 3L sintéticas para las pruebas del clasificador de Etapa 1 (005).

Cada corrida tiene un estado estable con ruido pequeño y, desde su instante de inicio, una señal
propia de su familia: LOCA baja la presión y sube la inyección de emergencia; ATWS/TRIP_OK baja el
caudal de agua de alimentación y sube la temperatura media. Así el modelo puede aprender rápido.
"""
import csv
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from preparacion_pwr3l.config import PASOS, VARIABLES, VARIABLES_ENTRADA
from preparacion_pwr3l.descubrimiento import GEMELA_DE, Corrida

COL = {v: i for i, v in enumerate(VARIABLES)}
GEMELAS = [("R21", "R59"), ("R22", "R60"), ("R23", "R61"), ("R24", "R62"),
           ("R26", "R53"), ("R47", "R54"), ("R49", "R56"), ("R50", "R57")]


def serie_sintetica(clase: str, inicio, semilla: int) -> np.ndarray:
    generador = np.random.default_rng(semilla)
    serie = 1.0 + 0.01 * generador.standard_normal((PASOS, len(VARIABLES)))
    if inicio is None:
        return serie
    t = np.arange(PASOS, dtype=float)
    rampa = np.clip(t - inicio, 0, None)
    if clase in ("LOCA", "LOCAC"):
        serie[:, COL["P"]] -= 0.05 * rampa
        serie[:, COL["WECS"]] += 0.05 * rampa
    elif clase in ("ATWS", "TRIP_OK"):
        serie[:, COL["WFWA"]] -= 0.05 * rampa
        serie[:, COL["WFWB"]] -= 0.05 * rampa
        serie[:, COL["TAVG"]] += 0.03 * rampa
    return serie


def corrida_sintetica(rid, clase, inicio, semilla, area=None):
    corrida = Corrida(rid, clase, "auto", f"auto/{rid}_{clase}/plotdata.csv", area=area, estado="usable")
    corrida.gemela = GEMELA_DE.get(rid)
    corrida.filas = PASOS
    corrida.paso_segundos = 1
    corrida.serie = serie_sintetica(clase, inicio, semilla)
    return corrida


def construir_sinteticas(semilla: int = 0):
    generador = np.random.default_rng(semilla)
    corridas, inicios = [], {}
    for n in range(31, 41):
        rid = f"R{n}"
        corridas.append(corrida_sintetica(rid, "NORM", None, n))
        inicios[rid] = None
    numero = 200
    for i, area in enumerate((2, 5, 10, 20, 50, 100, 500, 2000)):
        for clase in ("LOCA", "LOCAC"):
            rid = f"R{numero}"
            inicio = float(generador.integers(5, 60))
            corridas.append(corrida_sintetica(rid, clase, inicio, numero, area=area))
            inicios[rid] = inicio
            numero += 1
    for atws, trip in GEMELAS:
        inicio = float(generador.integers(5, 60))
        for rid, clase in ((atws, "ATWS"), (trip, "TRIP_OK")):
            corridas.append(corrida_sintetica(rid, clase, inicio, int(rid[1:])))
            inicios[rid] = inicio
    return corridas, inicios


@pytest.fixture(scope="session")
def _sinteticas_base():
    return construir_sinteticas()


@pytest.fixture
def sinteticas(_sinteticas_base):
    """Corridas nuevas en cada prueba (las pruebas pueden modificarlas)."""
    corridas, inicios = construir_sinteticas()
    return SimpleNamespace(corridas=corridas, inicios=dict(inicios), variables=VARIABLES_ENTRADA)


def escribir_arbol_eventos(raiz: Path) -> Path:
    """Árbol PWR 3L mínimo con las tres fuentes del instante de inicio (sin datos de planta)."""
    raiz = Path(raiz)
    auto = raiz / "auto" / "R41_LOCA"
    auto.mkdir(parents=True)
    (auto / "validacion.json").write_text(json.dumps({"corrida": "R41", "t_inicio_real": 25.0}), encoding="utf-8")
    (raiz / "auto" / "R42_LOCA").mkdir()
    for carpeta in ("LOCA HOT/R10_LOCA_hot_50cm_t60", "ATWS/R27_ATWS_LOFW_tripman_FAILED_t30_op90",
                    "TRIP_OK/R60_TRIP_OK_LOFW_t48", "LOCA HOT/R09_LOCA_hot_2000cm2_t0"):
        (raiz / carpeta).mkdir(parents=True)
    with open(raiz / "validacion_corridas.csv", "w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["corrida", "clase", "estado", "t_plan", "t_inicio_real"])
        escritor.writerow(["R10_LOCA_hot_50cm_t60", "LOCA", "OK", "60.0", "61.0"])
        escritor.writerow(["R27_ATWS_LOFW_tripman_FAILED_t30_op90 [failed]", "ATWS", "OK", "30.0", "32.0"])
        escritor.writerow(["R27_ATWS_LOFW_tripman_FAILED_t30_op90 [mitigation]", "ATWS", "OK", "30.0", "101.0"])
        escritor.writerow(["R09_LOCA_hot_2000cm2_t0", "LOCA", "OK", "0.0", "1.0"])
    return raiz


@pytest.fixture
def arbol_eventos(tmp_path):
    return escribir_arbol_eventos(tmp_path / "PWR 3L")
