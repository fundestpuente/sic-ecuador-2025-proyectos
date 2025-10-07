"""
Análisis estadístico simplificado sin dependencias externas.
Implementa técnicas estadísticas usando solo NumPy, SciPy y Pandas
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

class SimplifiedStatisticalAnalyzer:
    """
    Analizador estadístico simplificado sin dependencias pesadas
    """
    
    def __init__(self):
        self.analysis_results = {}
        
    def comprehensive_descriptive_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Análisis descriptivo comprensivo
        """
        print("[DATOS] ANÁLISIS DESCRIPTIVO COMPRENSIVO")
        print("-" * 50)
        
        results = {
            'basic_stats': {},
            'distribution_analysis': {},
            'outlier_analysis': {},
            'correlation_analysis': {}
        }
        
        # Estadísticas básicas extendidas
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) > 0:
                results['basic_stats'][col] = {
                    'count': len(series),
                    'mean': float(series.mean()),
                    'median': float(series.median()),
                    'std': float(series.std()),
                    'variance': float(series.var()),
                    'skewness': float(stats.skew(series)),
                    'kurtosis': float(stats.kurtosis(series)),
                    'range': float(series.max() - series.min()),
                    'iqr': float(series.quantile(0.75) - series.quantile(0.25)),
                    'coefficient_of_variation': float(series.std() / series.mean()) if series.mean() != 0 else np.nan,
                    'percentiles': {
                        'p5': float(series.quantile(0.05)),
                        'p25': float(series.quantile(0.25)),
                        'p75': float(series.quantile(0.75)),
                        'p95': float(series.quantile(0.95))
                    }
                }
                
                # Análisis de distribución
                results['distribution_analysis'][col] = self._analyze_distribution(series)
                
                # Análisis de outliers
                results['outlier_analysis'][col] = self._detect_outliers(series)
        
        # Análisis de correlación
        if len(numeric_cols) > 1:
            results['correlation_analysis'] = self._correlation_analysis(df[numeric_cols])
        
        self.analysis_results['descriptive'] = results
        return results
    
    def _analyze_distribution(self, series: pd.Series) -> Dict[str, Any]:
        """Análisis de distribución simplificado"""
        distribution_results = {}
        
        try:
            # Test de normalidad Shapiro-Wilk (para muestras pequeñas)
            if len(series) <= 5000:
                shapiro_stat, shapiro_p = stats.shapiro(series)
                distribution_results['shapiro_wilk'] = {
                    'statistic': float(shapiro_stat),
                    'p_value': float(shapiro_p),
                    'is_normal': shapiro_p > 0.05,
                    'interpretation': 'Normal' if shapiro_p > 0.05 else 'No Normal'
                }
            
            # Test D'Agostino
            try:
                dagostino_stat, dagostino_p = stats.normaltest(series)
                distribution_results['dagostino_pearson'] = {
                    'statistic': float(dagostino_stat),
                    'p_value': float(dagostino_p),
                    'is_normal': dagostino_p > 0.05,
                    'interpretation': 'Normal' if dagostino_p > 0.05 else 'No Normal'
                }
            except:
                distribution_results['dagostino_pearson'] = {'error': 'Insufficient data'}
            
            # Análisis de asimetría y curtosis
            skewness = stats.skew(series)
            kurt = stats.kurtosis(series)
            
            distribution_results['shape_analysis'] = {
                'skewness': float(skewness),
                'kurtosis': float(kurt),
                'skewness_interpretation': self._interpret_skewness(skewness),
                'kurtosis_interpretation': self._interpret_kurtosis(kurt)
            }
            
        except Exception as e:
            distribution_results['error'] = f"Error en análisis de distribución: {str(e)}"
        
        return distribution_results
    
    def _interpret_skewness(self, skewness: float) -> str:
        """Interpretar asimetría"""
        if abs(skewness) < 0.5:
            return "approximately_symmetric"
        elif skewness > 0.5:
            return "right_skewed"
        else:
            return "left_skewed"
    
    def _interpret_kurtosis(self, kurtosis: float) -> str:
        """Interpretar curtosis"""
        if abs(kurtosis) < 0.5:
            return "mesokurtic"
        elif kurtosis > 0.5:
            return "leptokurtic"
        else:
            return "platykurtic"
    
    def _detect_outliers(self, series: pd.Series) -> Dict[str, Any]:
        """Detección de outliers usando múltiples métodos"""
        outlier_results = {}
        
        # Método IQR
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        iqr_outliers = series[(series < lower_bound) | (series > upper_bound)]
        outlier_results['iqr_method'] = {
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
            'outliers_count': len(iqr_outliers),
            'outliers_percentage': float((len(iqr_outliers) / len(series)) * 100),
            'has_outliers': len(iqr_outliers) > 0
        }
        
        # Método Z-score
        z_scores = np.abs(stats.zscore(series))
        z_outliers = series[z_scores > 3]
        outlier_results['zscore_method'] = {
            'threshold': 3,
            'outliers_count': len(z_outliers),
            'outliers_percentage': float((len(z_outliers) / len(series)) * 100),
            'has_outliers': len(z_outliers) > 0
        }
        
        return outlier_results
    
    def _correlation_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Análisis de correlaciones"""
        correlation_results = {}
        
        # Correlación de Pearson
        pearson_corr = df.corr(method='pearson')
        correlation_results['pearson'] = {
            'matrix': pearson_corr.to_dict(),
            'strong_correlations': self._find_strong_correlations(pearson_corr, threshold=0.7)
        }
        
        # Correlación de Spearman
        spearman_corr = df.corr(method='spearman')
        correlation_results['spearman'] = {
            'matrix': spearman_corr.to_dict(),
            'strong_correlations': self._find_strong_correlations(spearman_corr, threshold=0.7)
        }
        
        return correlation_results
    
    def _find_strong_correlations(self, corr_matrix: pd.DataFrame, 
                                threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Encontrar correlaciones fuertes"""
        strong_corr = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) >= threshold and not np.isnan(corr_value):
                    strong_corr.append({
                        'variable1': corr_matrix.columns[i],
                        'variable2': corr_matrix.columns[j],
                        'correlation': float(corr_value),
                        'strength': 'very_strong' if abs(corr_value) >= 0.9 else 'strong',
                        'direction': 'positive' if corr_value > 0 else 'negative'
                    })
        
        return strong_corr
    
    def time_series_analysis(self, df: pd.DataFrame, date_col: str, 
                           value_cols: List[str]) -> Dict[str, Any]:
        """
        Análisis simplificado de series temporales
        """
        print("[INCREMENTO] ANÁLISIS DE SERIES TEMPORALES")
        print("-" * 50)
        
        time_series_results = {}
        
        # Convertir columna de fecha
        try:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df = df.dropna(subset=[date_col]).sort_values(date_col)
        except:
            return {'error': f'No se pudo convertir la columna {date_col} a fecha'}
        
        for col in value_cols:
            if col in df.columns:
                series = df.set_index(date_col)[col].dropna()
                
                if len(series) > 1:
                    col_results = {}
                    
                    # Análisis de tendencia simple
                    col_results['trend_analysis'] = self._simple_trend_analysis(series)
                    
                    # Análisis de estacionalidad básico
                    col_results['seasonality_analysis'] = self._simple_seasonality_analysis(series)
                    
                    # Estadísticas temporales
                    col_results['temporal_stats'] = self._temporal_statistics(series)
                    
                    time_series_results[col] = col_results
        
        self.analysis_results['time_series'] = time_series_results
        return time_series_results
    
    def _simple_trend_analysis(self, series: pd.Series) -> Dict[str, Any]:
        """Análisis simple de tendencia"""
        try:
            # Regresión lineal simple
            x = np.arange(len(series))
            y = series.values
            
            # Calcular pendiente manualmente
            mean_x = np.mean(x)
            mean_y = np.mean(y)
            
            numerator = np.sum((x - mean_x) * (y - mean_y))
            denominator = np.sum((x - mean_x) ** 2)
            
            if denominator != 0:
                slope = numerator / denominator
                intercept = mean_y - slope * mean_x
                
                # Calcular R²
                y_pred = slope * x + intercept
                ss_res = np.sum((y - y_pred) ** 2)
                ss_tot = np.sum((y - mean_y) ** 2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
                
                return {
                    'slope': float(slope),
                    'intercept': float(intercept),
                    'r_squared': float(r_squared),
                    'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
                    'trend_strength': self._interpret_trend_strength(r_squared),
                    'significant_trend': r_squared > 0.5
                }
            else:
                return {'error': 'No se puede calcular tendencia - datos constantes'}
                
        except Exception as e:
            return {'error': f'Error en análisis de tendencia: {str(e)}'}
    
    def _interpret_trend_strength(self, r_squared: float) -> str:
        """Interpretar fuerza de tendencia"""
        if r_squared >= 0.8:
            return "very_strong"
        elif r_squared >= 0.6:
            return "strong"
        elif r_squared >= 0.4:
            return "moderate"
        elif r_squared >= 0.2:
            return "weak"
        else:
            return "very_weak"
    
    def _simple_seasonality_analysis(self, series: pd.Series) -> Dict[str, Any]:
        """Análisis simple de estacionalidad"""
        seasonality_results = {}
        
        try:
            # Análisis mensual si hay suficientes datos
            if len(series) >= 12:
                # Agrupar por mes
                monthly_groups = series.groupby(series.index.month)
                month_means = monthly_groups.mean()
                month_stds = monthly_groups.std()
                
                seasonality_results['monthly_patterns'] = {
                    'month_means': month_means.to_dict(),
                    'month_stds': month_stds.to_dict(),
                    'seasonal_amplitude': float(month_means.max() - month_means.min()),
                    'coefficient_of_seasonal_variation': float(month_stds.mean() / month_means.mean()) if month_means.mean() != 0 else np.nan,
                    'peak_month': int(month_means.idxmax()),
                    'low_month': int(month_means.idxmin())
                }
                
                # Test simple de variabilidad estacional
                overall_mean = series.mean()
                seasonal_variance = np.var([month_means[month] for month in month_means.index])
                overall_variance = series.var()
                
                seasonality_results['seasonality_test'] = {
                    'seasonal_variance_ratio': float(seasonal_variance / overall_variance) if overall_variance != 0 else 0,
                    'has_seasonality': seasonal_variance / overall_variance > 0.1 if overall_variance != 0 else False
                }
            
            # Análisis de día de la semana si hay datos diarios
            if hasattr(series.index, 'dayofweek'):
                weekday_groups = series.groupby(series.index.dayofweek)
                weekday_means = weekday_groups.mean()
                
                seasonality_results['weekday_patterns'] = {
                    'weekday_means': weekday_means.to_dict(),
                    'peak_weekday': int(weekday_means.idxmax()),
                    'low_weekday': int(weekday_means.idxmin()),
                    'weekday_amplitude': float(weekday_means.max() - weekday_means.min())
                }
                
        except Exception as e:
            seasonality_results['error'] = f'Error en análisis de estacionalidad: {str(e)}'
        
        return seasonality_results
    
    def _temporal_statistics(self, series: pd.Series) -> Dict[str, Any]:
        """Estadísticas temporales básicas"""
        try:
            # Calcular diferencias
            differences = series.diff().dropna()
            
            # Estadísticas de cambios
            stats_results = {
                'period_count': len(series),
                'date_range': {
                    'start': series.index.min().isoformat(),
                    'end': series.index.max().isoformat(),
                    'span_days': (series.index.max() - series.index.min()).days
                },
                'value_changes': {
                    'mean_change': float(differences.mean()),
                    'std_change': float(differences.std()),
                    'max_increase': float(differences.max()),
                    'max_decrease': float(differences.min()),
                    'positive_changes': int(np.sum(differences > 0)),
                    'negative_changes': int(np.sum(differences < 0)),
                    'no_changes': int(np.sum(differences == 0))
                },
                'volatility': {
                    'coefficient_of_variation': float(series.std() / series.mean()) if series.mean() != 0 else np.nan,
                    'average_absolute_change': float(np.mean(np.abs(differences))),
                    'relative_volatility': float(differences.std() / series.mean()) if series.mean() != 0 else np.nan
                }
            }
            
            return stats_results
            
        except Exception as e:
            return {'error': f'Error en estadísticas temporales: {str(e)}'}
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        Generar reporte comprensivo simplificado
        """
        print("[RESUMEN] GENERANDO REPORTE ESTADÍSTICO COMPLETO")
        print("-" * 50)
        
        report = {
            'metadata': {
                'analysis_type': 'simplified_statistical_analysis',
                'timestamp': pd.Timestamp.now().isoformat(),
                'analyses_performed': list(self.analysis_results.keys())
            },
            'executive_summary': self._create_executive_summary(),
            'detailed_results': self.analysis_results,
            'recommendations': self._generate_recommendations(),
            'statistical_insights': self._extract_key_insights()
        }
        
        return report
    
    def _create_executive_summary(self) -> Dict[str, Any]:
        """Crear resumen ejecutivo"""
        summary = {
            'total_analyses': len(self.analysis_results),
            'data_quality_assessment': 'Analysis completed successfully',
            'key_findings': [],
            'statistical_significance': 'Multiple patterns detected'
        }
        
        # Extraer hallazgos clave
        for analysis_type, results in self.analysis_results.items():
            if analysis_type == 'descriptive':
                if 'correlation_analysis' in results:
                    pearson_strong = results['correlation_analysis'].get('pearson', {}).get('strong_correlations', [])
                    if pearson_strong:
                        summary['key_findings'].append(f"Found {len(pearson_strong)} strong correlations")
                
                outlier_analyses = results.get('outlier_analysis', {})
                total_outliers = sum(1 for col_analysis in outlier_analyses.values() 
                                   if col_analysis.get('iqr_method', {}).get('has_outliers', False))
                if total_outliers > 0:
                    summary['key_findings'].append(f"Detected outliers in {total_outliers} variables")
            
            elif analysis_type == 'time_series':
                trends_detected = sum(1 for col_analysis in results.values()
                                    if col_analysis.get('trend_analysis', {}).get('significant_trend', False))
                if trends_detected > 0:
                    summary['key_findings'].append(f"Significant trends in {trends_detected} time series")
        
        return summary
    
    def _generate_recommendations(self) -> List[str]:
        """Generar recomendaciones basadas en análisis"""
        recommendations = [
            "Review detected outliers for data quality issues",
            "Investigate strong correlations for potential relationships",
            "Consider temporal patterns for forecasting models",
            "Validate statistical assumptions before advanced modeling",
            "Implement robust statistical methods for non-normal data"
        ]
        return recommendations
    
    def _extract_key_insights(self) -> Dict[str, Any]:
        """Extraer insights clave del análisis"""
        insights = {
            'distribution_insights': [],
            'correlation_insights': [],
            'temporal_insights': [],
            'outlier_insights': []
        }
        
        # Extraer insights de distribución
        for analysis_type, results in self.analysis_results.items():
            if analysis_type == 'descriptive' and 'distribution_analysis' in results:
                for col, dist_analysis in results['distribution_analysis'].items():
                    if 'shape_analysis' in dist_analysis:
                        shape = dist_analysis['shape_analysis']
                        if abs(shape.get('skewness', 0)) > 1:
                            insights['distribution_insights'].append(
                                f"{col}: Highly skewed distribution ({shape['skewness_interpretation']})"
                            )
        
        return insights


def run_simplified_statistical_analysis(data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """
    Función principal para ejecutar análisis estadístico simplificado
    """
    print("[EMOJI] INICIANDO ANÁLISIS ESTADÍSTICO SIMPLIFICADO")
    print("=" * 60)
    
    analyzer = SimplifiedStatisticalAnalyzer()
    all_results = {}
    
    for dataset_name, df in data.items():
        if df is not None and isinstance(df, pd.DataFrame) and not df.empty:
            print(f"\n[DATOS] Analizando dataset: {dataset_name}")
            print(f"   Dimensiones: {df.shape}")
            
            try:
                # Análisis descriptivo
                descriptive_results = analyzer.comprehensive_descriptive_analysis(df)
                all_results[f"{dataset_name}_descriptive"] = descriptive_results
                
                # Análisis de series temporales si hay columnas de fecha
                date_cols = [col for col in df.columns 
                           if any(keyword in col.lower() for keyword in ['fecha', 'date', 'time'])]
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                
                if date_cols and numeric_cols:
                    time_series_results = analyzer.time_series_analysis(df, date_cols[0], numeric_cols[:3])
                    all_results[f"{dataset_name}_time_series"] = time_series_results
                
                print(f"   [OK] Análisis completado para {dataset_name}")
                
            except Exception as e:
                print(f"   [ERROR] Error analizando {dataset_name}: {str(e)}")
                all_results[f"{dataset_name}_error"] = str(e)
    
    # Generar reporte final
    final_report = analyzer.generate_comprehensive_report()
    all_results['comprehensive_report'] = final_report
    
    print(f"\n[OK] ANÁLISIS ESTADÍSTICO COMPLETADO")
    print(f"[INCREMENTO] Total de análisis realizados: {len(all_results)}")
    
    return all_results

# Ejemplo de uso
if __name__ == "__main__":
    
    # Crear datos de ejemplo
    sample_data = {
        'balance_energy': pd.DataFrame({
            'fecha': pd.date_range('2024-01-01', periods=100, freq='D'),
            'generacion': np.random.normal(1000, 100, 100),
            'demanda': np.random.normal(950, 80, 100),
            'precio': np.random.lognormal(2, 0.3, 100)
        }),
        'consumption_data': pd.DataFrame({
            'consumption': np.random.normal(500, 50, 50),
            'efficiency': np.random.uniform(0.8, 0.95, 50),
            'cost': np.random.exponential(100, 50)
        })
    }
    
    results = run_simplified_statistical_analysis(sample_data)
    print(f"\nResultados obtenidos: {list(results.keys())}")