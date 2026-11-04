"""Pruebas de integración del comando entrenar-etapa2 con corridas sintéticas (009)."""
import json

import numpy as np
import pytest

torch = pytest.importorskip("torch")

import clasificador_etapa2.cli as cli  # noqa: E402
from clasificador_etapa2.canales import desviacion_pico  # noqa: E402
from clasificador_etapa2.entrenamiento import ajustar_escalador_canales  # noqa: E402
from tests.etapa2.conftest import COL  # noqa: E402


@pytest.fixture
def con_sinteticas(sinteticas, monkeypatch):
    monkeypatch.setattr(cli, "cargar_corridas", lambda origen: sinteticas.corridas)
    monkeypatch.setattr(cli, "inicios_evento", lambda origen, corridas: dict(sinteticas.inicios))
    monkeypatch.setattr(
        cli,
        "canales_corrida",
        lambda origen, corrida: np.column_stack([
            desviacion_pico(sinteticas.pwr[corrida.id]),
            desviacion_pico(corrida.serie[:, COL["PWNT"]]),
        ]),
    )
    return sinteticas


def ejecutar(salida, *extra):
    return cli.main(["--origen", "no-se-usa", "--salida", str(salida), "--epocas", "4", *extra])


def test_publica_los_cuatro_artefactos_y_configuracion(con_sinteticas, tmp_path):
    salida = tmp_path / "etapa2"
    assert ejecutar(salida) == 0
    for nombre in ("modelo.pt", "modelo.json", "reporte.json", "reporte.txt"):
        assert (salida / nombre).is_file(), nombre

    modelo = json.loads((salida / "modelo.json").read_text(encoding="utf-8"))
    for clave in (
        "clases", "canales", "ventana_s", "ventana_pico_s", "media_movil_s",
        "horizonte_entrenamiento_s", "umbral", "confirmacion_s", "hiperparametros",
        "semilla", "pesos_clase", "escalador", "historial", "mejor_epoca",
        "muestras", "corridas", "version", "entorno",
    ):
        assert clave in modelo, clave
    assert modelo["clases"] == ["LOCA", "LOCAC"]
    assert modelo["canales"] == ["PWR", "PWNT"]
    assert len(modelo["pesos_clase"]) == 2


def test_corridas_solo_loca_locac_sin_solape_y_escalador_de_entrenamiento(con_sinteticas, tmp_path):
    salida = tmp_path / "etapa2"
    assert ejecutar(salida) == 0
    modelo = json.loads((salida / "modelo.json").read_text(encoding="utf-8"))
    por_id = {c.id: c for c in con_sinteticas.corridas}
    conjuntos = [set(modelo["corridas"][c]) for c in ("train", "val", "test")]
    assert not (conjuntos[0] & conjuntos[1] or conjuntos[0] & conjuntos[2] or conjuntos[1] & conjuntos[2])
    for ids in conjuntos:
        for cid in ids:
            assert por_id[cid].clase in ("LOCA", "LOCAC")

    x_train = np.stack([
        np.column_stack([
            desviacion_pico(con_sinteticas.pwr[r]),
            desviacion_pico(por_id[r].serie[:, COL["PWNT"]]),
        ])
        for r in modelo["corridas"]["train"]
    ])
    esperado = ajustar_escalador_canales(x_train)
    np.testing.assert_allclose(modelo["escalador"]["media"], esperado.media)
    np.testing.assert_allclose(modelo["escalador"]["escala"], esperado.escala)

    reporte = json.loads((salida / "reporte.json").read_text(encoding="utf-8"))
    assert [c["corrida"] for c in reporte["corridas"]] == modelo["corridas"]["test"]


def test_dos_ejecuciones_con_misma_semilla_son_identicas(con_sinteticas, tmp_path):
    assert ejecutar(tmp_path / "a") == 0
    assert ejecutar(tmp_path / "b") == 0
    a = json.loads((tmp_path / "a" / "modelo.json").read_text(encoding="utf-8"))
    b = json.loads((tmp_path / "b" / "modelo.json").read_text(encoding="utf-8"))
    assert a == b


def test_reentrenar_reemplaza_solo_artefactos_propios(con_sinteticas, tmp_path):
    salida = tmp_path / "etapa2"
    salida.mkdir()
    ajeno = salida / "nota.txt"
    ajeno.write_text("conservar", encoding="utf-8")
    assert ejecutar(salida) == 0
    assert ajeno.read_text(encoding="utf-8") == "conservar"


def test_codigos_de_salida_sin_torch_y_error_de_datos(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "_torch_disponible", lambda: False)
    assert cli.main(["--origen", "no-existe", "--salida", str(tmp_path / "s")]) == 3

    monkeypatch.setattr(cli, "_torch_disponible", lambda: True)
    assert cli.main(["--origen", str(tmp_path / "no-existe"), "--salida", str(tmp_path / "s")]) == 1
