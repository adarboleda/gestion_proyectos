"""Fixtures del tiempo de detección (008): árbol de fallas sintético y modelo de 005 entrenado en sintético."""
from types import SimpleNamespace

import pytest

from ayudas_tiempo import cargar_sinteticas_etapa1, escribir_arbol_fallas


@pytest.fixture
def arbol_fallas(tmp_path):
    return escribir_arbol_fallas(tmp_path / "PWR 3L")


@pytest.fixture(scope="session")
def modelo_sintetico(tmp_path_factory):
    """Modelo de 005 entrenado (4 épocas) con las corridas sintéticas y la semilla 42."""
    pytest.importorskip("torch")
    import clasificador_etapa1.cli as cli_etapa1

    sinteticas = cargar_sinteticas_etapa1()
    corridas, inicios = sinteticas.construir_sinteticas()
    salida = tmp_path_factory.mktemp("modelo_etapa1") / "etapa1"
    with pytest.MonkeyPatch.context() as parche:
        parche.setattr(cli_etapa1, "cargar_corridas", lambda origen: corridas)
        parche.setattr(cli_etapa1, "inicios_evento", lambda origen, lista: dict(inicios))
        codigo = cli_etapa1.main(["--origen", "sintetico", "--salida", str(salida), "--epocas", "4"])
    assert codigo == 0
    return SimpleNamespace(ruta=salida, construir=sinteticas.construir_sinteticas)
