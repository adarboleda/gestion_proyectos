"""Rutas de los datasets reales de IA-Nuclear para las pruebas que los usan.

La raíz se toma de la variable de entorno ``IANUCLEAR_DATOS``; si no está, de ``../IA-Nuclear``
respecto de la raíz del repositorio. Las pruebas que dependen de estas rutas se omiten si no existen.
"""
import os
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parents[1]


def raiz_ianuclear() -> Path:
    configurada = os.environ.get("IANUCLEAR_DATOS", "").strip()
    if configurada:
        return Path(configurada).expanduser().resolve()
    return (RAIZ_REPOSITORIO / ".." / "IA-Nuclear").resolve()


def ruta_pwr3l() -> Path:
    return raiz_ianuclear() / "PWR 3L"


def ruta_nppad() -> Path:
    return raiz_ianuclear() / "NuclearPowerPlantAccidentData" / "Operation_csv_data"
