"""
Modelo de datos para información energética
Incluye clases para balance energético, consumo y producción
"""

from datetime import datetime
from typing import Dict, List, Optional, Union
import json


class EnergyBalance:
    """
    Clase para representar el balance energético nacional
    """
    
    def __init__(self, mes: str, año: int):
        self.mes = mes
        self.año = año
        self.fecha_registro = datetime.now()
        
        # Potencia nominal por tipo de generación (MW)
        self.potencia_nominal = {
            'hidraulica': 0.0,
            'eolica': 0.0,
            'fotovoltaica': 0.0,
            'biomasa': 0.0,
            'biogas': 0.0,
            'termica_mci': 0.0,
            'termica_turbinas': 0.0,
            'otros': 0.0
        }
        
        # Potencia efectiva por tipo (MW)
        self.potencia_efectiva = {
            'hidraulica': 0.0,
            'eolica': 0.0,
            'fotovoltaica': 0.0,
            'biomasa': 0.0,
            'biogas': 0.0,
            'termica_mci': 0.0,
            'termica_turbinas': 0.0,
            'otros': 0.0
        }
        
        # Producción y consumo (GWh)
        self.produccion_total = 0.0
        self.importaciones = 0.0
        self.exportaciones = 0.0
        self.energia_servicio_publico = 0.0
        self.energia_disponible = 0.0
        self.consumo_total = 0.0
    
    def agregar_potencia_nominal(self, tipo: str, valor: float):
        """Agrega potencia nominal por tipo de generación"""
        if tipo in self.potencia_nominal:
            self.potencia_nominal[tipo] = valor
        else:
            raise ValueError(f"Tipo de generación '{tipo}' no válido")
    
    def agregar_potencia_efectiva(self, tipo: str, valor: float):
        """Agrega potencia efectiva por tipo de generación"""
        if tipo in self.potencia_efectiva:
            self.potencia_efectiva[tipo] = valor
        else:
            raise ValueError(f"Tipo de generación '{tipo}' no válido")
    
    def calcular_total_potencia_nominal(self) -> float:
        """Calcula el total de potencia nominal"""
        return sum(self.potencia_nominal.values())
    
    def calcular_total_potencia_efectiva(self) -> float:
        """Calcula el total de potencia efectiva"""
        return sum(self.potencia_efectiva.values())
    
    def calcular_energia_renovable(self) -> Dict[str, float]:
        """Calcula estadísticas de energía renovable"""
        renovables = ['hidraulica', 'eolica', 'fotovoltaica', 'biomasa', 'biogas']
        
        total_renovable_nominal = sum(
            self.potencia_nominal[tipo] for tipo in renovables
        )
        total_renovable_efectiva = sum(
            self.potencia_efectiva[tipo] for tipo in renovables
        )
        
        total_nominal = self.calcular_total_potencia_nominal()
        total_efectiva = self.calcular_total_potencia_efectiva()
        
        porcentaje_nominal = (total_renovable_nominal / total_nominal * 100) if total_nominal > 0 else 0
        porcentaje_efectiva = (total_renovable_efectiva / total_efectiva * 100) if total_efectiva > 0 else 0
        
        return {
            'total_renovable_nominal': total_renovable_nominal,
            'total_renovable_efectiva': total_renovable_efectiva,
            'porcentaje_nominal': porcentaje_nominal,
            'porcentaje_efectiva': porcentaje_efectiva
        }
    
    def calcular_balance_energetico(self) -> Dict[str, float]:
        """Calcula el balance energético total"""
        disponible_total = self.produccion_total + self.importaciones
        consumo_y_exportaciones = self.consumo_total + self.exportaciones
        balance = disponible_total - consumo_y_exportaciones
        
        return {
            'energia_disponible_total': disponible_total,
            'consumo_y_exportaciones': consumo_y_exportaciones,
            'balance': balance,
            'eficiencia': (self.energia_servicio_publico / self.produccion_total * 100) if self.produccion_total > 0 else 0
        }
    
    def obtener_resumen(self) -> Dict:
        """Obtiene un resumen completo del balance energético"""
        return {
            'periodo': f"{self.mes}-{self.año}",
            'fecha_registro': self.fecha_registro.isoformat(),
            'potencia_nominal_total': self.calcular_total_potencia_nominal(),
            'potencia_efectiva_total': self.calcular_total_potencia_efectiva(),
            'energia_renovable': self.calcular_energia_renovable(),
            'balance_energetico': self.calcular_balance_energetico(),
            'produccion_total': self.produccion_total,
            'importaciones': self.importaciones,
            'exportaciones': self.exportaciones,
            'consumo_total': self.consumo_total
        }
    
    def to_json(self) -> str:
        """Convierte el objeto a JSON"""
        data = {
            'mes': self.mes,
            'año': self.año,
            'fecha_registro': self.fecha_registro.isoformat(),
            'potencia_nominal': self.potencia_nominal,
            'potencia_efectiva': self.potencia_efectiva,
            'produccion_total': self.produccion_total,
            'importaciones': self.importaciones,
            'exportaciones': self.exportaciones,
            'energia_servicio_publico': self.energia_servicio_publico,
            'energia_disponible': self.energia_disponible,
            'consumo_total': self.consumo_total,
            'resumen': self.obtener_resumen()
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Crea una instancia desde un diccionario"""
        balance = cls(data['mes'], data['año'])
        
        if 'potencia_nominal' in data:
            balance.potencia_nominal.update(data['potencia_nominal'])
        
        if 'potencia_efectiva' in data:
            balance.potencia_efectiva.update(data['potencia_efectiva'])
        
        balance.produccion_total = data.get('produccion_total', 0.0)
        balance.importaciones = data.get('importaciones', 0.0)
        balance.exportaciones = data.get('exportaciones', 0.0)
        balance.energia_servicio_publico = data.get('energia_servicio_publico', 0.0)
        balance.energia_disponible = data.get('energia_disponible', 0.0)
        balance.consumo_total = data.get('consumo_total', 0.0)
        
        return balance
    
    def __str__(self):
        return f"EnergyBalance({self.mes}-{self.año}, Total: {self.calcular_total_potencia_nominal():.2f} MW)"
    
    def __repr__(self):
        return self.__str__()


class RegionalConsumption:
    """
    Clase para representar el consumo energético regional
    """
    
    def __init__(self, region: str, mes: str, año: int):
        self.region = region
        self.mes = mes
        self.año = año
        self.fecha_registro = datetime.now()
        
        # Datos por categoría y tipo
        self.consumo_por_categoria = {
            'residencial': {'mwh': 0.0, 'clientes': 0, 'facturacion': 0.0},
            'comercial': {'mwh': 0.0, 'clientes': 0, 'facturacion': 0.0},
            'industrial': {'mwh': 0.0, 'clientes': 0, 'facturacion': 0.0},
            'alumbrado_publico': {'mwh': 0.0, 'clientes': 0, 'facturacion': 0.0},
            'otros': {'mwh': 0.0, 'clientes': 0, 'facturacion': 0.0}
        }
    
    def agregar_consumo(self, categoria: str, mwh: float, clientes: int, facturacion: float):
        """Agrega datos de consumo por categoría"""
        if categoria in self.consumo_por_categoria:
            self.consumo_por_categoria[categoria]['mwh'] += mwh
            self.consumo_por_categoria[categoria]['clientes'] += clientes
            self.consumo_por_categoria[categoria]['facturacion'] += facturacion
        else:
            # Si no existe la categoría, la crea
            self.consumo_por_categoria[categoria] = {
                'mwh': mwh,
                'clientes': clientes,
                'facturacion': facturacion
            }
    
    def calcular_total_mwh(self) -> float:
        """Calcula el consumo total en MWh"""
        return sum(cat['mwh'] for cat in self.consumo_por_categoria.values())
    
    def calcular_total_clientes(self) -> int:
        """Calcula el total de clientes"""
        return sum(cat['clientes'] for cat in self.consumo_por_categoria.values())
    
    def calcular_total_facturacion(self) -> float:
        """Calcula la facturación total"""
        return sum(cat['facturacion'] for cat in self.consumo_por_categoria.values())
    
    def calcular_consumo_promedio_cliente(self) -> float:
        """Calcula el consumo promedio por cliente"""
        total_mwh = self.calcular_total_mwh()
        total_clientes = self.calcular_total_clientes()
        return (total_mwh / total_clientes) if total_clientes > 0 else 0
    
    def calcular_tarifa_promedio(self) -> float:
        """Calcula la tarifa promedio por MWh"""
        total_facturacion = self.calcular_total_facturacion()
        total_mwh = self.calcular_total_mwh()
        return (total_facturacion / total_mwh) if total_mwh > 0 else 0
    
    def obtener_categoria_mayor_consumo(self) -> str:
        """Obtiene la categoría con mayor consumo"""
        if not self.consumo_por_categoria:
            return None
        
        categoria_max = max(
            self.consumo_por_categoria.items(),
            key=lambda x: x[1]['mwh']
        )
        return categoria_max[0]
    
    def calcular_distribucion_porcentual(self) -> Dict[str, float]:
        """Calcula la distribución porcentual por categoría"""
        total_mwh = self.calcular_total_mwh()
        
        if total_mwh == 0:
            return {}
        
        return {
            categoria: (datos['mwh'] / total_mwh * 100)
            for categoria, datos in self.consumo_por_categoria.items()
        }
    
    def obtener_resumen(self) -> Dict:
        """Obtiene un resumen del consumo regional"""
        return {
            'region': self.region,
            'periodo': f"{self.mes}-{self.año}",
            'fecha_registro': self.fecha_registro.isoformat(),
            'total_mwh': self.calcular_total_mwh(),
            'total_clientes': self.calcular_total_clientes(),
            'total_facturacion': self.calcular_total_facturacion(),
            'consumo_promedio_cliente': self.calcular_consumo_promedio_cliente(),
            'tarifa_promedio': self.calcular_tarifa_promedio(),
            'categoria_mayor_consumo': self.obtener_categoria_mayor_consumo(),
            'distribucion_porcentual': self.calcular_distribucion_porcentual()
        }
    
    def to_json(self) -> str:
        """Convierte el objeto a JSON"""
        data = {
            'region': self.region,
            'mes': self.mes,
            'año': self.año,
            'fecha_registro': self.fecha_registro.isoformat(),
            'consumo_por_categoria': self.consumo_por_categoria,
            'resumen': self.obtener_resumen()
        }
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def __str__(self):
        return f"RegionalConsumption({self.region}, {self.mes}-{self.año}, {self.calcular_total_mwh():.2f} MWh)"
    
    def __repr__(self):
        return self.__str__()


# Ejemplo de uso
if __name__ == "__main__":
    # Crear balance energético
    balance = EnergyBalance("Octubre", 2024)
    balance.agregar_potencia_nominal('hidraulica', 5198.80)
    balance.agregar_potencia_nominal('eolica', 71.13)
    balance.agregar_potencia_nominal('termica_mci', 2099.91)
    
    balance.produccion_total = 2500.0
    balance.importaciones = 100.0
    balance.exportaciones = 50.0
    balance.consumo_total = 2400.0
    
    print("=== BALANCE ENERGÉTICO ===")
    print(balance)
    resumen = balance.obtener_resumen()
    print(f"Energía renovable: {resumen['energia_renovable']['porcentaje_nominal']:.2f}%")
    
    # Crear consumo regional
    consumo_guayas = RegionalConsumption("Guayas", "Octubre", 2024)
    consumo_guayas.agregar_consumo('residencial', 800.0, 50000, 120000.0)
    consumo_guayas.agregar_consumo('comercial', 300.0, 5000, 60000.0)
    consumo_guayas.agregar_consumo('industrial', 400.0, 500, 80000.0)
    
    print("\n=== CONSUMO REGIONAL ===")
    print(consumo_guayas)
    resumen_regional = consumo_guayas.obtener_resumen()
    print(f"Consumo promedio por cliente: {resumen_regional['consumo_promedio_cliente']:.4f} MWh")
    print(f"Categoría mayor consumo: {resumen_regional['categoria_mayor_consumo']}")
    
    # Exportar a JSON
    print("\n=== EXPORTAR A JSON ===")
    balance_json = balance.to_json()
    print("Balance energético exportado a JSON")
    print(balance_json)
    
    consumo_json = consumo_guayas.to_json()
    print("Consumo regional exportado a JSON")
    print(consumo_json)