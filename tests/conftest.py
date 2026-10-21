"""Fixtures compartidas: dataset sintético con la misma estructura que NPPAD."""
import csv
import hashlib
import shutil
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

# Copias independientes de las constantes del proyecto: las pruebas no deben depender del
# módulo que verifican.
VARIABLES_PLANTA = ["P", "TAVG", "THA", "TCA", "WRCA", "WRCB", "LVPZ", "LVCR", "PWNT", "PWR", "WECS", "WLR"]
VARIABLES_MARGEN = ["DNBR", "TPCT", "SCMA", "SCMB", "TSAT", "FRCL", "FRZR"]
VARIABLES = VARIABLES_PLANTA + VARIABLES_MARGEN
CARPETAS = {"Normal": 1, "LOCA": 100, "LOCAC": 100, "ATWS": 1}
FILAS = 160


def _escribir_simulacion(ruta: Path, semilla: int) -> None:
    rng = np.random.default_rng(semilla)
    columnas = ["TIME"] + VARIABLES + ["EXTRA1", "EXTRA2"]
    datos = {"TIME": np.arange(FILAS) * 10.0}
    for i, nombre in enumerate(VARIABLES + ["EXTRA1", "EXTRA2"]):
        base = 10.0 ** (i % 4) + i
        datos[nombre] = base + rng.normal(scale=1.0 + 0.1 * i, size=FILAS) + np.linspace(0, semilla % 7, FILAS)
    orden = ["TIME"] + list(rng.permutation(columnas[1:]))
    pd.DataFrame(datos)[orden].to_csv(ruta, index=False)


@pytest.fixture(scope="session")
def _origen_base(tmp_path_factory) -> Path:
    base = tmp_path_factory.mktemp("nppad_sintetico") / "Operation_csv_data"
    for indice, (carpeta, cantidad) in enumerate(CARPETAS.items()):
        (base / carpeta).mkdir(parents=True)
        for n in range(1, cantidad + 1):
            _escribir_simulacion(base / carpeta / f"{n}.csv", semilla=1000 * (indice + 1) + n)
    return base


@pytest.fixture
def origen_sintetico(_origen_base, tmp_path) -> Path:
    """Copia modificable del dataset sintético: 1 Normal, 100 LOCA, 100 LOCAC y 1 ATWS."""
    destino = tmp_path / "Operation_csv_data"
    shutil.copytree(_origen_base, destino)
    return destino


def _leer_texto(ruta: Path) -> pd.DataFrame:
    return pd.read_csv(ruta, dtype=str, keep_default_na=False)


def _quitar_columna(ruta: Path, columna: str) -> None:
    _leer_texto(ruta).drop(columns=[columna]).to_csv(ruta, index=False)


def _poner_valor(ruta: Path, columna: str, fila: int, valor: str) -> None:
    datos = _leer_texto(ruta)
    datos.loc[fila, columna] = valor
    datos.to_csv(ruta, index=False)


def _truncar(ruta: Path, filas: int) -> None:
    _leer_texto(ruta).iloc[:filas].to_csv(ruta, index=False)


def _hash_origen(origen: Path) -> str:
    resumen = hashlib.sha256()
    for archivo in sorted(origen.rglob("*.csv")):
        resumen.update(str(archivo.relative_to(origen)).encode())
        resumen.update(archivo.read_bytes())
    return resumen.hexdigest()


def _hash_directorio(directorio: Path) -> dict:
    return {str(a.relative_to(directorio)): a.read_bytes() for a in sorted(directorio.rglob("*")) if a.is_file()}


def _leer_independiente(ruta: Path, columnas: list, filas: int = 150) -> np.ndarray:
    """Lectura con el módulo csv y float(): referencia independiente de pandas."""
    with open(ruta, newline="") as f:
        lector = csv.DictReader(f)
        return np.array(
            [[float(fila[c]) for c in columnas] for _, fila in zip(range(filas), lector)],
            dtype=np.float64,
        )


@pytest.fixture
def ayudas() -> SimpleNamespace:
    return SimpleNamespace(
        quitar_columna=_quitar_columna,
        poner_valor=_poner_valor,
        truncar=_truncar,
        hash_origen=_hash_origen,
        contenido_directorio=_hash_directorio,
        leer_independiente=_leer_independiente,
        VARIABLES_PLANTA=VARIABLES_PLANTA,
        VARIABLES_MARGEN=VARIABLES_MARGEN,
        VARIABLES=VARIABLES,
    )
