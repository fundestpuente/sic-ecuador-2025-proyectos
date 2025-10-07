"""
Implementación de Memoización para optimizar cálculos costosos en análisis energético
Decoradores y técnicas de caché para mejorar rendimiento
"""

import time
import functools
import hashlib
import json
from typing import Any, Dict, Callable, Tuple
import pickle

class MemoizationDecorator:
    """
    Decorador personalizado para memoización con características avanzadas
    """
    
    def __init__(self, max_size=128, ttl=None, persistent=False):
        """
        Args:
            max_size: Tamaño máximo del caché
            ttl: Tiempo de vida en segundos (None = sin expiración)
            persistent: Si guardar caché en disco
        """
        self.max_size = max_size
        self.ttl = ttl
        self.persistent = persistent
        self.cache = {}
        self.access_times = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Crear clave única para los argumentos
            cache_key = self._make_key(args, kwargs)
            current_time = time.time()
            
            # Verificar si está en caché y no ha expirado
            if cache_key in self.cache:
                cached_time, cached_result = self.cache[cache_key]
                if self.ttl is None or (current_time - cached_time) < self.ttl:
                    self.hit_count += 1
                    self.access_times[cache_key] = current_time
                    return cached_result
                else:
                    # Expirado, eliminar del caché
                    del self.cache[cache_key]
                    del self.access_times[cache_key]
            
            # No está en caché o ha expirado, calcular resultado
            self.miss_count += 1
            result = func(*args, **kwargs)
            
            # Gestionar tamaño del caché (LRU)
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            # Guardar en caché
            self.cache[cache_key] = (current_time, result)
            self.access_times[cache_key] = current_time
            
            return result
        
        # Añadir métodos de utilidad al wrapper
        wrapper.cache_info = lambda: {
            'hits': self.hit_count,
            'misses': self.miss_count,
            'hit_rate': self.hit_count / (self.hit_count + self.miss_count) if (self.hit_count + self.miss_count) > 0 else 0,
            'cache_size': len(self.cache),
            'max_size': self.max_size
        }
        wrapper.cache_clear = lambda: self._clear_cache()
        
        return wrapper
    
    def _make_key(self, args, kwargs):
        """Crear clave única para argumentos"""
        # Combinar args y kwargs en una estructura hasheable
        key_data = (args, tuple(sorted(kwargs.items())))
        key_str = str(key_data)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _evict_lru(self):
        """Eliminar el elemento menos recientemente usado"""
        if not self.access_times:
            return
        
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.cache[lru_key]
        del self.access_times[lru_key]
    
    def _clear_cache(self):
        """Limpiar todo el caché"""
        self.cache.clear()
        self.access_times.clear()
        self.hit_count = 0
        self.miss_count = 0


class EnergyCalculationCache:
    """
    Sistema de caché especializado para cálculos energéticos
    """
    
    def __init__(self):
        self.calculation_cache = {}
        self.computation_times = {}
        
    @MemoizationDecorator(max_size=100, ttl=3600)  # 1 hora TTL
    def calculate_energy_consumption_pattern(self, region_data, time_series, weather_factors):
        """
        Cálculo costoso: Patrón de consumo energético con factores climáticos
        Simula un cálculo complejo que se beneficia de memoización
        """
        print(f"[CICLO] Calculando patrón de consumo para región con {len(time_series)} puntos de datos...")
        
        # Simular cálculo costoso
        time.sleep(0.1)  # Simular procesamiento intensivo
        
        # Algoritmo complejo simulado
        base_consumption = sum(region_data.get('historical_consumption', [100, 120, 95, 110]))
        
        # Factor de temperatura
        temp_factor = 1.0
        if 'temperature' in weather_factors:
            avg_temp = sum(weather_factors['temperature']) / len(weather_factors['temperature'])
            if avg_temp > 25:  # Calor -> más AC
                temp_factor = 1.2 + (avg_temp - 25) * 0.02
            elif avg_temp < 15:  # Frío -> más calefacción
                temp_factor = 1.1 + (15 - avg_temp) * 0.015
        
        # Factor de humedad
        humidity_factor = 1.0
        if 'humidity' in weather_factors:
            avg_humidity = sum(weather_factors['humidity']) / len(weather_factors['humidity'])
            if avg_humidity > 80:
                humidity_factor = 1.05 + (avg_humidity - 80) * 0.001
        
        # Factor estacional
        seasonal_factor = 1.0
        if len(time_series) >= 12:  # Datos anuales
            summer_months = [time_series[i] for i in [11, 0, 1, 2]]  # Dic-Mar
            winter_months = [time_series[i] for i in [5, 6, 7, 8]]   # Jun-Sep
            
            summer_avg = sum(summer_months) / len(summer_months)
            winter_avg = sum(winter_months) / len(winter_months)
            seasonal_factor = (summer_avg / winter_avg) if winter_avg > 0 else 1.0
        
        # Calcular patrón final
        pattern = {
            'base_consumption': base_consumption,
            'temp_adjusted': base_consumption * temp_factor,
            'humidity_adjusted': base_consumption * temp_factor * humidity_factor,
            'seasonal_pattern': [val * seasonal_factor for val in time_series],
            'factors': {
                'temperature': temp_factor,
                'humidity': humidity_factor,
                'seasonal': seasonal_factor
            },
            'total_annual_mwh': base_consumption * temp_factor * humidity_factor * seasonal_factor * 12
        }
        
        return pattern
    
    @MemoizationDecorator(max_size=50, ttl=1800)  # 30 minutos TTL
    def calculate_load_forecasting(self, historical_data, economic_indicators, population_growth):
        """
        Cálculo costoso: Pronóstico de carga con indicadores económicos
        """
        print("[INCREMENTO] Ejecutando modelo de pronóstico de carga...")
        
        # Simular procesamiento intensivo
        time.sleep(0.15)
        
        # Modelo simplificado de pronóstico
        base_load = sum(historical_data) / len(historical_data)
        
        # Factor económico
        gdp_growth = economic_indicators.get('gdp_growth', 0.02)
        economic_factor = 1 + (gdp_growth * 0.8)  # Elasticidad 0.8
        
        # Factor demográfico
        pop_factor = 1 + population_growth
        
        # Factor de eficiencia (mejoras tecnológicas)
        efficiency_factor = 0.98  # 2% mejora anual
        
        # Proyección a 5 años
        projections = []
        current_load = base_load
        
        for year in range(5):
            current_load *= economic_factor * pop_factor * efficiency_factor
            projections.append({
                'year': 2024 + year,
                'projected_load_mwh': current_load,
                'economic_component': current_load * (economic_factor - 1),
                'demographic_component': current_load * (pop_factor - 1),
                'efficiency_savings': current_load * (1 - efficiency_factor)
            })
        
        return {
            'base_load': base_load,
            'projections': projections,
            'factors_used': {
                'economic': economic_factor,
                'demographic': pop_factor,
                'efficiency': efficiency_factor
            }
        }
    
    @MemoizationDecorator(max_size=200, ttl=7200)  # 2 horas TTL
    def calculate_grid_stability_metrics(self, load_data, generation_data, transmission_capacity):
        """
        Cálculo costoso: Métricas de estabilidad de red eléctrica
        """
        print("[ELECTRICO] Analizando estabilidad de red eléctrica...")
        
        # Simular análisis complejo
        time.sleep(0.2)
        
        # Calcular métricas de estabilidad
        total_load = sum(load_data)
        total_generation = sum(generation_data)
        
        # Balance oferta-demanda
        supply_demand_ratio = total_generation / total_load if total_load > 0 else 0
        
        # Variabilidad de carga
        load_variance = sum((x - (total_load / len(load_data))) ** 2 for x in load_data) / len(load_data)
        load_stability = 1 / (1 + load_variance / 1000)  # Normalizar
        
        # Capacidad de transmisión
        peak_load = max(load_data)
        transmission_adequacy = transmission_capacity / peak_load if peak_load > 0 else 0
        
        # Reserva rodante
        spinning_reserve = (total_generation - peak_load) / peak_load if peak_load > 0 else 0
        
        # Índice de confiabilidad compuesto
        reliability_index = (
            supply_demand_ratio * 0.3 +
            load_stability * 0.2 +
            min(transmission_adequacy, 2) * 0.25 +  # Cap at 2
            max(0, min(spinning_reserve, 0.5)) * 2 * 0.25  # 0-50% reserve
        )
        
        return {
            'supply_demand_ratio': supply_demand_ratio,
            'load_stability_score': load_stability,
            'transmission_adequacy': transmission_adequacy,
            'spinning_reserve_ratio': spinning_reserve,
            'reliability_index': reliability_index,
            'classification': 'Estable' if reliability_index > 0.8 else 'Inestable' if reliability_index < 0.4 else 'Moderado'
        }


# Decoradores funcionales adicionales
def timing_memoize(func):
    """Decorador que combina memoización con medición de tiempo"""
    cache = {}
    execution_times = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = str((args, tuple(sorted(kwargs.items()))))
        
        if key in cache:
            print(f"Cache HIT para {func.__name__} (tiempo original: {execution_times[key]:.3f}s)")
            return cache[key]
        
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        cache[key] = result
        execution_times[key] = execution_time
        
        print(f"Cache MISS para {func.__name__} - Ejecutado en {execution_time:.3f}s")
        return result
    
    wrapper.cache = cache
    wrapper.execution_times = execution_times
    return wrapper


@timing_memoize
def complex_energy_simulation(grid_config, demand_profile, renewable_mix):
    """
    Función ejemplo que se beneficia de memoización
    Simula un cálculo complejo de red eléctrica
    """
    # Simular cálculo costoso
    time.sleep(0.3)
    
    # Cálculos simulados
    base_cost = sum(demand_profile) * grid_config.get('cost_per_mwh', 100)
    renewable_savings = base_cost * renewable_mix * 0.3
    transmission_losses = base_cost * 0.05
    
    return {
        'total_cost': base_cost - renewable_savings + transmission_losses,
        'renewable_savings': renewable_savings,
        'transmission_losses': transmission_losses,
        'efficiency_score': (base_cost - transmission_losses) / base_cost
    }


def demo_memoization():
    """
    Demostración de técnicas de memoización
    """
    print("DEMOSTRACIÓN DE MEMOIZACIÓN\n")
    
    calc_cache = EnergyCalculationCache()
    
    # 1. Demo cálculo de patrón de consumo
    print("=" * 60)
    print("1 CÁLCULO DE PATRÓN DE CONSUMO (CON MEMOIZACIÓN)")
    print("=" * 60)
    
    region_data = {
        'name': 'Guayaquil',
        'historical_consumption': [1200, 1350, 1180, 1280, 1420, 1310]
    }
    
    time_series = [100, 95, 110, 125, 130, 115, 105, 98, 108, 122, 135, 118]
    weather_factors = {
        'temperature': [28, 30, 32, 29, 27, 26],
        'humidity': [85, 88, 82, 79, 81, 84]
    }
    
    # Primera ejecución (cache miss)
    print("Primera ejecución:")
    start = time.time()
    result1 = calc_cache.calculate_energy_consumption_pattern(region_data, time_series, weather_factors)
    time1 = time.time() - start
    print(f"⏱ Tiempo: {time1:.3f}s")
    
    # Segunda ejecución (cache hit)
    print("\nSegunda ejecución (mismos parámetros):")
    start = time.time()
    result2 = calc_cache.calculate_energy_consumption_pattern(region_data, time_series, weather_factors)
    time2 = time.time() - start
    print(f"⏱ Tiempo: {time2:.3f}s")
    print(f"Aceleración: {time1/time2:.1f}x más rápido")
    
    # Mostrar estadísticas de caché
    cache_stats = calc_cache.calculate_energy_consumption_pattern.cache_info()
    print(f"\nEstadísticas de caché:")
    print(f"   Hits: {cache_stats['hits']}")
    print(f"   Misses: {cache_stats['misses']}")
    print(f"   Hit rate: {cache_stats['hit_rate']:.1%}")
    
    # 2. Demo pronóstico de carga
    print("\n" + "=" * 60)
    print("2 PRONÓSTICO DE CARGA")
    print("=" * 60)
    
    historical_data = [1500, 1450, 1520, 1480, 1510, 1490, 1530, 1470]
    economic_indicators = {'gdp_growth': 0.035}
    population_growth = 0.015
    
    forecast_result = calc_cache.calculate_load_forecasting(historical_data, economic_indicators, population_growth)
    
    print("Proyecciones de carga:")
    for projection in forecast_result['projections'][:3]:  # Mostrar solo 3 años
        print(f"   {projection['year']}: {projection['projected_load_mwh']:.0f} MWh")
    
    # 3. Demo decorador timing_memoize
    print("\n" + "=" * 60)
    print("3 SIMULACIÓN COMPLEJA CON TIMING")
    print("=" * 60)
    
    grid_config = {'cost_per_mwh': 120, 'efficiency': 0.92}
    demand_profile = [1000, 1100, 950, 1050, 1200]
    renewable_mix = 0.25
    
    # Primera ejecución
    result_sim1 = complex_energy_simulation(grid_config, demand_profile, renewable_mix)
    
    # Segunda ejecución (mismos parámetros)
    result_sim2 = complex_energy_simulation(grid_config, demand_profile, renewable_mix)
    
    print(f"\nCosto total simulado: ${result_sim1['total_cost']:,.0f}")
    print(f"Ahorros renovables: ${result_sim1['renewable_savings']:,.0f}")
    print(f"Eficiencia: {result_sim1['efficiency_score']:.1%}")
    
    return calc_cache


if __name__ == "__main__":
    demo_memoization()