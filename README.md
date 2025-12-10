Descripción del contenido de la carpeta trash-collection con la version en C++
La carpeta trash-collection contiene un sistema en C++ para resolver un problema de recolección de basura municipal usando heurísticas de enrutamiento de vehículos (VRP).
Estructura del proyecto
baseClasses/: Clases base reutilizables
Node: Punto 2D con coordenadas (x, y)
TwNode, TwPath, TwBucket: Manejo de ventanas de tiempo
OSRMClient: Cliente para OSRM (Open Source Routing Machine)
Move: Representación de movimientos de optimización
Utilidades: logging, estadísticas, timers
baseTrash/: Clases específicas del problema de recolección
Prob_trash: Define el problema (contenedores, depósitos, vertederos, vehículos)
Solution: Representa una solución con flota de vehículos
Trashnode: Nodo con ventana de tiempo y demanda
BaseVehicle, ExtendedVehicle: Representación de vehículos
initTrash/: Generación de soluciones iniciales
TruckManyVisitsDump: Genera soluciones iniciales con múltiples estrategias
BasicOperations: Operaciones básicas de inserción/eliminación de nodos
GivenInitialSol: Carga soluciones iniciales desde archivo
solverTrash/: Algoritmos de optimización
TabuOpt: Búsqueda tabú
FleetOpt: Optimización de la flota
Vehicle, TripVehicle: Representación de vehículos y viajes
OptSol: Solución optimizada
integration/: Puntos de entrada y wrappers
trash.cpp: Programa principal de línea de comandos
trash_pg.cpp: Integración con PostgreSQL
vrptools_wrapper.cpp: Wrapper para extensión de PostgreSQL
Flujo de trabajo implementado
Carga de datos: lee 4 archivos de entrada:
*.containers.txt: Contenedores (id, lon, lat, open, close, service, demand)
*.otherlocs.txt: Depósitos y vertederos (id, lon, lat, open, close)
*.vehicles.txt: Vehículos (vid, start_id, dump_id, end_id, capacity, max_trips, shift_start, shift_end)
*.dmatrix-time.txt: Matriz de costos de viaje (from_id, to_id, cost)
Inicialización del problema (Prob_trash):
Valida datos
Configura nodos fantasma (PhantomNodes) para OSRM
Construye estructuras de datos para ventanas de tiempo
Generación de solución inicial (TruckManyVisitsDump):
Prueba 7 estrategias diferentes
Construye rutas: Depósito → Contenedores → Vertedero → [más contenedores → vertedero] → Depósito
Respeta capacidad, ventanas de tiempo y restricciones
Optimización (TabuOpt):
Búsqueda tabú con movimientos:
Intra-swap (intercambio dentro de una ruta)
Inter-swap (intercambio entre rutas)
Insert (inserción de nodos)
Aspiración tabú
Iteraciones hasta convergencia
Optimización de flota (FleetOpt):
Optimiza el número de vehículos
Reconstruye la flota eliminando vehículos innecesarios
Salida: genera solución en formato para PostgreSQL o texto
Restricciones del problema
Capacidad de vehículos
Ventanas de tiempo para contenedores y vehículos
Múltiples viajes por vehículo (puede visitar el vertedero varias veces)
Depósitos y vertederos con ubicaciones específicas
Sin U-turns (usando OSRM para rutas reales)
Restricciones de topología urbana (vía OSRM)

Descripcion de los archivos de datos de ingreso
Formato del archivo c_du_rm_cl_02.dmatrix-time.txt
380	381	1.2
380	3876	0.383333333333333
380	3881	1.55
380	3895	1.45
380	3928	1.46666666666667
380	3938	1.55
380	3944	1.15
380	3988	0.233333333333333

from_id  to_id  cost (en minutos)

Formato del archivo c_du_rm_cl_02.vehicles.txt
1	1000001	1000002	1000001	20	10000	360	840
2	1000001	1000002	1000001	20	10000	360	840
3	1000001	1000002	1000001	20	10000	360	840

vid  start_id  dump_id  end_id  capacity  max_trips  shift_start  shift_end

Capacidad de carga (unidades de residuo)
Tiempo en minutos desde medianoche cuando el vehículo puede comenzar

Formato del archivo c_du_rm_cl_02.containers.txt
1823	-56.1966389637971	-34.8689860154415	1320	1800	216	1.5	-1
3881	-56.2011012911348	-34.8672619905013	1320	1800	288	1.5	-1
3883	-56.2018310948997	-34.8670624916253	1320	1800	288	1.5	-1
3887	-56.2026568925075	-34.8689903855425	1320	1800	216	1.5	-1
id  x  y  opens  closes  service  demand  street_id

Columna 4 (opens): Hora de apertura de la ventana de tiempo
Tiempo en minutos desde medianoche cuando el contenedor puede ser visitado
Columna 5 (closes): Hora de cierre de la ventana de tiempo
Tiempo en minutos desde medianoche cuando el contenedor debe ser visitado antes de
Columna 6 (service): Tiempo de servicio
Tiempo en minutos requerido para recolectar el contenedor
Columna 7 (demand): Demanda/cantidad de residuos
Cantidad de residuos a recolectar (unidades de capacidad)
Columna 8 (street_id): ID de la calle
Identificador de la calle donde está ubicado el contenedor
Entero, -1 si no está definido

Formato del archivo c_du_rm_cl_02.otherlocs.txt
1000003	-56.0948369999999	-34.848821	0	28800
1000001	-56.12955	-34.89931	0	28800
1000002	-56.09528	-34.84983	0	28800
id  x  y  opens  closes
Columna 4 (opens): Hora de apertura de la ventana de tiempo
Tiempo en minutos desde medianoche cuando la ubicación puede ser usada
Columna 5 (closes): Hora de cierre de la ventana de tiempo
Tiempo en minutos desde medianoche cuando la ubicación debe cerrar
28800 = 20 dias (sin restriccion de tiempo)

