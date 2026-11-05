"""Pruebas unitarias para validar la existencia y estructura canónica de data_processed/metadata.json."""
import json
from pathlib import Path


def test_metadata_json_existe_y_es_json_valido(ruta_metadata_json: Path):
    assert ruta_metadata_json.is_file(), f"No se encontró el archivo de metadatos en {ruta_metadata_json}"
    contenido = ruta_metadata_json.read_text(encoding="utf-8")
    data = json.loads(contenido)
    assert isinstance(data, dict)


def test_metadata_json_contiene_12_variables_de_entrada(ruta_metadata_json: Path):
    data = json.loads(ruta_metadata_json.read_text(encoding="utf-8"))
    variables_esperadas = [
        "P", "TAVG", "THA", "TCA", "WRCA", "WRCB",
        "LVPZ", "LVCR", "PWNT", "PWR", "WECS", "WLR"
    ]
    assert data.get("selected_features") == variables_esperadas
    assert len(data["selected_features"]) == 12


def test_metadata_json_contiene_7_variables_de_margen_con_categorias(ruta_metadata_json: Path):
    data = json.loads(ruta_metadata_json.read_text(encoding="utf-8"))
    margenes_esperados = ["DNBR", "TPCT", "SCMA", "SCMB", "TSAT", "FRCL", "FRZR"]
    assert data.get("margin_features") == margenes_esperados
    assert len(data["margin_features"]) == 7

    categorias = data.get("margin_feature_categories", {})
    assert set(categorias.keys()) == {"thermal_margins", "damage_indicators"}
    assert categorias["thermal_margins"] == ["DNBR", "TPCT", "SCMA", "SCMB", "TSAT"]
    assert categorias["damage_indicators"] == ["FRCL", "FRZR"]


def test_metadata_json_parametros_temporales_y_clases(ruta_metadata_json: Path):
    data = json.loads(ruta_metadata_json.read_text(encoding="utf-8"))
    assert data.get("class_mapping") == {"NORM": 0, "LOCA": 1, "LOCAC": 2, "ATWS": 3}
    assert data.get("sequence_length") == 150
    assert data.get("time_step_seconds") == 10
    assert data.get("sequence_duration_seconds") == 1500
    assert data.get("split_ratios_target") == {"train": 0.7, "val": 0.15, "test": 0.15}


def test_metadata_json_conteos_de_archivos_y_muestras(ruta_metadata_json: Path):
    data = json.loads(ruta_metadata_json.read_text(encoding="utf-8"))
    assert data.get("file_counts") == {"NORM": 1, "LOCA": 100, "LOCAC": 100, "ATWS": 1}

    sample_counts = data.get("sample_counts", {})
    for clase in ["NORM", "LOCA", "LOCAC", "ATWS"]:
        assert clase in sample_counts
        assert "train" in sample_counts[clase]
        assert "val" in sample_counts[clase]
        assert "test" in sample_counts[clase]

    assert sample_counts["NORM"]["test"] == 0, "NORM debe tener 0 muestras en test por restricción de filas"


def test_metadata_json_declara_limitaciones_conocidas_y_escalador(ruta_metadata_json: Path):
    data = json.loads(ruta_metadata_json.read_text(encoding="utf-8"))
    limitaciones = data.get("known_limitations", [])
    assert isinstance(limitaciones, list)
    assert len(limitaciones) >= 4

    texto_total = " ".join(limitaciones).lower()
    assert "norm" in texto_total
    assert "autocorrelacion" in texto_total or "autocorrelación" in texto_total or "correlacionadas" in texto_total
    assert "desbalance" in texto_total

    escalador = data.get("scaler", {})
    assert escalador.get("fitted_on") == "train_only"

