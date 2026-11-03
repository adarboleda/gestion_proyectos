"""Extremo a extremo con el árbol sintético: conjuntos sin fuga, 300 pasos y cinco clases."""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from preparacion_pwr3l.cli import _crear_parser, main
from preparacion_pwr3l.config import CONJUNTOS, VARIABLES_ENTRADA
from preparacion_pwr3l.lectura import cargar_corridas

GEMELAS_DEL_ARBOL = [("R21", "R59"), ("R47", "R54"), ("R49", "R56"), ("R50", "R57"), ("R51", "R58"), ("R91", "R99"), ("R92", "R100")]
AREA_2000 = {"R09", "R77", "R03", "R07b"}


@pytest.fixture(scope="module")
def preparada(arbol_pwr3l, tmp_path_factory):
    salida = tmp_path_factory.mktemp("salida") / "data_processed_pwr3l"
    codigo = main(["--origen", str(arbol_pwr3l), "--salida", str(salida)])
    return codigo, salida


def _cargar(salida, nombre):
    return np.load(salida / nombre)


def _ids_por_conjunto(origen, salida):
    """Ids de cada conjunto reconstruidos comparando las filas sin escalar con las corridas."""
    usables = [c for c in cargar_corridas(origen) if c.estado == "usable"]
    media = _cargar(salida, "scaler_mean.npy")
    escala = _cargar(salida, "scaler_std.npy")
    ids = {}
    for conjunto in CONJUNTOS:
        x = _cargar(salida, f"X_{conjunto}.npy").astype(np.float64) * escala + media
        ids[conjunto] = []
        for fila in x:
            coincide = [c.id for c in usables if np.allclose(c.serie[:, :26], fila, rtol=1e-5, atol=1e-3)]
            assert len(coincide) == 1
            ids[conjunto].append(coincide[0])
    return ids


def test_codigo_cero_y_artefactos(preparada):
    codigo, salida = preparada
    assert codigo == 0
    for conjunto in CONJUNTOS:
        assert (salida / f"X_{conjunto}.npy").is_file() and (salida / f"y_{conjunto}.npy").is_file()
    assert (salida / "scaler_mean.npy").is_file() and (salida / "scaler_std.npy").is_file()


def test_formas_tipos_y_etiquetas(preparada):
    _, salida = preparada
    total = 0
    for conjunto in CONJUNTOS:
        x, y = _cargar(salida, f"X_{conjunto}.npy"), _cargar(salida, f"y_{conjunto}.npy")
        assert x.shape[1:] == (300, len(VARIABLES_ENTRADA)) and x.dtype == np.float32
        assert y.dtype == np.int64 and len(y) == len(x) and set(y.tolist()) <= {0, 1, 2, 3, 4}
        total += len(y)
    assert total == 45  # 50 corridas − 2 descartadas (R07, R27) − 2 OOD (R20, R64) − 1 corta (R55)
    assert _cargar(salida, "scaler_mean.npy").shape == (26,)


def test_sin_fuga_y_grupos_en_un_solo_conjunto(arbol_pwr3l, preparada):
    _, salida = preparada
    ids = _ids_por_conjunto(arbol_pwr3l, salida)
    vistos = [i for conjunto in CONJUNTOS for i in ids[conjunto]]
    assert len(vistos) == len(set(vistos))
    assert not set(vistos) & {"R07", "R27", "R20", "R64", "R55"}
    conjunto_de = {i: c for c in CONJUNTOS for i in ids[c]}
    for a, b in GEMELAS_DEL_ARBOL:
        assert conjunto_de[a] == conjunto_de[b]
    assert len({conjunto_de[i] for i in AREA_2000}) == 1


def test_escalador_ajustado_solo_con_entrenamiento(arbol_pwr3l, preparada):
    _, salida = preparada
    ids = _ids_por_conjunto(arbol_pwr3l, salida)
    series = {c.id: c.serie for c in cargar_corridas(arbol_pwr3l) if c.estado == "usable"}
    filas = np.concatenate([series[i][:, :26] for i in ids["train"]])
    assert np.allclose(_cargar(salida, "scaler_mean.npy"), filas.mean(axis=0), rtol=1e-12, atol=0)


def test_reproducible_byte_a_byte(arbol_pwr3l, preparada, tmp_path):
    _, salida = preparada
    otra = tmp_path / "otra"
    assert main(["--origen", str(arbol_pwr3l), "--salida", str(otra)]) == 0
    for archivo in salida.iterdir():
        assert (otra / archivo.name).read_bytes() == archivo.read_bytes(), archivo.name


def test_origen_sin_cambios(copia_pwr3l, ayudantes, tmp_path):
    antes = ayudantes.hash_arbol(copia_pwr3l)
    assert main(["--origen", str(copia_pwr3l), "--salida", str(tmp_path / "s")]) == 0
    assert ayudantes.hash_arbol(copia_pwr3l) == antes


def test_archivo_defectuoso_codigo_1_sin_salida(copia_pwr3l, ayudantes, tmp_path, capsys):
    ayudantes.corromper_csv(copia_pwr3l / "auto" / "R44_LOCA" / "plotdata.csv", "quitar", "DNBR")
    salida = tmp_path / "s"
    assert main(["--origen", str(copia_pwr3l), "--salida", str(salida)]) == 1
    error = capsys.readouterr().err
    assert "auto/R44_LOCA/plotdata.csv" in error and "falta la variable" in error
    assert not salida.exists()


def test_reejecucion_sobre_salida_previa(arbol_pwr3l, tmp_path):
    salida = tmp_path / "s"
    salida.mkdir()
    (salida / "ajeno.txt").write_text("no tocar", encoding="utf-8")
    np.save(salida / "X_train.npy", np.zeros(3))
    assert main(["--origen", str(arbol_pwr3l), "--salida", str(salida)]) == 0
    assert (salida / "ajeno.txt").read_text(encoding="utf-8") == "no tocar"
    assert np.load(salida / "X_train.npy").shape[1:] == (300, 26)


def test_valores_por_defecto_separados_de_nppad():
    argumentos = _crear_parser().parse_args([])
    assert argumentos.origen == "../IA-Nuclear/PWR 3L"
    assert argumentos.salida == "data_processed_pwr3l"
    assert argumentos.semilla == 42


def test_reporte_impreso_con_las_nueve_secciones(arbol_pwr3l, tmp_path, capsys):
    from preparacion_pwr3l.reporte import SECCIONES

    assert main(["--origen", str(arbol_pwr3l), "--salida", str(tmp_path / "s")]) == 0
    texto = capsys.readouterr().out
    posiciones = [texto.index(f"== {seccion} ==") for seccion in SECCIONES]
    assert posiciones == sorted(posiciones)
    assert "R55" in texto and "metadata.json" in texto


def test_metadata_cumple_el_contrato(arbol_pwr3l, preparada, ayudantes):
    import json

    from preparacion_pwr3l.config import CLASES

    _, salida = preparada
    metadata = json.loads((salida / "metadata.json").read_text(encoding="utf-8"))
    claves = {
        "version_formato", "planta", "origen", "semilla", "proporciones", "pasos_por_muestra", "paso_segundos",
        "clases", "variables_entrada", "variables_margen", "corridas_encontradas", "conteos_muestras", "totales",
        "corridas", "grupos", "excluidas", "escalador", "advertencias", "limitaciones",
    }
    assert set(metadata) == claves
    assert metadata["clases"] == CLASES and metadata["pasos_por_muestra"] == 300 and metadata["paso_segundos"] == 1
    assert metadata["variables_entrada"] == VARIABLES_ENTRADA
    assert sum(sum(v.values()) for v in metadata["corridas_encontradas"].values()) == ayudantes.NUMERO_CORRIDAS
    assert {e["id"] for e in metadata["excluidas"]} == ayudantes.IDS_DESCARTADAS | ayudantes.IDS_OOD | ayudantes.IDS_CORTAS
    assert metadata["escalador"]["ajustado_con"] == "train"
    # la fila i de cada conjunto es la corrida metadata.corridas[c][i]
    ids = _ids_por_conjunto(arbol_pwr3l, salida)
    clase_de = {c.id: c.clase for c in cargar_corridas(arbol_pwr3l)}
    for conjunto in CONJUNTOS:
        assert metadata["corridas"][conjunto] == ids[conjunto]
        y = _cargar(salida, f"y_{conjunto}.npy").tolist()
        assert y == [CLASES[clase_de[i]] for i in ids[conjunto]]
        assert metadata["totales"][conjunto] == len(y)
        agrupadas = [i for lista in metadata["grupos"][conjunto].values() for i in lista]
        assert sorted(agrupadas) == sorted(ids[conjunto])


def test_python_m(arbol_pwr3l, tmp_path):
    raiz = Path(__file__).resolve().parents[3]
    resultado = subprocess.run(
        [sys.executable, "-m", "preparacion_pwr3l", "--origen", str(arbol_pwr3l), "--salida", str(tmp_path / "s")],
        cwd=raiz, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert resultado.returncode == 0, resultado.stderr
    assert (tmp_path / "s" / "X_train.npy").is_file()
