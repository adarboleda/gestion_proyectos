"""Entrenamiento corto de la Etapa 2 con el dataset real de PWR 3L (se omite sin datos o sin PyTorch)."""
import hashlib
import json

import pytest

pytest.importorskip("torch")

from datos_reales import ruta_pwr3l  # noqa: E402

import clasificador_etapa2.cli as cli  # noqa: E402

ORIGEN = ruta_pwr3l()

pytestmark = pytest.mark.skipif(not ORIGEN.is_dir(), reason="dataset PWR 3L no disponible")


def hash_origen() -> str:
    resumen = hashlib.sha256()
    for archivo in sorted(p for p in ORIGEN.rglob("*") if p.is_file()):
        resumen.update(str(archivo.relative_to(ORIGEN)).encode())
        resumen.update(archivo.read_bytes())
    return resumen.hexdigest()


def test_entrenamiento_corto_etapa2_con_dataset_real(tmp_path, capsys):
    antes = hash_origen()
    salida = tmp_path / "etapa2"
    assert cli.main(["--origen", str(ORIGEN), "--salida", str(salida), "--epocas", "2"]) == 0
    capsys.readouterr()
    assert hash_origen() == antes

    modelo = json.loads((salida / "modelo.json").read_text(encoding="utf-8"))
    assert {c: len(v) for c, v in modelo["corridas"].items()} == {"train": 25, "val": 6, "test": 5}

    reporte = json.loads((salida / "reporte.json").read_text(encoding="utf-8"))
    assert [c["corrida"] for c in reporte["corridas"]] == modelo["corridas"]["test"]

