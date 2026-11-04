"""Extremo a extremo con la carpeta PWR 3L real (se omite si no está disponible)."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from datos_reales import ruta_pwr3l
from preparacion_pwr3l.cli import main
from preparacion_pwr3l.config import CONJUNTOS, GEMELAS
from preparacion_pwr3l.descubrimiento import descubrir_corridas

ORIGEN = ruta_pwr3l()  # variable IANUCLEAR_DATOS o ../IA-Nuclear (tests/datos_reales.py)
CORTAS = {"R38": 295, "R41": 295, "R42": 289, "R43": 294, "R82": 299, "R91": 295, "R98": 299, "R55": 295, "R63": 295}
OOD = {"R20", "R64", "R65", "R66", "R107", "R108"}

pytestmark = pytest.mark.skipif(not ORIGEN.is_dir(), reason="carpeta PWR 3L no disponible")


@pytest.fixture(scope="module")
def preparada(tmp_path_factory, ayudantes_modulo):
    antes = ayudantes_modulo(ORIGEN)
    salida = tmp_path_factory.mktemp("real") / "data_processed_pwr3l"
    codigo = main(["--origen", str(ORIGEN), "--salida", str(salida)])
    metadata = json.loads((salida / "metadata.json").read_text(encoding="utf-8"))
    return codigo, salida, metadata, antes


def _hash_arbol(raiz: Path) -> str:
    resumen = hashlib.sha256()
    for ruta in sorted(raiz.rglob("*")):
        if ruta.is_file():
            resumen.update(ruta.relative_to(raiz).as_posix().encode())
            resumen.update(ruta.read_bytes())
    return resumen.hexdigest()


@pytest.fixture(scope="module")
def ayudantes_modulo():
    return _hash_arbol


def test_codigo_cero_y_conteos(preparada):
    codigo, _, metadata, _ = preparada
    assert codigo == 0
    encontradas = metadata["corridas_encontradas"]
    assert sum(sum(v.values()) for v in encontradas.values()) == 109
    assert sum(v["descartada"] for v in encontradas.values()) == 3
    assert encontradas["OOD"]["ood"] == 6
    for clase in ("NORM", "LOCA", "LOCAC", "ATWS", "TRIP_OK"):
        assert encontradas[clase]["usable"] + encontradas[clase]["corta"] == 20, clase
    assert sum(metadata["totales"].values()) == 91


def test_cortas_con_su_numero_de_filas(preparada):
    _, _, metadata, _ = preparada
    cortas = {e["id"]: e["detalle"] for e in metadata["excluidas"] if e["motivo"] == "corta"}
    assert set(cortas) == set(CORTAS)
    for rid, filas in CORTAS.items():
        assert f"tiene {filas} filas" in cortas[rid]


def test_descartadas_ood_y_r07b(preparada):
    _, _, metadata, _ = preparada
    excluidas = {e["id"]: e["motivo"] for e in metadata["excluidas"]}
    assert {r for r, m in excluidas.items() if m == "descartada"} == {"R07", "R27", "R28"}
    assert {r for r, m in excluidas.items() if m == "ood"} == OOD
    usadas = {i for c in CONJUNTOS for i in metadata["corridas"][c]}
    assert "R07b" in usadas and not usadas & (OOD | {"R07", "R27", "R28"} | set(CORTAS))


def test_tabla_de_gemelas_coincide_con_config_json():
    declaradas = {}
    for carpeta in (ORIGEN / "auto").glob("R*_*"):
        configuracion = carpeta / "config.json"
        if configuracion.is_file():
            gemela = json.loads(configuracion.read_text(encoding="utf-8-sig")).get("gemelo_de") or ""
            if gemela:
                declaradas[carpeta.name.split("_")[0]] = gemela
    tabla = {a: b for par in GEMELAS for a, b in (par, par[::-1])}
    assert declaradas and all(tabla.get(rid) == gemela for rid, gemela in declaradas.items())


def test_restricciones_de_grupo(preparada):
    _, salida, metadata, _ = preparada
    conjunto_de = {i: c for c in CONJUNTOS for i in metadata["corridas"][c]}
    assert len(conjunto_de) == 91
    for a, b in GEMELAS:
        if a in conjunto_de and b in conjunto_de:
            assert conjunto_de[a] == conjunto_de[b], (a, b)
    corridas = {c.id: c for c in descubrir_corridas(ORIGEN)}
    por_area = {}
    for rid, conjunto in conjunto_de.items():
        if corridas[rid].area is not None:
            por_area.setdefault(corridas[rid].area, set()).add(conjunto)
    assert all(len(conjuntos) == 1 for conjuntos in por_area.values())
    for conjunto in CONJUNTOS:
        assert np.load(salida / f"X_{conjunto}.npy").shape == (metadata["totales"][conjunto], 300, 26)


def test_origen_sin_cambios(preparada, ayudantes_modulo):
    *_, antes = preparada
    assert ayudantes_modulo(ORIGEN) == antes
