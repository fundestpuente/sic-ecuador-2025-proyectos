#====================================================================#
#                             3. Graficos                            #
#====================================================================#
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


## Paleta de colores definida

COLORES = {
    "GOOD": "#2ecc71",    # verde
    "BAD": "#e74c3c",     # rojo
    "NEUTRAL": "#bda0e3", # lila
    "MALE": "#3498db",    # azul
    "FEMALE": "#ff6fae",  # rosa
    "SECONDARY": "#f39c12" # ámbar / secundario
}

def color_genero(valor):
    if not isinstance(valor, str):
        return COLORES["NEUTRAL"]
    v = valor.strip().lower()
    # admite variaciones comunes
    if v in {"hombre", "masculino", "m"}:
        return COLORES["MALE"]
    if v in {"mujer", "femenino", "f"}:
        return COLORES["FEMALE"]
    if v in {"no especifica", "otro", "no binario", "nb", "x"}:
        return COLORES["NEUTRAL"]
    return COLORES["NEUTRAL"]


def grafico_finanzas_personales(df_finanzas, cedula):
    # Filtrar usuario específico
    usuario = df_finanzas[df_finanzas['cedula'] == cedula].iloc[0]

    # Calcular totales
    total_ingresos = sum(usuario['ingresos'].values())
    total_gastos_prio = sum(usuario['gastos_prioritarios'].values())
    total_gastos_sec = sum(usuario['gastos_secundarios'].values())
    total_gastos = total_gastos_prio + total_gastos_sec
    ahorro_actual = total_ingresos * (usuario['porcentaje_ahorro'] / 100)

    # Crear figura con dos subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

    # Gráfico 1: Ingresos vs Gastos Prioritarios vs Gastos Secundarios (Pie)
    categorias = ['Ingresos', 'Gastos Prioritarios', 'Gastos Secundarios']
    valores = [total_ingresos, total_gastos_prio, total_gastos_sec]
    colores = [COLORES["GOOD"], COLORES["BAD"], COLORES["SECONDARY"]]
    
    ax1.pie(
        valores,
        labels=categorias,
        autopct='%1.1f%%',
        colors=colores,
        startangle=90
    )
    ax1.set_title(f'Distribución Financiera\n{usuario["nombre"]} {usuario["apellido"]}')

    # Gráfico 2: Desglose de todos los gastos (Barras)
    # Preparar datos para el gráfico de barras
    gastos_prioritarios = list(usuario['gastos_prioritarios'].items())
    gastos_secundarios = list(usuario['gastos_secundarios'].items())
    
    # Combinar todos los gastos
    todos_gastos = gastos_prioritarios + gastos_secundarios
    categorias_gastos = [gasto[0] for gasto in todos_gastos]
    valores_gastos = [gasto[1] for gasto in todos_gastos]
    
    # Definir colores para las barras
    colores_barras = [COLORES["BAD"]] * len(gastos_prioritarios) + [COLORES["SECONDARY"]] * len(gastos_secundarios)
    
    # Crear gráfico de barras
    bars = ax2.bar(categorias_gastos, valores_gastos, color=colores_barras, alpha=0.8)
    ax2.set_title('Desglose de Gastos Individuales')
    ax2.set_ylabel('Monto ($)')
    ax2.set_xlabel('Categorías de Gastos')
    
    # Rotar etiquetas del eje x para mejor legibilidad
    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
    
    # Añadir valores en las barras
    for bar in bars:
        height = bar.get_height()
        ax2.annotate(f'${height:,.0f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)

    # Ajustar layout
    plt.tight_layout()
    plt.show()

def grafico_comparativo_completo(df_finanzas, cedula):
    # Filtrar usuario específico
    usuario = df_finanzas[df_finanzas['cedula'] == cedula].iloc[0]

    # Calcular totales REALES
    total_ingresos = sum(usuario['ingresos'].values())
    total_gastos_prio = sum(usuario['gastos_prioritarios'].values())
    total_gastos_sec = sum(usuario['gastos_secundarios'].values())
    total_gastos = total_gastos_prio + total_gastos_sec

    # Calcular ahorro REAL
    ahorro_real = total_ingresos - total_gastos
    porcentaje_ahorro_real = (ahorro_real / total_ingresos) * 100 if total_ingresos > 0 else 0

    # Ahorro esperado
    porcentaje_ahorro_esperado = usuario['porcentaje_ahorro']
    ahorro_esperado = total_ingresos * (porcentaje_ahorro_esperado / 100)

    # Crear gráfico único
    fig, ax = plt.subplots(figsize=(10, 6))

    # Configurar posiciones de las barras
      # color condicional: verde si alcanza/supera la meta, rojo si no
    color_real = COLORES["GOOD"] if ahorro_real >= ahorro_esperado else COLORES["BAD"]

    categorias = ['Ahorro Real', 'Ahorro Esperado']
    montos = [ahorro_real, ahorro_esperado]
    porcentajes = [porcentaje_ahorro_real, porcentaje_ahorro_esperado]
    colores = [color_real, COLORES["NEUTRAL"]]
    # Crear barras más delgadas (reducido de 0.6 a 0.4)
    bars = ax.bar(categorias, montos, color=colores, alpha=0.8, width=0.4)

    # Personalización del gráfico
    ax.set_ylabel('Monto ($)')
    ax.set_title(f'Comparación: Ahorro Real vs Esperado\n{usuario["nombre"]} {usuario["apellido"]}')
    ax.grid(axis='y', alpha=0.3)

    # Aumentar el límite del eje Y en un 30% del valor más alto
    max_monto = max(montos)
    ax.set_ylim(0, max_monto * 1.3)

    # Añadir valores en las barras con formato combinado
    for bar, monto, porcentaje in zip(bars, montos, porcentajes):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (max_monto * 1.3 - max_monto) * 0.1,
                f'${monto:.2f} ({porcentaje:.1f}%)',
                ha='center', va='bottom', fontweight='bold', fontsize=11)

    # Línea de referencia para el ahorro esperado
    ax.axhline(y=ahorro_esperado, color=COLORES["BAD"], linestyle='--', alpha=0.8,
               label=f'Meta: ${ahorro_esperado:.2f} ({porcentaje_ahorro_esperado}%)')
    
    # Añadir diferencia
    diferencia_monto = ahorro_real - ahorro_esperado
    diferencia_porcentaje = porcentaje_ahorro_real - porcentaje_ahorro_esperado

    if abs(diferencia_monto) > 0:
        color_diferencia = '#27ae60' if diferencia_monto > 0 else '#e74c3c'
        simbolo_monto = '+' if diferencia_monto > 0 else ''
        simbolo_porcentaje = '+' if diferencia_porcentaje > 0 else ''

        ax.text(0.5, max_monto * 0.8,
               f'Diferencia: {simbolo_monto}${diferencia_monto:.2f}\n({simbolo_porcentaje}{diferencia_porcentaje:.1f}%)',
               ha='center', va='center', fontsize=10, fontweight='bold',
               bbox=dict(boxstyle="round,pad=0.3", facecolor=color_diferencia, alpha=0.3))

    ax.legend()
    plt.tight_layout()
    plt.show()


#===========================================================GRAFICAS GENERALES===============================================

#GRAFICO GENERAL 1

def proporcion_ingresos(df_tipo_ingreso):
    fig, ax = plt.subplots(figsize=(8, 8))

    # Gráfico de pastel que representa la cantidad de jovenes con ingresos con relacion a los que no reciben ingresos.
    conteo_ingresos = df_tipo_ingreso['tipo_ingreso'].value_counts().reindex([1,0],fill_value=0)
    ax.pie(conteo_ingresos.values, labels=['Con Ingresos', 'Sin Ingresos'],
       autopct='%1.1f%%', colors=[COLORES["GOOD"], COLORES["BAD"]], startangle=90)
    ax.set_title('Proporción de usuarios con/sin Ingresos')

    plt.tight_layout()
    plt.show()

#GRAFICA GENERAL 2

def dificultad_financiera_general(df_equilibrio):
    plt.figure(figsize=(12, 6))

    # Histograma que muestra el nivel de dificultad que presentan los usuarios con 
    # relacion al manejo de sus finanzas.
    
    ax = sns.histplot(data=df_equilibrio, x='dificultad_equilibrio', bins=5,
                  kde=True, color=COLORES["NEUTRAL"])
    plt.title('Distribución de Niveles de Dificultad Financiera - Todos los Usuarios')
    plt.xlabel('Nivel de Dificultad (1=Muy fácil, 5=Muy difícil)')
    plt.ylabel('Cantidad de Usuarios')

    # Añadir estadísticas
    media = df_equilibrio['dificultad_equilibrio'].mean()
    plt.axvline(media, color=COLORES["BAD"], linestyle='--',
            label=f'Dificultad Promedio: {media:.2f}')
    plt.legend()

    plt.tight_layout()
    plt.show()

#GRAFICO GENERAL 3

#Grafico de barras que representa el porcentaje de ahorro esperado por rango de edad de los 
#jovenes con relacion al que realmente estan obteniendo.

def edad_vs_ahorro(df_finanzas):
    # Calculo del ahorro real del joven
    df_finanzas['ahorro_real'] = df_finanzas.apply(
        lambda x: sum(x['ingresos'].values()) * (x['porcentaje_ahorro'] / 100), axis=1
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    # Creación del gráfico de barras
    df_finanzas['grupo_edad'] = pd.cut(
        df_finanzas['edad'],
        bins=[17, 20, 23, 26, 30],
        labels=['18-20', '21-23', '24-26', '27+']
    )

    datos_agrupados = df_finanzas.groupby('grupo_edad').agg({
        'porcentaje_ahorro': 'mean',
        'ahorro_real': 'mean'
    }).reset_index()

    x = range(len(datos_agrupados))
    ancho = 0.35

    # % Ahorro (AZUL = hombre)
    ax.bar(
        x, datos_agrupados['porcentaje_ahorro'], ancho,
        label='% Ahorro', alpha=0.7, color=COLORES["MALE"]
    )
    ax.set_xlabel('Grupo de Edad')
    ax.set_ylabel('Porcentaje de Ahorro (%)', color=COLORES["MALE"])
    ax.tick_params(axis='y', labelcolor=COLORES["MALE"])

    # Ahorro real ($) (VERDE = bien)
    ax_twin = ax.twinx()
    ax_twin.bar(
        [i + ancho for i in x], datos_agrupados['ahorro_real'], ancho,
        label='Ahorro Real ($)', color=COLORES["GOOD"], alpha=0.7
    )
    ax_twin.set_ylabel('Ahorro Real ($)', color=COLORES["GOOD"])
    ax_twin.tick_params(axis='y', labelcolor=COLORES["GOOD"])

    ax.set_xticks([i + ancho/2 for i in x])
    ax.set_xticklabels(datos_agrupados['grupo_edad'])
    ax.set_title('Ahorro por Grupo de Edad')

    # Leyenda combinada
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax_twin.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2)

    plt.tight_layout()
    plt.show()

    
#GRAFICO GENERAL 4
#Tipo: grafico de caja
# Relacion entre el genero y los gastos

def distribucion_gastos_por_genero(df_finanzas):
    
    #Grafico comparativo del gasto secundario promedio por género en toda la muestra
    
    #1.- Calcular gastos secundario por usuario
    gastos_por_genero=[]
    
    for i in range(len(df_finanzas)):
        fila=df_finanzas.iloc[i]
        genero= fila.get("genero","No especifica")
        if isinstance(fila.get("gastos_secundarios"), dict):
            total_gastos_sec = sum(fila["gastos_secundarios"].values())
        else:
            total_gastos_sec = 0.0

        gastos_por_genero.append({"genero": genero, "total_gastos_secundarios": total_gastos_sec})

    #2.- Crear DataFrame con resultados
    df_gastos = pd.DataFrame(gastos_por_genero)
    
    #3.- Agrupar por género y calcular promedio 
    resumen = df_gastos.groupby("genero", dropna=False)["total_gastos_secundarios"].mean().reset_index()
    resumen = resumen.sort_values("total_gastos_secundarios", ascending=False)

    #4.- Crear Grafico y establecer datos
    fig, ax = plt.subplots(figsize=(8, 5))
    colores = [color_genero(g) for g in resumen["genero"]]

    barras = ax.bar(resumen["genero"], resumen["total_gastos_secundarios"], color=colores, alpha=0.85)
    ax.set_title("Promedio de gastos secundarios por género", fontsize=13, fontweight="bold")
    ax.set_xlabel("Género")
    ax.set_ylabel("Gasto promedio (USD)")
    ax.grid(axis="y", alpha=0.3)

    # Etiquetas encima de cada barra
    for bar in barras:
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + 5,
                f"${bar.get_height():.2f}",
                ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.tight_layout()
    plt.show()
   
    
    
    
    





