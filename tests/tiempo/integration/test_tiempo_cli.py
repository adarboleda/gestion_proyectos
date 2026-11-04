"""Comando `medir-tiempo-deteccion` con el modelo sintético de 005 (US2, contracts/cli.md y salidas.md)."""
import csv
import io
import json

import pytest

pytest.importorskip("torch")

import tiempo_deteccion.cli as cli  # noqa: E402
from ayudas_tiempo import casos_sinteticos, fallas_sinteticas  # noqa: E402

ARCHIVOS = {"tiempos.json", "tiempos.csv", "lineas_tiempo.csv", "reporte.txt"}


@pytest.fixture
def con_sinteticas(modelo_sintetico, monkeypatch):
    corridas, inicios = modelo_sintetico.construir()
    monkeypatch.setattr(cli, "cargar_corridas", lambda origen: corridas)
    monkeypatch.setattr(cli, "instantes_falla", lambda origen, lista: fallas_sinteticas(lista, inicios, inciertas={"R22"}))
    monkeypatch.setattr(cli, "construir_casos", lambda origen, semilla: casos_sinteticos(corridas, inicios, semilla))
    return modelo_sintetico


def ejecutar(modelo, salida, *extra):
    return cli.main(["--origen", "sintetico", "--modelo", str(modelo.ruta), "--salida", str(salida), *extra])


def leer_csv(ruta):
    return list(csv.DictReader(io.StringIO(ruta.read_text(encoding="utf-8"))))


def test_publica_los_cuatro_archivos(con_sinteticas, tmp_path, capsys):
    salida = tmp_path / "resultados"
    assert ejecutar(con_sinteticas, salida) == 0
    assert {p.name for p in salida.iterdir()} == ARCHIVOS
    impreso = capsys.readouterr().out
    assert impreso == (salida / "reporte.txt").read_text(encoding="utf-8")


def test_contenido_de_tiempos(con_sinteticas, tmp_path, capsys):
    salida = tmp_path / "resultados"
    ejecutar(con_sinteticas, salida)
    datos = json.loads((salida / "tiempos.json").read_text(encoding="utf-8"))
    assert {"aviso", "configuracion", "corridas", "resumen", "metas", "falsas_alarmas", "confusiones",
            "inciertas", "instantes"} <= set(datos)
    assert "consultiv" in datos["aviso"].lower()
    assert datos["configuracion"]["meta_diagnostico_s"] == 10 and datos["configuracion"]["meta_atws_s"] == 3
    assert {"diagnostico_10s", "atws_3s"} == set(datos["metas"])
    modelo = json.loads((con_sinteticas.ruta / "modelo.json").read_text(encoding="utf-8"))
    evaluadas = set(modelo["corridas"]["val"]) | set(modelo["corridas"]["test"])
    assert {c["corrida"] for c in datos["corridas"]} == evaluadas
    filas = leer_csv(salida / "tiempos.csv")
    assert {f["corrida"] for f in filas} == evaluadas
    for fila in filas:
        if fila["t_confirmacion"] and fila["t_falla"]:
            assert float(fila["tiempo_diagnostico_s"]) == pytest.approx(float(fila["t_confirmacion"]) - float(fila["t_falla"]))


def test_reporte_con_aviso_tiempos_y_metas(con_sinteticas, tmp_path, capsys):
    ejecutar(con_sinteticas, tmp_path / "resultados")
    texto = capsys.readouterr().out
    assert "consultiv" in texto.lower()
    assert "10 s" in texto and "3 s" in texto
    assert "Inciertas" in texto
    assert "Falsas alarmas" in texto


def test_dos_ejecuciones_identicas(con_sinteticas, tmp_path, capsys):
    ejecutar(con_sinteticas, tmp_path / "a")
    ejecutar(con_sinteticas, tmp_path / "b")
    for nombre in ARCHIVOS:
        assert (tmp_path / "a" / nombre).read_bytes() == (tmp_path / "b" / nombre).read_bytes(), nombre


def test_reemplaza_sin_tocar_otros_archivos(con_sinteticas, tmp_path, capsys):
    salida = tmp_path / "resultados"
    salida.mkdir()
    (salida / "notas.txt").write_text("mío", encoding="utf-8")
    (salida / "tiempos.json").write_text("viejo", encoding="utf-8")
    assert ejecutar(con_sinteticas, salida) == 0
    assert (salida / "notas.txt").read_text(encoding="utf-8") == "mío"
    assert (salida / "tiempos.json").read_text(encoding="utf-8") != "viejo"


def test_modelo_de_otra_semilla_termina_con_codigo_1(con_sinteticas, tmp_path, capsys):
    salida = tmp_path / "resultados"
    assert ejecutar(con_sinteticas, salida, "--semilla", "7") == 1
    assert "no corresponde" in capsys.readouterr().err
    assert not salida.exists()


def test_modelo_inexistente_termina_con_codigo_1(con_sinteticas, tmp_path, capsys):
    salida = tmp_path / "resultados"
    codigo = cli.main(["--origen", "sintetico", "--modelo", str(tmp_path / "no_hay"), "--salida", str(salida)])
    assert codigo == 1
    assert not salida.exists()


def test_sin_pytorch_termina_con_codigo_3(con_sinteticas, monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cli, "_torch_disponible", lambda: False)
    salida = tmp_path / "resultados"
    assert ejecutar(con_sinteticas, salida) == 3
    assert "PyTorch" in capsys.readouterr().err
    assert not salida.exists()
