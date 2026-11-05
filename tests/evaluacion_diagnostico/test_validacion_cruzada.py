"""Pruebas unitarias para validación cruzada agrupada sin fuga de información."""
import numpy as np
import pytest

from evaluacion_diagnostico.validacion_cruzada import (
    agregar_metricas_folds,
    particionar_kfold_por_grupos,
)


def test_particionar_kfold_por_grupos_sin_fuga(corridas_sinteticas_pwr3l):
    k = 5
    folds = particionar_kfold_por_grupos(corridas_sinteticas_pwr3l, k=k, semilla=42)
    assert len(folds) == k

    test_corridas_vistas = set()

    for fold_idx, (train_corridas, test_corridas) in enumerate(folds):
        train_ids = {c.id for c in train_corridas}
        test_ids = {c.id for c in test_corridas}
        train_grupos = {c.grupo for c in train_corridas}
        test_grupos = {c.grupo for c in test_corridas}

        # No solapamiento de corridas (principio II)
        assert len(train_ids & test_ids) == 0, f"Fuga de corridas en fold {fold_idx}"

        # No solapamiento de grupos (mismo par LOCA/LOCAC o gemelos en el mismo conjunto)
        assert len(train_grupos & test_grupos) == 0, f"Fuga de grupos en fold {fold_idx}"

        # Cada corrida debe aparecer en test
        assert len(test_ids & test_corridas_vistas) == 0, f"Corrida repetida en test de varios folds"
        test_corridas_vistas.update(test_ids)

    # Cobertura completa de todas las corridas
    assert test_corridas_vistas == {c.id for c in corridas_sinteticas_pwr3l}


def test_agregar_metricas_folds():
    # Resultados sintéticos de 5 folds
    resultados = [
        {"fold": 1, "exactitud_con_abstencion": 0.95, "tasa_abstencion": 0.05, "tasa_errores_alta_confianza": 0.0},
        {"fold": 2, "exactitud_con_abstencion": 0.97, "tasa_abstencion": 0.03, "tasa_errores_alta_confianza": 0.0},
        {"fold": 3, "exactitud_con_abstencion": 0.94, "tasa_abstencion": 0.06, "tasa_errores_alta_confianza": 0.0},
        {"fold": 4, "exactitud_con_abstencion": 0.96, "tasa_abstencion": 0.03, "tasa_errores_alta_confianza": 0.01},
        {"fold": 5, "exactitud_con_abstencion": 0.98, "tasa_abstencion": 0.02, "tasa_errores_alta_confianza": 0.0},
    ]

    resumen = agregar_metricas_folds(resultados)
    assert "exactitud_con_abstencion" in resumen
    assert "tasa_abstencion" in resumen
    assert "tasa_errores_alta_confianza" in resumen

    acc_res = resumen["exactitud_con_abstencion"]
    assert round(acc_res["media"], 3) == 0.960
    assert 0.01 < acc_res["std"] < 0.02
    assert len(acc_res["ci_95"]) == 2
    assert acc_res["ci_95"][0] < acc_res["media"] < acc_res["ci_95"][1]
