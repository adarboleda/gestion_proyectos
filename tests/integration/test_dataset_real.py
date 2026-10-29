"""Extremo a extremo con el dataset NPPAD real (se omite si no está disponible)."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from preparacion_datos.cli import main
from preparacion_datos.config import ORIGEN_POR_DEFECTO, REFERENCIA_POR_DEFECTO

RAIZ = Path(__file__).resolve().parents[2]
ORIGEN = (RAIZ / ORIGEN_POR_DEFECTO).resolve()
REFERENCIA = (RAIZ / REFERENCIA_POR_DEFECTO).resolve()
CARPETAS = ("Normal", "LOCA", "LOCAC", "ATWS")

pytestmark = pytest.mark.skipif(not ORIGEN.is_dir(), reason="dataset NPPAD no disponible")


def hash_origen() -> str:
    resumen = hashlib.sha256()
    for carpeta in CARPETAS:
        for archivo in sorted((ORIGEN / carpeta).glob("*.csv")):
            resumen.update(f"{carpeta}/{archivo.name}".encode())
            resumen.update(archivo.read_bytes())
    return resumen.hexdigest()


def test_preparacion_completa_con_el_dataset_real(tmp_path, capsys):
    salida = tmp_path / "data_processed"
    antes = hash_origen()
    codigo = main(["--origen", str(ORIGEN), "--salida", str(salida), "--referencia", str(REFERENCIA)])
    texto = capsys.readouterr().out
    assert codigo == 0, texto
    assert hash_origen() == antes

    metadata = json.loads((salida / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["paso_segundos"] == 10
    assert metadata["duracion_muestra_segundos"] == 1500
    assert metadata["totales"] == {"train": 142, "val": 30, "test": 30}
    assert metadata["conteos_muestras"] == {
        "NORM": {"train": 1, "val": 0, "test": 0},
        "LOCA": {"train": 70, "val": 15, "test": 15},
        "LOCAC": {"train": 70, "val": 15, "test": 15},
        "ATWS": {"train": 1, "val": 0, "test": 0},
    }
    if REFERENCIA.is_file():
        assert metadata["referencia"]["estado"] == "COINCIDE"
    for conjunto, n in (("train", 142), ("val", 30), ("test", 30)):
        assert np.load(salida / f"X_{conjunto}.npy").shape == (n, 150, 12)
        assert np.load(salida / f"margins_{conjunto}.npy").shape == (n, 150, 7)
        assert np.load(salida / f"y_{conjunto}.npy").shape == (n,)
    assert "una sola simulación" in texto
    assert "paso medido de TIME: 10 s" in texto
