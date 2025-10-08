import pandas as pd
import matplotlib.pyplot as plt
import numpy

from src.cleaning import retornar_dataframe


class Data:
    def __init__(self):
        self.df = retornar_dataframe()

    def show_dataframe(self):
        print(self.df)

    def provincia_puntuacion(self):
        self.df['Puntuacion'] = pd.to_numeric(self.df['Puntuacion'], errors='coerce')
        self.df['Puntuacion'] = self.df['Puntuacion'].fillna(0)

        df_promedio_provincia = self.df.groupby('Provincia')['Puntuacion'].mean().reset_index()
        print(df_promedio_provincia)
        return df_promedio_provincia

    def genero_puntuacion_edad(self):
        df_edad_genero = self.df.copy()
        df_edad_genero = df_edad_genero.dropna(subset=['Edad','Genero'])
        df_edad_genero['Edad'] = pd.to_numeric(df_edad_genero['Edad'],errors='coerce')
        df_edad_genero['Puntuacion'] = pd.to_numeric(df_edad_genero['Puntuacion'], errors='coerce')

        df_edad_genero['Puntuacion'] = df_edad_genero['Puntuacion'].fillna(0)

        df_edad_genero['RangoEdad'] = pd.cut(df_edad_genero['Edad'], bins=[0,12,18,30,60,100],labels=['0-12','12-18','18-30','30-60','+60'],right=False)
        
        df_genero_puntuacion = (df_edad_genero.groupby(['Genero','RangoEdad'])['Puntuacion'].mean().reset_index())

        df_genero_puntuacion['Puntuacion'] = df_genero_puntuacion['Puntuacion'].fillna(0).round(2)
        print(df_genero_puntuacion)
        return df_genero_puntuacion

    def empresa_competencia(self):
        df_copia = self.df.copy()
        df_empresa_competencia = df_copia.rename(columns={'Registre su tipo de empresa organizacion ciudadano':'Empresa',
                                                          'Conoce su nivel de competencia digital e identifica claramente sus carencias con respecto a los requisitos de su entorno laboral': 'Entorno'})
        
        df_empresa_competencia['Si'] = df_empresa_competencia['Entorno'].apply(lambda x:1 if x =='Si' else 0)
        df_empresa_competencia['No'] = df_empresa_competencia['Entorno'].apply(lambda x:1 if x == 'No' else 0)

        df_si = df_empresa_competencia.groupby('Empresa')['Si'].sum().reset_index()
        df_no = df_empresa_competencia.groupby('Empresa')['No'].sum().reset_index()

        df_resultado = pd.merge(df_si,df_no,on='Empresa')

        print(df_resultado)
        return df_resultado

    def tecnologias_si_no(self):
        columnas_tecnologicas = [
            'Conoce las oportunidades que el IOT (Internet de las cosas) puede aportar en su trabajo y empresa',
            'Conoce las oportunidades que el IA (Inteligencia artificial) puede aportar en su trabajo y empresa',
            'Conoce o ha utilizado servicios de alojamiento de archivos en la nube',
            'Ha participado en consultas ciudadanas o encuestas a traves de internet (online) a propuestas de organizaciones publicas o sociales',
            'Participa en experiencias innovadoras relacionadas con el uso de nuevas tecnologias'
        ]
        
        resultados = []
        
        for columna in columnas_tecnologicas:
            if columna in self.df.columns:
                conteo = self.df[columna].value_counts()
                si_count = conteo.get('Si', 0)
                no_count = conteo.get('No', 0)
                
                resultados.append({
                    'Pregunta': columna,
                    'Si': si_count,
                    'No': no_count
                })
        
        df_resultado = pd.DataFrame(resultados)
        print(df_resultado)
        return df_resultado

    def participacion_innovacion_ciiu_genero(self):
        """
        Procesa datos de participación en experiencias innovadoras por CIIU y género
        """
        # Variable de interés
        col = "Participa en experiencias innovadoras relacionadas con el uso de nuevas tecnologias"
        
        # Convertir 'Si' a 1 y 'No' a 0
        df_copy = self.df.copy()
        df_copy[col] = df_copy[col].map({'Si': 1, 'No': 0})
        
        # Diccionario con códigos cortos para CIIU
        ciiu_map = {
            'Actividades de los hogares como empleadores, actividades no diferenciadas de los hogares': 'Ac0',
            'Actividades de alojamiento y de servicio de comida.': 'Ac1',
            'Actividades de atencion de la salud humana y de asistencia social.': 'Ac2',
            'Como productores de bienes y servicios para uso propio.': 'Ac3',
            'Actividades de organizaciones y organos extraterritoriales.': 'Ac4',
            'Actividades de servicios administrativos y de apoyo.': 'Ac5',
            'Actividades financieras y de seguros.': 'Ac6',
            'Actividades inmobiliarias.': 'Ac7',
            'Actividades profesionales, cientificas y tecnicas.': 'Ac8',
            'Agricultura, ganadería y pesca.': 'Ac9',
            'Artes, entretenimiento y recreacion.': 'Ac10',
            'Comercio al por mayor y al por menor, reparacion de vehiculos automotores y motocicletas.': 'Ac11',
            'Construccion.': 'Ac12',
            'Ensenanza.': 'Ac13',
            'Industrias manufactureras.': 'Ac14',
            'Informacion y comunicacion.': 'Ac15',
            'Otras actividades de servicios.': 'Ac16',
            'Suministro de electricidad, gas, vapor y aire acondicionado.': 'Ac17',
            'Transporte y almacenamiento.': 'Ac18'
        }
        
        # Reemplazar nombres largos por códigos cortos
        df_copy['CIIU'] = df_copy['CIIU'].map(ciiu_map)
        
        # Filtrar solo Femenino y Masculino
        df_copy = df_copy[df_copy['Genero'].isin(['Femenino', 'Masculino'])]
        
        # Definir el orden correcto de CIIU
        orden_ciiu = ['Ac1','Ac2','Ac3','Ac4','Ac5','Ac6','Ac7','Ac8','Ac9','Ac10',
                      'Ac11','Ac12','Ac13','Ac14','Ac15','Ac16','Ac17','Ac18']
        
        # Convertir CIIU en categoría ordenada
        df_copy['CIIU'] = pd.Categorical(df_copy['CIIU'], categories=orden_ciiu, ordered=True)
        
        # Agrupar por CIIU y Género
        df_group = df_copy.groupby(['CIIU', 'Genero'], observed=True)[col].mean().unstack(fill_value=0) * 100
        
        print("Participación en experiencias innovadoras por CIIU y Género (%):")
        print(df_group)
        return df_group

    def dashboard_competencia_digital_ciiu(self):
        """
        Procesa datos para dashboard de competencia digital por CIIU
        """
        # Lista de preguntas originales
        preguntas_originales = [
            "Tiene conocimientos de computacion y navegacion en internet",
            "Conoce las oportunidades que el IOT (Internet de las cosas) puede aportar en su trabajo y empresa",
            "Conoce las oportunidades que el IA (Inteligencia artificial) puede aportar en su trabajo y empresa",
            "Conoce como utilizar herramientas de busqueda avanzada en Internet para mejorar los resultados en funcion de sus necesidades",
            "Identifica parametros que deben cumplir las paginas web y la informacion online para considerar su confiabilidad y calidad",
            "Clasifica la informacion mediante archivos y carpetas para facilitar su localizacion posterior",
            "Conoce o ha utilizado servicios de alojamiento de archivos en la nube",
            "Ha participado en consultas ciudadanas o encuestas a traves de internet (online) a propuestas de organizaciones publicas o sociales",
            "Usted sabe como generar un perfil publico, personal o profesional en las Redes Sociales, controlando los detalles de la imagen que quiere transmitir",
            "Es capaz de utilizar los diferentes medios digitales para exponer de manera creativa esquemas graficos, mapas conceptuales, infografias",
            "Sabe editar y modificar con herramientas digitales, el formato de diferentes tipos de archivo textos, fotografias, videos",
            "Conoce los fundamentos de los procesos digitales y de la creacion de software. Entiendo los principios de la programacion",
            "Conoce y actua con prudencia cuando recibe mensajes cuyo remitente, contenido o archivo adjunto sea desconocido (SPAM)",
            "Se interesa en conocer las politicas de privacidad de las plataformas que utiliza en Internet, asi como el tratamiento que hacen de sus datos personales",
            "Se mantiene informado y actualizado sobre habitos saludables y seguros en el uso de la tecnologia, y los fomenta y los difunde",
            "Es capaz de evaluar y elegir de manera adecuada un dispositivo, software, aplicacion o servicio para realizar sus tareas",
            "Participa en experiencias innovadoras relacionadas con el uso de nuevas tecnologias",
            "Conoce su nivel de competencia digital e identifica claramente sus carencias con respecto a los requisitos de su entorno laboral"
        ]
        
        # Crear nombres cortos para la gráfica
        preguntas_cortas = [f"Pregunta {i+1}" for i in range(len(preguntas_originales))]
        mapa_preguntas = dict(zip(preguntas_originales, preguntas_cortas))
        
        # Filtrar solo Femenino y Masculino
        df_copy = self.df[self.df['Genero'].isin(['Femenino', 'Masculino'])].copy()
        
        # Diccionario con códigos cortos para CIIU
        ciiu_map = {
            'Actividades de alojamiento y de servicio de comida.': 'A1',
            'Actividades de atencion de la salud humana y de asistencia social.': 'A2',
            'Actividades profesionales, cientificas y tecnicas.': 'A3',
            'Agricultura, ganadería y pesca.': 'A4',
            'Artes, entretenimiento y recreacion.': 'A5',
            'Comercio al por mayor y al por menor, reparacion de vehiculos automotores y motocicletas.': 'A6',
            'Construccion.': 'A7',
            'Ensenanza.': 'A8',
            'Industrias manufactureras.': 'A9',
            'Informacion y comunicacion.': 'A10',
            'Otras actividades de servicios.': 'A11',
            'Transporte y almacenamiento.': 'A12'
        }
        
        df_copy['CIIU'] = df_copy['CIIU'].map(ciiu_map)
        df_copy = df_copy.dropna(subset=['CIIU'])
        
        # Asegurar orden de CIIU de A1 a A12
        orden_ciiu = [f"A{i}" for i in range(1, 13)]
        df_copy['CIIU'] = pd.Categorical(df_copy['CIIU'], categories=orden_ciiu, ordered=True)
        
        print("Dashboard de competencia digital por CIIU preparado")
        print(f"Total de preguntas: {len(preguntas_originales)}")
        print(f"Total de registros: {len(df_copy)}")
        
        return df_copy, preguntas_originales, mapa_preguntas
