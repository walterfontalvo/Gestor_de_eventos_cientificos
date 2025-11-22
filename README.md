# Proyecto Gestor de Eventos Científicos

El objetivo de este proyecto es gestionar eventos científicos en distintas ciudades, integrando conceptos de POO, concurrencia, paradigmas funcionales, persistencia en archivos y base de datos, consumo de APIs públicas y pruebas automatizadas.

## Estructura principal

```
Gestor_de_eventos_cientificos/
├── datos/
│   ├── eventos.db            # Base de datos SQLite generada
│   └── eventos.json          # Datos de ejemplo en formato JSON
├── gestor_eventos/           # Paquete principal
│   ├── __init__.py
│   ├── models.py             # Clases Ciudad, Evento y Conferencia
│   ├── processing.py         # Utilidades funcionales (map, filter, reduce)
│   ├── storage.py            # Persistencia en JSON y SQLite
│   └── weather.py            # Consulta concurrente a la API de Open-Meteo
├── tests/
│   ├── __init__.py
│   └── test_modelos.py       # Pruebas unitarias con unittest
└── run_demo.py               # Script demostrativo de punta a punta
```

## Requisitos previos

1. Python 3.11+ 
2. Entorno virtual activado (recomendado).
3. Dependencias estándar incluidas en la biblioteca estándar de Python (no se requiere instalar paquetes adicionales).

## Uso

### 1. Ejecutar la demo completa

```
python run_demo.py
```

El script realizará estas acciones:
- Carga o genera datos de eventos de ejemplo.
- Exporta la información a `datos/eventos.json`.
- Inicializa la base `datos/eventos.db` e inserta ciudades y eventos.
- Recupera los eventos desde SQLite y muestra un resumen (filtrado, ordenamiento y estadísticos).
- Consulta concurrentemente el clima usando la API pública [Open-Meteo](https://open-meteo.com/).

### 2. Ejecutar las pruebas unitarias

```
python -m unittest discover -s tests -v
```

Las pruebas cubren la lógica de encapsulamiento, validaciones y herencia de los modelos.

## Notas de diseño

- **POO**: se implementaron las clases `Ciudad`, `Evento` y `Conferencia`, aplicando herencia, encapsulamiento mediante propiedades y métodos específicos para cada tipo.
- **Concurrencia**: se usa `ThreadPoolExecutor` para consultar el clima actual de cada ciudad mediante hilos.
- **Paradigma funcional**: en `processing.py` se emplean `map`, `filter`, `sorted`, `lambda` y `reduce` para manipular colecciones de eventos.
- **Persistencia**: el módulo `storage.py` permite exportar/importar JSON y operar con SQLite (`sqlite3`).
- **API pública**: `weather.py` consume Open-Meteo sin requerir claves.
- **Pruebas**: `tests/test_modelos.py` valida los comportamientos críticos de los modelos.

## Resultados esperados

Tras ejecutar `run_demo.py` deberías ver un resumen en consola y los archivos actualizados en la carpeta `datos/`. Las pruebas unitarias deben finalizar con estado `OK`.
