"""Pruebas de integración para reporte.py y cli.py de evaluacion_diagnostico."""
import json
from pathlib import Path
import pytest

from evaluacion_diagnostico.reporte import construir_reporte_json, formatear_reporte_texto
import evaluacion_diagnostico.cli as cli


def test_formatear_reporte_y_construir_json():
    val_metrics = {
        "n_muestras": 100,
        "aciertos_con_confianza": 90,
        "exactitud_con_abstencion": 0.90,
        "exactitud_con_abstencion_ci": [0.82, 0.94],
        "abstenciones": 8,
        "tasa_abstencion": 0.08,
        "tasa_abstencion_ci": [0.04, 0.15],
        "errores_alta_confianza": 2,
        "tasa_errores_alta_confianza": 0.02,
        "tasa_errores_alta_confianza_ci": [0.005, 0.07],
        "exactitud_decididas": 0.978,
        "exactitud_decididas_ci": [0.92, 0.99],
        "exactitud_estandar": 0.92,
        "matriz_confusion_3x4": [[30, 0, 0, 2], [0, 30, 1, 3], [0, 1, 30, 3]],
        "col_class_names": ["NORM", "LOCA", "TRANS", "UNCERTAIN"],
        "row_class_names": ["NORM", "LOCA", "TRANS"],
        "lista_errores_alta_confianza": [
            {"indice": 5, "clase_real": "LOCA", "clase_predicha": "TRANS", "confianza": 0.85}
        ],
    }

    test_metrics = dict(val_metrics, n_muestras=80, aciertos_con_confianza=72, exactitud_con_abstencion=0.90)

    cv_summary = {
        "k_folds": 5,
        "semilla": 42,
        "umbral": 0.80,
        "epocas_por_fold": 5,
        "folds": [
            {"fold": 1, "exactitud_con_abstencion": 0.90, "tasa_abstencion": 0.08, "tasa_errores_alta_confianza": 0.02}
        ],
        "resumen": {
            "exactitud_con_abstencion": {"media": 0.91, "std": 0.02, "ci_95": [0.88, 0.94]},
            "tasa_abstencion": {"media": 0.07, "std": 0.01, "ci_95": [0.05, 0.09]},
            "tasa_errores_alta_confianza": {"media": 0.02, "std": 0.01, "ci_95": [0.01, 0.03]},
            "exactitud_decididas": {"media": 0.97, "std": 0.01, "ci_95": [0.95, 0.99]},
            "exactitud_estandar": {"media": 0.93, "std": 0.02, "ci_95": [0.90, 0.96]},
        },
    }

    reporte_dict = construir_reporte_json(val_metrics, test_metrics, cv_summary)
    assert reporte_dict["aviso"]
    assert "validacion" in reporte_dict
    assert "prueba" in reporte_dict
    assert "validacion_cruzada" in reporte_dict

    texto = formatear_reporte_texto(reporte_dict)
    assert "EVALUACIÓN DEL DIAGNÓSTICO" in texto
    assert "Validación" in texto
    assert "Prueba" in texto
    assert "Validación Cruzada" in texto
    assert "UNCERTAIN" in texto
    assert "Wilson" in texto or "IC 95%" in texto


def test_cli_parser_y_salida_en_carpeta(tmp_path, monkeypatch):
    salida = tmp_path / "eval_diag"

    # Mock de ejecucion rápida sin GPU
    def mock_evaluar_completo(*args, **kwargs):
        val = {
            "n_muestras": 10, "aciertos_con_confianza": 8, "exactitud_con_abstencion": 0.8,
            "exactitud_con_abstencion_ci": [0.5, 0.9], "abstenciones": 2, "tasa_abstencion": 0.2,
            "tasa_abstencion_ci": [0.05, 0.5], "errores_alta_confianza": 0, "tasa_errores_alta_confianza": 0.0,
            "tasa_errores_alta_confianza_ci": [0.0, 0.3], "exactitud_decididas": 1.0,
            "exactitud_decididas_ci": [0.6, 1.0], "exactitud_estandar": 0.8,
            "matriz_confusion_3x4": [[3, 0, 0, 1], [0, 3, 0, 1], [0, 0, 2, 0]],
            "col_class_names": ["NORM", "LOCA", "TRANS", "UNCERTAIN"], "row_class_names": ["NORM", "LOCA", "TRANS"],
            "lista_errores_alta_confianza": [],
        }
        test = dict(val)
        cv = {
            "k_folds": 2, "semilla": 42, "umbral": 0.80, "epocas_por_fold": 1,
            "folds": [{"fold": 1, "exactitud_con_abstencion": 0.8, "tasa_abstencion": 0.2, "tasa_errores_alta_confianza": 0.0}],
            "resumen": {
                "exactitud_con_abstencion": {"media": 0.8, "std": 0.0, "ci_95": [0.8, 0.8]},
                "tasa_abstencion": {"media": 0.2, "std": 0.0, "ci_95": [0.2, 0.2]},
                "tasa_errores_alta_confianza": {"media": 0.0, "std": 0.0, "ci_95": [0.0, 0.0]},
            },
        }
        return val, test, cv

    monkeypatch.setattr(cli, "ejecutar_evaluacion_completa", mock_evaluar_completo)

    codigo = cli.main(["--salida", str(salida)])
    assert codigo == 0

    assert (salida / "evaluacion_diagnostico.json").is_file()
    assert (salida / "evaluacion_diagnostico.txt").is_file()

    data = json.loads((salida / "evaluacion_diagnostico.json").read_text(encoding="utf-8"))
    assert data["validacion"]["exactitud_con_abstencion"] == 0.8
    assert "UNCERTAIN" in data["validacion"]["col_class_names"]


def test_cli_falta_torch(monkeypatch):
    monkeypatch.setattr(cli, "_torch_disponible", lambda: False)
    codigo = cli.main([])
    assert codigo == 3


def test_cli_error_datos(monkeypatch, tmp_path):
    def mock_fallar(*args, **kwargs):
        raise ValueError("Error simulado de datos")

    monkeypatch.setattr(cli, "ejecutar_evaluacion_completa", mock_fallar)
    codigo = cli.main(["--salida", str(tmp_path / "out")])
    assert codigo == 1


def test_cli_error_escritura(monkeypatch, tmp_path):
    def mock_evaluar(*args, **kwargs):
        return {}, {}, {}

    monkeypatch.setattr(cli, "ejecutar_evaluacion_completa", mock_evaluar)
    monkeypatch.setattr(cli, "publicar", lambda s, a: (_ for _ in ()).throw(OSError("Disco protegido")))
    codigo = cli.main(["--salida", str(tmp_path / "out")])
    assert codigo == 1

