import matplotlib.pyplot as plt
import os
import seaborn as sns
import pandas as pd

from src.processing_data import Data


class Graphics:
    def __init__(self):
        self.data = Data()
    
    def generar_direccion(self):
        script_dir = os.path.dirname(__file__)
        new_path = os.path.join(script_dir,'..','graphics')
        new_path = os.path.abspath(new_path)

        if not os.path.exists(new_path):
            os.makedirs(new_path, exist_ok=True)
        
        return new_path
    
    def grafico_prov_pun(self):
        provincia_puntuacion = self.data.provincia_puntuacion().sort_values('Puntuacion',ascending=True)

        colores = sns.color_palette("Blues",len(provincia_puntuacion))
        plt.figure(figsize=(12,8))

        bars = plt.barh(provincia_puntuacion['Provincia'],provincia_puntuacion['Puntuacion'],color=colores,edgecolor='black',height=0.6)

        for bar in bars:
            width = bar.get_width()
            plt.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                    f'{width:.2f}', va='center', fontsize=10, fontweight='bold', color='black')
        
        plt.xlabel('Puntuacion Promedio')
        plt.ylabel('Provincia')
        plt.grid(axis='x',linestyle='--',alpha=0.7)
        sns.despine(left=True, bottom=True)
        plt.title('Promedio de Puntuación por Provincia')
        plt.xticks(rotation=45)

        plt.tight_layout()

        ruta_guardado  = os.path.join(self.generar_direccion(),'grafico_provincia.png')
        plt.savefig(ruta_guardado, format='png', dpi=300, bbox_inches='tight')

        plt.show()
        plt.close()


    def grafico_gen_pun(self):
        df = self.data.genero_puntuacion_edad()

        rango_edad = ['0-12','12-18','18-30','30-60','+60']
        df['RangoEdad'] = pd.Categorical(df['RangoEdad'],categories=rango_edad,ordered=True)

        plt.figure(figsize=(12,8))

        bars = sns.barplot(
            data=df,
            x='RangoEdad',
            y='Puntuacion',
            hue='Genero',
            dodge=True,
            palette='Set2'
        )

        plt.title('Promedio de Puntuación por Género y Rango de Edad', fontsize=16, fontweight='bold')
        plt.xlabel('Rango de Edad', fontsize=12, fontweight='bold')
        plt.ylabel('Puntuación Promedio', fontsize=12, fontweight='bold')
        plt.xticks(fontsize=12,fontweight='bold',ha='center')
        plt.ylim(0, df['Puntuacion'].max() + 1)
        plt.legend(title='Género')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        sns.despine(left=True, bottom=True)
        plt.tight_layout()
        
        ruta_guardado  = os.path.join(self.generar_direccion(),'grafico_edad.png')
        plt.savefig(ruta_guardado, format='png', dpi=300, bbox_inches='tight')

        plt.show()
        plt.close()

    def grafico_empresa_ent(self):
        df = self.data.empresa_competencia()

        df_melt = df.melt(
            id_vars='Empresa',
            value_vars=['Si','No'],
            var_name='Respuesta',
            value_name='Cantidad'
        )

        plt.figure(figsize=(12,8))
        ax = sns.barplot(
            data=df_melt,
            x='Empresa',
            y='Cantidad',
            hue='Respuesta',
            dodge=True,
            palette='Set2'
        )

        for container in ax.containers:
            ax.bar_label(container) #type:ignore

        plt.title('Competencia Digital por Tipo de Empresa', fontsize=14)
        plt.xticks(rotation=45,ha='right')
        plt.legend(title='Conoce su nivel de competencia')
        plt.tight_layout()

        ruta_guardado  = os.path.join(self.generar_direccion(),'grafico_empresa.png')
        plt.savefig(ruta_guardado, format='png', dpi=300, bbox_inches='tight')

        plt.show()
        plt.close()

    def graphic_si_no(self):
        
        df = self.data.tecnologias_si_no() 

        df = df.sort_values('Si', ascending=False)

        etiquetas_cortas = {
            "Conoce las oportunidades que el IOT (Internet de las cosas) puede aportar en su trabajo y empresa": "IoT",
            "Conoce las oportunidades que el IA (Inteligencia artificial) puede aportar en su trabajo y empresa": "IA",
            "Conoce o ha utilizado servicios de alojamiento de archivos en la nube": "Nube",
            "Ha participado en consultas ciudadanas o encuestas a traves de internet (online) a propuestas de organizaciones publicas o sociales": "Participación",
            "Participa en experiencias innovadoras relacionadas con el uso de nuevas tecnologias": "Innovación"
        }
        df['Etiqueta'] = df['Pregunta'].astype(str).map(lambda x: etiquetas_cortas.get(x, x))

        # 2) Pasar a formato largo para seaborn
        df_melt = df.melt(
            id_vars=['Pregunta', 'Etiqueta'],
            value_vars=['Si', 'No'],
            var_name='Respuesta',
            value_name='Cantidad'
        )

        # 3) Graficar
        plt.figure(figsize=(12, 8))
        ax = sns.barplot(
            data=df_melt,
            x='Etiqueta',
            y='Cantidad',
            hue='Respuesta',
            dodge=True,
            palette='Set2'
        )

        # Etiquetas en barras
        for container in ax.containers:
            ax.bar_label(container, fontsize=10) #type:ignore

        plt.title('Uso de Tecnologías Digitales (Sí vs No)', fontsize=16, fontweight='bold')
        plt.xlabel('Pregunta')
        plt.ylabel('Cantidad de respuestas')
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.legend(title='Respuesta')
        plt.tight_layout()
        ruta_guardado = os.path.join(self.generar_direccion(), 'grafico_tecnologias_si_no.png')
        plt.savefig(ruta_guardado, format='png', dpi=300, bbox_inches='tight')

        plt.show()
        plt.close()

    def grafico_participacion_innovacion_ciiu_genero(self):
        """
        Genera gráfico de barras apiladas de participación en experiencias innovadoras por CIIU y género
        """
        df_group = self.data.participacion_innovacion_ciiu_genero()
        
        # Graficar barras apiladas
        fig, ax = plt.subplots(figsize=(16, 10))
        df_group.plot(kind='bar', stacked=True, ax=ax, colormap='Paired')
        
        ax.set_title("Participación en experiencias innovadoras por CIIU y Género", fontsize=16)
        ax.set_xlabel("CIIU (actividades)", fontsize=12)
        ax.set_ylabel("% de participantes", fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.legend(title="Género")
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Ajuste de márgenes
        plt.tight_layout()
        
        ruta_guardado = os.path.join(self.generar_direccion(), 'grafico_participacion_innovacion_ciiu_genero.png')
        plt.savefig(ruta_guardado, format='png', dpi=300, bbox_inches='tight')
        
        plt.show()
        plt.close()

    def dashboard_competencia_digital_ciiu(self):
        """
        Genera dashboard con múltiples gráficos de competencia digital por CIIU
        """
        import numpy as np
        
        df, preguntas_originales, mapa_preguntas = self.data.dashboard_competencia_digital_ciiu()
        
        # Crear subplots
        filas = int(np.ceil(len(preguntas_originales)/2))
        fig, axes = plt.subplots(filas, 2, figsize=(18, filas*5))
        axes = axes.flatten()
        
        # Colores personalizados
        colores = {'Si': '#FF0000', 'No': '#89CFF0'}
        
        for i, col in enumerate(preguntas_originales):
            # Normalizar texto de respuestas
            df[col] = df[col].astype(str).str.strip().str.lower().replace({
                'sí': 'Si', 'si': 'Si', 'no': 'No', 'nan': None
            })
            
            # Agrupar y calcular porcentaje
            df_group = df.groupby(['CIIU', col], observed=True).size().unstack(fill_value=0)
            df_percent = df_group.div(df_group.sum(axis=1), axis=0) * 100
            
            # Reordenar columnas si faltan
            for respuesta in ['Si', 'No']:
                if respuesta not in df_percent.columns:
                    df_percent[respuesta] = 0
            df_percent = df_percent[['Si', 'No']]
            
            # Crear gráfico horizontal
            ax = axes[i]
            df_percent.plot(kind='barh', ax=ax, color=[colores['Si'], colores['No']], edgecolor='black')
            
            # Etiquetas y título
            ax.set_title(mapa_preguntas[col], fontsize=13, pad=10)
            ax.set_xlabel("% de respuestas", fontsize=11)
            ax.set_ylabel("CIIU", fontsize=11)
            
            # Añadir valores sobre las barras
            for container in ax.containers:
                ax.bar_label(container, fmt='%.1f%%', label_type='edge', fontsize=9)
            
            # Leyenda afuera
            ax.legend(title="Respuesta", bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(axis='x', linestyle='--', alpha=0.7)
        
        plt.tight_layout(pad=3.0)
        plt.suptitle("Conocimientos y oportunidades digitales por sector (CIIU)", fontsize=16, y=1.02)
        
        ruta_guardado = os.path.join(self.generar_direccion(), 'dashboard_competencia_digital_ciiu.png')
        plt.savefig(ruta_guardado, format='png', dpi=300, bbox_inches='tight')
        
        plt.show()
        plt.close()
            
