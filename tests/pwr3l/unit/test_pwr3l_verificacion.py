"""Pruebas de la verificación independiente de fuga del reparto PWR 3L (004, historia 3)."""
import pytest

from preparacion_pwr3l.grupos import Grupo, formar_grupos
from preparacion_pwr3l.particion import repartir
from preparacion_pwr3l.verificacion import ErrorFuga, verificar_reparto


def preparar(fabricar):
    corridas = fabricar.variadas()
    reparto = repartir(formar_grupos(corridas))
    return corridas, reparto, {c.id: c for c in corridas}


def otro_conjunto(conjunto):
    return {"train": "test", "val": "train", "test": "train"}[conjunto]


def mover(reparto, corrida, destino):
    origen = reparto.conjunto_de_corrida[corrida.id]
    reparto.corridas[origen].remove(corrida)
    reparto.corridas[destino].append(corrida)


def violaciones(corridas, reparto):
    with pytest.raises(ErrorFuga) as error:
        verificar_reparto(corridas, reparto)
    return error.value


def test_un_reparto_correcto_no_tiene_violaciones(fabricar):
    corridas, reparto, _ = preparar(fabricar)
    verificar_reparto(corridas, reparto)


def test_corrida_en_dos_conjuntos(fabricar):
    corridas, reparto, por_id = preparar(fabricar)
    norm = por_id["R01"]
    actual = reparto.conjunto_de_corrida["R01"]
    reparto.corridas[otro_conjunto(actual)].append(norm)
    error = violaciones(corridas, reparto)
    esperado = sorted([actual, otro_conjunto(actual)], key=("train", "val", "test").index)
    assert f"la corrida R01 está en {esperado[0]} y en {esperado[1]}" in error.violaciones


def test_area_partida(fabricar):
    corridas, reparto, por_id = preparar(fabricar)
    actual = reparto.conjunto_de_corrida["R04"]
    mover(reparto, por_id["R04"], otro_conjunto(actual))
    error = violaciones(corridas, reparto)
    linea = next(v for v in error.violaciones if v.startswith("el área de 50 cm² está partida"))
    assert f"R04 ({otro_conjunto(actual)})" in linea and f"R10 ({actual})" in linea


def test_gemelas_separadas(fabricar):
    corridas, reparto, por_id = preparar(fabricar)
    actual = reparto.conjunto_de_corrida["R59"]
    mover(reparto, por_id["R59"], otro_conjunto(actual))
    error = violaciones(corridas, reparto)
    assert any(v.startswith("las gemelas R21") and "R59" in v for v in error.violaciones)


@pytest.mark.parametrize("rid, estado", [("R63", "corta"), ("R07", "descartada"), ("R20", "ood")])
def test_corrida_excluida_dentro_de_un_conjunto(fabricar, rid, estado):
    corridas, reparto, por_id = preparar(fabricar)
    reparto.corridas["val"].append(por_id[rid])
    error = violaciones(corridas, reparto)
    assert f"la corrida {rid} ({estado}) está en val" in error.violaciones


def test_grupo_partido(fabricar):
    corridas, reparto, por_id = preparar(fabricar)
    actual = reparto.conjunto_de_corrida["R03"]
    mover(reparto, por_id["R03"], otro_conjunto(actual))
    error = violaciones(corridas, reparto)
    assert any(v.startswith("el grupo AREA-2000 está partido") for v in error.violaciones)


def test_corrida_usable_sin_conjunto(fabricar):
    corridas, reparto, por_id = preparar(fabricar)
    reparto.corridas[reparto.conjunto_de_corrida["R02"]].remove(por_id["R02"])
    error = violaciones(corridas, reparto)
    assert "la corrida usable R02 no está en ningún conjunto" in error.violaciones


def test_varias_violaciones_juntas(fabricar):
    corridas, reparto, por_id = preparar(fabricar)
    reparto.corridas["val"].append(por_id["R20"])
    reparto.corridas[reparto.conjunto_de_corrida["R02"]].remove(por_id["R02"])
    error = violaciones(corridas, reparto)
    assert len(error.violaciones) >= 2
    assert str(error).startswith("FUGA DE DATOS: ")


def test_repartir_nunca_devuelve_un_reparto_con_fuga(fabricar):
    por_id = {c.id: c for c in fabricar.variadas()}
    # Agrupación errónea a propósito: el área de 50 cm² repartida en dos grupos que el reparto separa
    grupos = [
        Grupo("AREA-50", "LOCA", [por_id["R10"], por_id["R77"]]),
        Grupo("AREA-50-bis", "LOCA", [por_id["R04"]]),
    ]
    with pytest.raises(ErrorFuga, match="50 cm"):
        repartir(grupos)
