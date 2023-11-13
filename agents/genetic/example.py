import random
import numpy as np
import networkx as nx

# Definir las acciones disponibles y las restricciones de dependencia
acciones_disponibles = ['A', 'B', 'C', 'D', 'E']
restricciones = {
    'B': 'A',
    'C': 'B',
    'D': 'C',
    'E': 'D'
}

# Parámetros del algoritmo genético
tamano_poblacion = 100
num_generaciones = 100
probabilidad_mutacion = 0.1

# Función de evaluación: Calcular la puntuación de una secuencia
def evaluar_secuencia(secuencia):
    # Aquí debes definir cómo se califica una secuencia en función de tus objetivos
    # En este ejemplo, simplemente contaremos la cantidad de 'A' en la secuencia
    return secuencia.count('A')

# Inicialización de la población
poblacion = [''.join(random.choices(acciones_disponibles, k=len(acciones_disponibles))) for _ in range(tamano_poblacion)]

# Ciclo de generaciones
for generacion in range(num_generaciones):
    # Evaluar la aptitud de cada individuo en la población
    puntuaciones = [evaluar_secuencia(individuo) for individuo in poblacion]

    # Seleccionar a los mejores individuos
    mejores_indices = np.argsort(puntuaciones)[-tamano_poblacion:]
    poblacion = [poblacion[i] for i in mejores_indices]

    # Cruzar a los individuos para crear una nueva generación
    nueva_generacion = []
    while len(nueva_generacion) < tamano_poblacion:
        padre = random.choice(poblacion)
        madre = random.choice(poblacion)
        punto_cruce = random.randint(1, len(acciones_disponibles) - 1)
        hijo = padre[:punto_cruce] + madre[punto_cruce:]
        
        # Verificar y corregir las restricciones de dependencia
        grafo = nx.DiGraph()
        for accion in hijo:
            grafo.add_node(accion)
        for i in range(1, len(hijo)):
            grafo.add_edge(hijo[i - 1], hijo[i])
        for accion, accion_dependiente in restricciones.items():
            if nx.has_path(grafo, source=accion, target=accion_dependiente):
                continue
            # Corregir la restricción moviendo la acción dependiente
            pos_accion_dependiente = hijo.index(accion_dependiente)
            pos_accion = hijo.index(accion)
            hijo = hijo[:pos_accion] + hijo[pos_accion + 1:pos_accion_dependiente] + accion + hijo[pos_accion_dependiente:]

        nueva_generacion.append(hijo)

    poblacion = nueva_generacion

    # Aplicar mutaciones
    for i in range(tamano_poblacion):
        if random.random() < probabilidad_mutacion:
            indice_mutation = random.randint(0, len(acciones_disponibles) - 1)
            poblacion[i] = poblacion[i][:indice_mutation] + random.choice(acciones_disponibles) + poblacion[i][indice_mutation + 1:]

# Encontrar la mejor secuencia
mejor_secuencia = max(poblacion, key=evaluar_secuencia)
mejor_puntuacion = evaluar_secuencia(mejor_secuencia)

print("Mejor secuencia encontrada:", mejor_secuencia)
print("Puntuación de la mejor secuencia:", mejor_puntuacion)

