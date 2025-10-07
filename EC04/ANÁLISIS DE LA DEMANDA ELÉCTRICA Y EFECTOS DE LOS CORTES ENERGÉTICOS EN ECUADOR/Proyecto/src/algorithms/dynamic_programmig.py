"""
Algoritmos de Programación Dinámica para optimización energética
Implementación de soluciones con enfoque bottom-up y memoización
"""

from functools import lru_cache
import json

class DynamicProgrammingOptimizer:
    """
    Implementa algoritmos de programación dinámica para optimización energética
    """
    
    def __init__(self):
        self.memo_tables = {}
        self.solutions_cache = {}
        self.debug_mode = False
    
    def optimize_capacity_planning(self, time_periods, max_capacity, demand_forecast):
        """
        Programación dinámica para planificación óptima de capacidad energética
        Problema: Determinar la mejor estrategia de expansión de capacidad a lo largo del tiempo
        
        Args:
            time_periods: Número de períodos de tiempo
            max_capacity: Capacidad máxima posible
            demand_forecast: Lista de demandas proyectadas por período
            
        Returns:
            dict: Plan óptimo de expansión de capacidad
        """
        if self.debug_mode:
            print(f"[EMOJI]  Optimizando expansión de capacidad para {time_periods} períodos")
        
        # Tabla DP: dp[periodo][capacidad_actual] = costo mínimo
        dp = {}
        decisions = {}
        
        # Costos de construcción y operación
        def construction_cost(new_capacity):
            """Costo de construir nueva capacidad (no lineal)"""
            if new_capacity == 0:
                return 0
            # Costo base + economías de escala
            return 1000000 + (new_capacity * 50000) + (new_capacity ** 1.5) * 1000
        
        def operational_cost(capacity, demand):
            """Costo operacional por período"""
            if capacity >= demand:
                # Costo de operación normal + costo de capacidad ociosa
                return demand * 100 + (capacity - demand) * 20
            else:
                # Costo de operación + penalización por déficit
                return capacity * 100 + (demand - capacity) * 500
        
        # Inicialización: período 0
        for cap in range(max_capacity + 1):
            initial_construction = construction_cost(cap)
            initial_operation = operational_cost(cap, demand_forecast[0])
            dp[(0, cap)] = initial_construction + initial_operation
            decisions[(0, cap)] = cap  # Capacidad construida inicialmente
        
        # Llenar tabla DP
        for period in range(1, time_periods):
            for current_cap in range(max_capacity + 1):
                min_cost = float('inf')
                best_decision = 0
                
                # Probar todas las opciones de capacidad anterior
                for prev_cap in range(current_cap + 1):  # Solo podemos aumentar capacidad
                    if (period - 1, prev_cap) not in dp:
                        continue
                    
                    # Costo de expandir capacidad
                    expansion = current_cap - prev_cap
                    expansion_cost = construction_cost(expansion)
                    
                    # Costo operacional en este período
                    op_cost = operational_cost(current_cap, demand_forecast[period])
                    
                    # Costo total
                    total_cost = dp[(period - 1, prev_cap)] + expansion_cost + op_cost
                    
                    if total_cost < min_cost:
                        min_cost = total_cost
                        best_decision = prev_cap
                
                dp[(period, current_cap)] = min_cost
                decisions[(period, current_cap)] = best_decision
        
        # Encontrar solución óptima
        final_min_cost = float('inf')
        final_capacity = 0
        
        for cap in range(max_capacity + 1):
            if dp[(time_periods - 1, cap)] < final_min_cost:
                final_min_cost = dp[(time_periods - 1, cap)]
                final_capacity = cap
        
        # Reconstruir plan óptimo
        optimal_plan = []
        current_period = time_periods - 1
        current_capacity = final_capacity
        
        while current_period >= 0:
            if current_period == 0:
                expansion = current_capacity
            else:
                prev_capacity = decisions[(current_period, current_capacity)]
                expansion = current_capacity - prev_capacity
                current_capacity = prev_capacity
            
            optimal_plan.append({
                'period': current_period,
                'total_capacity': current_capacity + expansion if current_period == 0 else current_capacity + expansion,
                'expansion': expansion,
                'demand': demand_forecast[current_period],
                'construction_cost': construction_cost(expansion),
                'operational_cost': operational_cost(
                    current_capacity + expansion if current_period == 0 else current_capacity + expansion,
                    demand_forecast[current_period]
                )
            })
            
            current_period -= 1
        
        optimal_plan.reverse()
        
        # Recalcular correctamente las capacidades
        total_capacity = 0
        for i, plan in enumerate(optimal_plan):
            total_capacity += plan['expansion']
            plan['total_capacity'] = total_capacity
        
        result = {
            'optimal_plan': optimal_plan,
            'total_cost': final_min_cost,
            'final_capacity': final_capacity,
            'algorithm': 'dynamic_programming_capacity',
            'dp_table_size': len(dp)
        }
        
        if self.debug_mode:
            print(f"[DATOS] Costo total óptimo: ${final_min_cost:,.0f}")
            print(f"[EMOJI] Capacidad final: {final_capacity} MW")
            
        return result
    
    @lru_cache(maxsize=1000)
    def knapsack_energy_projects(self, budget, project_index, projects_tuple):
        """
        Problema de la mochila para selección de proyectos energéticos
        Usa memoización automática con lru_cache
        
        Args:
            budget: Presupuesto disponible
            project_index: Índice del proyecto actual
            projects_tuple: Tupla de proyectos (costo, beneficio, nombre)
            
        Returns:
            tuple: (beneficio_máximo, proyectos_seleccionados)
        """
        # Caso base
        if project_index == 0 or budget == 0:
            return 0, []
        
        projects = list(projects_tuple)
        costo, beneficio, nombre = projects[project_index - 1]
        
        # Si el proyecto no cabe en el presupuesto
        if costo > budget:
            return self.knapsack_energy_projects(budget, project_index - 1, projects_tuple)
        
        # Opción 1: No incluir el proyecto actual
        benefit_without, projects_without = self.knapsack_energy_projects(
            budget, project_index - 1, projects_tuple
        )
        
        # Opción 2: Incluir el proyecto actual
        benefit_with_current, projects_with_current = self.knapsack_energy_projects(
            budget - costo, project_index - 1, projects_tuple
        )
        benefit_with_current += beneficio
        
        # Retornar la mejor opción
        if benefit_with_current > benefit_without:
            return benefit_with_current, projects_with_current + [nombre]
        else:
            return benefit_without, projects_without
    
    def optimize_energy_projects(self, projects, total_budget):
        """
        Optimización de selección de proyectos energéticos usando programación dinámica
        
        Args:
            projects: Lista de tuplas (costo, beneficio, nombre, tipo)
            total_budget: Presupuesto total disponible
            
        Returns:
            dict: Selección óptima de proyectos
        """
        if self.debug_mode:
            print(f"[DINERO] Optimizando selección con presupuesto ${total_budget:,}")
        
        # Convertir a tupla para usar con lru_cache
        projects_tuple = tuple((costo, beneficio, nombre) for costo, beneficio, nombre, _ in projects)
        
        max_benefit, selected_projects = self.knapsack_energy_projects(
            total_budget, len(projects), projects_tuple
        )
        
        # Calcular detalles de la solución
        selected_details = []
        total_cost = 0
        
        for project_name in selected_projects:
            for costo, beneficio, nombre, tipo in projects:
                if nombre == project_name:
                    selected_details.append({
                        'nombre': nombre,
                        'tipo': tipo,
                        'costo': costo,
                        'beneficio': beneficio,
                        'roi': (beneficio / costo) if costo > 0 else 0
                    })
                    total_cost += costo
                    break
        
        result = {
            'selected_projects': selected_details,
            'total_benefit': max_benefit,
            'total_cost': total_cost,
            'budget_used': (total_cost / total_budget) * 100,
            'remaining_budget': total_budget - total_cost,
            'avg_roi': (max_benefit / total_cost) if total_cost > 0 else 0,
            'algorithm': 'dynamic_programming_knapsack'
        }
        
        if self.debug_mode:
            print(f"[INCREMENTO] Beneficio máximo: {max_benefit:,}")
            print(f"[EMOJI] Costo total: ${total_cost:,}")
            print(f"[DATOS] ROI promedio: {result['avg_roi']:.2f}")
        
        return result
    
    def optimize_maintenance_schedule(self, equipment_list, time_horizon, maintenance_costs):
        """
        Programación dinámica para optimizar calendario de mantenimiento
        
        Args:
            equipment_list: Lista de equipos con su estado
            time_horizon: Horizonte de tiempo para planificación
            maintenance_costs: Costos de mantenimiento por tipo
            
        Returns:
            dict: Calendario óptimo de mantenimiento
        """
        if self.debug_mode:
            print(f"[CONFIG] Optimizando mantenimiento para {len(equipment_list)} equipos")
        
        # Estados posibles: 0=nuevo, 1=bueno, 2=regular, 3=malo, 4=crítico
        states = 5
        
        # Tabla DP: dp[equipo][tiempo][estado] = costo mínimo
        dp = {}
        decisions = {}
        
        def degradation_prob(current_state, action):
            """Probabilidad de degradación según estado y acción"""
            if action == 'mantener':
                return max(0, current_state - 1)  # Mejora un nivel
            else:  # no mantener
                return min(states - 1, current_state + 1)  # Empeora un nivel
        
        def cost_function(state, action, equipment_type):
            """Función de costo por estado y acción"""
            base_cost = maintenance_costs.get(equipment_type, 1000)
            
            if action == 'mantener':
                return base_cost * (state + 1)  # Más caro mantener equipos en peor estado
            else:
                # Costo de no mantener (riesgo de falla)
                return state * 200  # Penalización por degradación
        
        # Inicialización para tiempo final
        for eq_idx, (eq_name, eq_type, initial_state) in enumerate(equipment_list):
            for state in range(states):
                dp[(eq_idx, time_horizon - 1, state)] = 0
                decisions[(eq_idx, time_horizon - 1, state)] = 'no_mantener'
        
        # Llenar tabla DP hacia atrás
        for t in range(time_horizon - 2, -1, -1):
            for eq_idx, (eq_name, eq_type, initial_state) in enumerate(equipment_list):
                for state in range(states):
                    min_cost = float('inf')
                    best_action = 'no_mantener'
                    
                    for action in ['mantener', 'no_mantener']:
                        immediate_cost = cost_function(state, action, eq_type)
                        next_state = degradation_prob(state, action)
                        future_cost = dp.get((eq_idx, t + 1, next_state), 0)
                        total_cost = immediate_cost + future_cost
                        
                        if total_cost < min_cost:
                            min_cost = total_cost
                            best_action = action
                    
                    dp[(eq_idx, t, state)] = min_cost
                    decisions[(eq_idx, t, state)] = best_action
        
        # Construir calendario óptimo
        maintenance_schedule = []
        total_cost = 0
        
        for eq_idx, (eq_name, eq_type, initial_state) in enumerate(equipment_list):
            equipment_schedule = {
                'equipment': eq_name,
                'type': eq_type,
                'initial_state': initial_state,
                'schedule': []
            }
            
            current_state = initial_state
            for t in range(time_horizon):
                action = decisions.get((eq_idx, t, current_state), 'no_mantener')
                cost = cost_function(current_state, action, eq_type)
                
                equipment_schedule['schedule'].append({
                    'period': t,
                    'state': current_state,
                    'action': action,
                    'cost': cost
                })
                
                total_cost += cost
                current_state = degradation_prob(current_state, action)
            
            maintenance_schedule.append(equipment_schedule)
        
        result = {
            'maintenance_schedule': maintenance_schedule,
            'total_cost': total_cost,
            'time_horizon': time_horizon,
            'algorithm': 'dynamic_programming_maintenance'
        }
        
        return result
    
    def set_debug_mode(self, debug=True):
        """Activar/desactivar modo debug"""
        self.debug_mode = debug
    
    def clear_cache(self):
        """Limpiar caché de memoización"""
        self.knapsack_energy_projects.cache_clear()
        self.memo_tables = {}
        self.solutions_cache = {}


def demo_dynamic_programming():
    """
    Demostración de los algoritmos de programación dinámica
    """
    print("[OBJETIVO] DEMOSTRACIÓN DE PROGRAMACIÓN DINÁMICA\n")
    
    optimizer = DynamicProgrammingOptimizer()
    optimizer.set_debug_mode(True)
    
    # 1. Demo planificación de capacidad
    print("=" * 60)
    print("1[EMOJI]⃣  PLANIFICACIÓN DINÁMICA DE CAPACIDAD")
    print("=" * 60)
    
    time_periods = 5
    max_capacity = 20
    demand_forecast = [8, 12, 15, 18, 16]  # MWh por período
    
    result1 = optimizer.optimize_capacity_planning(time_periods, max_capacity, demand_forecast)
    
    print("\n[RESUMEN] PLAN ÓPTIMO DE EXPANSIÓN:")
    for period_data in result1['optimal_plan']:
        print(f"  Período {period_data['period']}: "
              f"{period_data['expansion']} MW nuevos, "
              f"{period_data['total_capacity']} MW total, "
              f"demanda: {period_data['demand']} MW")
    
    # 2. Demo selección de proyectos
    print("\n" + "=" * 60)
    print("2[EMOJI]⃣  SELECCIÓN ÓPTIMA DE PROYECTOS")
    print("=" * 60)
    
    projects = [
        (5000000, 8000000, "Solar Atacama", "Renovable"),
        (3000000, 4500000, "Eólico Patagonia", "Renovable"),
        (8000000, 10000000, "Hidroeléctrica Andes", "Renovable"),
        (2000000, 2800000, "Biomasa Costera", "Renovable"),
        (6000000, 7200000, "Geotérmica Volcán", "Renovable"),
        (4000000, 5000000, "Solar Techo Urbano", "Distribuida"),
    ]
    
    budget = 15000000  # $15 millones
    
    result2 = optimizer.optimize_energy_projects(projects, budget)
    
    print(f"\n[NEGOCIO] PROYECTOS SELECCIONADOS:")
    for project in result2['selected_projects']:
        print(f"  [EMOJI]  {project['nombre']} ({project['tipo']}): "
              f"${project['costo']:,} → ROI: {project['roi']:.2f}")
    
    # 3. Demo calendario de mantenimiento
    print("\n" + "=" * 60)
    print("3[EMOJI]⃣  CALENDARIO ÓPTIMO DE MANTENIMIENTO")
    print("=" * 60)
    
    equipment_list = [
        ("Turbina A", "Hidráulica", 2),
        ("Generador B", "Térmico", 1),
        ("Transformador C", "Distribución", 3),
    ]
    
    maintenance_costs = {
        "Hidráulica": 50000,
        "Térmico": 30000,
        "Distribución": 20000
    }
    
    result3 = optimizer.optimize_maintenance_schedule(equipment_list, 4, maintenance_costs)
    
    print(f"\n[CONFIG] CALENDARIO DE MANTENIMIENTO:")
    for equipment in result3['maintenance_schedule']:
        print(f"\n  {equipment['equipment']} ({equipment['type']}):")
        for period in equipment['schedule']:
            action_symbol = "[CONFIG]" if period['action'] == 'mantener' else "[PAUSA]"
            print(f"    Período {period['period']}: {action_symbol} {period['action']} "
                  f"(estado: {period['state']}, costo: ${period['cost']:,})")
    
    print(f"\n[DINERO] Costo total de mantenimiento: ${result3['total_cost']:,}")
    
    return optimizer


if __name__ == "__main__":
    demo_dynamic_programming()