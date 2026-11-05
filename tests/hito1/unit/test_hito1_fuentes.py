"""Lectura y validación de los archivos de resultados de cada tarea."""
import hashlib
import json

import pytest

from informe_hito1.config import FUENTES
from informe_hito1.fuentes import ErrorFuente, cargar_fuentes


def test_lee_las_cinco_fuentes_con_su_sha256(resultados):
    datos, fuentes = cargar_fuentes(resultados)
    assert set(datos) == set(FUENTES) == {"etapa1", "regla", "tiempos", "etapa2", "diagnostico"}
    assert datos["regla"]["regla"]["umbral_pwnt_pct"] == pytest.approx(19.291046)
    ruta = resultados["tiempos"] / "tiempos.json"
    registro = next(f for f in fuentes if f["archivo"].endswith("tiempos.json"))
    assert registro["sha256"] == hashlib.sha256(ruta.read_bytes()).hexdigest()
    assert registro["kan"] == "KAN-25" and registro["comando"] == "medir-tiempo-deteccion"


def test_archivo_ausente_nombra_el_comando(resultados):
    (resultados["etapa2"] / "reporte.json").unlink()
    with pytest.raises(ErrorFuente) as info:
        cargar_fuentes(resultados)
    assert "reporte.json" in str(info.value) and "entrenar-etapa2" in str(info.value)


def test_json_ilegible(resultados):
    (resultados["diagnostico"] / "evaluacion_diagnostico.json").write_text("{no", encoding="utf-8")
    with pytest.raises(ErrorFuente, match="ilegible"):
        cargar_fuentes(resultados)


def test_falta_una_clave_requerida(resultados):
    ruta = resultados["tiempos"] / "tiempos.json"
    contenido = json.loads(ruta.read_text(encoding="utf-8"))
    del contenido["metas"]
    ruta.write_text(json.dumps(contenido), encoding="utf-8")
    with pytest.raises(ErrorFuente, match="metas"):
        cargar_fuentes(resultados)
