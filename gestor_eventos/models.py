"""Modelos principales para la gestión de eventos científicos."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class Ciudad:
    """Representa una ciudad donde se desarrolla un evento."""

    nombre: str
    pais: str
    latitud: float
    longitud: float
    _descripcion: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        self.nombre = self.nombre.title().strip()
        self.pais = self.pais.title().strip()
        self.descripcion = self._descripcion

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        self._descripcion = (valor or "").strip()

    def actualizar_descripcion(self, nueva_descripcion: str) -> None:
        self.descripcion = nueva_descripcion

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nombre": self.nombre,
            "pais": self.pais,
            "latitud": self.latitud,
            "longitud": self.longitud,
            "descripcion": self.descripcion,
        }

    @classmethod
    def desde_dict(cls, data: Dict[str, Any]) -> "Ciudad":
        return cls(
            nombre=data["nombre"],
            pais=data["pais"],
            latitud=float(data["latitud"]),
            longitud=float(data["longitud"]),
            _descripcion=data.get("descripcion", ""),
        )

    def __str__(self) -> str:
        return f"{self.nombre}, {self.pais} ({self.latitud}, {self.longitud})"


class Evento:
    """Evento genérico con control de encapsulamiento para capacidad y asistentes."""

    def __init__(
        self,
        titulo: str,
        fecha: datetime,
        ciudad: Ciudad,
        capacidad_maxima: int,
        categoria: str = "general",
        asistentes_registrados: int = 0,
    ) -> None:
        if not isinstance(fecha, datetime):
            fecha = datetime.fromisoformat(str(fecha))
        self.titulo = titulo
        self.fecha = fecha
        self.ciudad = ciudad
        self.categoria = categoria
        self._asistentes_registrados = 0
        self._capacidad_maxima = 0
        self.capacidad_maxima = capacidad_maxima
        self.asistentes_registrados = asistentes_registrados

    @property
    def capacidad_maxima(self) -> int:
        return self._capacidad_maxima

    @capacidad_maxima.setter
    def capacidad_maxima(self, valor: int) -> None:
        if valor <= 0:
            raise ValueError("La capacidad máxima debe ser positiva.")
        self._capacidad_maxima = valor
        if self._asistentes_registrados > valor:
            self._asistentes_registrados = valor

    @property
    def asistentes_registrados(self) -> int:
        return self._asistentes_registrados

    @asistentes_registrados.setter
    def asistentes_registrados(self, valor: int) -> None:
        if valor < 0:
            raise ValueError("La cantidad de asistentes no puede ser negativa.")
        if valor > self.capacidad_maxima:
            raise ValueError("No se pueden registrar más asistentes que la capacidad máxima.")
        self._asistentes_registrados = valor

    def registrar_asistentes(self, cantidad: int) -> None:
        nueva_cantidad = self.asistentes_registrados + cantidad
        self.asistentes_registrados = nueva_cantidad

    @property
    def cupos_disponibles(self) -> int:
        return self.capacidad_maxima - self.asistentes_registrados

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tipo": self.__class__.__name__,
            "titulo": self.titulo,
            "fecha": self.fecha.isoformat(),
            "ciudad": self.ciudad.to_dict(),
            "capacidad_maxima": self.capacidad_maxima,
            "asistentes_registrados": self.asistentes_registrados,
            "categoria": self.categoria,
        }

    @classmethod
    def desde_dict(cls, data: Dict[str, Any]) -> "Evento":
        ciudad = Ciudad.desde_dict(data["ciudad"])
        return cls(
            titulo=data["titulo"],
            fecha=datetime.fromisoformat(data["fecha"]),
            ciudad=ciudad,
            capacidad_maxima=int(data["capacidad_maxima"]),
            categoria=data.get("categoria", "general"),
            asistentes_registrados=int(data["asistentes_registrados"]),
        )

    def __str__(self) -> str:
        return (
            f"{self.titulo} en {self.ciudad.nombre} el {self.fecha.date()} "
            f"({self.asistentes_registrados}/{self.capacidad_maxima} asistentes)"
        )


class Conferencia(Evento):
    """Especialización de Evento que agrega ponentes y temática."""

    def __init__(
        self,
        titulo: str,
        fecha: datetime,
        ciudad: Ciudad,
        capacidad_maxima: int,
        tematica: str,
        ponentes: List[str] | None = None,
        modalidad: str = "presencial",
        asistentes_registrados: int = 0,
    ) -> None:
        super().__init__(
            titulo=titulo,
            fecha=fecha,
            ciudad=ciudad,
            capacidad_maxima=capacidad_maxima,
            categoria="conferencia",
            asistentes_registrados=asistentes_registrados,
        )
        self.tematica = tematica
        self.ponentes = ponentes or []
        self.modalidad = modalidad

    def agregar_ponente(self, nombre: str) -> None:
        if nombre not in self.ponentes:
            self.ponentes.append(nombre)

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "tematica": self.tematica,
            "ponentes": self.ponentes,
            "modalidad": self.modalidad,
        })
        return data

    @classmethod
    def desde_dict(cls, data: Dict[str, Any]) -> "Conferencia":
        ciudad = Ciudad.desde_dict(data["ciudad"])
        return cls(
            titulo=data["titulo"],
            fecha=datetime.fromisoformat(data["fecha"]),
            ciudad=ciudad,
            capacidad_maxima=int(data["capacidad_maxima"]),
            tematica=data.get("tematica", ""),
            ponentes=list(data.get("ponentes", [])),
            modalidad=data.get("modalidad", "presencial"),
            asistentes_registrados=int(data["asistentes_registrados"]),
        )
