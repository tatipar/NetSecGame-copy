import random
import numpy as np

# Definir las acciones disponibles y la longitud máxima de la secuencia
def mapeo_acciones(id_accion):
    mapeo = {
        0: ActionType.ScanNetwork,
        1: ActionType.FindServices,
        2: ActionType.FindData,
        3: ActionType.ExploitService,
        4: ActionType.ExfiltrateData,
        5: ActionType.NoAction
    }    
    # Verificar si el número está en el diccionario y devolver la cadena correspondiente
    try: 
        return mapeo[id_accion]
    except ValueError:
        print("Entrada no válida.")


acciones_disponibles = [0, 1, 2, 3, 4, 5]
longitud_maxima_acciones = 20

# Parámetros del algoritmo genético
tamano_poblacion = 100
num_generaciones = 100
probabilidad_mutacion = 0.1

# Función de evaluación: Calcular la puntuación de una secuencia
# DEFINIR FUNCION DE FITNESS
#def evaluar_secuencia(secuencia):
#    # Aquí debes definir cómo se califica una secuencia en función de tus objetivos
#    # En este ejemplo, simplemente contaremos la cantidad de 'A' en la secuencia
#    return secuencia.count('A')

# Inicialización de la población
poblacion = [random.choices(acciones_disponibles, k=longitud_maxima_acciones) for _ in range(tamano_poblacion)]

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
        punto_cruce = random.randint(1, longitud_maxima_acciones) - 1)
        hijo = padre[:punto_cruce] + madre[punto_cruce:]
        nueva_generacion.append(hijo)
    poblacion = nueva_generacion

    # Aplicar mutaciones
    for i in range(tamano_poblacion):
        if random.random() < probabilidad_mutacion:
            indice_mutation = random.randint(0, longitud_maxima_acciones - 1)
            poblacion[i] = poblacion[i][:indice_mutation] + random.choice(acciones_disponibles) + poblacion[i][indice_mutation + 1:]

# Encontrar la mejor secuencia
mejor_secuencia = max(poblacion, key=evaluar_secuencia)
mejor_puntuacion = evaluar_secuencia(mejor_secuencia)

print("Mejor secuencia encontrada:", mejor_secuencia)
print("Puntuación de la mejor secuencia:", mejor_puntuacion)

