"""Reproducción causal de la Etapa 1 con el modelo guardado y su verificación (US2, FR-004, FR-005, FR-007)."""
import json
import shutil

import numpy as np
import pytest

pytest.importorskip("torch")

from clasificador_etapa1.prediccion import cargar  # noqa: E402
from preparacion_pwr3l.grupos import formar_grupos  # noqa: E402
from preparacion_pwr3l.particion import repartir  # noqa: E402
from tiempo_deteccion.reproduccion import ErrorModelo, familias_confirmadas, reproducir, verificar_modelo  # noqa: E402


@pytest.fixture
def reparto_sintetico(modelo_sintetico):
    corridas, _ = modelo_sintetico.construir()
    return repartir(formar_grupos(corridas), 42)


def test_verificar_modelo_acepta_el_del_reparto(modelo_sintetico, reparto_sintetico):
    configuracion = verificar_modelo(modelo_sintetico.ruta, reparto_sintetico)
    assert configuracion["corridas"]["test"] == [c.id for c in reparto_sintetico.corridas["test"]]


def test_verificar_modelo_rechaza_otro_reparto(modelo_sintetico):
    corridas, _ = modelo_sintetico.construir()
    otro = repartir(formar_grupos(corridas), 7)
    with pytest.raises(ErrorModelo, match="no corresponde"):
        verificar_modelo(modelo_sintetico.ruta, otro)


def test_verificar_modelo_rechaza_corridas_alteradas(modelo_sintetico, reparto_sintetico, tmp_path):
    copia = tmp_path / "modelo"
    shutil.copytree(modelo_sintetico.ruta, copia)
    configuracion = json.loads((copia / "modelo.json").read_text(encoding="utf-8"))
    configuracion["corridas"]["test"] = configuracion["corridas"]["test"][1:]
    (copia / "modelo.json").write_text(json.dumps(configuracion), encoding="utf-8")
    with pytest.raises(ErrorModelo):
        verificar_modelo(copia, reparto_sintetico)


def test_verificar_modelo_inexistente(reparto_sintetico, tmp_path):
    with pytest.raises(ErrorModelo, match="no existe"):
        verificar_modelo(tmp_path / "no_hay", reparto_sintetico)


def test_reproducir_da_295_segundos_por_corrida(modelo_sintetico, reparto_sintetico):
    clasificador = cargar(modelo_sintetico.ruta)
    corridas = reparto_sintetico.corridas["test"]
    lineas = reproducir(clasificador, corridas, "test")
    assert list(lineas) == [c.id for c in corridas]
    for linea in lineas.values():
        assert linea.conjunto == "test"
        assert linea.tau.tolist() == list(range(5, 300))
        assert linea.probabilidades.shape == (295, 3)
        np.testing.assert_allclose(linea.probabilidades.sum(axis=1), 1.0, atol=1e-5)
        assert len(linea.confirmada) == 295


def test_reproducir_es_causal(modelo_sintetico, reparto_sintetico):
    clasificador = cargar(modelo_sintetico.ruta)
    corrida = reparto_sintetico.corridas["test"][0]
    antes = reproducir(clasificador, [corrida], "test")[corrida.id].probabilidades
    corrida.serie = corrida.serie.copy()
    corrida.serie[101:] += 5.0  # se alteran los datos posteriores a τ = 100
    despues = reproducir(clasificador, [corrida], "test")[corrida.id].probabilidades
    hasta = 100 - 5 + 1  # filas de τ = 5…100
    np.testing.assert_array_equal(antes[:hasta], despues[:hasta])
    assert not np.array_equal(antes[hasta:], despues[hasta:])


def test_familias_confirmadas_exige_dos_segundos_seguidos():
    p = np.array([
        [0.9, 0.05, 0.05],  # NORM una vez
        [0.9, 0.05, 0.05],  # NORM dos veces → confirmada
        [0.1, 0.85, 0.05],  # LOCA una vez
        [0.1, 0.85, 0.05],  # LOCA dos veces → confirmada
        [0.1, 0.10, 0.80],  # TRANS una vez (≥ 0,80 justo)
        [0.4, 0.30, 0.30],  # ninguna
    ])
    assert familias_confirmadas(p, 0.80) == ["", "NORM", "", "LOCA", "", ""]
