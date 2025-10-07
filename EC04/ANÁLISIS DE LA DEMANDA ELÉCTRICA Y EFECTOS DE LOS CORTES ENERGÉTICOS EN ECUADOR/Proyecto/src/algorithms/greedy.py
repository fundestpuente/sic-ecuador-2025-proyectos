"""
Algoritmos Greedy para optimización energética
Implementación de estrategias golosas para distribución y gestión energética
"""

class GreedyEnergyOptimizer:
    """
    Implementa algoritmos greedy para optimización energética
    """
    
    def __init__(self):
        self.solutions = []
        self.debug_mode = False
    
    def optimize_energy_distribution(self, regions_demand, available_energy):
        """
        Algoritmo greedy para distribuir energía disponible entre regiones
        Estrategia: Priorizar regiones con mayor eficiencia (demanda/población)
        
        Args:
            regions_demand: Lista de tuplas (region, demanda_mwh, poblacion, prioridad)
            available_energy: Energía total disponible para distribuir
            
        Returns:
            dict: Distribución óptima de energía
        """
        if self.debug_mode:
            print(f"Iniciando distribucion greedy de {available_energy} MWh")
        
        # Calcular eficiencia para cada región (ratio demanda/población)
        regions_with_efficiency = []
        for region, demanda, poblacion, prioridad in regions_demand:
            if poblacion > 0:
                eficiencia = demanda / poblacion  # MWh per capita
                regions_with_efficiency.append({
                    'region': region,
                    'demanda': demanda,
                    'poblacion': poblacion,
                    'prioridad': prioridad,
                    'eficiencia': eficiencia,
                    'ratio_prioridad': prioridad / eficiencia if eficiencia > 0 else 0
                })
        
        # Estrategia greedy: Ordenar por prioridad y eficiencia
        regions_sorted = sorted(
            regions_with_efficiency,
            key=lambda x: (-x['prioridad'], x['eficiencia']),
            reverse=False
        )
        
        # Distribuir energía de forma greedy
        distribution = {}
        remaining_energy = available_energy
        total_satisfied_demand = 0
        
        for region_data in regions_sorted:
            region = region_data['region']
            demanda = region_data['demanda']
            
            if remaining_energy <= 0:
                distribution[region] = 0
                continue
            
            # Asignar la menor cantidad entre demanda y energía disponible
            assigned_energy = min(demanda, remaining_energy)
            distribution[region] = assigned_energy
            remaining_energy -= assigned_energy
            total_satisfied_demand += assigned_energy
            
            if self.debug_mode:
                satisfaction = (assigned_energy / demanda) * 100 if demanda > 0 else 100
                print(f" {region}: {assigned_energy:.1f} MWh ({satisfaction:.1f}% satisfacción)")
        
        # Calcular métricas de la solución
        total_demand = sum(r['demanda'] for r in regions_with_efficiency)
        satisfaction_rate = (total_satisfied_demand / total_demand) * 100 if total_demand > 0 else 0
        
        result = {
            'distribution': distribution,
            'total_assigned': total_satisfied_demand,
            'total_demand': total_demand,
            'satisfaction_rate': satisfaction_rate,
            'remaining_energy': remaining_energy,
            'algorithm': 'greedy_priority_efficiency'
        }
        
        self.solutions.append(result)
        return result
    
    def minimize_outage_impact(self, outages_data, maintenance_capacity):
        """
        Algoritmo greedy para minimizar impacto de cortes programados
        Estrategia: Priorizar cortes con menor impacto por hora de mantenimiento
        
        Args:
            outages_data: Lista de tuplas (sector, duracion_horas, usuarios_afectados, criticidad)
            maintenance_capacity: Horas de mantenimiento disponibles
            
        Returns:
            dict: Plan óptimo de cortes programados
        """
        if self.debug_mode:
            print(f"Optimizando cortes con {maintenance_capacity} horas disponibles")
        
        # Calcular eficiencia de cada corte (impacto por hora)
        outages_with_efficiency = []
        for sector, duracion, usuarios, criticidad in outages_data:
            # Impacto = usuarios afectados * criticidad * duración
            impacto_total = usuarios * criticidad * duracion
            # Eficiencia = impacto por hora de mantenimiento
            eficiencia_hora = impacto_total / duracion if duracion > 0 else float('inf')
            
            outages_with_efficiency.append({
                'sector': sector,
                'duracion': duracion,
                'usuarios': usuarios,
                'criticidad': criticidad,
                'impacto_total': impacto_total,
                'eficiencia_hora': eficiencia_hora
            })
        
        # Estrategia greedy: Ordenar por menor impacto por hora (más eficiente)
        outages_sorted = sorted(
            outages_with_efficiency,
            key=lambda x: x['eficiencia_hora']
        )
        
        # Seleccionar cortes de forma greedy
        selected_outages = []
        remaining_capacity = maintenance_capacity
        total_users_affected = 0
        total_impact = 0
        
        for outage in outages_sorted:
            if remaining_capacity >= outage['duracion']:
                selected_outages.append(outage)
                remaining_capacity -= outage['duracion']
                total_users_affected += outage['usuarios']
                total_impact += outage['impacto_total']
                
                if self.debug_mode:
                    print(f"  {outage['sector']}: {outage['duracion']}h, "
                          f"{outage['usuarios']} usuarios, impacto: {outage['impacto_total']:.1f}")
        
        result = {
            'selected_outages': selected_outages,
            'total_duration': maintenance_capacity - remaining_capacity,
            'total_users_affected': total_users_affected,
            'total_impact': total_impact,
            'remaining_capacity': remaining_capacity,
            'algorithm': 'greedy_minimal_impact'
        }
        
        return result
    
    def optimize_load_balancing(self, generators_data, total_demand):
        """
        Algoritmo greedy para balance de carga entre generadores
        Estrategia: Activar generadores en orden de eficiencia (costo/MWh)
        
        Args:
            generators_data: Lista de tuplas (planta, capacidad_mwh, costo_mwh, tipo)
            total_demand: Demanda total a satisfacer
            
        Returns:
            dict: Plan óptimo de generación
        """
        if self.debug_mode:
            print(f"Optimizando generación para {total_demand} MWh de demanda")
        
        # Ordenar generadores por eficiencia (menor costo por MWh)
        generators_sorted = sorted(
            generators_data,
            key=lambda x: x[2]  # costo_mwh
        )
        
        # Seleccionar generadores de forma greedy
        selected_generators = []
        remaining_demand = total_demand
        total_capacity = 0
        total_cost = 0
        
        for planta, capacidad, costo_mwh, tipo in generators_sorted:
            if remaining_demand <= 0:
                break
            
            # Determinar cuánta energía generar con esta planta
            generation = min(capacidad, remaining_demand)
            generator_cost = generation * costo_mwh
            
            selected_generators.append({
                'planta': planta,
                'tipo': tipo,
                'capacidad_total': capacidad,
                'generation_assigned': generation,
                'costo_mwh': costo_mwh,
                'costo_total': generator_cost
            })
            
            remaining_demand -= generation
            total_capacity += generation
            total_cost += generator_cost
            
            if self.debug_mode:
                utilization = (generation / capacidad) * 100 if capacidad > 0 else 0
                print(f"  {planta} ({tipo}): {generation:.1f} MWh "
                      f"({utilization:.1f}% utilización), ${generator_cost:.0f}")
        
        demand_satisfaction = (total_capacity / total_demand) * 100 if total_demand > 0 else 0
        avg_cost_mwh = total_cost / total_capacity if total_capacity > 0 else 0
        
        result = {
            'selected_generators': selected_generators,
            'total_generation': total_capacity,
            'total_demand': total_demand,
            'demand_satisfaction': demand_satisfaction,
            'total_cost': total_cost,
            'avg_cost_mwh': avg_cost_mwh,
            'remaining_demand': remaining_demand,
            'algorithm': 'greedy_cost_optimization'
        }
        
        return result
    
    def set_debug_mode(self, debug=True):
        """Activar/desactivar modo debug"""
        self.debug_mode = debug
    
    def get_all_solutions(self):
        """Obtener todas las soluciones generadas"""
        return self.solutions
    
    def clear_solutions(self):
        """Limpiar historial de soluciones"""
        self.solutions = []


def demo_greedy_algorithms():
    """
    Demostración de los algoritmos greedy implementados
    """
    print("DEMOSTRACIÓN DE ALGORITMOS GREEDY\n")
    
    optimizer = GreedyEnergyOptimizer()
    optimizer.set_debug_mode(True)
    
    # 1. Demo distribución de energía
    print("=" * 60)
    print("1 DISTRIBUCIÓN GREEDY DE ENERGÍA")
    print("=" * 60)
    
    regions_data = [
        ("Guayaquil", 1500, 2800000, 5),    # alta prioridad, alta población
        ("Quito", 1200, 2200000, 5),        # alta prioridad, alta población  
        ("Cuenca", 400, 580000, 4),         # media prioridad
        ("Ambato", 300, 450000, 3),         # baja prioridad
        ("Machala", 250, 320000, 3),        # baja prioridad
    ]
    
    available_energy = 3000  # MWh disponibles
    
    result1 = optimizer.optimize_energy_distribution(regions_data, available_energy)
    print(f"\nRESULTADO: {result1['satisfaction_rate']:.1f}% de demanda satisfecha")
    print(f"Energía restante: {result1['remaining_energy']:.1f} MWh")
    
    # 2. Demo minimización de impacto de cortes
    print("\n" + "=" * 60)
    print("2 MINIMIZACIÓN DE IMPACTO DE CORTES")
    print("=" * 60)
    
    outages_data = [
        ("Industrial Norte", 4, 15000, 2),    # 4h, 15k usuarios, criticidad media
        ("Residencial Sur", 6, 45000, 3),     # 6h, 45k usuarios, criticidad alta
        ("Comercial Centro", 2, 8000, 1),     # 2h, 8k usuarios, criticidad baja
        ("Hospital Central", 8, 2000, 5),     # 8h, 2k usuarios, criticidad máxima
        ("Universidad", 3, 12000, 2),         # 3h, 12k usuarios, criticidad media
    ]
    
    maintenance_hours = 15
    
    result2 = optimizer.minimize_outage_impact(outages_data, maintenance_hours)
    print(f"\nRESULTADO: {len(result2['selected_outages'])} cortes seleccionados")
    print(f"Total usuarios afectados: {result2['total_users_affected']:,}")
    print(f"⏱ Tiempo utilizado: {result2['total_duration']} de {maintenance_hours} horas")
    
    # 3. Demo balance de carga
    print("\n" + "=" * 60)
    print("3 BALANCE GREEDY DE GENERACIÓN")
    print("=" * 60)
    
    generators_data = [
        ("Hidroeléctrica Coca", 800, 45, "Renovable"),     # alta capacidad, bajo costo
        ("Térmica Trinitaria", 600, 120, "Térmica"),       # media capacidad, alto costo
        ("Solar Salinas", 200, 35, "Renovable"),           # baja capacidad, muy bajo costo
        ("Eólica Villonaco", 150, 40, "Renovable"),        # baja capacidad, bajo costo
        ("Térmica Gonzalo", 400, 110, "Térmica"),          # media capacidad, alto costo
    ]
    
    total_demand = 1800  # MWh de demanda
    
    result3 = optimizer.optimize_load_balancing(generators_data, total_demand)
    print(f"\n RESULTADO: {result3['demand_satisfaction']:.1f}% de demanda satisfecha")
    print(f"Costo promedio: ${result3['avg_cost_mwh']:.2f}/MWh")
    print(f"Costo total: ${result3['total_cost']:,.0f}")
    
    return optimizer


if __name__ == "__main__":
    demo_greedy_algorithms()