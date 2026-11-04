"""Pruebas unitarias de la evaluación con abstención (UNCERTAIN) para la Etapa 2 (009)."""
import numpy as np
import pytest

torch = pytest.importorskip("torch")

from clasificador_etapa1.muestras import Muestras  # noqa: E402
from clasificador_etapa2.config import AVISO_REPORTE, INCIERTO, UMBRAL, VENTANA_S  # noqa: E402
from clasificador_etapa2.evaluacion import (  # noqa: E402
    confirmacion_corrida,
    decidir,
    evaluar_probabilidades,
    formatear_reporte,
    metricas_segmento,
)
from preparacion_pwr3l.descubrimiento import Corrida  # noqa: E402


def test_decidir_aplica_umbral_080():
    probs = np.array([
        [0.80, 0.20],  # LOCA (0)
        [0.15, 0.85],  # LOCAC (1)
        [0.79, 0.21],  # UNCERTAIN (-1)
        [0.50, 0.50],  # UNCERTAIN (-1)
    ], dtype=np.float32)
    decisiones = decidir(probs, umbral=UMBRAL)
    assert decisiones.tolist() == [0, 1, -1, -1]


def test_metricas_segmento_con_abstencion_y_matriz_2x3():
    # 4 muestras: 2 LOCA (0) y 2 LOCAC (1)
    y = np.array([0, 0, 1, 1], dtype=np.int64)
    probs = np.array([
        [0.90, 0.10],  # acierto LOCA
        [0.70, 0.30],  # UNCERTAIN
        [0.85, 0.15],  # error con confianza (real LOCAC, pred LOCA)
        [0.10, 0.90],  # acierto LOCAC
    ], dtype=np.float32)
    m = metricas_segmento(y, probs)
    # Matriz 2x3: filas [LOCA, LOCAC], columnas [LOCA, LOCAC, UNCERTAIN]
    assert m["matriz"] == [[1, 0, 1], [1, 1, 0]]
    assert m["muestras"] == 4
    assert m["abstenciones"] == 1
    assert np.isclose(m["cobertura"], 3 / 4)
    assert np.isclose(m["exactitud_decisiones"], 2 / 3)
    assert m["errores_confianza"] == 1
    # LOCA: 1 acierto de 2 predicciones LOCA (prec=0.5), 1 de 2 reales (exh=0.5) → F1=0.5
    assert np.isclose(m["por_clase"]["LOCA"]["precision"], 0.5)
    assert np.isclose(m["por_clase"]["LOCA"]["exhaustividad"], 0.5)
    # LOCAC: 1 acierto de 1 predicción LOCAC (prec=1.0), 1 de 2 reales (exh=0.5) → F1=2/3
    assert np.isclose(m["por_clase"]["LOCAC"]["precision"], 1.0)
    assert np.isclose(m["por_clase"]["LOCAC"]["exhaustividad"], 0.5)


def test_metricas_segmento_cuando_una_rama_no_tiene_muestras_en_prueba():
    # Caso C1 del análisis: solo hay muestras de LOCAC (1), ninguna de LOCA (0)
    y = np.array([1, 1], dtype=np.int64)
    probs = np.array([[0.05, 0.95], [0.40, 0.60]], dtype=np.float32)
    m = metricas_segmento(y, probs)
    assert m["matriz"][0] == [0, 0, 0]
    assert m["por_clase"]["LOCA"] == {"precision": 0.0, "exhaustividad": 0.0, "f1": 0.0, "soporte": 0}
    assert m["por_clase"]["LOCAC"]["soporte"] == 2


def test_confirmacion_corrida_correcta_equivocada_y_sin_decision():
    ks = np.arange(0, 6, dtype=np.float64)
    # Corrida LOCA (0) confirmada en k=2 (dos segundos seguidos k=1,2 con p>=0.80)
    probs_ok = np.array([
        [0.60, 0.40],
        [0.85, 0.15],
        [0.90, 0.10],
        [0.92, 0.08],
        [0.50, 0.50],
        [0.50, 0.50],
    ], dtype=np.float32)
    c_loca = Corrida("R44", "LOCA", "auto", "auto/R44_LOCA/plotdata.csv", area=100, estado="usable")
    r_ok = confirmacion_corrida(c_loca, ks, probs_ok)
    assert r_ok["confirmada"] == "LOCA" and r_ok["correcta"] is True and r_ok["tiempo_s"] == 2.0
    assert r_ok["error_confirmado"] is False

    # Corrida LOCAC (1) que nunca tiene 2 segundos seguidos >=0.80 → sin decisión (UNCERTAIN)
    probs_inc = np.array([
        [0.50, 0.50],
        [0.10, 0.85],
        [0.50, 0.50],
        [0.10, 0.85],
        [0.50, 0.50],
        [0.50, 0.50],
    ], dtype=np.float32)
    c_locac = Corrida("R19", "LOCAC", "auto", "auto/R19_LOCAC/plotdata.csv", area=10, estado="usable")
    r_inc = confirmacion_corrida(c_locac, ks, probs_inc)
    assert r_inc["confirmada"] == INCIERTO and r_inc["tiempo_s"] is None and r_inc["error_confirmado"] is False

    # Corrida LOCAC (1) donde se confirma por error LOCA (0) dos segundos seguidos
    r_err = confirmacion_corrida(c_locac, ks, probs_ok)
    assert r_err["error_confirmado"] is True and r_err["correcta"] is False


def test_evaluar_probabilidades_horizontes_areas_metas_y_reporte():
    c1 = Corrida("R44", "LOCA", "auto", "auto/R44_LOCA/plotdata.csv", area=100, estado="usable")
    c2 = Corrida("R19", "LOCAC", "auto", "auto/R19_LOCAC/plotdata.csv", area=10, estado="usable")
    ks = np.arange(0, 31, dtype=np.float64)
    taus = np.arange(10, 41, dtype=np.int64)
    muestras = Muestras(
        x=np.zeros((62, VENTANA_S, 2), dtype=np.float32),
        y=np.concatenate([np.zeros(31, dtype=np.int64), np.ones(31, dtype=np.int64)]),
        tau=np.concatenate([taus, taus]),
        k=np.concatenate([ks, ks]),
        corrida=np.array(["R44"] * 31 + ["R19"] * 31, dtype=object),
    )
    # R44 se decide bien como LOCA (0.95); R19 se abstiene (0.55)
    probs = np.vstack([
        np.tile([0.95, 0.05], (31, 1)),
        np.tile([0.45, 0.55], (31, 1)),
    ]).astype(np.float32)

    rep = evaluar_probabilidades(muestras, probs, [c1, c2])
    assert len(rep["horizontes"]) == 7
    assert [c["corrida"] for c in rep["corridas"]] == ["R44", "R19"]
    assert rep["metas"]["SC-001_sin_errores_confianza_30s"]["cumple"] is True
    assert rep["metas"]["SC-002_loca_50cm2_en_10s"]["cumple"] is True
    assert any("incertidumbre" in a.lower() for a in rep["advertencias"])

    texto = formatear_reporte(rep)
    assert AVISO_REPORTE in texto
    assert "UNCERTAIN" in texto and "R44" in texto and "R19" in texto

