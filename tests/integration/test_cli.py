"""Pruebas de extremo a extremo de la línea de órdenes sobre un dataset sintético."""
import numpy as np
import pytest

from preparacion_datos.cli import main

CONJUNTOS = ("train", "val", "test")
ARTEFACTOS = (
    [f"{prefijo}_{c}.npy" for prefijo in ("X", "y") for c in CONJUNTOS]
    + ["scaler_mean.npy", "scaler_std.npy"]
)


@pytest.fixture(autouse=True)
def sin_referencia_externa(tmp_path, monkeypatch):
    """Ejecuta desde un directorio donde `../IA-Nuclear/...` no existe."""
    carpeta = tmp_path / "trabajo"
    carpeta.mkdir()
    monkeypatch.chdir(carpeta)


def ejecutar(origen, salida, *extra):
    return main(["--origen", str(origen), "--salida", str(salida), *extra])


def test_ejecucion_correcta_escribe_los_artefactos_con_forma_y_tipo(origen_sintetico, tmp_path):
    salida = tmp_path / "salida"
    assert ejecutar(origen_sintetico, salida) == 0
    for nombre in ARTEFACTOS:
        assert (salida / nombre).is_file(), nombre
    tamanos = {"train": 142, "val": 30, "test": 30}
    for c, n in tamanos.items():
        x, y = np.load(salida / f"X_{c}.npy"), np.load(salida / f"y_{c}.npy")
        assert x.shape == (n, 150, 12) and x.dtype == np.float32
        assert y.shape == (n,) and y.dtype == np.int64
        assert set(np.unique(y)) <= {0, 1, 2, 3}
    for nombre in ("scaler_mean.npy", "scaler_std.npy"):
        parametros = np.load(salida / nombre)
        assert parametros.shape == (12,) and parametros.dtype == np.float64


@pytest.mark.parametrize(
    "defecto, causa",
    [
        ("columna", "falta la variable"),
        ("texto", "valor no numérico"),
        ("vacio", "valor faltante"),
        ("infinito", "valor no finito"),
        ("corto", "menos de 150 pasos"),
    ],
)
def test_archivo_defectuoso_detiene_sin_escribir_ningun_conjunto(
    origen_sintetico, ayudas, tmp_path, capsys, defecto, causa
):
    ruta = origen_sintetico / "LOCAC" / "12.csv"
    if defecto == "columna":
        ayudas.quitar_columna(ruta, "DNBR")
    elif defecto == "texto":
        ayudas.poner_valor(ruta, "DNBR", 30, "abc")
    elif defecto == "vacio":
        ayudas.poner_valor(ruta, "DNBR", 30, "")
    elif defecto == "infinito":
        ayudas.poner_valor(ruta, "DNBR", 30, "inf")
    else:
        ayudas.truncar(ruta, 149)
    salida = tmp_path / "salida"
    assert ejecutar(origen_sintetico, salida) == 1
    error = capsys.readouterr().err
    assert "LOCAC/12.csv" in error
    assert causa in error
    assert not salida.exists()


def test_archivo_defectuoso_deja_intacta_una_salida_previa(origen_sintetico, ayudas, tmp_path, capsys):
    salida = tmp_path / "salida"
    assert ejecutar(origen_sintetico, salida) == 0
    antes = ayudas.contenido_directorio(salida)
    ayudas.quitar_columna(origen_sintetico / "LOCA" / "3.csv", "P")
    assert ejecutar(origen_sintetico, salida) == 1
    assert "LOCA/3.csv" in capsys.readouterr().err
    assert ayudas.contenido_directorio(salida) == antes


def test_normal_y_atws_aparecen_solo_en_entrenamiento(origen_sintetico, tmp_path):
    salida = tmp_path / "salida"
    assert ejecutar(origen_sintetico, salida) == 0
    y_train, y_val, y_test = (np.load(salida / f"y_{c}.npy") for c in CONJUNTOS)
    assert not np.isin(y_val, (0, 3)).any()
    assert not np.isin(y_test, (0, 3)).any()
    assert (y_train == 0).sum() == 1
    assert (y_train == 3).sum() == 1


def test_dos_ejecuciones_producen_archivos_identicos(origen_sintetico, ayudas, tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    assert ejecutar(origen_sintetico, a) == 0
    assert ejecutar(origen_sintetico, b) == 0
    assert ayudas.contenido_directorio(a) == ayudas.contenido_directorio(b)


def test_los_csv_de_origen_no_cambian(origen_sintetico, ayudas, tmp_path):
    antes = ayudas.hash_origen(origen_sintetico)
    assert ejecutar(origen_sintetico, tmp_path / "salida") == 0
    assert ayudas.hash_origen(origen_sintetico) == antes


def test_salida_previa_se_reemplaza_sin_tocar_archivos_ajenos(origen_sintetico, tmp_path):
    salida = tmp_path / "salida"
    salida.mkdir()
    (salida / "X_train.npy").write_bytes(b"obsoleto")
    (salida / "notas.txt").write_text("archivo ajeno")
    assert ejecutar(origen_sintetico, salida) == 0
    assert (salida / "notas.txt").read_text() == "archivo ajeno"
    assert np.load(salida / "X_train.npy").shape == (142, 150, 12)
