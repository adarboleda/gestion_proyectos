"""Pruebas de la evaluación: métricas, horizontes, confirmación, falsas alarmas y metas (005, historia 2)."""
import math

import numpy as np
import pytest

from clasificador_etapa1.evaluacion import (
    confirmadas,
    evaluar_probabilidades,
    falsas_alarmas,
    metas,
    metricas,
    por_horizonte,
    primeros_s,
    tiempos_confirmacion,
)
from clasificador_etapa1.muestras import Muestras
from preparacion_pwr3l.descubrimiento import Corrida

ALTA = [0.05, 0.9, 0.05]  # LOCA seguro
BAJA = [0.3, 0.4, 0.3]  # LOCA, pero sin confianza
NORMAL = [0.95, 0.03, 0.02]


def muestras_de(filas):
    """filas: (corrida, tau, k, y) → Muestras con x vacío."""
    corridas, taus, ks, ys = zip(*filas)
    n = len(filas)
    return Muestras(np.zeros((n, 30, 1), np.float32), np.array(ys, np.int64), np.array(taus, np.int64),
                    np.array(ks, np.float64), np.array(corridas, dtype=object))


def corrida(rid, clase, area=None):
    return Corrida(rid, clase, "auto", f"auto/{rid}/plotdata.csv", area=area, estado="usable")


def test_metricas_globales():
    y = np.array([0, 0, 1, 1, 2, 2])
    pred = np.array([0, 1, 1, 1, 2, 0])
    m = metricas(y, pred)
    assert m["matriz"] == [[1, 1, 0], [0, 2, 0], [1, 0, 1]]
    assert m["por_familia"]["LOCA"]["precision"] == pytest.approx(2 / 3, abs=1e-4)
    assert m["por_familia"]["LOCA"]["exhaustividad"] == pytest.approx(1.0)
    assert m["por_familia"]["TRANS"]["exhaustividad"] == pytest.approx(0.5)
    assert m["f1_macro"] == pytest.approx(np.mean([0.5, 0.8, 2 / 3]), abs=1e-4)


def test_familia_sin_muestras_no_inventa_metricas():
    m = metricas(np.array([0, 0, 1]), np.array([0, 0, 1]))
    assert m["por_familia"]["TRANS"]["soporte"] == 0
    assert m["por_familia"]["TRANS"]["exhaustividad"] is None


def test_horizonte_usa_k_igual_h_y_las_muestras_normales():
    filas = [("R904", 10, math.nan, 0), ("R904", 11, math.nan, 0),
             ("R903", 30, 2.0, 1), ("R903", 31, 3.0, 1), ("R905", 40, 2.0, 2)]
    probs = np.array([NORMAL, NORMAL, ALTA, NORMAL, NORMAL])
    tabla = {h["h"]: h for h in por_horizonte(muestras_de(filas), probs, horizontes=(2, 3))}
    assert tabla[2]["exhaustividad"] == {"LOCA": 1.0, "TRANS": 0.0}
    assert tabla[3]["exhaustividad"] == {"LOCA": 0.0, "TRANS": None}
    assert 0 <= tabla[2]["f1_macro"] <= 1
    completas = tabla[2]["metricas"]
    assert completas["por_familia"]["LOCA"]["exhaustividad"] == 1.0
    assert completas["por_familia"]["TRANS"]["exhaustividad"] == 0.0
    assert set(completas["por_familia"]["NORM"]) == {"precision", "exhaustividad", "f1", "soporte"}
    assert sum(map(sum, completas["matriz"])) == 4  # 2 normales + 2 eventos en k = 2


def test_f1_de_los_primeros_30_s():
    filas = [("R904", 10, math.nan, 0), ("R903", 30, 5.0, 1), ("R903", 80, 55.0, 1)]
    probs = np.array([NORMAL, ALTA, NORMAL])  # el fallo en k = 55 no cuenta
    assert primeros_s(muestras_de(filas), probs, 30) == pytest.approx(1.0)


def test_confirmacion_exige_dos_segundos_seguidos_sobre_el_umbral():
    probs = np.array([ALTA, BAJA, ALTA, ALTA])
    assert confirmadas(probs)[:, 1].tolist() == [False, False, False, True]


def test_tiempo_de_confirmacion_y_no_detectada():
    # L1: inicio en τ=10; confianza alta desde τ=10 → se confirma en τ=11 (k=1)
    filas = [("R901", t, t - 10.0, 0 if t < 10 else 1) for t in range(8, 16)]
    filas += [("R902", t, t - 10.0, 0 if t < 10 else 1) for t in range(8, 16)]
    probs = np.array([NORMAL, NORMAL] + [ALTA] * 6 + [NORMAL, NORMAL] + [BAJA] * 6)
    corridas = [corrida("R901", "LOCA", 100), corrida("R902", "LOCAC", 5)]
    tabla = {d["corrida"]: d for d in tiempos_confirmacion(muestras_de(filas), probs, corridas, {"R901": 10.0, "R902": 10.0})}
    assert tabla["R901"]["tiempo_s"] == 1.0
    assert tabla["R902"]["tiempo_s"] is None
    assert tabla["R901"]["area"] == 100 and tabla["R901"]["familia"] == "LOCA"


def test_confirmacion_que_empieza_antes_del_inicio_no_cuenta_como_deteccion():
    # confianza alta ya en τ=9 (antes del inicio en 10): la detección válida exige τ−1 ≥ inicio
    filas = [("R903", t, t - 10.0, 0 if t < 10 else 1) for t in range(8, 13)]
    probs = np.array([NORMAL, ALTA, ALTA, ALTA, ALTA])
    d = tiempos_confirmacion(muestras_de(filas), probs, [corrida("R903", "LOCA", 50)], {"R903": 10.0})[0]
    assert d["tiempo_s"] == 1.0


def test_falsas_alarmas_en_corridas_norm_y_tramos_previos():
    filas = [("R904", t, math.nan, 0) for t in range(5, 11)]
    filas += [("R903", t, t - 20.0, 0 if t < 20 else 1) for t in range(15, 22)]
    probs = np.array([NORMAL, ALTA, ALTA, ALTA, NORMAL, BAJA,  # N: un episodio de 2 instantes confirmados
                      NORMAL, ALTA, ALTA, NORMAL, NORMAL, ALTA, ALTA])  # L: uno antes del inicio
    fa = falsas_alarmas(muestras_de(filas), probs, corridas_norm={"R904"})
    assert fa["corridas_norm"] == {"instantes": 2, "episodios": 1, "corridas": ["R904"]}
    assert fa["tramos_previos"] == {"instantes": 1, "episodios": 1, "corridas": ["R903"]}


def test_metas_con_su_valor_y_sin_datos():
    deteccion = [{"familia": "LOCA", "area": 100, "tiempo_s": 4.0}, {"familia": "LOCA", "area": 5, "tiempo_s": None}]
    fa = {"corridas_norm": {"instantes": 0, "episodios": 0, "corridas": []}}
    r = metas(deteccion, fa, f1_primeros=0.85, hay_corridas_norm=True)
    assert r["SC-001"]["cumple"] is True and r["SC-002"]["cumple"] is True and r["SC-003"]["cumple"] is True
    sin = metas([{"familia": "LOCA", "area": 5, "tiempo_s": 3.0}], fa, f1_primeros=0.5, hay_corridas_norm=False)
    assert sin["SC-001"]["cumple"] == "sin datos"
    assert sin["SC-002"]["cumple"] == "sin datos"
    assert sin["SC-003"]["cumple"] is False


def test_reporte_completo(sinteticas):
    filas = [("R31", t, math.nan, 0) for t in range(5, 15)]
    filas += [("R200", t, t - 10.0, 0 if t < 10 else 1) for t in range(5, 30)]
    probs = np.array([NORMAL] * 10 + [NORMAL] * 5 + [ALTA] * 20)
    por_id = {c.id: c for c in sinteticas.corridas}
    reporte = evaluar_probabilidades(muestras_de(filas), probs, [por_id["R31"], por_id["R200"]], {"R200": 10.0, "R31": None})
    for clave in ("aviso", "conjunto_prueba", "global", "horizontes", "primeros_30s", "deteccion", "falsas_alarmas", "metas"):
        assert clave in reporte, clave
    assert sum(map(sum, reporte["global"]["matriz"])) == len(filas)
    assert [d["corrida"] for d in reporte["deteccion"]] == ["R200"]
    assert "consultivo" in reporte["aviso"]
