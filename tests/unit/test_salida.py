"""Pruebas de la publicación de artefactos: todos juntos o ninguno, sin tocar archivos ajenos."""
import os

import numpy as np
import pytest

from preparacion_datos import salida as modulo
from preparacion_datos.salida import publicar


def contenido(directorio):
    return {a.name: a.read_bytes() for a in sorted(directorio.iterdir()) if a.is_file()}


def nuevos():
    return {
        "A.npy": np.arange(3),
        "B.npy": np.arange(4),
        "C.npy": np.arange(5),
        "D.npy": np.arange(6),
        "meta.json": '{"k": 1}\n',
    }


def preparar_salida_previa(salida):
    salida.mkdir()
    for nombre in ("A.npy", "B.npy", "C.npy"):
        (salida / nombre).write_bytes(f"viejo-{nombre}".encode())
    (salida / "ajeno.txt").write_text("no tocar")


def test_publica_todos_los_archivos_y_no_deja_temporales(tmp_path):
    salida = tmp_path / "salida"
    publicar(salida, nuevos())
    assert sorted(a.name for a in salida.iterdir()) == ["A.npy", "B.npy", "C.npy", "D.npy", "meta.json"]
    np.testing.assert_array_equal(np.load(salida / "C.npy"), np.arange(5))
    assert (salida / "meta.json").read_text(encoding="utf-8") == '{"k": 1}\n'
    assert [a.name for a in tmp_path.iterdir()] == ["salida"]


def test_reemplaza_solo_los_publicados_y_conserva_los_ajenos(tmp_path):
    salida = tmp_path / "salida"
    preparar_salida_previa(salida)
    publicar(salida, nuevos())
    assert (salida / "ajeno.txt").read_text() == "no tocar"
    np.testing.assert_array_equal(np.load(salida / "A.npy"), np.arange(3))


@pytest.mark.parametrize("falla_en", range(1, 9))
def test_un_fallo_a_mitad_de_la_publicacion_restaura_la_salida_previa(tmp_path, monkeypatch, falla_en):
    salida = tmp_path / "salida"
    preparar_salida_previa(salida)
    antes = contenido(salida)
    real = os.replace
    llamadas = []

    def replace_con_fallo(origen, destino):
        llamadas.append(1)
        if len(llamadas) == falla_en:
            raise OSError("fallo simulado")
        return real(origen, destino)

    monkeypatch.setattr(modulo.os, "replace", replace_con_fallo)
    try:
        publicar(salida, nuevos())
    except OSError:
        pass
    else:
        # Con menos movimientos que `falla_en` la publicación termina bien: nada que restaurar.
        assert len(llamadas) < falla_en
        return
    assert contenido(salida) == antes
    assert [a.name for a in tmp_path.iterdir()] == ["salida"]


def test_un_fallo_sin_salida_previa_no_deja_la_carpeta_creada(tmp_path, monkeypatch):
    salida = tmp_path / "salida"
    real = os.replace
    llamadas = []

    def replace_con_fallo(origen, destino):
        llamadas.append(1)
        if len(llamadas) == 3:
            raise OSError("fallo simulado")
        return real(origen, destino)

    monkeypatch.setattr(modulo.os, "replace", replace_con_fallo)
    with pytest.raises(OSError):
        publicar(salida, nuevos())
    assert not salida.exists()
    assert [a.name for a in tmp_path.iterdir()] == []
