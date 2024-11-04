import mathutils

"""
interpola.py

Algoritmos de interpolación

Autores: Grupo 5.


"""

def lineal(t: float,t0: float,t1: float ,x0: float ,x1: float):
    
    pos = x0 + (t - t0)/(t1 - t0)*(x1 - x0)
    
    return pos

def catmull_rom(t: float, t0: float, t1: float, t2: float, t3: float, 
                p0: float, p1: float, p2: float, p3: float, tension: float):

    # Normalización de u
    u = (t - t1) / (t2 - t1)
    
    # Vector de potencias de u
    U = mathutils.Vector([u**3, u**2, u, 1])
    
    # Matriz modificada de Catmull-Rom
    M = mathutils.Matrix([
        [-tension, 2 - tension, tension - 2, tension],
        [2 * tension, tension - 3, 3 - 2 * tension, -tension],
        [-tension, 0, tension, 0],
        [0, 1, 0, 0]
    ])
    
    # Vector de posiciones
    B = mathutils.Vector([p0, p1, p2, p3])
    
    # Producto escalar y matricial para el cálculo del polinomio de Catmull-Rom
    C = U @ M @ B
    
    return C


def hermite(t: float, t0: float, t1: float, p0: float, p1: float, v0: float, v1: float):
    """Interpolación Hermite usando álgebra lineal y vectores"""

    # Verifica que t0 y t1 no sean iguales para evitar división por cero
    if t0 == t1:
        raise ValueError("t0 y t1 no pueden ser iguales para la interpolación.")

    # Normalización de t en el intervalo [t0, t1]
    t_norm = (t - t0) / (t1 - t0)

    # Vector de potencias de t_norm
    T = mathutils.Vector([t_norm**3, t_norm**2, t_norm, 1])

    # Matriz base de Hermite
    H = mathutils.Matrix([
        [2, -2, 1, 1],
        [-3, 3, -2, -1],
        [0, 0, 1, 0],
        [1, 0, 0, 0]
    ])

    # Vector de posiciones y tangentes (tangentes escaladas por la duración del intervalo)
    P = mathutils.Vector([p0, p1, v0 * (t1 - t0), v1 * (t1 - t0)])

    # Producto escalar y matricial para el cálculo del polinomio de Hermite
    pos = T @ H @ P
    
    return pos


