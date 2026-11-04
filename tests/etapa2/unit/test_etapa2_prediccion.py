"""Pruebas unitarias de la clasificación consultiva con el modelo guardado de Etapa 2 (009)."""
import json

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from clasificador_etapa1.modelo import BiLSTMEtapa1  # noqa: E402
from clasificador_etapa2.config import (  # noqa: E402
    AVISO,
    CANALES,
    CLASES,
    HIPERPARAMETROS,
    INCIERTO,
    NO_APLICA,
    UMBRAL,
    VENTANA_S,
)
from clasificador_etapa2.prediccion import cargar  # noqa: E402


def _guardar_modelo_prueba(carpeta, sesgo_loca: float):
    carpeta.mkdir(parents=True, exist_ok=True)
    hp = dict(HIPERPARAMETROS)
    modelo = BiLSTMEtapa1(entradas=2, unidades=hp["unidades"], capas=hp["capas"], dropout=hp["dropout"], clases=2)
    with torch.no_grad():
        modelo.salida.weight.zero_()
        modelo.salida.bias[:] = torch.tensor([sesgo_loca, 0.0])
    torch.save(modelo.state_dict(), carpeta / "modelo.pt")
    config = {
        "clases": list(CLASES),
        "canales": list(CANALES),
        "ventana_s": VENTANA_S,
        "umbral": UMBRAL,
        "hiperparametros": hp,
        "escalador": {"media": [0.0, 0.0], "escala": [1.0, 1.0], "filas_ajuste": 100},
    }
    (carpeta / "modelo.json").write_text(json.dumps(config), encoding="utf-8")


def test_clasificar_devuelve_rama_cuando_supera_umbral(tmp_path):
    _guardar_modelo_prueba(tmp_path, sesgo_loca=3.0)  # softmax([3, 0]) ≈ [0.952, 0.048]
    clf = cargar(tmp_path)
    serie = np.full((20, 2), 100.0)
    res = clf.clasificar(serie, familia_etapa1="LOCA")
    assert res["recomendacion"] == "LOCA"
    assert np.isclose(sum(res["probabilidades"].values()), 1.0)
    assert res["probabilidades"]["LOCA"] >= UMBRAL
    assert res["aviso"] == AVISO


def test_clasificar_se_abstiene_con_uncertain_bajo_080(tmp_path):
    _guardar_modelo_prueba(tmp_path, sesgo_loca=0.2)  # softmax([0.2, 0]) ≈ [0.55, 0.45] < 0.80
    clf = cargar(tmp_path)
    res = clf.clasificar(np.full((15, 2), 100.0), familia_etapa1="LOCA")
    assert res["recomendacion"] == INCIERTO
    assert np.isclose(sum(res["probabilidades"].values()), 1.0)
    assert res["aviso"] == AVISO


@pytest.mark.parametrize("familia", ["NORM", "TRANS", "INCIERTO", "UNCERTAIN"])
def test_clasificar_no_aplica_si_etapa1_no_es_loca(tmp_path, familia):
    _guardar_modelo_prueba(tmp_path, sesgo_loca=3.0)
    clf = cargar(tmp_path)
    res = clf.clasificar(np.full((10, 2), 100.0), familia_etapa1=familia)
    assert res["recomendacion"] == NO_APLICA
    assert res["probabilidades"] is None
    assert res["aviso"] == AVISO


def test_clasificar_rechaza_serie_vacia_o_forma_invalida(tmp_path):
    _guardar_modelo_prueba(tmp_path, sesgo_loca=3.0)
    clf = cargar(tmp_path)
    with pytest.raises(ValueError):
        clf.clasificar(np.empty((0, 2)), familia_etapa1="LOCA")
    with pytest.raises(ValueError):
        clf.clasificar(np.ones((10, 3)), familia_etapa1="LOCA")
    with pytest.raises(ValueError):
        clf.clasificar(np.ones(10), familia_etapa1="LOCA")

