"""Pruebas de la agrupación de corridas que no pueden separarse (004, historia 1)."""
import copy

import pytest

from preparacion_pwr3l.descubrimiento import ErrorDatos
from preparacion_pwr3l.grupos import Grupo, formar_grupos
from preparacion_pwr3l.lectura import cargar_corridas


def por_clave(grupos):
    return {g.clave: g for g in grupos}


def ids(grupo: Grupo):
    return [c.id for c in grupo.corridas]


def test_loca_y_locac_de_la_misma_area_van_en_un_grupo_con_sus_repeticiones(fabricar):
    grupos = por_clave(formar_grupos(fabricar.variadas()))
    assert sorted(ids(grupos["AREA-50"])) == ["R04", "R10", "R77"]
    assert sorted(ids(grupos["AREA-2000"])) == ["R03", "R09", "R15"]
    assert sorted(ids(grupos["AREA-200"])) == ["R05", "R11"]


def test_areas_distintas_forman_grupos_distintos(fabricar):
    grupos = por_clave(formar_grupos(fabricar.variadas()))
    assert ids(grupos["AREA-7700"]) == ["R08"]
    assert ids(grupos["AREA-8500"]) == ["R14"]
    assert ids(grupos["AREA-3000"]) == ["R80"]


def test_gemelas_usables_forman_un_grupo_en_orden_natural(fabricar):
    grupos = por_clave(formar_grupos(fabricar.variadas()))
    assert ids(grupos["GEMELAS-R21-R59"]) == ["R21", "R59"]
    assert ids(grupos["GEMELAS-R22-R60"]) == ["R22", "R60"]


def test_clave_de_gemelas_en_orden_natural_y_no_alfabetico(fabricar):
    corridas = [fabricar.corrida("R100", "TRIP_OK"), fabricar.corrida("R92", "ATWS")]
    assert [g.clave for g in formar_grupos(corridas)] == ["GEMELAS-R92-R100"]


def test_gemela_con_pareja_corta_queda_sola(fabricar):
    grupos = por_clave(formar_grupos(fabricar.variadas()))
    assert ids(grupos["R29"]) == ["R29"]
    todas = [c.id for g in grupos.values() for c in g.corridas]
    assert "R63" not in todas


def test_norm_forma_grupos_individuales(fabricar):
    grupos = por_clave(formar_grupos(fabricar.variadas()))
    for rid in ("R01", "R02", "R31", "R32"):
        assert ids(grupos[rid]) == [rid]
        assert grupos[rid].familia == "NORM"


def test_corridas_excluidas_no_estan_en_ningun_grupo(fabricar):
    todas = {c.id for g in formar_grupos(fabricar.variadas()) for c in g.corridas}
    assert not todas & {"R63", "R41", "R07", "R20"}


def test_cada_corrida_usable_en_exactamente_un_grupo_y_familia_correcta(fabricar):
    corridas = fabricar.variadas()
    grupos = formar_grupos(corridas)
    vistas = [c.id for g in grupos for c in g.corridas]
    usables = sorted(c.id for c in corridas if c.estado == "usable")
    assert sorted(vistas) == usables
    assert len(vistas) == len(set(vistas))
    familias = {g.clave: g.familia for g in grupos}
    assert familias["AREA-50"] == "LOCA"
    assert familias["GEMELAS-R21-R59"] == "ATWS"
    assert familias["R29"] == "ATWS"
    for grupo in grupos:
        assert grupo.tamano == len(grupo.corridas)


def test_resultado_independiente_del_orden_de_entrada(fabricar):
    directo = formar_grupos(fabricar.variadas())
    invertido = formar_grupos(list(reversed(fabricar.variadas())))
    assert [(g.clave, ids(g)) for g in directo] == [(g.clave, ids(g)) for g in invertido]
    familias = [g.familia for g in directo]
    orden = {"NORM": 0, "LOCA": 1, "ATWS": 2}
    assert familias == sorted(familias, key=orden.get)


def test_loca_usable_sin_area_detiene_con_error_que_nombra_el_archivo(fabricar):
    corridas = fabricar.variadas() + [fabricar.corrida("R44", "LOCA", area=None)]
    with pytest.raises(ErrorDatos) as error:
        formar_grupos(corridas)
    assert "auto/R44_LOCA/plotdata.csv" in str(error.value)
    assert "área de rotura" in str(error.value)


def test_sin_corridas_usables_detiene_con_error(fabricar):
    corridas = [fabricar.corrida("R41", "LOCA", estado="corta", area=5)]
    with pytest.raises(ValueError, match="usable"):
        formar_grupos(corridas)


def test_con_el_arbol_sintetico_todas_las_usables_quedan_agrupadas(copia_pwr3l):
    corridas = cargar_corridas(copia_pwr3l)
    grupos = formar_grupos(corridas)
    agrupadas = sorted(c.id for g in grupos for c in g.corridas)
    assert agrupadas == sorted(c.id for c in corridas if c.estado == "usable")
    assert any(g.clave.startswith("AREA-") and g.tamano > 1 for g in grupos)
    assert "GEMELAS-R47-R54" in {g.clave for g in grupos}


def test_agrupar_no_modifica_las_corridas(fabricar):
    corridas = fabricar.variadas()
    antes = [(c.estado, c.area, c.gemela, id(c.serie)) for c in corridas]
    formar_grupos(corridas)
    assert [(c.estado, c.area, c.gemela, id(c.serie)) for c in corridas] == antes
