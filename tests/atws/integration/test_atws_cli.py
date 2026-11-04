"""Extremo a extremo de evaluar-regla-atws con el árbol sintético."""
import csv
import io
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from regla_atws.cli import _crear_parser, main
from regla_atws.config import AVISO


@pytest.fixture(scope="module")
def evaluada(arbol_atws, tmp_path_factory):
    salida = tmp_path_factory.mktemp("res") / "resultados_regla_atws"
    codigo = main(["--origen", str(arbol_atws), "--salida", str(salida)])
    return codigo, salida


def _filas(salida):
    return list(csv.DictReader(io.StringIO((salida / "evaluacion.csv").read_text(encoding="utf-8"))))


def test_codigo_cero_y_artefactos(evaluada):
    codigo, salida = evaluada
    assert codigo == 0
    assert (salida / "regla.json").is_file() and (salida / "evaluacion.csv").is_file()


def test_una_fila_por_corrida_usable_con_su_conjunto(evaluada, ayudantes_atws):
    _, salida = evaluada
    filas = _filas(salida)
    assert len(filas) == ayudantes_atws.NUMERO_CORRIDAS
    assert len({f["id"] for f in filas}) == len(filas)
    assert {f["conjunto"] for f in filas} == {"train", "val", "test"}


def test_todos_los_atws_detectados_y_ninguna_falsa_alarma(evaluada, ayudantes_atws):
    _, salida = evaluada
    for fila in _filas(salida):
        esperado = "posible ATWS" if fila["id"] in ayudantes_atws.IDS_ATWS else "sin ATWS"
        assert fila["recomendacion"] == esperado, fila
        assert fila["acierto"] == "True"


def test_extraccion_de_barras_por_alto_flujo(evaluada):
    _, salida = evaluada
    fila = next(f for f in _filas(salida) if f["id"] == "R96")
    assert fila["fuente_senal"] == "alto flujo" and fila["tipo_senal"] == "scram high flux"


def test_regla_calibrada_con_entrenamiento_y_aviso(evaluada):
    _, salida = evaluada
    regla = json.loads((salida / "regla.json").read_text(encoding="utf-8"))
    assert regla["calibrada_con"] == "train" and regla["espera_s"] == 2.0
    assert regla["retardos_s"]["turbine trip"] == 5.0
    assert regla["margen"]["minimo_atws_pct"] > regla["umbral_pwnt_pct"] > regla["margen"]["maximo_no_atws_pct"]
    assert regla["aviso"] == AVISO


def test_cambiar_validacion_y_prueba_no_cambia_la_regla(arbol_atws, copia_atws, evaluada, ayudantes_atws, tmp_path):
    _, salida = evaluada
    conjuntos = {f["id"]: (f["conjunto"], f["clase"]) for f in _filas(salida)}
    for rid, (conjunto, clase) in conjuntos.items():
        if conjunto != "train":
            ayudantes_atws.cambiar_pwnt(copia_atws, f"{rid}_{clase}", np.full(ayudantes_atws.FILAS, 50.0))
    otra = tmp_path / "otra"
    assert main(["--origen", str(copia_atws), "--salida", str(otra)]) == 0
    assert (otra / "regla.json").read_bytes() == (salida / "regla.json").read_bytes()


def test_reproducible_byte_a_byte(arbol_atws, evaluada, tmp_path):
    _, salida = evaluada
    assert main(["--origen", str(arbol_atws), "--salida", str(tmp_path / "b")]) == 0
    for archivo in salida.iterdir():
        assert (tmp_path / "b" / archivo.name).read_bytes() == archivo.read_bytes(), archivo.name


def test_sin_registro_de_eventos_codigo_1_sin_salida(copia_atws, tmp_path, capsys):
    (copia_atws / "auto" / "R54_TRIP_OK" / "transientlist.dat").unlink()
    assert main(["--origen", str(copia_atws), "--salida", str(tmp_path / "s")]) == 1
    assert "auto/R54_TRIP_OK" in capsys.readouterr().err
    assert not (tmp_path / "s").exists()


def test_origen_sin_cambios(copia_atws, ayudantes_atws, tmp_path):
    antes = ayudantes_atws.hash_arbol(copia_atws)
    assert main(["--origen", str(copia_atws), "--salida", str(tmp_path / "s")]) == 0
    assert ayudantes_atws.hash_arbol(copia_atws) == antes


def test_valores_por_defecto():
    argumentos = _crear_parser().parse_args([])
    assert argumentos.origen == "../IA-Nuclear/PWR 3L"
    assert argumentos.salida == "resultados_regla_atws" and argumentos.semilla == 42


def test_python_m(arbol_atws, tmp_path):
    raiz = Path(__file__).resolve().parents[3]
    resultado = subprocess.run(
        [sys.executable, "-m", "regla_atws", "--origen", str(arbol_atws), "--salida", str(tmp_path / "s")],
        cwd=raiz, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert resultado.returncode == 0, resultado.stderr


def test_resumen_y_reporte_impreso(arbol_atws, tmp_path, capsys):
    from regla_atws.reporte import SECCIONES

    assert main(["--origen", str(arbol_atws), "--salida", str(tmp_path / "s")]) == 0
    texto = capsys.readouterr().out
    assert [texto.index(f"== {s} ==") for s in SECCIONES] == sorted(texto.index(f"== {s} ==") for s in SECCIONES)
    resumen = json.loads((tmp_path / "s" / "resumen.json").read_text(encoding="utf-8"))
    assert resumen["aviso"] == AVISO and resumen["errores"] == []
    assert sum(c["total"] for c in resumen["por_conjunto"].values()) == 42  # 10 NORM + 10 LOCA/LOCAC + 22 ATWS/TRIP_OK
