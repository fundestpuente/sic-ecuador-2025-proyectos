"""
Analizador principal de datos energéticos
Incluye análisis de períodos antes, durante y después de cortes
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

class EnergyAnalyzer:
    def analyze_correlations(self) -> Dict[str, Any]:
        """
        Análisis de correlaciones entre variables clave (facturación, energía, cortes).
        Devuelve coeficientes de correlación y matrices si es posible.
        """
        resultado = {}
        # Correlación en facturación
        if self.facturacion_data is not None:
            df = self.facturacion_data
            cols = []
            if "facturacion_dolares" in df.columns:
                cols.append("facturacion_dolares")
            if "energia_vendida_mwh" in df.columns:
                cols.append("energia_vendida_mwh")
            if len(cols) >= 2:
                corr = df[cols].corr().to_dict()
                resultado["correlacion_facturacion_energia"] = corr.get("facturacion_dolares", {}).get("energia_vendida_mwh", None)
                resultado["matriz_correlacion"] = corr
        # Correlación con cortes si es posible
        if self.cortes_data is not None and self.facturacion_data is not None:
            # Ejemplo: correlación entre cantidad de cortes por región y facturación por región
            cortes_por_region = self.cortes_data["unidad_de_negocio"].value_counts()
            if "unidad_de_negocio" in self.facturacion_data.columns and "facturacion_dolares" in self.facturacion_data.columns:
                fact_por_region = self.facturacion_data.groupby("unidad_de_negocio")["facturacion_dolares"].sum()
                df_corr = pd.DataFrame({
                    "cortes": cortes_por_region,
                    "facturacion": fact_por_region
                }).dropna()
                if len(df_corr) > 1:
                    corr_val = df_corr["cortes"].corr(df_corr["facturacion"])
                    resultado["correlacion_cortes_facturacion"] = float(corr_val)
        if not resultado:
            resultado["error"] = "No hay suficientes datos para correlaciones"
        return resultado
    def analyze_facturacion_detallada(self) -> Dict[str, Any]:
        """
        Análisis detallado de la facturación eléctrica.
        Devuelve métricas agregadas y estadísticas básicas.
        """
        if self.facturacion_data is None or len(self.facturacion_data) == 0:
            return {"error": "No hay datos de facturación disponibles"}

        df = self.facturacion_data
        resultado = {
            "total_registros": len(df),
        }
        # Sumar facturación y energía vendida si existen las columnas
        if "facturacion_dolares" in df.columns:
            resultado["facturacion_total_dolares"] = float(df["facturacion_dolares"].sum())
            resultado["facturacion_promedio_dolares"] = float(df["facturacion_dolares"].mean())
        if "energia_vendida_mwh" in df.columns:
            resultado["energia_total_vendida_mwh"] = float(df["energia_vendida_mwh"].sum())
            resultado["energia_promedio_vendida_mwh"] = float(df["energia_vendida_mwh"].mean())
        # Estadísticas por unidad de negocio si existe
        if "unidad_de_negocio" in df.columns and "facturacion_dolares" in df.columns:
            resultado["facturacion_por_unidad"] = (
                df.groupby("unidad_de_negocio")["facturacion_dolares"].sum().to_dict()
            )
        return resultado
    def analyze_balance_energetico(self) -> Dict[str, Any]:
        """
        Análisis general del balance energético para todos los datos disponibles.
        Devuelve métricas agregadas y estadísticas básicas.
        """
        if self.balance_data is None or len(self.balance_data) == 0:
            return {"error": "No hay datos de balance energético disponibles"}

        df = self.balance_data
        resultado = {
            "total_registros": len(df),
        }
        # Sumar generación y demanda si existen las columnas
        if "generacion_total_mwh" in df.columns:
            resultado["generacion_total_mwh"] = float(df["generacion_total_mwh"].sum())
        if "demanda_total_mwh" in df.columns:
            resultado["demanda_total_mwh"] = float(df["demanda_total_mwh"].sum())
        # Llamar a análisis por período completo
        resultado.update(self._analyze_balance_period(df, "global"))
        return resultado
    """
    Clase principal para análisis de datos energéticos
    """
    
    def __init__(self, balance_data=None, facturacion_data=None, cortes_data=None):
        """
        Inicializa el analizador con los datos
        
        Args:
            balance_data: DataFrame con datos de balance energético
            facturacion_data: DataFrame con datos de facturación
            cortes_data: DataFrame con datos de cortes programados
        """
        self.balance_data = balance_data
        self.facturacion_data = facturacion_data
        self.cortes_data = cortes_data
        
        # Definir períodos
        self.fecha_inicio_cortes = "2024-09-01"
        self.fecha_fin_cortes = "2024-12-31"
        
        # Análisis adicionales
        self.balance_analysis = {}
        self.facturacion_analysis = {}
        self.correlation_analysis = {}
        
        print(f"[OK] EnergyAnalyzer inicializado")
        if balance_data is not None:
            print(f"   [DATOS] Balance: {len(balance_data)} registros")
        if facturacion_data is not None:
            print(f"   [DINERO] Facturación: {len(facturacion_data)} registros")
        if cortes_data is not None:
            print(f"   [ELECTRICO] Cortes: {len(cortes_data)} registros")
    
    def analyze_before_outages(self) -> Dict[str, Any]:
        """
        Analiza el período antes de los cortes programados
        
        Returns:
            Diccionario con análisis del período pre-cortes
        """
        print("[DATOS] Analizando período ANTES de cortes (sep 2023 -agosto 2024)...")
        
        analysis = {
            "periodo": "antes_cortes",
            "fecha_inicio": "2023-09-01",
            "fecha_fin": "2024-08-31",
            "timestamp": datetime.now().isoformat()
        }
        
        # Análisis básico si tenemos datos de facturación
        if self.facturacion_data is not None:
            # Filtrar datos del período
            df_periodo = self._filter_by_period(
                self.facturacion_data, 
                "2023-09-01", 
                "2024-08-31"
            )
            
            if len(df_periodo) > 0:
                analysis.update(self._calculate_period_stats(df_periodo, "antes_cortes"))
            else:
                analysis["error"] = "No hay datos para el período antes de cortes"
        
        # Análisis de balance si disponible
        if self.balance_data is not None:
            balance_stats = self._analyze_balance_period(self.balance_data, "antes_cortes")
            analysis["balance_energetico"] = balance_stats
        
        print(f"[OK] Análisis período antes de cortes completado")
        return analysis
    
    def analyze_during_outages(self) -> Dict[str, Any]:
        """
        Analiza el período durante los cortes programados
        
        Returns:
            Diccionario con análisis del período de cortes
        """
        print("[DATOS] Analizando período DURANTE cortes (septiembre-diciembre 2024)...")
        
        analysis = {
            "periodo": "durante_cortes",
            "fecha_inicio": self.fecha_inicio_cortes,
            "fecha_fin": self.fecha_fin_cortes,
            "timestamp": datetime.now().isoformat()
        }
        
        # Análisis específico de cortes
        if self.cortes_data is not None:
            analysis["cortes_stats"] = self._analyze_outages()
        
        # Análisis de facturación durante cortes
        if self.facturacion_data is not None:
            df_periodo = self._filter_by_period(
                self.facturacion_data,
                self.fecha_inicio_cortes,
                self.fecha_fin_cortes
            )
            
            if len(df_periodo) > 0:
                analysis.update(self._calculate_period_stats(df_periodo, "durante_cortes"))
        
        print(f"[OK] Análisis período durante cortes completado")
        return analysis
    
    def analyze_after_outages(self) -> Dict[str, Any]:
        """
        Analiza el período después de los cortes programados
        
        Returns:
            Diccionario con análisis del período post-cortes
        """
        print("[DATOS] Analizando período DESPUÉS de cortes (enero 2025+)...")
        
        analysis = {
            "periodo": "despues_cortes",
            "fecha_inicio": "2025-01-01",
            "fecha_fin": "2025-12-31",
            "timestamp": datetime.now().isoformat()
        }
        
        # Como estamos en octubre 2025, podríamos tener algunos datos
        if self.facturacion_data is not None:
            df_periodo = self._filter_by_period(
                self.facturacion_data,
                "2025-01-01",
                "2025-12-31"
            )
            
            if len(df_periodo) > 0:
                analysis.update(self._calculate_period_stats(df_periodo, "despues_cortes"))
            else:
                analysis["nota"] = "Datos del período post-cortes aún no disponibles"
        
        print(f"[OK] Análisis período después de cortes completado")
        return analysis
    
    def analyze_regional_impact(self) -> Dict[str, Any]:
        """
        Analiza el impacto por región
        
        Returns:
            Diccionario con análisis de impacto regional
        """
        print("[EMOJI] Analizando impacto por región...")
        
        regional_analysis = {
            "timestamp": datetime.now().isoformat(),
            "regiones": {}
        }
        
        if self.cortes_data is not None:
            # Análisis de cortes por región
            cortes_por_region = self.cortes_data.groupby('unidad_de_negocio').agg({
                'duracion_horas': ['count', 'sum', 'mean'],
                'fecha_inicio': ['min', 'max']
            }).round(2)
            
            for region in cortes_por_region.index:
                regional_analysis["regiones"][region] = {
                    "total_cortes": int(cortes_por_region.loc[region, ('duracion_horas', 'count')]),
                    "duracion_total_horas": float(cortes_por_region.loc[region, ('duracion_horas', 'sum')]),
                    "duracion_promedio_horas": float(cortes_por_region.loc[region, ('duracion_horas', 'mean')]),
                    "primer_corte": str(cortes_por_region.loc[region, ('fecha_inicio', 'min')]),
                    "ultimo_corte": str(cortes_por_region.loc[region, ('fecha_inicio', 'max')])
                }
        
        print(f"[OK] Análisis regional completado para {len(regional_analysis['regiones'])} regiones")
        return regional_analysis
    
    def find_critical_hours(self) -> Dict[str, Any]:
        """
        Identifica horarios críticos de cortes
        
        Returns:
            Diccionario con análisis de horarios críticos
        """
        print("⏰ Identificando horarios críticos...")
        
        critical_hours = {
            "timestamp": datetime.now().isoformat(),
            "horarios_criticos": {}
        }
        
        if self.cortes_data is not None:
            # Extraer hora de inicio
            self.cortes_data['hora_inicio_num'] = self.cortes_data['hora_inicio'].apply(
                lambda x: int(str(x).split(':')[0]) if ':' in str(x) else 0
            )
            
            # Contar cortes por hora
            horarios_count = self.cortes_data.groupby('hora_inicio_num').size().sort_values(ascending=False)
            
            for hora, count in horarios_count.head(10).items():
                critical_hours["horarios_criticos"][f"{hora:02d}:00"] = int(count)
            
            # Estadísticas adicionales
            critical_hours["estadisticas"] = {
                "hora_mas_critica": f"{horarios_count.index[0]:02d}:00",
                "cortes_en_hora_critica": int(horarios_count.iloc[0]),
                "total_horarios_diferentes": len(horarios_count)
            }
        
        print(f"[OK] Horarios críticos identificados")
        return critical_hours
    
    def _filter_by_period(self, df: pd.DataFrame, fecha_inicio: str, fecha_fin: str) -> pd.DataFrame:
        """Filtra DataFrame por período de fechas"""
        # Implementación simplificada - podría mejorarse según estructura real de datos
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')
            mask = (df['fecha'] >= fecha_inicio) & (df['fecha'] <= fecha_fin)
            return df[mask]
        elif 'mes_archivo' in df.columns and 'año_archivo' in df.columns:
            # Filtrar por año y mes del archivo
            año_inicio, mes_inicio = map(int, fecha_inicio.split('-')[:2])
            año_fin, mes_fin = map(int, fecha_fin.split('-')[:2])
            
            mask = ((df['año_archivo'] == año_inicio) & (df['mes_archivo'] >= mes_inicio)) | \
                   ((df['año_archivo'] == año_fin) & (df['mes_archivo'] <= mes_fin)) | \
                   ((df['año_archivo'] > año_inicio) & (df['año_archivo'] < año_fin))
            return df[mask]
        else:
            return df  # Retornar todo si no se puede filtrar
    
    def _calculate_period_stats(self, df: pd.DataFrame, periodo: str) -> Dict[str, Any]:
        """Calcula estadísticas para un período específico"""
        stats = {
            f"total_registros_{periodo}": len(df)
        }
        
        # Buscar columnas de MWh para calcular consumo
        mwh_columns = [col for col in df.columns if 'MWh_' in col]
        if mwh_columns:
            total_consumo = df[mwh_columns].sum().sum()
            stats[f"consumo_total_mwh_{periodo}"] = float(total_consumo)
        
        # Buscar columnas de facturación
        fact_columns = [col for col in df.columns if 'FACT_' in col]
        if fact_columns:
            total_facturacion = df[fact_columns].sum().sum()
            stats[f"facturacion_total_usd_{periodo}"] = float(total_facturacion)
        
        # Buscar columnas de clientes
        client_columns = [col for col in df.columns if 'Clientes_' in col]
        if client_columns:
            total_clientes = df[client_columns].sum().sum()
            stats[f"total_clientes_{periodo}"] = int(total_clientes)
        
        return stats
    
    def _analyze_balance_period(self, df: pd.DataFrame, periodo: str) -> Dict[str, Any]:
        """Analiza balance energético para un período"""
        return {
            f"registros_balance_{periodo}": len(df),
            "nota": "Análisis de balance energético pendiente de implementar"
        }
    
    def _analyze_outages(self) -> Dict[str, Any]:
        """Analiza estadísticas específicas de cortes"""
        if self.cortes_data is None:
            return {}
        
        return {
            "total_cortes": len(self.cortes_data),
            "duracion_total_horas": float(self.cortes_data['duracion_horas'].sum()),
            "duracion_promedio_horas": float(self.cortes_data['duracion_horas'].mean()),
            "regiones_afectadas": int(self.cortes_data['unidad_de_negocio'].nunique()),
            "cantones_afectados": int(self.cortes_data['canton'].nunique()),
            "region_mas_afectada": self.cortes_data['unidad_de_negocio'].value_counts().index[0]
        }
    
    def get_full_analysis(self) -> Dict[str, Any]:
        """
        Ejecuta análisis completo de todos los períodos
        
        Returns:
            Diccionario con análisis completo
        """
        print("[DEBUG] Ejecutando análisis completo...")
        
        full_analysis = {
            "metadata": {
                "proyecto": "Análisis Demanda Eléctrica Ecuador",
                "fecha_analisis": datetime.now().isoformat(),
                "version": "1.0"
            },
            "analisis_temporal": {
                "antes_cortes": self.analyze_before_outages(),
                "durante_cortes": self.analyze_during_outages(),
                "despues_cortes": self.analyze_after_outages()
            },
            "analisis_regional": self.analyze_regional_impact(),
            "horarios_criticos": self.find_critical_hours()
        }
        
        print("[OK] Análisis completo finalizado")
        return full_analysis


# Ejemplo de uso
if __name__ == "__main__":
    print("🧪 Probando EnergyAnalyzer...")
    
    # Crear analizador sin datos (para prueba)
    analyzer = EnergyAnalyzer()
    
    # Simular algunos datos de prueba
    import pandas as pd
    
    # Datos de cortes simulados
    cortes_test = pd.DataFrame({
        'fecha_inicio': pd.date_range('2024-09-01', periods=10, freq='D'),
        'fecha_fin': pd.date_range('2024-09-01', periods=10, freq='D'),
        'hora_inicio': ['22:00'] * 10,
        'hora_fin': ['02:00'] * 10,
        'unidad_de_negocio': ['GUAYAQUIL', 'MANABI'] * 5,
        'canton': ['Guayaquil', 'Portoviejo'] * 5,
        'duracion_horas': [4.0] * 10
    })
    
    analyzer.cortes_data = cortes_test
    
    # Ejecutar análisis de prueba
    resultado_antes = analyzer.analyze_before_outages()
    print(f"[DATOS] Resultado de prueba: {resultado_antes}")

    resultado_durante = analyzer.analyze_during_outages()
    print(f"[DATOS] Resultado de prueba: {resultado_durante}")

    resultado_despues = analyzer.analyze_after_outages()
    print(f"[DATOS] Resultado de prueba: {resultado_despues}")
    
    impacto_regional = analyzer.analyze_regional_impact()
    print(f"[DATOS] Impacto regional: {impacto_regional}")

    horarios_criticos = analyzer.find_critical_hours()
    print(f"[DATOS] Horarios críticos: {horarios_criticos}")
    
    # Realizar análisis completo
    analisis_completo = analyzer.get_full_analysis()
    print(f"[DATOS] Análisis completo: {analisis_completo}")

    print("[OK] Prueba de EnergyAnalyzer completada")