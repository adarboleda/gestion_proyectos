"""Pruebas para validar el contenido, estructura y secciones de docs/README_FASE1.md y su enlace en README.md."""
from pathlib import Path


def test_readme_fase1_existe_y_longitud(ruta_readme_fase1: Path):
    assert ruta_readme_fase1.is_file(), f"No se encontró el archivo {ruta_readme_fase1}"
    lineas = ruta_readme_fase1.read_text(encoding="utf-8").splitlines()
    assert len(lineas) >= 120, f"El README de Fase 1 debe ser exhaustivo y tener al menos 120 líneas (tiene {len(lineas)})"


def test_readme_fase1_contiene_origen_y_licencia(ruta_readme_fase1: Path):
    texto = ruta_readme_fase1.read_text(encoding="utf-8")
    assert "PCTRAN" in texto
    assert "Tsinghua" in texto or "THU-INET" in texto
    assert "NPPAD" in texto
    assert "MIT" in texto
    assert "2022" in texto or "Sci Data" in texto


def test_readme_fase1_contiene_modelo_de_planta(ruta_readme_fase1: Path):
    texto = ruta_readme_fase1.read_text(encoding="utf-8")
    assert "PWR" in texto
    assert "lazo" in texto.lower() or "lazos" in texto.lower()
    assert "RCS" in texto or "primario" in texto.lower()
    assert "presurizador" in texto.lower()
    assert "ECCS" in texto or "emergencia" in texto.lower()


def test_readme_fase1_contiene_catalogo_de_12_variables_y_escalador(ruta_readme_fase1: Path):
    texto = ruta_readme_fase1.read_text(encoding="utf-8")
    variables = ["P", "TAVG", "THA", "TCA", "WRCA", "WRCB", "LVPZ", "LVCR", "PWNT", "PWR", "WECS", "WLR"]
    for var in variables:
        assert f"`{var}`" in texto or f" {var} " in texto or f"| {var} |" in texto, f"Falta variable de entrada {var}"

    assert "StandardScaler" in texto or "normaliz" in texto.lower()
    assert "train" in texto.lower() or "entrenamiento" in texto.lower()


def test_readme_fase1_contiene_catalogo_de_7_margenes_termicos(ruta_readme_fase1: Path):
    texto = ruta_readme_fase1.read_text(encoding="utf-8")
    margenes = ["DNBR", "TPCT", "SCMA", "SCMB", "TSAT", "FRCL", "FRZR"]
    for m in margenes:
        assert f"`{m}`" in texto or f" {m} " in texto or f"| {m} |" in texto, f"Falta variable de margen {m}"

    assert "sin normalizar" in texto.lower() or "unidades físicas" in texto.lower()


def test_readme_fase1_contiene_conteos_y_limitaciones(ruta_readme_fase1: Path):
    texto = ruta_readme_fase1.read_text(encoding="utf-8")
    # Conteos de archivos
    assert "100" in texto  # 100 LOCA y 100 LOCAC
    assert "Normal" in texto or "NORM" in texto
    assert "ATWS" in texto

    # Limitaciones explícitas
    assert "302" in texto or "450" in texto, "Debe citar la restricción de filas de NORM"
    assert "autocorrelaci" in texto.lower(), "Debe citar la autocorrelación temporal en NORM y ATWS"
    assert "desbalance" in texto.lower(), "Debe citar el desbalance de clases"
    assert "secundario" in texto.lower(), "Debe citar el alcance restringido sin variables secundarias"


def test_readme_principal_enlaza_fase1(ruta_readme_raiz: Path):
    assert ruta_readme_raiz.is_file()
    texto = ruta_readme_raiz.read_text(encoding="utf-8")
    assert "README_FASE1.md" in texto or "Fase 1" in texto
