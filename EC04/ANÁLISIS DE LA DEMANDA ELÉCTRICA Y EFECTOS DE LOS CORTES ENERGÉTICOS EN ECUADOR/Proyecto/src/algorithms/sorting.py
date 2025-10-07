"""
Algoritmos de ordenamiento para datos energéticos
Incluye QuickSort, Burbuja, Inserción y otros algoritmos
"""

import time
from functools import wraps

def medir_tiempo(func):
    """Decorador para medir tiempo de ejecución de algoritmos"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = func(*args, **kwargs)
        fin = time.time()
        return resultado
    return wrapper


@medir_tiempo
def quick_sort(lista, clave=None, reverso=False):
    """
    Algoritmo QuickSort para ordenamiento eficiente
    
    Args:
        lista: Lista a ordenar
        clave: Función para extraer el valor de comparación
        reverso: Si True, ordena de mayor a menor
    
    Returns:
        Lista ordenada
    """
    if len(lista) <= 1:
        return lista
    
    def obtener_valor(elemento):
        return clave(elemento) if clave else elemento
    
    pivote = lista[len(lista) // 2]
    valor_pivote = obtener_valor(pivote)
    
    if reverso:
        menores = [x for x in lista if obtener_valor(x) > valor_pivote]
        iguales = [x for x in lista if obtener_valor(x) == valor_pivote]
        mayores = [x for x in lista if obtener_valor(x) < valor_pivote]
    else:
        menores = [x for x in lista if obtener_valor(x) < valor_pivote]
        iguales = [x for x in lista if obtener_valor(x) == valor_pivote]
        mayores = [x for x in lista if obtener_valor(x) > valor_pivote]
    
    return (quick_sort(menores, clave, reverso) + 
            iguales + 
            quick_sort(mayores, clave, reverso))


@medir_tiempo
def bubble_sort(lista, clave=None, reverso=False):
    """
    Algoritmo Burbuja para ordenamiento simple
    
    Args:
        lista: Lista a ordenar
        clave: Función para extraer el valor de comparación
        reverso: Si True, ordena de mayor a menor
    
    Returns:
        Lista ordenada
    """
    n = len(lista)
    lista_copia = lista.copy()
    
    def obtener_valor(elemento):
        return clave(elemento) if clave else elemento
    
    for i in range(n):
        for j in range(0, n - i - 1):
            val_j = obtener_valor(lista_copia[j])
            val_j1 = obtener_valor(lista_copia[j + 1])
            
            if reverso:
                condition = val_j < val_j1
            else:
                condition = val_j > val_j1
            
            if condition:
                lista_copia[j], lista_copia[j + 1] = lista_copia[j + 1], lista_copia[j]
    
    return lista_copia


@medir_tiempo
def insertion_sort(lista, clave=None, reverso=False):
    """
    Algoritmo de Inserción para ordenamiento
    
    Args:
        lista: Lista a ordenar
        clave: Función para extraer el valor de comparación
        reverso: Si True, ordena de mayor a menor
    
    Returns:
        Lista ordenada
    """
    lista_copia = lista.copy()
    
    def obtener_valor(elemento):
        return clave(elemento) if clave else elemento
    
    for i in range(1, len(lista_copia)):
        elemento_actual = lista_copia[i]
        valor_actual = obtener_valor(elemento_actual)
        j = i - 1
        
        while j >= 0:
            valor_j = obtener_valor(lista_copia[j])
            
            if reverso:
                condition = valor_j < valor_actual
            else:
                condition = valor_j > valor_actual
            
            if condition:
                lista_copia[j + 1] = lista_copia[j]
                j -= 1
            else:
                break
        
        lista_copia[j + 1] = elemento_actual
    
    return lista_copia


@medir_tiempo
def selection_sort(lista, clave=None, reverso=False):
    """
    Algoritmo de Selección para ordenamiento
    
    Args:
        lista: Lista a ordenar
        clave: Función para extraer el valor de comparación
        reverso: Si True, ordena de mayor a menor
    
    Returns:
        Lista ordenada
    """
    lista_copia = lista.copy()
    n = len(lista_copia)
    
    def obtener_valor(elemento):
        return clave(elemento) if clave else elemento
    
    for i in range(n):
        indice_extremo = i
        
        for j in range(i + 1, n):
            valor_j = obtener_valor(lista_copia[j])
            valor_extremo = obtener_valor(lista_copia[indice_extremo])
            
            if reverso:
                condition = valor_j > valor_extremo
            else:
                condition = valor_j < valor_extremo
            
            if condition:
                indice_extremo = j
        
        lista_copia[i], lista_copia[indice_extremo] = lista_copia[indice_extremo], lista_copia[i]
    
    return lista_copia


@medir_tiempo
def merge_sort(lista, clave=None, reverso=False):
    """
    Algoritmo Merge Sort para ordenamiento estable
    
    Args:
        lista: Lista a ordenar
        clave: Función para extraer el valor de comparación
        reverso: Si True, ordena de mayor a menor
    
    Returns:
        Lista ordenada
    """
    if len(lista) <= 1:
        return lista
    
    def obtener_valor(elemento):
        return clave(elemento) if clave else elemento
    
    def merge(izquierda, derecha):
        resultado = []
        i = j = 0
        
        while i < len(izquierda) and j < len(derecha):
            val_izq = obtener_valor(izquierda[i])
            val_der = obtener_valor(derecha[j])
            
            if reverso:
                condition = val_izq >= val_der
            else:
                condition = val_izq <= val_der
            
            if condition:
                resultado.append(izquierda[i])
                i += 1
            else:
                resultado.append(derecha[j])
                j += 1
        
        resultado.extend(izquierda[i:])
        resultado.extend(derecha[j:])
        return resultado
    
    medio = len(lista) // 2
    izquierda = merge_sort(lista[:medio], clave, reverso)
    derecha = merge_sort(lista[medio:], clave, reverso)
    
    return merge(izquierda, derecha)


class OrdenadorDatosEnergeticos:
    """
    Clase especializada para ordenar datos energéticos
    """
    
    def __init__(self):
        self.algoritmos = {
            'quick': quick_sort,
            'bubble': bubble_sort,
            'insertion': insertion_sort,
            'selection': selection_sort,
            'merge': merge_sort
        }
    
    def ordenar_por_consumo(self, datos, algoritmo='quick', reverso=False):
        """Ordena datos por consumo energético"""
        if algoritmo not in self.algoritmos:
            raise ValueError(f"Algoritmo {algoritmo} no disponible")
        
        return self.algoritmos[algoritmo](
            datos, 
            clave=lambda x: x.get('consumo', 0),
            reverso=reverso
        )
    
    def ordenar_por_fecha(self, datos, algoritmo='quick', reverso=False):
        """Ordena datos por fecha"""
        if algoritmo not in self.algoritmos:
            raise ValueError(f"Algoritmo {algoritmo} no disponible")
        
        return self.algoritmos[algoritmo](
            datos,
            clave=lambda x: x.get('fecha', ''),
            reverso=reverso
        )
    
    def ordenar_por_region(self, datos, algoritmo='quick', reverso=False):
        """Ordena datos por región"""
        if algoritmo not in self.algoritmos:
            raise ValueError(f"Algoritmo {algoritmo} no disponible")
        
        return self.algoritmos[algoritmo](
            datos,
            clave=lambda x: x.get('region', ''),
            reverso=reverso
        )
    
    def ordenar_por_facturacion(self, datos, algoritmo='quick', reverso=False):
        """Ordena datos por facturación"""
        if algoritmo not in self.algoritmos:
            raise ValueError(f"Algoritmo {algoritmo} no disponible")
        
        return self.algoritmos[algoritmo](
            datos,
            clave=lambda x: x.get('facturacion', 0),
            reverso=reverso
        )
    
    def ordenar_por_clientes(self, datos, algoritmo='quick', reverso=False):
        """Ordena datos por número de clientes"""
        if algoritmo not in self.algoritmos:
            raise ValueError(f"Algoritmo {algoritmo} no disponible")
        
        return self.algoritmos[algoritmo](
            datos,
            clave=lambda x: x.get('clientes', 0),
            reverso=reverso
        )
    
    def comparar_algoritmos(self, datos, campo='consumo'):
        """Compara la velocidad de diferentes algoritmos"""
        print(f"\n=== COMPARACIÓN DE ALGORITMOS - CAMPO: {campo.upper()} ===")
        
        clave_func = lambda x: x.get(campo, 0)
        resultados = {}
        
        for nombre, algoritmo in self.algoritmos.items():
            print(f"\nProbando {nombre.upper()}:")
            inicio = time.time()
            resultado = algoritmo(datos, clave=clave_func)
            fin = time.time()
            
            tiempo = fin - inicio
            resultados[nombre] = {
                'tiempo': tiempo,
                'elementos': len(resultado)
            }
            print(f"Tiempo: {tiempo:.6f} segundos")
        
        # Mostrar ranking
        ranking = sorted(resultados.items(), key=lambda x: x[1]['tiempo'])
        print(f"\n=== RANKING DE VELOCIDAD ===")
        for i, (algoritmo, datos_alg) in enumerate(ranking, 1):
            print(f"{i}. {algoritmo.upper()}: {datos_alg['tiempo']:.6f}s")
        
        return resultados
    
    def obtener_top_consumidores(self, datos, n=10):
        """Obtiene los top N consumidores usando QuickSort"""
        datos_ordenados = self.ordenar_por_consumo(datos, reverso=True)
        return datos_ordenados[:n]
    
    def obtener_regiones_mas_afectadas(self, datos_cortes, n=5):
        """Obtiene las regiones más afectadas por cortes"""
        # Contar cortes por región
        conteo_cortes = {}
        for corte in datos_cortes:
            region = corte.get('unidad_de_negocio', 'Unknown')
            conteo_cortes[region] = conteo_cortes.get(region, 0) + 1
        
        # Convertir a lista de tuplas y ordenar
        lista_regiones = [(region, count) for region, count in conteo_cortes.items()]
        lista_ordenada = quick_sort(lista_regiones, clave=lambda x: x[1], reverso=True)
        
        return lista_ordenada[:n]


# Ejemplos de uso para el proyecto energético
if __name__ == "__main__":
    # Datos de ejemplo
    datos_energia = [
        {'fecha': '2024-09-15', 'region': 'Guayas', 'consumo': 1500, 'facturacion': 200000},
        {'fecha': '2024-10-15', 'region': 'Manabi', 'consumo': 800, 'facturacion': 100000},
        {'fecha': '2024-11-15', 'region': 'El Oro', 'consumo': 600, 'facturacion': 80000},
        {'fecha': '2024-12-15', 'region': 'Esmeraldas', 'consumo': 1200, 'facturacion': 150000},
        {'fecha': '2024-08-15', 'region': 'Santa Elena', 'consumo': 700, 'facturacion': 90000}
    ]
    
    # Crear ordenador
    ordenador = OrdenadorDatosEnergeticos()
    
    print("=== DATOS ORIGINALES ===")
    for dato in datos_energia:
        print(f"Región: {dato['region']}, Consumo: {dato['consumo']}")
    
    print("\n=== ORDENAMIENTO POR CONSUMO (DESCENDENTE) ===")
    datos_ordenados = ordenador.ordenar_por_consumo(datos_energia, reverso=True)
    for dato in datos_ordenados:
        print(f"Región: {dato['region']}, Consumo: {dato['consumo']}")
    
    print("\n=== ORDENAMIENTO POR FECHA ===")
    datos_por_fecha = ordenador.ordenar_por_fecha(datos_energia)
    for dato in datos_por_fecha:
        print(f"Fecha: {dato['fecha']}, Región: {dato['region']}")
    
    print("\n=== TOP 3 CONSUMIDORES ===")
    top_consumidores = ordenador.obtener_top_consumidores(datos_energia, 3)
    for i, dato in enumerate(top_consumidores, 1):
        print(f"{i}. {dato['region']}: {dato['consumo']} MWh")
    
    # Comparar algoritmos con datos más grandes
    datos_grandes = datos_energia * 100  # Simular dataset más grande
    print(f"\n=== PRUEBA CON {len(datos_grandes)} ELEMENTOS ===")
    resultados = ordenador.comparar_algoritmos(datos_grandes)