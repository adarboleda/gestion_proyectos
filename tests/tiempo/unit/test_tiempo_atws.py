"""Tiempo de ATWS con la regla de 006 calibrada solo con entrenamiento (US2, FR-006, FR-009)."""
import numpy as np
import pytest

from preparacion_pwr3l.descubrimiento import Corrida
from regla_atws.eventos import Senal
from regla_atws.regla import Caso
from tiempo_deteccion.atws import evaluar_atws
from tiempo_deteccion.falla import InstanteFalla


def _corrida(rid, clase):
    return Corrida(rid, clase, "auto", f"auto/{rid}_{clase}/plotdata.csv", estado="usable")


def _caso(rid, clase, conjunto, t_senal=None, scram=None, cae_en=None):
    pwnt = np.full(300, 100.0)
    if cae_en is not None:
        pwnt[np.arange(300) > cae_en] = 6.0
    senal = Senal(t_senal, "turbine trip", "registro") if t_senal is not None else None
    return Caso(_corrida(rid, clase), conjunto, senal, scram, pwnt)


def _falla(t, incierta=False):
    return InstanteFalla(t, "registro", "x", t, incierta, "validador antes" if incierta else None)


@pytest.fixture
def casos():
    return [
        # entrenamiento: retardo de «turbine trip» = 5 s; ATWS con flujo alto, TRIP_OK con flujo caído
        _caso("R60", "TRIP_OK", "train", 40.0, 45.0, cae_en=45),
        _caso("R61", "ATWS", "train", 40.0),
        _caso("R31", "NORM", "train"),
        # validación y prueba
        _caso("R62", "ATWS", "val", 30.0),  # demanda 35, decisión 37 → 2 s; desde la falla (28) → 9 s
        _caso("R63", "ATWS", "test", 50.0, cae_en=52),  # flujo caído → no detectado
        _caso("R64", "TRIP_OK", "test", 20.0),  # flujo alto sin ser ATWS → falsa alarma
        _caso("R65", "ATWS", "val", 10.0),  # incierta: tiempo desde la demanda sí, desde la falla no
        _caso("R32", "NORM", "test"),
    ]


@pytest.fixture
def fallas():
    return {"R62": _falla(28.0), "R63": _falla(48.0), "R64": _falla(19.0), "R65": _falla(12.0, incierta=True)}


def test_calibra_solo_con_entrenamiento(casos, fallas):
    regla, _ = evaluar_atws(casos, fallas)
    assert regla.retardos == {"turbine trip": 5.0}
    assert regla.umbral == pytest.approx((100.0 + 6.0) / 2)


def test_solo_evalua_validacion_y_prueba(casos, fallas):
    _, resultados = evaluar_atws(casos, fallas)
    assert set(resultados) == {"R62", "R63", "R64", "R65", "R32"}


def test_atws_detectado_tiempos_desde_demanda_y_desde_falla(casos, fallas):
    r = evaluar_atws(casos, fallas)[1]["R62"]
    assert r.recomendacion == "posible ATWS" and r.es_atws
    assert (r.t_demanda, r.t_decision) == (35.0, 37)
    assert r.tiempo_desde_demanda_s == pytest.approx(2.0)
    assert r.tiempo_desde_falla_s == pytest.approx(9.0)
    assert not r.falsa_alarma


def test_atws_no_detectado(casos, fallas):
    r = evaluar_atws(casos, fallas)[1]["R63"]
    assert r.recomendacion == "sin ATWS"
    assert r.tiempo_desde_demanda_s is None and r.tiempo_desde_falla_s is None
    assert r.motivo == "flujo caído"


def test_posible_atws_sin_atws_es_falsa_alarma(casos, fallas):
    r = evaluar_atws(casos, fallas)[1]["R64"]
    assert r.recomendacion == "posible ATWS" and not r.es_atws
    assert r.falsa_alarma
    assert r.tiempo_desde_demanda_s is None


def test_atws_incierto_conserva_el_tiempo_desde_la_demanda(casos, fallas):
    r = evaluar_atws(casos, fallas)[1]["R65"]
    assert r.tiempo_desde_demanda_s == pytest.approx(2.0)
    assert r.tiempo_desde_falla_s is None


def test_norm_sin_demanda(casos, fallas):
    r = evaluar_atws(casos, fallas)[1]["R32"]
    assert r.recomendacion == "sin ATWS" and r.motivo == "sin demanda" and not r.falsa_alarma
