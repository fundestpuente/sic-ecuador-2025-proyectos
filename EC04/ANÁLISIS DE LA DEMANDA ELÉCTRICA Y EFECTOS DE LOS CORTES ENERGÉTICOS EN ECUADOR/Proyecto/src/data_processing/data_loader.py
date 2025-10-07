"""
Cargador de datos para el proyecto energético
Maneja la carga de todos los datasets del proyecto
"""

import pandas as pd
import os
import glob
from typing import Dict, List, Optional
import json
from datetime import datetime

class DataLoader:
    """
    Clase principal para cargar todos los datos del proyecto
    """
    
    def __init__(self, base_path: Optional[str] = None, project_root: Optional[str] = None):
        """
        Inicializa el cargador de datos
        
        Args:
            base_path: Ruta base donde están los datos
        """
        # Determinar el project_root a partir de la ubicación del archivo si no se pasa
        if project_root:
            self.project_root = os.path.abspath(project_root)
        else:
            # data_loader.py está en Proyecto/src/data_processing -> subir dos niveles a Proyecto
            self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

        # Si no se pasa base_path, usar data/raw dentro del proyecto
        if base_path is None:
            base_path = os.path.join(self.project_root, 'data', 'raw')
        else:
            # Si se pasa una ruta relativa, interpretarla respecto al project_root
            if not os.path.isabs(base_path):
                base_path = os.path.join(self.project_root, base_path)

        self.base_path = os.path.abspath(base_path)
        self.balance_path = os.path.join(self.base_path, "Balance_mensual")
        self.facturacion_path = os.path.join(self.base_path, "Facturacion_mensual")
        self.cortes_path = os.path.join(self.base_path, "Cortes_programados")

        # Ruta por defecto para exportaciones dentro de Proyecto/data/exports
        self.exports_path = os.path.join(self.project_root, 'data', 'exports')
        
        # Cache para datos cargados
        self._balance_cache = None
        self._facturacion_cache = None
        self._cortes_cache = None
    
    def load_cortes_data(self) -> Optional[pd.DataFrame]:
        """
        Carga datos de cortes programados
        
        Returns:
            DataFrame con datos de cortes o None si hay error
        """
        if self._cortes_cache is not None:
            return self._cortes_cache
        
        try:
            cortes_file = os.path.join(self.cortes_path, "cortes_programados_sep_dic2024.csv")
            
            if not os.path.exists(cortes_file):
                print(f"[ERROR] Archivo no encontrado: {cortes_file}")
                return None
            
            # Intentar diferentes codificaciones
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(cortes_file, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                print(f"[ERROR] No se pudo leer el archivo de cortes con ninguna codificación")
                return None
            
            # Limpiar datos
            df = self._clean_cortes_data(df)
            
            self._cortes_cache = df
            print(f"[OK] Cortes programados cargados: {len(df)} registros")
            
            return df
            
        except Exception as e:
            print(f"[ERROR] Error cargando cortes: {str(e)}")
            return None
    
    def _clean_cortes_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y procesa datos de cortes"""
        df_clean = df.copy()
        
        # Corregir nombre de columna con error tipográfico
        if 'fecha_incio' in df_clean.columns:
            df_clean['fecha_inicio'] = df_clean['fecha_incio']
            df_clean = df_clean.drop('fecha_incio', axis=1)
        
        # Convertir fechas (formato esperado: DD/MM/YYYY)
        try:
            df_clean['fecha_inicio'] = pd.to_datetime(df_clean['fecha_inicio'], format='%d/%m/%Y')
            df_clean['fecha_fin'] = pd.to_datetime(df_clean['fecha_fin'], format='%d/%m/%Y')
        except Exception:
            # Intentar con dayfirst=True para formatos mixtos
            try:
                df_clean['fecha_inicio'] = pd.to_datetime(df_clean['fecha_inicio'], dayfirst=False, errors='coerce')
                df_clean['fecha_fin'] = pd.to_datetime(df_clean['fecha_fin'], dayfirst=False, errors='coerce')
            except Exception:
                # Último recurso: inferir formato
                df_clean['fecha_inicio'] = pd.to_datetime(df_clean['fecha_inicio'], infer_datetime_format=True, errors='coerce')
                df_clean['fecha_fin'] = pd.to_datetime(df_clean['fecha_fin'], infer_datetime_format=True, errors='coerce')
        
        # Calcular duración en horas
        def calcular_duracion(hora_inicio, hora_fin):
            try:
                inicio = pd.to_datetime(hora_inicio, format='%H:%M').time()
                fin = pd.to_datetime(hora_fin, format='%H:%M').time()
                
                inicio_min = inicio.hour * 60 + inicio.minute
                fin_min = fin.hour * 60 + fin.minute
                
                # Si cruza medianoche
                if fin_min < inicio_min:
                    fin_min += 24 * 60
                
                return (fin_min - inicio_min) / 60
            except:
                return 0
        
        df_clean['duracion_horas'] = df_clean.apply(
            lambda row: calcular_duracion(row['hora_inicio'], row['hora_fin']), axis=1
        )
        
        # Limpiar nombres de regiones
        df_clean['unidad_de_negocio'] = df_clean['unidad_de_negocio'].str.upper().str.strip()
        df_clean['canton'] = df_clean['canton'].str.upper().str.strip()
        
        return df_clean
    
    def load_balance_data(self) -> Optional[pd.DataFrame]:
        """
        Carga todos los archivos de balance energético
        
        Returns:
            DataFrame consolidado con todos los balances mensuales
        """
        if self._balance_cache is not None:
            return self._balance_cache
        
        try:
            # Buscar todos los archivos CSV de balance
            pattern = os.path.join(self.balance_path, "*.csv")
            archivos = glob.glob(pattern)
            
            if not archivos:
                print(f"[ERROR] No se encontraron archivos de balance en: {self.balance_path}")
                return None
            
            balance_data = []
            
            for archivo in archivos:
                try:
                    # Extraer fecha del nombre del archivo
                    nombre_archivo = os.path.basename(archivo)
                    fecha_info = self._extract_date_from_filename(nombre_archivo)
                    
                    # Este tipo de archivo tiene formato especial, necesita procesamiento personalizado
                    df_archivo = self._load_balance_file(archivo, fecha_info)
                    
                    if df_archivo is not None:
                        balance_data.append(df_archivo)
                        
                except Exception as e:
                    print(f"[WARNING] Error procesando {archivo}: {str(e)}")
                    continue
            
            if balance_data:
                df_consolidated = pd.concat(balance_data, ignore_index=True)
                self._balance_cache = df_consolidated
                print(f"[OK] Balance energético cargado: {len(df_consolidated)} registros de {len(archivos)} archivos")
                return df_consolidated
            else:
                print("[ERROR] No se pudieron cargar datos de balance")
                return None
                
        except Exception as e:
            print(f"[ERROR] Error cargando balance: {str(e)}")
            return None
    
    def _load_balance_file(self, filepath: str, fecha_info: Dict) -> Optional[pd.DataFrame]:
        """Carga un archivo individual de balance energético"""
        try:
            # Intentar diferentes codificaciones
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            lines = None
            
            for encoding in encodings:
                try:
                    with open(filepath, 'r', encoding=encoding) as f:
                        lines = f.readlines()
                    break
                except UnicodeDecodeError:
                    continue
            
            if lines is None:
                print(f"[WARNING] No se pudo leer {filepath} con ninguna codificación")
                return None
            
            # Extraer datos relevante
            data_dict = {
                'archivo': os.path.basename(filepath),
                'año': fecha_info.get('año'),
                'mes': fecha_info.get('mes'),
                'fecha_archivo': fecha_info.get('fecha_completa')
            }
            
            # Procesar líneas buscando datos de potencia y energía
            for line in lines:
                if 'Hidr' in line or 'hidraulica' in line.lower():
                    # Extraer datos de energía hidráulica
                    pass
                elif 'E[EMOJI]lica' in line or 'eolica' in line.lower():
                    # Extraer datos de energía eólica
                    pass
                # ... más procesamiento según estructura del archivo
            
            return pd.DataFrame([data_dict])
            
        except Exception as e:
            print(f"Error procesando archivo de balance {filepath}: {str(e)}")
            return None
    
    def load_facturacion_data(self) -> Optional[pd.DataFrame]:
        """
        Carga todos los archivos de facturación
        
        Returns:
            DataFrame consolidado con facturación por región
        """
        if self._facturacion_cache is not None:
            return self._facturacion_cache
        
        try:
            pattern = os.path.join(self.facturacion_path, "*.csv")
            archivos = glob.glob(pattern)
            
            if not archivos:
                print(f"[ERROR] No se encontraron archivos de facturación en: {self.facturacion_path}")
                return None
            
            facturacion_data = []
            
            for archivo in archivos:
                try:
                    # Intentar diferentes codificaciones para archivos CSV
                    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
                    df = None
                    
                    for encoding in encodings:
                        try:
                            df = pd.read_csv(archivo, sep=';', encoding=encoding)
                            break
                        except UnicodeDecodeError:
                            continue
                    
                    if df is None:
                        print(f"[WARNING] No se pudo leer {archivo} con ninguna codificación")
                        continue
                    
                    # Agregar información del archivo
                    fecha_info = self._extract_date_from_filename(os.path.basename(archivo))
                    df['año_archivo'] = fecha_info.get('año')
                    df['mes_archivo'] = fecha_info.get('mes')
                    df['archivo_origen'] = os.path.basename(archivo)
                    
                    facturacion_data.append(df)
                    
                except Exception as e:
                    print(f"[WARNING] Error procesando {archivo}: {str(e)}")
                    continue
            
            if facturacion_data:
                df_consolidated = pd.concat(facturacion_data, ignore_index=True)
                df_consolidated = self._clean_facturacion_data(df_consolidated)
                
                self._facturacion_cache = df_consolidated
                print(f"[OK] Facturación cargada: {len(df_consolidated)} registros de {len(archivos)} archivos")
                return df_consolidated
            else:
                return None
                
        except Exception as e:
            print(f"[ERROR] Error cargando facturación: {str(e)}")
            return None
    
    def _clean_facturacion_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia datos de facturación"""
        df_clean = df.copy()
        
        # Convertir columnas numéricas
        columnas_numericas = [col for col in df_clean.columns if 
                            'MWh_' in col or 'FACT_' in col or 'Clientes_' in col]
        
        for col in columnas_numericas:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Limpiar strings
        columnas_texto = ['Categoria', 'Voltaje', 'Grupo_consumo', 'Tipo_consumo', 'Tarifa']
        for col in columnas_texto:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()
        
        return df_clean
    
    def _extract_date_from_filename(self, filename: str) -> Dict:
        """Extrae información de fecha del nombre del archivo"""
        fecha_info = {'año': None, 'mes': None, 'fecha_completa': None}
        
        try:
            # Buscar patrones de fecha en el nombre
            if '2024' in filename:
                fecha_info['año'] = 2024
            elif '2025' in filename:
                fecha_info['año'] = 2025
            elif '2023' in filename:
                fecha_info['año'] = 2023
            
            # Buscar mes
            meses = {
                'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
                'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
                'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12,
                'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6,
                'jul': 7, 'ago': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12
            }
            
            filename_lower = filename.lower()
            for mes_nombre, mes_num in meses.items():
                if mes_nombre in filename_lower:
                    fecha_info['mes'] = mes_num
                    break
            
            # Crear fecha completa si tenemos año y mes
            if fecha_info['año'] and fecha_info['mes']:
                fecha_info['fecha_completa'] = f"{fecha_info['año']}-{fecha_info['mes']:02d}-01"
            
        except Exception as e:
            print(f"Error extrayendo fecha de {filename}: {str(e)}")
        
        return fecha_info
    
    def get_data_summary(self) -> Dict:
        """
        Obtiene un resumen de todos los datos cargados
        
        Returns:
            Diccionario con estadísticas de los datos
        """
        summary = {
            'fecha_carga': datetime.now().isoformat(),
            'cortes': None,
            'balance': None,
            'facturacion': None
        }
        
        # Resumen de cortes
        if self._cortes_cache is not None:
            df_cortes = self._cortes_cache
            summary['cortes'] = {
                'total_registros': len(df_cortes),
                'fecha_inicio': df_cortes['fecha_inicio'].min().strftime('%Y-%m-%d'),
                'fecha_fin': df_cortes['fecha_fin'].max().strftime('%Y-%m-%d'),
                'regiones_afectadas': df_cortes['unidad_de_negocio'].nunique(),
                'cantones_afectados': df_cortes['canton'].nunique(),
                'duracion_total_horas': df_cortes['duracion_horas'].sum(),
                'duracion_promedio_horas': df_cortes['duracion_horas'].mean()
            }
        
        # Resumen de facturación
        if self._facturacion_cache is not None:
            df_fact = self._facturacion_cache
            summary['facturacion'] = {
                'total_registros': len(df_fact),
                'archivos_procesados': df_fact['archivo_origen'].nunique(),
                'categorias': df_fact['Categoria'].nunique() if 'Categoria' in df_fact.columns else 0,
                'tarifas': df_fact['Tarifa'].nunique() if 'Tarifa' in df_fact.columns else 0,
                'consumo_total_MWh': df_fact[[col for col in df_fact.columns if 'MWh_' in col]].sum().sum(),
                'facturacion_total_USD': df_fact[[col for col in df_fact.columns if 'FACT_' in col]].sum().sum(),
                'clientes_totales': df_fact[[col for col in df_fact.columns if 'Clientes_' in col]].sum().sum()
            }
        
        # Resumen de balance
        if self._balance_cache is not None:
            df_balance = self._balance_cache
            summary['balance'] = {
                'total_registros': len(df_balance),
                'archivos_procesados': df_balance['archivo'].nunique() if 'archivo' in df_balance.columns else 0,
                'anios_cubiertos': df_balance['año'].nunique() if 'año' in df_balance.columns else 0,
                'meses_cubiertos': df_balance['mes'].nunique() if 'mes' in df_balance.columns else 0
            }
        
        return summary
    
    def export_summary(self, filepath: Optional[str] = None):
        """Exporta resumen de datos a JSON.

        Si `filepath` es None se usará por defecto `Proyecto/data/exports/data_summary.json`.
        Si `filepath` es relativo se interpretará respecto al `project_root`.
        """
        try:
            if filepath is None:
                filepath = os.path.join(self.exports_path, 'data_summary.json')
            else:
                # Si la ruta es relativa, resolverla respecto al project_root
                if not os.path.isabs(filepath):
                    filepath = os.path.join(self.project_root, filepath)

            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            summary = self.get_data_summary()

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

            print(f"[OK] Resumen exportado a: {filepath}")

        except Exception as e:
            print(f"[ERROR] Error exportando resumen: {str(e)}")


# Función de conveniencia para carga rápida
def load_all_data(base_path: str = "data/raw") -> Dict[str, pd.DataFrame]:
    """
    Carga todos los datos de una vez
    
    Returns:
        Diccionario con todos los DataFrames cargados
    """
    loader = DataLoader(base_path)
    
    return {
        'cortes': loader.load_cortes_data(),
        'facturacion': loader.load_facturacion_data(),
        'balance': loader.load_balance_data()
    }


# Ejemplo de uso

if __name__ == "__main__":
    
    print("Probando cargador de datos...")
    
    loader = DataLoader()
    
    # Cargar cortes (más simple para empezar)
    df_cortes = loader.load_cortes_data()
    if df_cortes is not None:
        print(f"Cortes cargados: {len(df_cortes)} registros")
        print(f"Regiones: {df_cortes['unidad_de_negocio'].unique()}")
        print(df_cortes.columns.tolist())
    
    # Cargar facturación
    df_facturacion = loader.load_facturacion_data()
    if df_facturacion is not None:
        print(f"Facturación cargada: {len(df_facturacion)} registros")
        print(df_facturacion.columns.tolist())

    # Cargar balance
    df_balance = loader.load_balance_data()
    if df_balance is not None:
        print(f"Balance cargado: {len(df_balance)} registros")
        print(df_balance.columns.tolist())

    # Generar resumen
    summary = loader.get_data_summary()
    print(f"\nResumen de datos:")
    print(json.dumps(summary, indent=2, default=str))
    
    # Exportar resumen
    loader.export_summary()
    
    print("\n[OK] Prueba de cargador completada")
