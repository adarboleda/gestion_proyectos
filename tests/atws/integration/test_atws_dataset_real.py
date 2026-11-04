"""Regla de ATWS con la carpeta PWR 3L real (se omite si no está disponible)."""
import csv
import hashlib
import io
import json
from pathlib import Path

import pytest

from datos_reales import ruta_pwr3l
from regla_atws.cli import main

ORIGEN = ruta_pwr3l()

pytestmark = pytest.mark.skipif(not ORIGEN.is_dir(), reason="carpeta PWR 3L no disponible")


def _hash(raiz: Path) -> str:
    resumen = hashlib.sha256()
    for ruta in sorted(raiz.rglob("*")):
        if ruta.is_file():
            resumen.update(ruta.relative_to(raiz).as_posix().encode())
            resumen.update(ruta.read_bytes())
    return resumen.hexdigest()


@pytest.fixture(scope="module")
def evaluada(tmp_path_factory):
    antes = _hash(ORIGEN)
    salida = tmp_path_factory.mktemp("real") / "resultados_regla_atws"
    codigo = main(["--origen", str(ORIGEN), "--salida", str(salida)])
    filas = list(csv.DictReader(io.StringIO((salida / "evaluacion.csv").read_text(encoding="utf-8"))))
    regla = json.loads((salida / "regla.json").read_text(encoding="utf-8"))
    resumen = json.loads((salida / "resumen.json").read_text(encoding="utf-8"))
    return codigo, filas, regla, resumen, antes


def test_codigo_cero_y_91_corridas(evaluada):
    codigo, filas, *_ = evaluada
    assert codigo == 0 and len(filas) == 91
    assert [sum(f["conjunto"] == c for f in filas) for c in ("train", "val", "test")] == [63, 15, 13]
    assert sum(f["clase"] == "ATWS" for f in filas) == 18


def test_regla_separa_entrenamiento(evaluada):
    _, _, regla, resumen, _ = evaluada
    assert regla["margen"]["solape"] is False
    assert regla["margen"]["minimo_atws_pct"] > regla["umbral_pwnt_pct"] > regla["margen"]["maximo_no_atws_pct"]
    assert resumen["por_conjunto"]["train"]["falsas_alarmas"] == 0
    assert resumen["por_conjunto"]["train"]["atws_omitidos"] == 0


def test_todos_los_atws_detectados_dentro_de_la_meta(evaluada):
    _, filas, _, resumen, _ = evaluada
    atws = [f for f in filas if f["clase"] == "ATWS"]
    assert all(f["recomendacion"] == "posible ATWS" for f in atws)
    assert all(float(f["t_deteccion_demanda"]) <= 3.0 for f in atws)
    assert all(t["cumplen_meta"] == t["detectados"] for t in resumen["tiempos"].values())


def test_extraccion_de_barras_por_alto_flujo(evaluada):
    _, filas, *_ = evaluada
    r97 = next(f for f in filas if f["id"] == "R97")
    assert r97["fuente_senal"] == "alto flujo" and r97["recomendacion"] == "posible ATWS"


def test_falsas_alarmas_solo_por_tipos_no_vistos_en_entrenamiento(evaluada):
    """Con el reparto de 004 la única TRIP_OK de turbina usable (R54) queda en validación: su tipo no
    tiene retardo medido en entrenamiento y recibe el mayor de entrenamiento (2.5 s < 5 s reales)."""
    _, filas, regla, *_ = evaluada
    falsas = [f for f in filas if f["clase"] != "ATWS" and f["recomendacion"] == "posible ATWS"]
    assert all(f["retardo_por_defecto"] == "True" for f in falsas)
    assert "turbine trip" not in regla["retardos_s"]


def test_origen_sin_cambios(evaluada):
    *_, antes = evaluada
    assert _hash(ORIGEN) == antes
