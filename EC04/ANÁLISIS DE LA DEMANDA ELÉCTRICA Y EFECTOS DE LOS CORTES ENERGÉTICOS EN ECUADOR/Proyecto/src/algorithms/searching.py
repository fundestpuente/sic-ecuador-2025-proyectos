"""
Algoritmos de búsqueda para datos energéticos
Incluye búsqueda secuencial y búsqueda binaria
"""

def busqueda_secuencial(lista, objetivo, clave=None):
    """
    Búsqueda secuencial en una lista
    
    Args:
        lista: Lista de elementos a buscar
        objetivo: Elemento a encontrar
        clave: Función para extraer el valor de comparación (opcional)
    
    Returns:
        Índice del elemento encontrado o -1 si no se encuentra
    """
    for i, elemento in enumerate(lista):
        valor = clave(elemento) if clave else elemento
        if valor == objetivo:
            return i
    return -1


def busqueda_secuencial_multiple(lista, objetivo, clave=None):
    """
    Búsqueda secuencial que retorna todos los índices donde se encuentra el objetivo
    
    Args:
        lista: Lista de elementos a buscar
        objetivo: Elemento a encontrar
        clave: Función para extraer el valor de comparación (opcional)
    
    Returns:
        Lista de índices donde se encontró el elemento
    """
    indices = []
    for i, elemento in enumerate(lista):
        valor = clave(elemento) if clave else elemento
        if valor == objetivo:
            indices.append(i)
    return indices


def busqueda_binaria(lista_ordenada, objetivo, clave=None):
    """
    Búsqueda binaria en una lista ordenada
    
    Args:
        lista_ordenada: Lista ordenada de elementos
        objetivo: Elemento a encontrar
        clave: Función para extraer el valor de comparación (opcional)
    
    Returns:
        Índice del elemento encontrado o -1 si no se encuentra
    """
    izquierda = 0
    derecha = len(lista_ordenada) - 1
    
    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        valor_medio = clave(lista_ordenada[medio]) if clave else lista_ordenada[medio]
        
        if valor_medio == objetivo:
            return medio
        elif valor_medio < objetivo:
            izquierda = medio + 1
        else:
            derecha = medio - 1
    
    return -1


def busqueda_binaria_rango(lista_ordenada, inicio, fin, clave=None):
    """
    Búsqueda binaria para encontrar elementos en un rango
    
    Args:
        lista_ordenada: Lista ordenada de elementos
        inicio: Valor de inicio del rango
        fin: Valor de fin del rango
        clave: Función para extraer el valor de comparación (opcional)
    
    Returns:
        Lista de elementos en el rango especificado
    """
    resultado = []
    
    # Encontrar índice de inicio
    idx_inicio = buscar_posicion_insercion(lista_ordenada, inicio, clave)
    
    # Buscar todos los elementos en el rango
    for i in range(idx_inicio, len(lista_ordenada)):
        valor = clave(lista_ordenada[i]) if clave else lista_ordenada[i]
        if valor <= fin:
            resultado.append(lista_ordenada[i])
        else:
            break
    
    return resultado


def buscar_posicion_insercion(lista_ordenada, objetivo, clave=None):
    """
    Encuentra la posición donde se debería insertar un elemento en una lista ordenada
    
    Args:
        lista_ordenada: Lista ordenada de elementos
        objetivo: Elemento a insertar
        clave: Función para extraer el valor de comparación (opcional)
    
    Returns:
        Índice donde se debería insertar el elemento
    """
    izquierda = 0
    derecha = len(lista_ordenada)
    
    while izquierda < derecha:
        medio = (izquierda + derecha) // 2
        valor_medio = clave(lista_ordenada[medio]) if clave else lista_ordenada[medio]
        
        if valor_medio < objetivo:
            izquierda = medio + 1
        else:
            derecha = medio
    
    return izquierda


class BuscadorDatosEnergeticos:
    """
    Clase especializada para buscar datos energéticos
    """
    
    def __init__(self, datos):
        """
        Inicializa el buscador con datos energéticos
        
        Args:
            datos: Lista de diccionarios con datos energéticos
        """
        self.datos = datos
        self.datos_ordenados_fecha = None
        self.datos_ordenados_consumo = None
    
    def buscar_por_region(self, region):
        """Busca todos los datos de una región específica"""
        return [dato for dato in self.datos if dato.get('region') == region]
    
    def buscar_por_fecha(self, fecha):
        """Busca datos de una fecha específica"""
        indices = busqueda_secuencial_multiple(
            self.datos, fecha, 
            clave=lambda x: x.get('fecha')
        )
        return [self.datos[i] for i in indices]
    
    def buscar_por_rango_fechas(self, fecha_inicio, fecha_fin):
        """Busca datos en un rango de fechas usando búsqueda binaria"""
        if not self.datos_ordenados_fecha:
            self._ordenar_por_fecha()
        
        return busqueda_binaria_rango(
            self.datos_ordenados_fecha, 
            fecha_inicio, fecha_fin,
            clave=lambda x: x.get('fecha')
        )
    
    def buscar_por_rango_consumo(self, consumo_min, consumo_max):
        """Busca datos en un rango de consumo"""
        if not self.datos_ordenados_consumo:
            self._ordenar_por_consumo()
        
        return busqueda_binaria_rango(
            self.datos_ordenados_consumo,
            consumo_min, consumo_max,
            clave=lambda x: x.get('consumo', 0)
        )
    
    def buscar_consumo_exacto(self, consumo):
        """Busca datos con un consumo exacto usando búsqueda binaria"""
        if not self.datos_ordenados_consumo:
            self._ordenar_por_consumo()
        
        indice = busqueda_binaria(
            self.datos_ordenados_consumo, 
            consumo,
            clave=lambda x: x.get('consumo', 0)
        )
        
        return self.datos_ordenados_consumo[indice] if indice != -1 else None
    
    def buscar_mayor_consumo(self):
        """Encuentra el registro con mayor consumo"""
        if not self.datos:
            return None
        
        mayor = self.datos[0]
        for dato in self.datos[1:]:
            if dato.get('consumo', 0) > mayor.get('consumo', 0):
                mayor = dato
        return mayor
    
    def buscar_menor_consumo(self):
        """Encuentra el registro con menor consumo"""
        if not self.datos:
            return None
        
        menor = self.datos[0]
        for dato in self.datos[1:]:
            if dato.get('consumo', 0) < menor.get('consumo', 0):
                menor = dato
        return menor
    
    def buscar_cortes_en_fecha(self, fecha):
        """Busca cortes programados en una fecha específica"""
        cortes = []
        for dato in self.datos:
            if (dato.get('fecha_inicio') == fecha or 
                dato.get('fecha_fin') == fecha):
                cortes.append(dato)
        return cortes
    
    def buscar_regiones_afectadas(self, fecha_inicio, fecha_fin):
        """Busca regiones afectadas por cortes en un período"""
        regiones_afectadas = set()
        
        for dato in self.datos:
            fecha_corte = dato.get('fecha_inicio')
            if fecha_corte and fecha_inicio <= fecha_corte <= fecha_fin:
                region = dato.get('unidad_de_negocio')
                if region:
                    regiones_afectadas.add(region)
        
        return list(regiones_afectadas)
    
    def _ordenar_por_fecha(self):
        """Ordena los datos por fecha (método privado)"""
        self.datos_ordenados_fecha = sorted(
            self.datos, 
            key=lambda x: x.get('fecha', ''))
    
    def _ordenar_por_consumo(self):
        """Ordena los datos por consumo (método privado)"""
        self.datos_ordenados_consumo = sorted(
            self.datos,
            key=lambda x: x.get('consumo', 0))


# Ejemplos de uso para el proyecto energético
if __name__ == "__main__":
    # Datos de ejemplo
    datos_energia = [
        {'fecha': '2024-09-15', 'region': 'Guayas', 'consumo': 1500},
        {'fecha': '2024-10-15', 'region': 'Manabi', 'consumo': 800},
        {'fecha': '2024-11-15', 'region': 'El Oro', 'consumo': 600},
        {'fecha': '2024-12-15', 'region': 'Guayas', 'consumo': 1200},
        {'fecha': '2024-08-15', 'region': 'Esmeraldas', 'consumo': 700}
    ]
    
    # Crear buscador
    buscador = BuscadorDatosEnergeticos(datos_energia)
    
    # Ejemplos de búsqueda
    print("=== BÚSQUEDAS SECUENCIALES ===")
    guayas_data = buscador.buscar_por_region('Guayas')
    print(f"Datos de Guayas: {len(guayas_data)} registros")
    
    octubre_data = buscador.buscar_por_fecha('2024-10-15')
    print(f"Datos de octubre: {octubre_data}")
    
    print("\n=== BÚSQUEDAS BINARIAS ===")
    rango_fechas = buscador.buscar_por_rango_fechas('2024-09-01', '2024-11-30')
    print(f"Datos sep-nov 2024: {len(rango_fechas)} registros")
    
    rango_consumo = buscador.buscar_por_rango_consumo(600, 1000)
    print(f"Datos consumo 600-1000: {len(rango_consumo)} registros")
    
    print("\n=== BÚSQUEDAS ESPECIALIZADAS ===")
    mayor_consumo = buscador.buscar_mayor_consumo()
    print(f"Mayor consumo: {mayor_consumo}")
    
    menor_consumo = buscador.buscar_menor_consumo()
    print(f"Menor consumo: {menor_consumo}")
    
    # Ejemplo con lista simple
    consumos = [500, 600, 700, 800, 1200, 1500]
    indice = busqueda_binaria(consumos, 800)
    print(f"Índice de consumo 800: {indice}")