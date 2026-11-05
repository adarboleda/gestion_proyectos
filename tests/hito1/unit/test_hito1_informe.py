"""Markdown del Hito 1."""
from informe_hito1.consolidar import consolidar
from informe_hito1.informe import SECCIONES, formatear_markdown


def _texto(datos):
    hito = consolidar(datos)
    hito["fuentes"] = [{"clave": "etapa1", "kan": "KAN-23", "responsable": "Abner Arboleda", "comando": "entrenar-etapa1",
                        "archivo": "modelos/etapa1/reporte.json", "sha256": "abc"}]
    return formatear_markdown(hito)


def test_once_secciones_en_orden(datos):
    texto = _texto(datos)
    posiciones = [texto.index(f"## {s}") for s in SECCIONES]
    assert posiciones == sorted(posiciones) and len(SECCIONES) == 11


def test_aviso_al_principio(datos):
    primeras = "\n".join(_texto(datos).splitlines()[:6])
    assert "consultiv" in primeras.lower()


def test_cada_seccion_de_datos_cita_su_kan(datos):
    texto = _texto(datos)
    for kan in ("KAN-22", "KAN-23", "KAN-24", "KAN-25", "KAN-26"):
        assert kan in texto


def test_tablas_con_los_valores_de_la_fuente(datos):
    texto = _texto(datos)
    assert "| NORM | 1107 | 0 | 12 | 74 |" in texto
    assert "10 de 10 (100 %)" in texto and "cumple sin decisiones (cobertura 0 %)" in texto
    assert "19.3 %" in texto and "R54" in texto


def test_validacion_cruzada_dice_que_reentrena(datos):
    texto = _texto(datos)
    assert "reentrena" in texto and "modelo publicado" in texto


def test_concordancia_y_nombres_legibles(datos):
    texto = _texto(datos)
    assert "1 falsa alarma (R54)" in texto and "1 falsas alarmas" not in texto
    assert "| Tasa de abstención | 32.8 % |" in texto and "tasa abstencion" not in texto
