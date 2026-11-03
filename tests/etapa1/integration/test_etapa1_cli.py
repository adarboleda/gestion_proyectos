"""Pruebas del comando entrenar-etapa1 con corridas sintéticas (005)."""
import json

import numpy as np
import pytest

torch = pytest.importorskip("torch")

import clasificador_etapa1.cli as cli  # noqa: E402
from preparacion_pwr3l.escalado import ajustar_escalador  # noqa: E402


@pytest.fixture
def con_sinteticas(sinteticas, monkeypatch):
    monkeypatch.setattr(cli, "cargar_corridas", lambda origen: sinteticas.corridas)
    monkeypatch.setattr(cli, "inicios_evento", lambda origen, corridas: dict(sinteticas.inicios))
    return sinteticas


def ejecutar(salida, *extra):
    return cli.main(["--origen", "no-se-usa", "--salida", str(salida), "--epocas", "3", *extra])


def test_publica_modelo_y_configuracion(con_sinteticas, tmp_path):
    salida = tmp_path / "etapa1"
    assert ejecutar(salida) == 0
    assert (salida / "modelo.pt").is_file()
    modelo = json.loads((salida / "modelo.json").read_text(encoding="utf-8"))
    for clave in ("familias", "variables", "ventana_s", "tau_min_s", "horizonte_entrenamiento_s", "umbral",
                  "confirmacion_s", "hiperparametros", "semilla", "pesos_clase", "escalador", "historial",
                  "mejor_epoca", "corridas", "version", "entorno"):
        assert clave in modelo, clave
    assert modelo["familias"] == ["NORM", "LOCA", "TRANS"]
    assert len(modelo["variables"]) == 26 and len(modelo["pesos_clase"]) == 3


def test_corridas_sin_repetir_y_escalador_de_entrenamiento(con_sinteticas, tmp_path):
    salida = tmp_path / "etapa1"
    assert ejecutar(salida) == 0
    modelo = json.loads((salida / "modelo.json").read_text(encoding="utf-8"))
    conjuntos = [set(modelo["corridas"][c]) for c in ("train", "val", "test")]
    assert not (conjuntos[0] & conjuntos[1] or conjuntos[0] & conjuntos[2] or conjuntos[1] & conjuntos[2])
    por_id = {c.id: c for c in con_sinteticas.corridas}
    x_train = np.stack([por_id[r].serie[:, :26] for r in modelo["corridas"]["train"]])
    esperado = ajustar_escalador(x_train)
    np.testing.assert_allclose(modelo["escalador"]["media"], esperado.media)
    np.testing.assert_allclose(modelo["escalador"]["escala"], esperado.escala)


def test_dos_ejecuciones_con_la_misma_semilla_son_identicas(con_sinteticas, tmp_path):
    assert ejecutar(tmp_path / "a") == 0
    assert ejecutar(tmp_path / "b") == 0
    a = json.loads((tmp_path / "a" / "modelo.json").read_text(encoding="utf-8"))
    b = json.loads((tmp_path / "b" / "modelo.json").read_text(encoding="utf-8"))
    assert a == b


def test_reentrenar_reemplaza_sin_tocar_otros_archivos(con_sinteticas, tmp_path):
    salida = tmp_path / "etapa1"
    salida.mkdir()
    (salida / "notas.txt").write_text("mío", encoding="utf-8")
    (salida / "modelo.json").write_text("viejo", encoding="utf-8")
    assert ejecutar(salida) == 0
    assert (salida / "notas.txt").read_text(encoding="utf-8") == "mío"
    assert json.loads((salida / "modelo.json").read_text(encoding="utf-8"))["familias"] == ["NORM", "LOCA", "TRANS"]


def test_evento_sin_inicio_termina_con_codigo_1(sinteticas, monkeypatch, tmp_path, capsys):
    from preparacion_pwr3l.descubrimiento import ErrorDatos

    def sin_inicio(origen, corridas):
        raise ErrorDatos("auto/R200_LOCA/plotdata.csv", "no se conoce el instante de inicio del evento")

    monkeypatch.setattr(cli, "cargar_corridas", lambda origen: sinteticas.corridas)
    monkeypatch.setattr(cli, "inicios_evento", sin_inicio)
    salida = tmp_path / "etapa1"
    assert ejecutar(salida) == 1
    assert "inicio del evento" in capsys.readouterr().err
    assert not salida.exists()


def test_fuga_en_el_reparto_termina_con_codigo_1(con_sinteticas, monkeypatch, tmp_path, capsys):
    from preparacion_pwr3l.particion import repartir as repartir_real

    def con_fuga(grupos, semilla=42):
        reparto = repartir_real(grupos, semilla)
        reparto.corridas["test"].append(reparto.corridas["train"][0])
        return reparto

    monkeypatch.setattr(cli, "repartir", con_fuga)
    salida = tmp_path / "etapa1"
    assert ejecutar(salida) == 1
    assert "FUGA DE DATOS" in capsys.readouterr().err
    assert not salida.exists()


def test_sin_pytorch_termina_con_codigo_3(con_sinteticas, monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cli, "_torch_disponible", lambda: False)
    salida = tmp_path / "etapa1"
    assert ejecutar(salida) == 3
    assert "PyTorch" in capsys.readouterr().err
    assert not salida.exists()


def test_publica_e_imprime_el_reporte(con_sinteticas, tmp_path, capsys):
    salida = tmp_path / "etapa1"
    assert ejecutar(salida) == 0
    impreso = capsys.readouterr().out
    reporte = json.loads((salida / "reporte.json").read_text(encoding="utf-8"))
    assert (salida / "reporte.txt").read_text(encoding="utf-8").strip() == impreso.strip()
    modelo = json.loads((salida / "modelo.json").read_text(encoding="utf-8"))
    por_id = {c.id: c for c in con_sinteticas.corridas}
    eventos_prueba = [r for r in modelo["corridas"]["test"] if por_id[r].clase != "NORM"]
    assert sorted(d["corrida"] for d in reporte["deteccion"]) == sorted(eventos_prueba)
    assert sum(map(sum, reporte["global"]["matriz"])) == modelo["muestras"]["test"]
    for texto in ("consultivo", "Horizonte", "Tiempo de confirmación", "Falsas alarmas", "Metas"):
        assert texto in impreso, texto
