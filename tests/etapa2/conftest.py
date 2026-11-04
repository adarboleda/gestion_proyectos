"""Corridas PWR 3L sintéticas para las pruebas del clasificador de Etapa 2 (009).

En las corridas LOCA (rama caliente) `PWR` y `PWNT` tienen un pulso positivo tras el inicio del
evento; en las LOCAC (rama fría) permanecen sin pico positivo. También se incluyen corridas NORM y
ATWS para comprobar que la Etapa 2 las ignora.
"""
import csv
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from preparacion_pwr3l.config import PASOS, VARIABLE_TIEMPO, VARIABLES
from preparacion_pwr3l.descubrimiento import GEMELA_DE, Corrida

COL = {v: i for i, v in enumerate(VARIABLES)}
GEMELAS = [("R21", "R59"), ("R22", "R60"), ("R23", "R61"), ("R24", "R62"),
           ("R26", "R53"), ("R47", "R54"), ("R49", "R56"), ("R50", "R57")]


def pwr_y_serie_sintetica(clase: str, inicio, semilla: int):
    generador = np.random.default_rng(semilla)
    serie = 100.0 + 0.02 * generador.standard_normal((PASOS, len(VARIABLES)))
    pwr = 100.0 + 0.02 * generador.standard_normal(PASOS)
    pwr[0] = 100.0
    serie[0, COL["PWNT"]] = 100.0
    if inicio is None:
        return pwr, serie
    t = np.arange(PASOS, dtype=float)
    activo = t >= inicio
    if clase == "LOCA":
        # En rama caliente hay sobrepotencia sostenida de PWR y PWNT respecto de t=0
        pwr[activo] += 2.5
        serie[activo, COL["PWNT"]] += 3.5
        serie[activo, COL["P"]] -= 0.05 * (t[activo] - inicio)
    elif clase == "LOCAC":
        # En rama fría no hay pico positivo (cae ligeramente tras el inicio)
        pwr[activo] -= 0.8
        serie[activo, COL["PWNT"]] -= 1.0
        serie[activo, COL["P"]] -= 0.05 * (t[activo] - inicio)
    elif clase in ("ATWS", "TRIP_OK"):
        serie[activo, COL["TAVG"]] += 0.03 * (t[activo] - inicio)
    return pwr, serie


def corrida_sintetica(rid: str, clase: str, inicio, semilla: int, area=None):
    corrida = Corrida(rid, clase, "auto", f"auto/{rid}_{clase}/plotdata.csv", area=area, estado="usable")
    corrida.gemela = GEMELA_DE.get(rid)
    corrida.filas = PASOS
    corrida.paso_segundos = 1
    pwr, serie = pwr_y_serie_sintetica(clase, inicio, semilla)
    corrida.serie = serie
    return corrida, pwr


def construir_sinteticas():
    generador = np.random.default_rng(9)
    corridas, inicios, pwr_por_id = [], {}, {}
    for n in range(31, 35):
        rid = f"R{n}"
        c, pwr = corrida_sintetica(rid, "NORM", None, n)
        corridas.append(c)
        inicios[rid] = None
        pwr_por_id[rid] = pwr
    numero = 200
    for area in (2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000):
        for clase in ("LOCA", "LOCAC"):
            rid = f"R{numero}"
            inicio = float(generador.integers(10, 45))
            c, pwr = corrida_sintetica(rid, clase, inicio, numero, area=area)
            corridas.append(c)
            inicios[rid] = inicio
            pwr_por_id[rid] = pwr
            numero += 1
    for atws, trip in GEMELAS[:4]:
        inicio = float(generador.integers(10, 45))
        for rid, clase in ((atws, "ATWS"), (trip, "TRIP_OK")):
            c, pwr = corrida_sintetica(rid, clase, inicio, int(rid[1:]))
            corridas.append(c)
            inicios[rid] = inicio
            pwr_por_id[rid] = pwr
    return corridas, inicios, pwr_por_id


@pytest.fixture
def sinteticas():
    corridas, inicios, pwr_por_id = construir_sinteticas()
    return SimpleNamespace(corridas=corridas, inicios=inicios, pwr=pwr_por_id)


def escribir_csv_corrida(ruta: Path, serie: np.ndarray, pwr=None, incluir_pwr: bool = True) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    encabezados = [VARIABLE_TIEMPO] + (["PWR"] if incluir_pwr else []) + list(VARIABLES)
    with open(ruta, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(encabezados)
        for fila_idx in range(len(serie)):
            fila = [float(fila_idx)]
            if incluir_pwr:
                valor_pwr = 100.0 if pwr is None else pwr[fila_idx]
                fila.append(valor_pwr)
            fila.extend(float(v) for v in serie[fila_idx])
            escritor.writerow(fila)
