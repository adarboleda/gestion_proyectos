"""Tiempos de diagnóstico, falsas alarmas, confusiones y metas (US2, FR-005, FR-008, FR-009, FR-014)."""
import numpy as np
import pytest

from preparacion_pwr3l.descubrimiento import Corrida
from tiempo_deteccion.atws import ResultadoATWS
from tiempo_deteccion.evaluacion import (
    falsas_alarmas_etapa1,
    metas,
    primera_familia,
    resultados_por_corrida,
    resumen,
    tiempo_diagnostico,
)
from tiempo_deteccion.falla import InstanteFalla
from tiempo_deteccion.reproduccion import LineaTiempo, familias_confirmadas

FAMILIAS = ("NORM", "LOCA", "TRANS")


def linea(rid="R1", conjunto="test", altas=()):
    """Línea de tiempo τ = 5…299: NORM con 0,9 salvo en los tramos `altas` = [(familia, desde, hasta)]."""
    tau = np.arange(5, 300)
    p = np.tile([0.9, 0.05, 0.05], (len(tau), 1))
    for familia, desde, hasta in altas:
        filas = (tau >= desde) & (tau <= hasta)
        p[filas] = 0.05
        p[filas, FAMILIAS.index(familia)] = 0.9
    return LineaTiempo(rid, conjunto, tau, p, familias_confirmadas(p, 0.80))


def falla(t, incierta=False):
    return InstanteFalla(t, "programado", "x", t, incierta, "validador antes" if incierta else None)


# --- (a)(b) tiempo de diagnóstico --------------------------------------------------------------

def test_tiempo_desde_la_falla():
    assert tiempo_diagnostico(linea(altas=[("LOCA", 24, 299)]), "LOCA", 20.0) == (25, 5.0)


def test_tiempo_con_falla_fraccionaria():
    # alta desde 40, pero τ − 1 debe ser ≥ 47,5 → τ = 49
    assert tiempo_diagnostico(linea(altas=[("LOCA", 40, 299)]), "LOCA", 47.5) == (49, 1.5)


def test_sin_confirmacion_no_detectado():
    assert tiempo_diagnostico(linea(), "LOCA", 20.0) == (None, None)
    assert tiempo_diagnostico(linea(altas=[("TRANS", 30, 299)]), "LOCA", 20.0) == (None, None)


# --- (c) falsas alarmas de la Etapa 1 ----------------------------------------------------------

def test_falsas_alarmas_en_corrida_norm():
    resultado = falsas_alarmas_etapa1(linea(altas=[("TRANS", 100, 105), ("LOCA", 200, 201)]), None)
    assert resultado == {"episodios": 2, "instantes": 6}


def test_falsas_alarmas_antes_de_la_falla():
    resultado = falsas_alarmas_etapa1(linea(altas=[("LOCA", 30, 33), ("LOCA", 61, 299)]), 60.0)
    assert resultado == {"episodios": 1, "instantes": 3}


def test_confirmacion_que_cruza_la_falla_no_es_alarma_ni_deteccion():
    # alta desde 60 y falla en 60,5: la confirmación en τ = 61 cruza la falla
    alta = linea(altas=[("LOCA", 60, 299)])
    assert falsas_alarmas_etapa1(alta, 60.5) == {"episodios": 0, "instantes": 0}
    assert tiempo_diagnostico(alta, "LOCA", 60.5) == (62, 1.5)


# --- (c2) primera familia y confusión ----------------------------------------------------------

def test_primera_familia_y_confusion():
    confundida = linea(altas=[("TRANS", 22, 26), ("LOCA", 30, 299)])
    assert primera_familia(confundida, 20.0) == "TRANS"
    assert tiempo_diagnostico(confundida, "LOCA", 20.0) == (31, 11.0)
    assert primera_familia(linea(), 20.0) == ""


# --- resultados, resumen y metas ---------------------------------------------------------------

def _corrida(rid, clase, area=None):
    return Corrida(rid, clase, "auto", f"auto/{rid}/plotdata.csv", area=area, estado="usable")


def _atws(rid, conjunto, clase, demanda=None, recomendacion="sin ATWS"):
    es_atws = clase == "ATWS"
    return ResultadoATWS(
        corrida=rid, conjunto=conjunto, clase=clase, es_atws=es_atws, recomendacion=recomendacion,
        motivo="flujo alto" if recomendacion == "posible ATWS" else "flujo caído", t_demanda=None, t_decision=None,
        tiempo_desde_demanda_s=demanda, tiempo_desde_falla_s=None,
        falsa_alarma=recomendacion == "posible ATWS" and not es_atws,
    )


@pytest.fixture
def escenario():
    entradas = [
        (_corrida("R41", "LOCA", 100), "test", falla(20.0), linea("R41", "test", [("LOCA", 24, 299)])),  # 5 s
        (_corrida("R42", "LOCA", 2), "test", falla(20.0), linea("R42", "test", [("TRANS", 22, 26), ("LOCA", 34, 299)])),  # 15 s
        (_corrida("R47", "ATWS"), "test", falla(30.0), linea("R47", "test", [("TRANS", 32, 299)])),  # 3 s
        (_corrida("R48", "ATWS"), "test", falla(30.0, incierta=True), linea("R48", "test", [("LOCA", 10, 12), ("TRANS", 50, 299)])),
        (_corrida("R49", "TRIP_OK"), "test", falla(40.0), linea("R49", "test", [("TRANS", 42, 299)])),  # 3 s
        (_corrida("R33", "NORM"), "test", None, linea("R33", "test", [("LOCA", 100, 101)])),  # 1 falsa alarma
        (_corrida("R44", "LOCA", 50), "val", falla(20.0), linea("R44", "val", [("LOCA", 22, 299)])),  # 3 s (referencia)
        (_corrida("R50", "ATWS"), "val", falla(30.0, incierta=True), linea("R50", "val", [("TRANS", 32, 299)])),
    ]
    atws = {
        "R47": _atws("R47", "test", "ATWS", 4.0, "posible ATWS"),
        "R48": _atws("R48", "test", "ATWS"),  # no detectado
        "R49": _atws("R49", "test", "TRIP_OK", recomendacion="posible ATWS"),  # falsa alarma de la regla
        "R50": _atws("R50", "val", "ATWS", 2.0, "posible ATWS"),  # incierto: cuenta para la meta de ATWS
        "R41": _atws("R41", "test", "LOCA"), "R42": _atws("R42", "test", "LOCA"),
        "R33": _atws("R33", "test", "NORM"), "R44": _atws("R44", "val", "LOCA"),
    }
    corridas = [(c, conjunto) for c, conjunto, _, _ in entradas]
    lineas = {c.id: l for c, _, _, l in entradas}
    fallas = {c.id: f for c, _, f, _ in entradas if f is not None}
    return resultados_por_corrida(corridas, lineas, fallas, atws)


def test_resultados_por_corrida(escenario):
    por_id = {r.corrida: r for r in escenario}
    assert por_id["R41"].tiempo_diagnostico_s == 5.0 and por_id["R41"].familia == "LOCA"
    assert por_id["R42"].primera_familia == "TRANS" and por_id["R42"].confusion
    assert not por_id["R41"].confusion
    assert por_id["R33"].falla is None and por_id["R33"].falsas_alarmas_etapa1 == {"episodios": 1, "instantes": 1}
    assert por_id["R48"].falsas_alarmas_etapa1 is None  # incierta: «antes de la falla» no es fiable
    assert por_id["R49"].atws.falsa_alarma


def test_meta_de_diagnostico_solo_prueba_y_sin_inciertas(escenario):
    meta = metas(escenario)["diagnostico_10s"]
    assert (meta["dentro"], meta["total"], meta["cumple"]) == (3, 4, False)  # R41, R47, R49 de R41, R42, R47, R49
    diagnostico = resumen(escenario)["diagnostico"]
    assert diagnostico["test"]["LOCA"]["corridas"] == 2 and diagnostico["test"]["LOCA"]["en_meta"] == 1
    assert diagnostico["test"]["TRANS"]["corridas"] == 2 and diagnostico["test"]["TRANS"]["en_meta"] == 2
    assert diagnostico["test"]["LOCA_por_area"] == {"2": [15.0], "100": [5.0]}


def test_meta_de_diagnostico_sin_datos(escenario):
    solo_val = [r for r in escenario if r.conjunto == "val"]
    assert metas(solo_val)["diagnostico_10s"]["cumple"] == "sin datos"


def test_meta_de_atws_validacion_y_prueba_con_inciertas(escenario):
    meta = metas(escenario)["atws_3s"]
    # R50 (val, 2 s, incierto) cumple; R47 (test, 4 s) no; R48 (test) no detectado → incumple
    assert (meta["dentro"], meta["total"], meta["cumple"]) == (1, 3, False)
    assert (meta["solo_prueba"]["dentro"], meta["solo_prueba"]["total"]) == (0, 2)


def test_validacion_aparece_como_referencia(escenario):
    datos = resumen(escenario)
    assert datos["diagnostico"]["val"]["total"]["corridas"] == 1  # R44; R50 es incierta
    assert datos["diagnostico"]["val"]["total"]["en_meta"] == 1
    assert datos["diagnostico"]["test"]["total"]["corridas"] == 4


def test_falsas_alarmas_y_confusiones_en_el_resumen(escenario):
    datos = resumen(escenario)
    prueba = datos["falsas_alarmas"]["test"]
    assert prueba["etapa1"]["corridas_norm"] == {"episodios": 1, "corridas": ["R33"]}
    assert prueba["etapa1"]["inciertas_no_contadas"] == ["R48"]
    assert prueba["regla"] == {"recomendaciones": 1, "corridas": ["R49"]}
    assert datos["confusiones"]["test"] == ["R42"]


# --- US3: comparación con el inicio del validador (FR-011) ---------------------------------------

def test_tiempo_desde_el_validador_como_en_005():
    from tiempo_deteccion.evaluacion import tiempo_desde_validador

    alta = linea(altas=[("LOCA", 24, 299)])
    # inicio del validador 21,3 → se redondea hacia arriba a 22 (005); confirmación en τ = 25 → 3 s
    assert tiempo_desde_validador(alta, "LOCA", 21.3) == 3.0
    assert tiempo_desde_validador(alta, "LOCA", None) is None
    assert tiempo_desde_validador(linea(), "LOCA", 21.3) is None


def test_resultado_incluye_el_tiempo_desde_el_validador():
    from tiempo_deteccion.evaluacion import resultados_por_corrida as resultados

    f = InstanteFalla(20.0, "programado", "x", 21.3, False, None)
    r = resultados([(_corrida("R41", "LOCA", 100), "test")], {"R41": linea("R41", "test", [("LOCA", 24, 299)])},
                   {"R41": f}, {})[0]
    assert (r.tiempo_diagnostico_s, r.tiempo_desde_validador_s) == (5.0, 3.0)
