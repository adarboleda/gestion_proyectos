"""Grupos de corridas emparejadas: gemelas ATWS/TRIP_OK y LOCA/LOCAC de igual área."""
import pytest

from preparacion_pwr3l.descubrimiento import Corrida
from preparacion_pwr3l.grupos import formar_grupos
from preparacion_pwr3l.lectura import cargar_corridas


def _corrida(rid, clase, area=None, gemela=None):
    return Corrida(rid, clase, "auto", f"auto/{rid}_{clase}/plotdata.csv", area=area, gemela=gemela, estado="usable")


@pytest.fixture(scope="module")
def grupos(arbol_pwr3l):
    usables = [c for c in cargar_corridas(arbol_pwr3l) if c.estado == "usable"]
    return {g.clave: g for g in formar_grupos(usables)}


def _ids(grupo):
    return [c.id for c in grupo.corridas]


def test_gemelas_atws_trip_ok_en_un_grupo(grupos):
    assert _ids(grupos["GEMELAS-R21-R59"]) == ["R21", "R59"]
    assert _ids(grupos["GEMELAS-R92-R100"]) == ["R92", "R100"]
    assert grupos["GEMELAS-R21-R59"].familia == "ATWS"


def test_loca_y_locac_de_igual_area_en_un_grupo(grupos):
    assert _ids(grupos["AREA-2000"]) == ["R09", "R77", "R03", "R07b"]  # incluye repeticiones de una clase
    assert _ids(grupos["AREA-50"]) == ["R10", "R76"]
    assert _ids(grupos["AREA-7700"]) == ["R88"]
    assert grupos["AREA-2000"].familia == "LOCA"


def test_norm_y_corridas_sin_pareja_en_grupos_propios(grupos):
    assert _ids(grupos["R01"]) == ["R01"] and grupos["R01"].familia == "NORM"
    assert _ids(grupos["R52"]) == ["R52"] and grupos["R52"].familia == "ATWS"


def test_gemela_corta_deja_a_la_otra_sola(grupos):
    assert _ids(grupos["GEMELAS-R48-R55"]) == ["R48"]


def test_cada_corrida_en_exactamente_un_grupo(arbol_pwr3l, grupos):
    usables = [c.id for c in cargar_corridas(arbol_pwr3l) if c.estado == "usable"]
    agrupadas = [c.id for g in grupos.values() for c in g.corridas]
    assert sorted(agrupadas) == sorted(usables) and len(agrupadas) == len(set(agrupadas))


def test_independiente_del_orden_de_entrada():
    corridas = [_corrida("R41", "LOCA", area=5), _corrida("R46", "LOCAC", area=5), _corrida("R31", "NORM")]
    a = [(g.clave, _ids(g)) for g in formar_grupos(corridas)]
    b = [(g.clave, _ids(g)) for g in formar_grupos(corridas[::-1])]
    assert a == b


def test_solo_acepta_corridas_usables():
    corta = _corrida("R55", "TRIP_OK", gemela="R48")
    corta.estado = "corta"
    with pytest.raises(ValueError):
        formar_grupos([corta])
