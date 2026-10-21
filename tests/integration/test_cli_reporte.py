"""Reporte impreso, metadata.json y comparación con la referencia a través de la línea de órdenes."""
import json

import numpy as np
import pytest

from preparacion_datos.cli import main

CONJUNTOS = ("train", "val", "test")
SECCIONES = [
    "1. Origen y configuración",
    "2. Muestras por clase y conjunto",
    "3. Simulaciones por conjunto",
    "4. Escalador",
    "5. Advertencias",
    "6. Limitaciones conocidas",
    "7. Comparación con la referencia",
    "8. Artefactos escritos",
]
CLAVES_METADATA = {
    "version_formato", "origen", "semilla", "proporciones", "pasos_por_muestra", "paso_segundos", "clases",
    "variables_planta", "variables_margen", "conteos_archivos", "conteos_muestras", "totales", "simulaciones",
    "escalador", "referencia", "advertencias", "limitaciones",
}


@pytest.fixture(autouse=True)
def directorio_de_trabajo(tmp_path, monkeypatch):
    carpeta = tmp_path / "trabajo"
    carpeta.mkdir()
    monkeypatch.chdir(carpeta)


def referencia(tmp_path, loca=(70, 15, 15), locac=(70, 15, 15)):
    ruta = tmp_path / "referencia.json"
    cuenta = lambda t: dict(zip(CONJUNTOS, t))  # noqa: E731
    ruta.write_text(json.dumps({"sample_counts": {"LOCA": cuenta(loca), "LOCAC": cuenta(locac)}}))
    return ruta


def ejecutar(origen, salida, *extra):
    return main(["--origen", str(origen), "--salida", str(salida), *extra])


def test_el_reporte_impreso_tiene_las_secciones_en_orden(origen_sintetico, tmp_path, capsys):
    assert ejecutar(origen_sintetico, tmp_path / "salida", "--sin-referencia") == 0
    salida = capsys.readouterr().out
    posiciones = [salida.index(seccion) for seccion in SECCIONES]
    assert posiciones == sorted(posiciones)
    assert "metadata.json" in salida.split("8. Artefactos escritos")[1]
    assert "una sola simulación" in salida.split("5. Advertencias")[1]


def test_metadata_json_tiene_todos_los_campos(origen_sintetico, tmp_path):
    salida = tmp_path / "salida"
    assert ejecutar(origen_sintetico, salida, "--sin-referencia") == 0
    metadata = json.loads((salida / "metadata.json").read_text(encoding="utf-8"))
    assert set(metadata) == CLAVES_METADATA
    assert metadata["totales"] == {"train": 142, "val": 30, "test": 30}
    assert metadata["conteos_muestras"]["LOCA"] == {"train": 70, "val": 15, "test": 15}
    assert metadata["conteos_muestras"]["NORM"] == {"train": 1, "val": 0, "test": 0}
    assert metadata["conteos_muestras"]["ATWS"] == {"train": 1, "val": 0, "test": 0}
    assert metadata["variables_planta"][0] == "P" and len(metadata["variables_planta"]) == 12
    assert metadata["variables_margen"][0] == "DNBR" and len(metadata["variables_margen"]) == 7
    assert metadata["semilla"] == 42 and metadata["pasos_por_muestra"] == 150
    assert metadata["referencia"]["estado"] == "OMITIDA"
    assert len(metadata["simulaciones"]["train"]) == 142
    assert metadata["escalador"]["filas_ajuste"] == 142 * 150
    for conjunto in CONJUNTOS:
        assert len(metadata["simulaciones"][conjunto]) == np.load(salida / f"y_{conjunto}.npy").shape[0]


def test_referencia_que_coincide_termina_con_codigo_0(origen_sintetico, tmp_path, capsys):
    assert ejecutar(origen_sintetico, tmp_path / "salida", "--referencia", str(referencia(tmp_path))) == 0
    assert "COINCIDE" in capsys.readouterr().out


def test_referencia_que_difiere_termina_con_codigo_2_y_deja_los_artefactos(origen_sintetico, tmp_path, capsys):
    salida = tmp_path / "salida"
    ruta = referencia(tmp_path, loca=(69, 16, 15))
    assert ejecutar(origen_sintetico, salida, "--referencia", str(ruta)) == 2
    texto = capsys.readouterr().out
    assert "DIFIERE" in texto and "LOCA" in texto.split("7. Comparación con la referencia")[1]
    assert (salida / "X_train.npy").is_file() and (salida / "metadata.json").is_file()
    assert json.loads((salida / "metadata.json").read_text(encoding="utf-8"))["referencia"]["estado"] == "DIFIERE"


def test_referencia_inexistente_no_falla(origen_sintetico, tmp_path, capsys):
    assert ejecutar(origen_sintetico, tmp_path / "salida", "--referencia", str(tmp_path / "no_existe.json")) == 0
    assert "NO DISPONIBLE" in capsys.readouterr().out


def test_sin_referencia_la_omite(origen_sintetico, tmp_path, capsys):
    assert ejecutar(origen_sintetico, tmp_path / "salida", "--sin-referencia") == 0
    assert "OMITIDA" in capsys.readouterr().out
