"""
Análisis principal EXPANDIDO de demanda eléctrica Ecuador 2024
Incluye análisis integrado de balance energético, facturación y correlaciones
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_processing.data_loader import DataLoader
from src.analysis.extended_analyzer import ExtendedEnergyAnalyzer
from src.visualization.integrated_dashboard import IntegratedDashboard
import json

def main():
    """Función principal del análisis expandido"""
    
    print("=" * 80)
    print("                   ANÁLISIS INTEGRADO DE ENERGÍA ECUADOR 2024")
    print("=" * 80)
    
    try:
        # 1. Cargar datos
        print("\n🔄 Cargando datos...")
        loader = DataLoader()
        
        balance_data = loader.load_balance_data()
        facturacion_data = loader.load_facturacion_data()
        cortes_data = loader.load_cortes_data()
        
        print(f"✅ Balance energético cargado: {len(balance_data)} registros")
        print(f"✅ Facturación cargada: {len(facturacion_data)} registros")
        print(f"✅ Cortes programados cargados: {len(cortes_data)} registros")
        
        # 2. Crear analizador expandido
        print("\n📊 Realizando análisis energético integrado...")
        analyzer = ExtendedEnergyAnalyzer(
            balance_data=balance_data,
            facturacion_data=facturacion_data,
            cortes_data=cortes_data
        )
        
        # 3. Ejecutar análisis originales
        print("\n📊 Analizando período ANTES de cortes (enero-agosto 2024)...")
        antes_cortes = analyzer.analyze_before_outages()
        print("✅ Análisis período antes de cortes completado")
        
        print("\n📊 Analizando período DURANTE cortes (septiembre-diciembre 2024)...")
        durante_cortes = analyzer.analyze_during_outages()
        print("✅ Análisis período durante cortes completado")
        
        print("\n📊 Analizando período DESPUÉS de cortes (enero 2025+)...")
        despues_cortes = analyzer.analyze_after_outages()
        print("✅ Análisis período después de cortes completado")
        
        print("\n🏢 Analizando impacto por región...")
        impacto_regional = analyzer.analyze_regional_impact()
        print("✅ Análisis regional completado para 11 regiones")
        
        print("\n⏰ Identificando horarios críticos...")
        horarios_criticos = analyzer.find_critical_hours()
        print("✅ Horarios críticos identificados")
        
        # 4. Ejecutar nuevos análisis expandidos
        print("\n🔋 Ejecutando análisis de balance energético nacional...")
        balance_analysis = analyzer.analyze_balance_energetico()
        
        print("\n💰 Ejecutando análisis detallado de facturación...")
        facturacion_analysis = analyzer.analyze_facturacion_detallada()
        
        print("\n🔗 Ejecutando análisis de correlaciones...")
        correlation_analysis = analyzer.analyze_correlations()
        # Resumen estadístico (Punto 3)
        print("\n📐 Ejecutando resumen estadístico (Punto 3)...")
        statistical_summary = analyzer.analyze_statistical_summary()
        print("✅ Resumen estadístico generado")
        
        # 5. Generar visualizaciones integradas
        print("\n📈 Generando visualizaciones integradas...")
        dashboard = IntegratedDashboard()
        
        # Asegurar carpeta de exportaciones (usar la ruta del DataLoader si existe)
        # Nota: en DataLoader se usa 'data/exports' en minúsculas
        export_dir = None
        try:
            export_dir = loader.exports_path  # viene de DataLoader
        except Exception:
            export_dir = os.path.join('data', 'exports')
        os.makedirs(export_dir, exist_ok=True)

        dashboard_path = os.path.join(export_dir, 'dashboard_integrado.png')

        # Dashboard integrado principal
        print("🎨 Creando dashboard integrado...")
        success = dashboard.create_integrated_dashboard(analyzer, dashboard_path)
        
        if success:
            print("✅ Dashboard integrado generado exitosamente")
        else:
            print("⚠️ Problemas generando dashboard integrado")
        
        # 6. Exportar resultados expandidos
        print("\n💾 Exportando resultados integrados...")
        
        resultados_integrados = {
            "analisis_original": {
                "antes_cortes": antes_cortes,
                "durante_cortes": durante_cortes,
                "despues_cortes": despues_cortes,
                "impacto_regional": impacto_regional,
                "horarios_criticos": horarios_criticos
            },
            "analisis_expandido": {
                "balance_energetico": balance_analysis,
                "facturacion_detallada": facturacion_analysis,
                "correlaciones": correlation_analysis,
                "resumen_estadistico": statistical_summary
            }
        }
        
        # Guardar resultados (JSON)
        resultados_path = os.path.join(export_dir, 'resultados_integrados.json')
        with open(resultados_path, 'w', encoding='utf-8') as f:
            json.dump(resultados_integrados, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Datos integrados guardados en: {resultados_path}")
        print(f"✅ Dashboard integrado guardado en: {dashboard_path}")
        
        print("\n🎉 ANÁLISIS INTEGRADO COMPLETADO EXITOSAMENTE!")
        print("📁 Revisa los archivos generados en Data/exports/")
        print("\n📊 RESUMEN DE ANÁLISIS REALIZADO:")
        print("   • Balance energético nacional (capacidad, generación, interconexiones)")
        print("   • Facturación detallada por región, categoría y voltaje") 
        print("   • Correlaciones entre balance, facturación y cortes")
        print("   • Impacto económico de la crisis energética")
        print("   • Eficiencia energética regional")
        print("   • Análisis temporal integrado")
        
    except Exception as e:
        print(f"\n❌ Error en análisis principal: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()