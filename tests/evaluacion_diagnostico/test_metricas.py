"""Pruebas unitarias para metricas.py: intervalos de Wilson, matriz 3x4 y métricas conjuntas."""
import numpy as np
import pytest

from evaluacion_diagnostico.metricas import (
    intervalo_wilson,
    matriz_confusion_con_abstencion,
    metricas_conjuntas,
)


def test_intervalo_wilson_propiedades_basicas():
    # Caso centrado k=5, n=10
    inferior, superior = intervalo_wilson(5, 10, nivel_confianza=0.95)
    assert 0.0 <= inferior <= 0.5 <= superior <= 1.0
    assert round(inferior, 3) == 0.237
    assert round(superior, 3) == 0.763

    # Caso extremo k=0 (sin aciertos o sin errores)
    inf_cero, sup_cero = intervalo_wilson(0, 10)
    assert inf_cero == 0.0
    assert 0.0 < sup_cero < 0.35

    # Caso extremo k=10
    inf_diez, sup_diez = intervalo_wilson(10, 10)
    assert sup_diez == 1.0
    assert 0.65 < inf_diez < 1.0

    # Caso n=0
    inf_nulo, sup_nulo = intervalo_wilson(0, 0)
    assert inf_nulo is None and sup_nulo is None


def test_matriz_confusion_con_abstencion():
    y_true = np.array([0, 0, 1, 1, 2, 2])
    y_pred = np.array([0, 1, 1, 0, 2, 1])
    is_uncertain = np.array([False, True, False, False, True, False])

    cm = matriz_confusion_con_abstencion(y_true, y_pred, is_uncertain, num_clases=3)
    assert cm.shape == (3, 4)

    # Fila 0 (clase 0, 2 muestras): una en 0, una incierta
    assert cm[0, 0] == 1
    assert cm[0, 3] == 1
    assert cm[0].sum() == 2

    # Fila 1 (clase 1, 2 muestras): una en 1, una predijo 0 (error decidido)
    assert cm[1, 1] == 1
    assert cm[1, 0] == 1
    assert cm[1].sum() == 2

    # Fila 2 (clase 2, 2 muestras): una incierta, una predijo 1 (error decidido)
    assert cm[2, 3] == 1
    assert cm[2, 1] == 1
    assert cm[2].sum() == 2


def test_metricas_conjuntas_suma_uno_y_valores_exactos(probabilidades_y_etiquetas_sinteticas):
    y_true, probs = probabilidades_y_etiquetas_sinteticas
    res = metricas_conjuntas(y_true, probs, umbral=0.80)

    # Totales
    assert res["n_muestras"] == 10
    assert res["aciertos_con_confianza"] == 5
    assert res["abstenciones"] == 3
    assert res["errores_alta_confianza"] == 2

    # Proporciones
    assert res["exactitud_con_abstencion"] == 0.5
    assert res["tasa_abstencion"] == 0.3
    assert res["tasa_errores_alta_confianza"] == 0.2

    # Propiedad matemática fundamental
    suma = res["exactitud_con_abstencion"] + res["tasa_abstencion"] + res["tasa_errores_alta_confianza"]
    assert abs(suma - 1.0) < 1e-6

    # Decididas (5 / 7)
    assert abs(res["exactitud_decididas"] - (5.0 / 7.0)) < 1e-4

    # Intervalos de Wilson presentes y acotados
    for clave_ci in [
        "exactitud_con_abstencion_ci",
        "tasa_abstencion_ci",
        "tasa_errores_alta_confianza_ci",
        "exactitud_decididas_ci",
    ]:
        ci = res[clave_ci]
        assert isinstance(ci, list) and len(ci) == 2
        assert 0.0 <= ci[0] <= ci[1] <= 1.0

    # Lista de errores con alta confianza
    lista_err = res["lista_errores_alta_confianza"]
    assert len(lista_err) == 2
    for err in lista_err:
        assert err["confianza"] >= 0.80
        assert err["clase_real"] != err["clase_predicha"]
