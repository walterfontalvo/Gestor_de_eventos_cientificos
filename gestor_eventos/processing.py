"""Funciones de procesamiento funcional sobre colecciones de eventos."""

from __future__ import annotations

from datetime import datetime
from functools import reduce
from typing import Iterable, List

from .models import Evento


def filtrar_eventos_por_ciudad(eventos: Iterable[Evento], nombre_ciudad: str) -> List[Evento]:
    """Devuelve los eventos que pertenecen a una ciudad concreta usando filter."""

    ciudad_normalizada = nombre_ciudad.strip().lower()
    return list(filter(lambda e: e.ciudad.nombre.lower() == ciudad_normalizada, eventos))


def ordenar_eventos_por_fecha(eventos: Iterable[Evento], descendente: bool = False) -> List[Evento]:
    """Ordena eventos por fecha usando sorted y funciones lambda."""

    return sorted(eventos, key=lambda e: e.fecha, reverse=descendente)


def resumen_asistentes(eventos: Iterable[Evento]) -> dict:
    """Genera un resumen usando map y reduce."""

    eventos_lista = list(eventos)
    total_eventos = len(eventos_lista)
    total_asistentes = reduce(
        lambda acc, valor: acc + valor,
        map(lambda e: e.asistentes_registrados, eventos_lista),
        0,
    )
    capacidad_total = reduce(
        lambda acc, valor: acc + valor,
        map(lambda e: e.capacidad_maxima, eventos_lista),
        0,
    )
    porcentaje_ocupacion = (
        (total_asistentes / capacidad_total * 100) if capacidad_total else 0.0
    )

    ciudades = list({e.ciudad.nombre for e in eventos_lista})

    return {
        "total_eventos": total_eventos,
        "total_asistentes": total_asistentes,
        "capacidad_total": capacidad_total,
        "porcentaje_ocupacion": round(porcentaje_ocupacion, 2),
        "ciudades": ciudades,
    }


def eventos_entre_fechas(
    eventos: Iterable[Evento], fecha_inicio: datetime, fecha_fin: datetime
) -> List[Evento]:
    """Devuelve los eventos cuya fecha está dentro del rango proporcionado."""

    return list(
        filter(
            lambda e: fecha_inicio <= e.fecha <= fecha_fin,
            eventos,
        )
    )
