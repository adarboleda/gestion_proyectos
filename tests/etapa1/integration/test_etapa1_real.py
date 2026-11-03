"""Entrenamiento corto con el dataset real de PWR 3L (se omite sin datos o sin PyTorch)."""
import hashlib
import json

import pytest

pytest.importorskip("torch")

from datos_reales import ruta_pwr3l  # noqa: E402

import clasificador_etapa1.cli as cli  # noqa: E402
from preparacion_pwr3l.lectura import cargar_corridas  # noqa: E402

ORIGEN = ruta_pwr3l()

pytestmark = pytest.mark.skipif(not ORIGEN.is_dir(), reason="dataset PWR 3L no disponible")


def hash_origen() -> str:
    resumen = hashlib.sha256()
    for archivo in sorted(p for p in ORIGEN.rglob("*") if p.is_file()):
        resumen.update(str(archivo.relative_to(ORIGEN)).encode())
        resumen.update(archivo.read_bytes())
    return resumen.hexdigest()


def test_entrenamiento_corto_con_el_dataset_real(tmp_path, capsys):
    antes = hash_origen()
    salida = tmp_path / "etapa1"
    assert cli.main(["--origen", str(ORIGEN), "--salida", str(salida), "--epocas", "2"]) == 0
    capsys.readouterr()
    assert hash_origen() == antes

    modelo = json.loads((salida / "modelo.json").read_text(encoding="utf-8"))
    assert {c: len(v) for c, v in modelo["corridas"].items()} == {"train": 63, "val": 15, "test": 13}

    reporte = json.loads((salida / "reporte.json").read_text(encoding="utf-8"))
    por_id = {c.id: c for c in cargar_corridas(ORIGEN)}
    eventos = sorted(r for r in modelo["corridas"]["test"] if por_id[r].clase != "NORM")
    assert sorted(d["corrida"] for d in reporte["deteccion"]) == eventos
