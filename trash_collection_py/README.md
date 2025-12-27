# Trash Collection VRP - Python Implementation

Refactorización del código C++ de recolección de basura municipal a Python.

## Descripción

nuevo texto

Este proyecto implementa un sistema de enrutamiento de vehículos (VRP) para la recolección de basura municipal. El sistema utiliza heurísticas de optimización para encontrar rutas eficientes para una flota de vehículos que deben recolectar basura de contenedores y llevarla a vertederos.

## Estructura del Proyecto

```
trash_collection_py/
├── src/
│   ├── base_classes/      # Clases base (Node, Move, OSRMClient, etc.)
│   ├── problem/           # Clases de problema (ProbTrash, TrashNode)
│   ├── solution/          # Clases de solución (Solution, Vehicle, Trip)
│   ├── initialization/    # Generación de soluciones iniciales
│   ├── optimization/      # Algoritmos de optimización (Tabu Search)
│   └── main.py            # Punto de entrada principal
├── tests/                 # Tests unitarios
├── requirements.txt       # Dependencias Python
└── README.md             # Este archivo
```

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar OSRM (opcional):
   - Instalar y configurar servidor OSRM
   - Establecer variable de entorno: `OSRM_BASE_URL=http://localhost:5000`

## Uso

```bash
python -m src.main <archivo_base>
```

Ejemplo:
```bash
python -m src.main tests/test_data/c_du_rm_cl_02
```

## Formato de Archivos de Entrada

El sistema requiere 4 archivos de entrada:

1. `*.containers.txt`: Contenedores (id, lon, lat, opens, closes, service, demand, street_id)
2. `*.otherlocs.txt`: Depósitos y vertederos (id, lon, lat, opens, closes)
3. `*.vehicles.txt`: Vehículos (vid, start_id, dump_id, end_id, capacity, max_trips, shift_start, shift_end)
4. `*.dmatrix-time.txt`: Matriz de costos (from_id, to_id, cost)

## Características

- Múltiples estrategias de inicialización
- Búsqueda tabú para optimización
- Optimización de flota
- Soporte para ventanas de tiempo
- Restricciones de capacidad
- Múltiples viajes por vehículo

## Notas

Esta es una refactorización del código C++ original. Algunas funcionalidades avanzadas pueden requerir implementación adicional.

