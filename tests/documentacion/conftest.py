"""Configuración y fixtures para pruebas de documentación y metadatos."""
from pathlib import Path
import pytest

RAIZ = Path(__file__).resolve().parents[2]


@pytest.fixture
def raiz_repo() -> Path:
    return RAIZ


@pytest.fixture
def ruta_readme_fase1(raiz_repo: Path) -> Path:
    return raiz_repo / "docs" / "README_FASE1.md"


@pytest.fixture
def ruta_metadata_json(raiz_repo: Path) -> Path:
    return raiz_repo / "data_processed" / "metadata.json"


@pytest.fixture
def ruta_readme_raiz(raiz_repo: Path) -> Path:
    return raiz_repo / "README.md"

