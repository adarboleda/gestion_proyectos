"""Informe del Hito 1 con los resultados reales del repositorio (se omite si no se han generado)."""
import json
from pathlib import Path

import pytest

from informe_hito1.cli import main
from informe_hito1.config import FUENTES

RAIZ = Path(__file__).resolve().parents[3]
RUTAS = {clave: RAIZ / fuente["carpeta"] for clave, fuente in FUENTES.items()}
DISPONIBLE = all((RUTAS[c] / n).is_file() for c, f in FUENTES.items() for n, _ in f["archivos"].values())

pytestmark = pytest.mark.skipif(not DISPONIBLE, reason="faltan los resultados reales (ver specs/007-hito1-resultados/quickstart.md)")


def _leer(clave, nombre):
    return json.loads((RUTAS[clave] / nombre).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def informe(tmp_path_factory):
    salida = tmp_path_factory.mktemp("hito1") / "informe"
    argumentos = [a for clave, ruta in RUTAS.items() for a in (f"--{clave}", str(ruta))] + ["--salida", str(salida)]
    assert main(argumentos) == 0
    return json.loads((salida / "hito1.json").read_text(encoding="utf-8")), (salida / "hito1.md").read_text(encoding="utf-8")


def test_metas_del_hito_iguales_a_008(informe):
    hito, texto = informe
    tiempos = _leer("tiempos", "tiempos.json")["metas"]
    metas = {m["id"]: m for m in hito["metas"]}
    assert metas["KAN-25 diagnóstico ≤ 10 s"]["valor"] == tiempos["diagnostico_10s"]["valor"]
    assert metas["KAN-25 ATWS ≤ 3 s"]["valor"] == tiempos["atws_3s"]["valor"]
    assert tiempos["diagnostico_10s"]["valor"] in texto


def test_matriz_y_abstencion_iguales_a_011(informe):
    hito, texto = informe
    prueba = _leer("diagnostico", "evaluacion_diagnostico.json")["prueba"]
    assert hito["diagnostico"]["prueba"]["matriz"] == prueba["matriz_confusion_3x4"]
    assert hito["diagnostico"]["prueba"]["tasa_abstencion"] == prueba["tasa_abstencion"]
    fila = "| NORM | " + " | ".join(str(v) for v in prueba["matriz_confusion_3x4"][0]) + " |"
    assert fila in texto


def test_regla_y_etapa2_iguales_a_sus_fuentes(informe):
    hito, _ = informe
    assert hito["regla"]["por_conjunto"] == _leer("regla", "resumen.json")["por_conjunto"]
    assert hito["etapa2"]["cobertura"] == _leer("etapa2", "reporte.json")["global"]["cobertura"]


def test_sha256_de_las_seis_fuentes(informe):
    hito, _ = informe
    assert len(hito["fuentes"]) == 6
