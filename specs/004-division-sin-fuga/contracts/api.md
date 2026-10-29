# Contrato: funciones públicas de la división sin fuga

Interfaz que usará la tarea KAN-18 (comando `preparar-pwr3l`) y comportamiento añadido a `preparar-datos`.

## `preparacion_pwr3l.grupos`

```text
formar_grupos(corridas: list[Corrida]) -> list[Grupo]
```

- Acepta todas las corridas de `lectura.cargar_corridas`; ignora las que no son `usable`.
- Devuelve los grupos ordenados por familia (NORM, LOCA, ATWS) y por clave.
- Errores: `ErrorDatos` si una LOCA/LOCAC usable no tiene área; `ValueError` si no hay corridas usables.

## `preparacion_pwr3l.particion`

```text
metas(n: int) -> dict[str, float]                     # {"train": 0.70n, "val": 0.15n, "test": 0.15n}
repartir(grupos: list[Grupo], semilla: int = 42) -> Reparto
```

- Cada grupo completo va a un solo conjunto; reparto por familia, de mayor a menor tamaño, empates sorteados con `semilla`, al conjunto de mayor déficit (desempate train → val → test).
- Mismo resultado con los mismos grupos y semilla, sin importar el orden de la lista.
- Llama a `verificar_reparto` antes de devolver; nunca devuelve un reparto con fuga.
- `Reparto`: ver [data-model.md](../data-model.md).

## `preparacion_pwr3l.verificacion`

```text
verificar_reparto(corridas: list[Corrida], reparto: Reparto) -> None
```

- `corridas`: todas las corridas, incluidas las excluidas.
- Sin violaciones: no devuelve nada. Con violaciones: `ErrorFuga` con todas ellas (reglas a–e de research §4).

## `preparacion_datos.verificacion` (NPPAD)

```text
verificar_particion(particion: dict[str, list[Simulacion]]) -> None
```

- Cada simulación en exactamente un conjunto; LOCA y LOCAC de igual severidad en el mismo conjunto.
- Violaciones: `ErrorFuga` con todas ellas.

## Cambio en `preparar-datos` (001)

- Tras repartir, ejecuta `verificar_particion`. Si hay fuga: mensaje `FUGA DE DATOS: …` en la salida de error, código de salida **1** y ningún artefacto publicado (la salida previa queda intacta).
- Sin fuga: comportamiento, artefactos y reporte idénticos a los de antes.

## Uso previsto por KAN-18

```text
corridas = cargar_corridas(origen)
reparto = repartir(formar_grupos(corridas), semilla)
# construir X/y/margins con reparto.corridas[conjunto]; reporte con reparto.conteos y reparto.grupos
```
