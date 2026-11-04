"""Instante de la falla de cada corrida (US1, FR-001…FR-003)."""
import pytest

from ayudas_tiempo import ESPERADO
from tiempo_deteccion.falla import InstanteFalla, instante_falla, instantes_falla


def _instante(arbol, rid):
    return instante_falla(arbol.raiz, arbol.por_id[rid])


@pytest.mark.parametrize("rid", ["R50", "R51", "R52", "R53"])
def test_iniciador_del_registro_en_atws_y_trip_ok(arbol_fallas, rid):
    t, fuente, incierta = ESPERADO[rid]
    falla = _instante(arbol_fallas, rid)
    assert isinstance(falla, InstanteFalla)
    assert (falla.t, falla.fuente, falla.incierta) == (t, fuente, incierta)
    assert falla.detalle  # la línea del registro


def test_las_lineas_en_t_cero_se_ignoran(arbol_fallas):
    falla = _instante(arbol_fallas, "R50")  # FWIV #4 a 0 % en t = 0 es la configuración inicial
    assert falla.t == 30.0
    assert "FWIV #1" in falla.detalle


@pytest.mark.parametrize("rid, detalle", [("R41", "1:100:50"), ("R42", "1:500:30;6:0:30"), ("R43", "7:0:50;8:0:0")])
def test_loca_automatica_usa_el_retardo_programado(arbol_fallas, rid, detalle):
    t, fuente, _ = ESPERADO[rid]
    falla = _instante(arbol_fallas, rid)
    assert (falla.t, falla.fuente) == (t, fuente)
    assert detalle in falla.detalle


def test_la_falla_8_no_es_el_iniciador(arbol_fallas):
    assert _instante(arbol_fallas, "R43").t == 50.0  # `7:0:50;8:0:0`


def test_loca_no_busca_en_el_registro(arbol_fallas):
    # R43 tiene «Turbine Trip Control Change: True» a los 60 s (consecuencia del scram)
    falla = _instante(arbol_fallas, "R43")
    assert falla.fuente == "programado" and falla.t == 50.0


def test_loca_manual_usa_el_instante_de_la_carpeta(arbol_fallas):
    falla = _instante(arbol_fallas, "R10")
    assert (falla.t, falla.fuente) == (60.0, "programado")
    assert "_t60" in falla.detalle
    assert falla.inicio_validador == 61.0


def test_extraccion_de_barras_no_toma_el_scram_como_iniciador(arbol_fallas):
    falla = _instante(arbol_fallas, "R96")
    assert (falla.t, falla.fuente) == (40.0, "programado")


def test_validador_antes_de_la_falla_marca_incierta(arbol_fallas):
    r47 = _instante(arbol_fallas, "R47")
    assert (r47.t, r47.incierta, r47.inicio_validador) == (45.0, True, 1.0)
    assert r47.motivo and "validador" in r47.motivo
    r22 = _instante(arbol_fallas, "R22")
    assert (r22.t, r22.fuente, r22.incierta, r22.inicio_validador) == (47.5, "registro", True, 13.0)


def test_dentro_de_la_tolerancia_no_es_incierta(arbol_fallas):
    falla = _instante(arbol_fallas, "R43")  # validador 50, falla 50
    assert not falla.incierta and falla.motivo is None
    assert not _instante(arbol_fallas, "R42").incierta  # validador 30,5, falla 30


def test_sin_ninguna_fuente(arbol_fallas):
    falla = _instante(arbol_fallas, "R60")
    assert falla.t is None and falla.fuente == "ninguna" and falla.incierta
    assert falla.inicio_validador is None
    assert falla.motivo


def test_norm_no_tiene_instante(arbol_fallas):
    assert _instante(arbol_fallas, "R31") is None


def test_instantes_falla_cubre_todas_las_corridas_de_evento(arbol_fallas):
    fallas = instantes_falla(arbol_fallas.raiz, arbol_fallas.corridas)
    assert set(fallas) == set(ESPERADO)
    for rid, (t, fuente, incierta) in ESPERADO.items():
        assert (fallas[rid].t, fallas[rid].fuente, fallas[rid].incierta) == (t, fuente, incierta), rid


def test_instantes_falla_ignora_corridas_no_usables(arbol_fallas):
    arbol_fallas.por_id["R41"].estado = "corta"
    assert "R41" not in instantes_falla(arbol_fallas.raiz, arbol_fallas.corridas)
