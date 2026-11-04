"""Calibración de retardos y umbral (solo entrenamiento) y evaluación de una corrida."""
import math

import numpy as np
import pytest

from preparacion_pwr3l.descubrimiento import Corrida, ErrorDatos
from regla_atws.eventos import Senal
from regla_atws.regla import Caso, Regla, calibrar, calibrar_retardos, calibrar_umbral, evaluar

FILAS = 300


def _caso(rid, clase, senal=None, scram=None, pwnt=None, conjunto="train"):
    corrida = Corrida(rid, clase, "auto", f"auto/{rid}_{clase}/plotdata.csv", estado="usable")
    return Caso(corrida, conjunto, senal, scram, np.full(FILAS, 100.0) if pwnt is None else np.asarray(pwnt, float))


def _caida(t):
    pwnt = np.full(FILAS, 100.0)
    pwnt[np.arange(FILAS) > t] = 6.0
    return pwnt


def _alto(nivel, desde=0):
    pwnt = np.full(FILAS, 100.0)
    pwnt[desde:] = nivel
    return pwnt


TURBINA = Senal(45.5, "turbine trip", "registro")
BOMBA = Senal(31.5, "rcp-a trip", "registro")


def _regla(umbral=20.0, retardos=None):
    retardos = {"turbine trip": 5.0, "rcp-a trip": 2.5} if retardos is None else retardos
    return Regla(umbral=umbral, retardos=retardos, retardo_por_defecto=max(retardos.values()), espera=2.0,
                 minimo_atws=40.0, maximo_no_atws=6.0, solape=False, falsas_alarmas_entrenamiento=0)


def test_retardo_por_tipo_es_el_mayor_de_entrenamiento():
    casos = [
        _caso("R54", "TRIP_OK", TURBINA, 50.5), _caso("R56", "TRIP_OK", BOMBA, 34.0),
        _caso("R58", "TRIP_OK", Senal(40.0, "rcp-a trip", "registro"), 41.0),
        _caso("R44", "LOCA", Senal(61.5, "scram lo rx press", "registro"), 62.0),
        _caso("R47", "ATWS", TURBINA, None),  # sin scram: no aporta retardo
    ]
    assert calibrar_retardos(casos) == {"turbine trip": 5.0, "rcp-a trip": 2.5, "scram lo rx press": 0.5}


def test_umbral_punto_medio_cuando_hay_separacion():
    calibrado = calibrar_umbral([37.0, 55.0, 88.0], [5.6, 5.9])
    assert calibrado["umbral"] == pytest.approx((37.0 + 5.9) / 2)
    assert calibrado["solape"] is False and calibrado["falsas_alarmas"] == 0
    assert calibrado["minimo_atws"] == 37.0 and calibrado["maximo_no_atws"] == 5.9


def test_umbral_con_solape_no_omite_ningun_atws():
    calibrado = calibrar_umbral([30.0, 60.0], [5.0, 35.0, 50.0])
    assert calibrado["solape"] is True
    assert calibrado["umbral"] < 30.0 and calibrado["umbral"] > 29.999
    assert calibrado["falsas_alarmas"] == 2


def test_calibrar_usa_solo_entrenamiento_y_cuenta_el_margen():
    casos = [
        _caso("R54", "TRIP_OK", TURBINA, 50.5, _caida(50.5)),
        _caso("R47", "ATWS", TURBINA, None, _alto(55.0, 46)),
        _caso("R56", "TRIP_OK", BOMBA, 34.0, _caida(34.0)),
        _caso("R49", "ATWS", BOMBA, None, _alto(37.0, 32)),
        _caso("R31", "NORM"),
    ]
    regla = calibrar(casos)
    assert regla.retardos == {"turbine trip": 5.0, "rcp-a trip": 2.5}
    assert regla.minimo_atws == 37.0 and regla.maximo_no_atws == 6.0
    assert regla.umbral == pytest.approx(21.5)
    with pytest.raises(ValueError):
        calibrar(casos + [_caso("R99", "TRIP_OK", TURBINA, 50.5, conjunto="val")])


def test_atws_sin_demanda_no_entra_en_el_umbral():
    casos = [
        _caso("R54", "TRIP_OK", TURBINA, 50.5, _caida(50.5)),
        _caso("R47", "ATWS", TURBINA, None, _alto(55.0, 46)),
        _caso("R97", "ATWS", None, None, _alto(90.0)),
    ]
    regla = calibrar(casos)
    assert regla.minimo_atws == pytest.approx(55.0)
    resultado = evaluar(regla, casos[2])
    assert resultado.recomendacion == "sin ATWS" and resultado.motivo == "sin demanda"
    assert resultado.acierto is False


def test_flujo_caido_es_sin_atws():
    resultado = evaluar(_regla(), _caso("R54", "TRIP_OK", TURBINA, 50.5, _caida(50.5)))
    assert resultado.t_demanda == 50.5 and resultado.t_decision == 53
    assert resultado.pwnt_decision == pytest.approx(6.0)
    assert resultado.recomendacion == "sin ATWS" and resultado.motivo == "flujo caído" and resultado.acierto


def test_flujo_alto_es_posible_atws_dentro_de_la_meta():
    resultado = evaluar(_regla(), _caso("R49", "ATWS", BOMBA, None, _alto(40.0, 32)))
    assert resultado.t_demanda == 34.0 and resultado.t_decision == math.ceil(34.0 + 2.0)
    assert resultado.recomendacion == "posible ATWS" and resultado.motivo == "flujo alto" and resultado.acierto
    assert 2.0 <= resultado.t_deteccion_demanda < 3.0
    assert resultado.t_deteccion_senal == pytest.approx(36 - 31.5)


def test_sin_demanda_es_sin_atws():
    resultado = evaluar(_regla(), _caso("R31", "NORM"))
    assert resultado.recomendacion == "sin ATWS" and resultado.motivo == "sin demanda" and resultado.acierto
    assert resultado.t_decision is None and resultado.pwnt_decision is None


def test_decision_fuera_de_la_ventana():
    tarde = Senal(296.0, "turbine trip", "registro")
    resultado = evaluar(_regla(), _caso("R47", "ATWS", tarde, None, _alto(60.0)))
    assert resultado.recomendacion == "sin ATWS" and resultado.motivo == "decisión fuera de la ventana"


def test_tipo_no_visto_usa_el_mayor_retardo():
    rara = Senal(30.0, "otdt", "registro")
    resultado = evaluar(_regla(), _caso("R95", "ATWS", rara, None, _alto(70.0, 31)))
    assert resultado.retardo == 5.0 and resultado.retardo_por_defecto is True
    assert resultado.t_decision == 37


def test_pwnt_inicial_no_positivo_detiene():
    pwnt = np.full(FILAS, 100.0)
    pwnt[0] = 0.0
    with pytest.raises(ErrorDatos, match="PWNT inicial no positivo"):
        evaluar(_regla(), _caso("R47", "ATWS", TURBINA, None, pwnt))


def test_flujo_relativo_al_valor_inicial():
    pwnt = np.full(FILAS, 98.0)
    pwnt[37:] = 49.0
    resultado = evaluar(_regla(), _caso("R25", "ATWS", Senal(30.0, "turbine trip", "registro"), None, pwnt))
    assert resultado.pwnt_decision == pytest.approx(50.0)
