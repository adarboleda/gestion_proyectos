"""Medición con el dataset real de PWR 3L y el modelo guardado (se omite sin datos, sin PyTorch o sin modelo)."""
import csv
import hashlib
import io
import json
from collections import Counter

import pytest

pytest.importorskip("torch")

from datos_reales import RAIZ_REPOSITORIO, ruta_pwr3l  # noqa: E402

import tiempo_deteccion.cli as cli  # noqa: E402

ORIGEN = ruta_pwr3l()
MODELO = RAIZ_REPOSITORIO / "modelos" / "etapa1"

pytestmark = [
    pytest.mark.skipif(not ORIGEN.is_dir(), reason="dataset PWR 3L no disponible"),
    pytest.mark.skipif(not (MODELO / "modelo.json").is_file(), reason="modelo de Etapa 1 no publicado (entrenar-etapa1)"),
]


def hash_origen() -> str:
    resumen = hashlib.sha256()
    for archivo in sorted(p for p in ORIGEN.rglob("*") if p.is_file()):
        resumen.update(str(archivo.relative_to(ORIGEN)).encode())
        resumen.update(archivo.read_bytes())
    return resumen.hexdigest()


def test_medicion_con_el_dataset_real(tmp_path, capsys):
    antes = hash_origen()
    salida = tmp_path / "tiempos"
    assert cli.main(["--origen", str(ORIGEN), "--modelo", str(MODELO), "--salida", str(salida)]) == 0
    capsys.readouterr()
    assert hash_origen() == antes

    datos = json.loads((salida / "tiempos.json").read_text(encoding="utf-8"))
    instantes = datos["instantes"]
    assert len(instantes) == 72
    assert Counter(i["fuente"] for i in instantes.values()) == {"registro": 29, "programado": 43}
    assert sorted(i["corrida"] for i in datos["inciertas"]) == ["R22", "R47", "R48", "R54", "R99"]

    modelo = json.loads((MODELO / "modelo.json").read_text(encoding="utf-8"))
    evaluadas = set(modelo["corridas"]["val"]) | set(modelo["corridas"]["test"])
    texto = (salida / "tiempos.csv").read_text(encoding="utf-8")
    filas = list(csv.DictReader(io.StringIO("".join(l for l in texto.splitlines(True) if not l.startswith("#")))))
    assert len(filas) == len(evaluadas) == 28
    assert {f["corrida"] for f in filas} == evaluadas
    assert {"diagnostico_10s", "atws_3s"} == set(datos["metas"])
