"""Extremo a extremo de informe-hito1 con resultados sintéticos."""
import json
import subprocess
import sys
from pathlib import Path

from informe_hito1.cli import _crear_parser, main


def _argumentos(resultados, salida):
    return ["--etapa1", str(resultados["etapa1"]), "--regla", str(resultados["regla"]), "--tiempos", str(resultados["tiempos"]),
            "--etapa2", str(resultados["etapa2"]), "--diagnostico", str(resultados["diagnostico"]), "--salida", str(salida)]


def test_publica_md_y_json_con_sha256(resultados, tmp_path):
    salida = tmp_path / "informe"
    assert main(_argumentos(resultados, salida)) == 0
    hito = json.loads((salida / "hito1.json").read_text(encoding="utf-8"))
    assert len(hito["fuentes"]) == 6 and all(len(f["sha256"]) == 64 for f in hito["fuentes"])
    assert (salida / "hito1.md").read_text(encoding="utf-8").startswith("# Hito 1")


def test_mismo_json_en_dos_ejecuciones(resultados, tmp_path):
    assert main(_argumentos(resultados, tmp_path / "a")) == 0
    assert main(_argumentos(resultados, tmp_path / "b")) == 0
    assert (tmp_path / "a" / "hito1.json").read_bytes() == (tmp_path / "b" / "hito1.json").read_bytes()


def test_falta_una_fuente_codigo_1_sin_salida(resultados, tmp_path, capsys):
    (resultados["diagnostico"] / "evaluacion_diagnostico.json").unlink()
    assert main(_argumentos(resultados, tmp_path / "s")) == 1
    assert "evaluar-diagnostico" in capsys.readouterr().err
    assert not (tmp_path / "s").exists()


def test_valores_por_defecto():
    a = _crear_parser().parse_args([])
    assert (a.etapa1, a.regla, a.tiempos, a.etapa2, a.diagnostico, a.salida) == (
        "modelos/etapa1", "resultados_regla_atws", "resultados_tiempo_deteccion", "modelos/etapa2",
        "resultados_evaluacion_diagnostico", "informe_hito1")


def test_python_m(resultados, tmp_path):
    raiz = Path(__file__).resolve().parents[3]
    r = subprocess.run([sys.executable, "-m", "informe_hito1", *_argumentos(resultados, tmp_path / "s")],
                       cwd=raiz, capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, r.stderr
