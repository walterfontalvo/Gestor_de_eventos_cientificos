"""Ejemplo de ejecución para la Actividad Final Integradora."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from gestor_eventos import (
    Conferencia,
    Evento,
    RUTA_DB,
    RUTA_JSON,
    cargar_eventos_de_json,
    consultar_clima_ciudades,
    exportar_eventos_a_json,
    filtrar_eventos_por_ciudad,
    guardar_evento_en_db,
    inicializar_db,
    listar_eventos_db,
    ordenar_eventos_por_fecha,
    resumen_asistentes,
)
from gestor_eventos.models import Ciudad


def _crear_eventos_de_muestra() -> list[Evento]:
    bogota = Ciudad("Bogotá", "Colombia", 4.711, -74.072)
    medellin = Ciudad("Medellín", "Colombia", 6.2442, -75.5812)
    quito = Ciudad("Quito", "Ecuador", -0.1807, -78.4678)

    return [
        Conferencia(
            "Ciencia de Datos en Salud",
            datetime.now() + timedelta(days=10),
            bogota,
            capacidad_maxima=350,
            tematica="Salud digital",
            ponentes=["Dra. Ruiz", "Dr. Romero"],
            modalidad="híbrido",
            asistentes_registrados=320,
        ),
        Evento(
            "Taller de Robótica Educativa",
            datetime.now() + timedelta(days=30),
            medellin,
            capacidad_maxima=120,
            categoria="taller",
            asistentes_registrados=95,
        ),
        Conferencia(
            "Simposio Andino de Energías Renovables",
            datetime.now() + timedelta(days=45),
            quito,
            capacidad_maxima=200,
            tematica="Energía limpia",
            ponentes=["Ing. Pérez"],
            asistentes_registrados=150,
        ),
    ]


def preparar_datos() -> list[Evento]:
    eventos = cargar_eventos_de_json()
    if not eventos:
        eventos = _crear_eventos_de_muestra()
        exportar_eventos_a_json(eventos)
    return eventos


def poblar_base_de_datos(eventos: list[Evento]) -> None:
    if RUTA_DB.exists():
        RUTA_DB.unlink()
    inicializar_db()
    for evento in eventos:
        guardar_evento_en_db(evento)


def mostrar_resumen(eventos: list[Evento]) -> None:
    print("\n=== Resumen general de eventos ===")
    resumen = resumen_asistentes(eventos)
    for clave, valor in resumen.items():
        print(f"{clave.replace('_', ' ').title()}: {valor}")

    print("\nEventos en Medellín:")
    for evento in filtrar_eventos_por_ciudad(eventos, "Medellín"):
        print("-", evento)

    print("\nEventos ordenados por fecha:")
    for evento in ordenar_eventos_por_fecha(eventos):
        print("-", evento)


def mostrar_clima(eventos: list[Evento]) -> None:
    ciudades = {evento.ciudad.nombre: evento.ciudad for evento in eventos}
    print("\n=== Consulta concurrente del clima ===")
    resultados = consultar_clima_ciudades(ciudades.values())
    for clave, data in resultados.items():
        if "error" in data:
            print(f"{clave}: Error al consultar -> {data['error']}")
        else:
            print(
                f"{data['ciudad']} ({data['pais']}) - "
                f"{data['temperatura']}°C, viento {data['viento']} km/h"
            )


def main() -> None:
    print("Preparando datos de eventos científicos...")
    eventos = preparar_datos()
    poblar_base_de_datos(eventos)

    print(f"Se guardaron {len(eventos)} eventos en {RUTA_JSON} y {RUTA_DB}.")

    eventos_db = listar_eventos_db()
    mostrar_resumen(eventos_db)
    mostrar_clima(eventos_db)

    print("\nEjecución completada. Revisa la carpeta 'datos' para ver los archivos generados.")


if __name__ == "__main__":
    main()
