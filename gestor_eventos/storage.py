"""Funciones de persistencia en archivos JSON y base de datos SQLite."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable, List, Sequence

from .models import Ciudad, Conferencia, Evento

BASE_DIR = Path(__file__).resolve().parent.parent
DATOS_DIR = BASE_DIR / "datos"
DATOS_DIR.mkdir(parents=True, exist_ok=True)

RUTA_JSON = DATOS_DIR / "eventos.json"
RUTA_DB = DATOS_DIR / "eventos.db"


def exportar_eventos_a_json(eventos: Iterable[Evento], ruta: Path | str = RUTA_JSON) -> Path:
    """Guarda la colección completa de eventos en un archivo JSON."""

    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    data = [evento.to_dict() for evento in eventos]
    ruta.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return ruta


def cargar_eventos_de_json(ruta: Path | str = RUTA_JSON) -> List[Evento]:
    """Carga eventos desde un archivo JSON si existe; en caso contrario devuelve lista vacía."""

    ruta = Path(ruta)
    if not ruta.exists():
        return []
    data = json.loads(ruta.read_text(encoding="utf-8"))
    eventos: List[Evento] = []
    for item in data:
        tipo = item.get("tipo", "Evento")
        if tipo == "Conferencia":
            eventos.append(Conferencia.desde_dict(item))
        else:
            eventos.append(Evento.desde_dict(item))
    return eventos


def inicializar_db(ruta: Path | str = RUTA_DB) -> None:
    """Crea las tablas necesarias en la base de datos SQLite."""

    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(ruta) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS ciudades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                pais TEXT NOT NULL,
                latitud REAL NOT NULL,
                longitud REAL NOT NULL,
                descripcion TEXT DEFAULT "",
                UNIQUE(nombre, pais)
            );

            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                fecha TEXT NOT NULL,
                categoria TEXT NOT NULL,
                capacidad_maxima INTEGER NOT NULL,
                asistentes_registrados INTEGER NOT NULL,
                ciudad_id INTEGER NOT NULL,
                datos_extra TEXT,
                FOREIGN KEY(ciudad_id) REFERENCES ciudades(id)
            );
            """
        )


def _obtener_id_ciudad(conn: sqlite3.Connection, ciudad: Ciudad) -> int:
    conn.execute(
        """
        INSERT INTO ciudades(nombre, pais, latitud, longitud, descripcion)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(nombre, pais) DO UPDATE SET
            latitud=excluded.latitud,
            longitud=excluded.longitud,
            descripcion=excluded.descripcion;
        """,
        (ciudad.nombre, ciudad.pais, ciudad.latitud, ciudad.longitud, ciudad.descripcion),
    )
    conn.commit()
    cursor = conn.execute(
        "SELECT id FROM ciudades WHERE nombre = ? AND pais = ?",
        (ciudad.nombre, ciudad.pais),
    )
    row = cursor.fetchone()
    if row is None:
        raise RuntimeError("No fue posible obtener el id de la ciudad.")
    return int(row[0])


def guardar_ciudad_en_db(ciudad: Ciudad, ruta: Path | str = RUTA_DB) -> int:
    """Inserta o actualiza una ciudad y devuelve su id."""

    ruta = Path(ruta)
    with sqlite3.connect(ruta) as conn:
        return _obtener_id_ciudad(conn, ciudad)


def guardar_evento_en_db(evento: Evento, ruta: Path | str = RUTA_DB) -> int:
    """Inserta un evento y devuelve su id."""

    ruta = Path(ruta)
    with sqlite3.connect(ruta) as conn:
        ciudad_id = _obtener_id_ciudad(conn, evento.ciudad)
        datos_extra = {}
        if isinstance(evento, Conferencia):
            datos_extra = {
                "tematica": evento.tematica,
                "ponentes": evento.ponentes,
                "modalidad": evento.modalidad,
            }
        cursor = conn.execute(
            """
            INSERT INTO eventos(
                titulo, fecha, categoria, capacidad_maxima,
                asistentes_registrados, ciudad_id, datos_extra
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (
                evento.titulo,
                evento.fecha.isoformat(),
                evento.categoria,
                evento.capacidad_maxima,
                evento.asistentes_registrados,
                ciudad_id,
                json.dumps(datos_extra, ensure_ascii=False),
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def _crear_ciudad_desde_row(row: Sequence) -> Ciudad:
    return Ciudad(
        nombre=row[1],
        pais=row[2],
        latitud=float(row[3]),
        longitud=float(row[4]),
        _descripcion=row[5] or "",
    )


def listar_ciudades_db(ruta: Path | str = RUTA_DB) -> List[Ciudad]:
    """Recupera todas las ciudades almacenadas."""

    ruta = Path(ruta)
    with sqlite3.connect(ruta) as conn:
        rows = conn.execute(
            "SELECT id, nombre, pais, latitud, longitud, descripcion FROM ciudades"
        ).fetchall()
    return [_crear_ciudad_desde_row(row) for row in rows]


def listar_eventos_db(ruta: Path | str = RUTA_DB) -> List[Evento]:
    """Recupera todos los eventos junto a sus ciudades."""

    ruta = Path(ruta)
    with sqlite3.connect(ruta) as conn:
        rows = conn.execute(
            """
            SELECT e.id, e.titulo, e.fecha, e.categoria,
                   e.capacidad_maxima, e.asistentes_registrados,
                   e.datos_extra,
                   c.id, c.nombre, c.pais, c.latitud, c.longitud, c.descripcion
            FROM eventos e
            JOIN ciudades c ON c.id = e.ciudad_id
            ORDER BY e.fecha ASC;
            """
        ).fetchall()

    eventos: List[Evento] = []
    for row in rows:
        ciudad = Ciudad(
            nombre=row[8],
            pais=row[9],
            latitud=float(row[10]),
            longitud=float(row[11]),
            _descripcion=row[12] or "",
        )
        datos_extra = json.loads(row[6] or "{}")
        if row[3] == "conferencia":
            evento = Conferencia(
                titulo=row[1],
                fecha=row[2],
                ciudad=ciudad,
                capacidad_maxima=int(row[4]),
                tematica=datos_extra.get("tematica", ""),
                ponentes=list(datos_extra.get("ponentes", [])),
                modalidad=datos_extra.get("modalidad", "presencial"),
                asistentes_registrados=int(row[5]),
            )
        else:
            evento = Evento(
                titulo=row[1],
                fecha=row[2],
                ciudad=ciudad,
                capacidad_maxima=int(row[4]),
                categoria=row[3],
                asistentes_registrados=int(row[5]),
            )
        eventos.append(evento)
    return eventos
