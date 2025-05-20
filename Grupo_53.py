import streamlit as st
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np

# Configuración inicial
st.set_page_config(page_title="Análisis de Supermercado - Myanmar", layout="wide", initial_sidebar_state='expanded')
sns.set_style("whitegrid")
custom_palette = ["#2b4576", "#4a7fb3", "#5a9bd5", "#78b8f0", "#adc6e5", "#d4e4f7"]
sns.set_palette(custom_palette)

st.title("🛍️ Análisis de Datos de una Cadena de Supermercados en Myanmar")

# Estilo de las métricas
st.markdown("""
<style>
[data-testid="block-container"] {    
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}
[data-testid="stVerticalBlock"] {    
    padding-left: 0rem;
    padding-right: 0rem;
}
[data-testid="stMetric"] {
    background-color: #adc6e5;
    text-align: center;
    padding: 15px 0;
}
[data-testid="stMetricLabel"] {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
""", unsafe_allow_html=True)

# Cargar datos con caché para mejorar rendimiento
@st.cache_data
def cargar_datos():
    df = pd.read_csv("data.csv")
    return df
# Cargar datos
df = cargar_datos()

df['Date'] = pd.to_datetime(df['Date'])

# Diccionario de traducción (inglés -> español)
traducciones = {
    "Health and beauty": "Salud y belleza",
    "Electronic accessories": "Accesorios electrónicos",
    "Home and lifestyle": "Hogar y estilo de vida",
    "Sports and travel": "Deportes y viajes",
    "Food and beverages": "Comida y bebidas",
    "Fashion accessories": "Accesorios de moda"
}

# Aplicar la traducción a la columna 'Product line'
df['Product line'] = df['Product line'].map(traducciones) 

# Diccionario de traducción (inglés -> español)
traducciones = {
    "Member": "Miembro",
    "Normal": "Normal"
}

# Aplicar la traducción a la columna 'Customer type'
df['Customer type'] = df['Customer type'].map(traducciones)

# Diccionario de traducción (inglés -> español)
traducciones = {
    "Ewallet": "Billetera electrónica",
    "Cash": "Efectivo",
    "Credit card": "Tarjeta de crédito"
}

# Aplicar la traducción a la columna 'Payment'
df['Payment'] = df['Payment'].map(traducciones)

# Diccionario de traducción (inglés -> español)
traducciones = {
    "Female": "Femenino",
    "Male": "Masculino"
}
# Aplicar la traducción a la columna 'Gender'
df['Gender'] = df['Gender'].map(traducciones) 

# FILTROS

st.sidebar.header("Filtros")
fecha_inicio = st.sidebar.date_input("Selecciona una fecha de inicio:", df["Date"].min())
fecha_fin = st.sidebar.date_input("Selecciona una fecha final:", df["Date"].max())

selected_branch = st.sidebar.multiselect("Selecciona sucursal:", df["Branch"].unique(), default=df["Branch"].unique())
selected_product_lines = st.sidebar.multiselect("Selecciona línea de producto:", df["Product line"].unique(), default=df["Product line"].unique())

# Filtrar DataFrame según filtros aplicados
df_filtered = df[
    (df['Date'] >= pd.to_datetime(fecha_inicio)) &
    (df['Date'] <= pd.to_datetime(fecha_fin)) &
    (df["Branch"].isin(selected_branch)) &
    (df["Product line"].isin(selected_product_lines))
]
st.write(f"Periodo evaluado: Desde el {fecha_inicio} hasta el {fecha_fin}.")

# SECCIÓN DE MÉTRICAS (Primera fila)
# Generación de métricas
df['Total'] = pd.to_numeric(df['Total'], errors='coerce')
df['gross income'] = pd.to_numeric(df['gross income'], errors='coerce')
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')

# Cálculo de métricas dinámicas con df_filtered
ventas_totales = df_filtered['Total'].sum()
total_unidades = df_filtered['Quantity'].sum()
ganancia_bruta = df_filtered['gross income'].sum()
calificacion_promedio = df_filtered['Rating'].mean()

# Mostrar métricas en columnas
st.subheader("Resumen de Métricas")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Ventas Totales", f"${ventas_totales:,.2f}")
col2.metric("Unidades Vendidas", f"{total_unidades:,}")
col3.metric("Ganancia Bruta", f"${ganancia_bruta:,.2f}")
col4.metric("Calificación Promedio", f"{calificacion_promedio:.2f} / 10")

# SECCIÓN DE GRÁFICOS
# Crear columnas (Segunda fila)
col1, col2 = st.columns(2)
with col1:    
    st.subheader("Evolución de las Ventas Totales")
    ventas_diarias = df_filtered.groupby("Date")["Total"].sum().reset_index()
    fig1, ax1 = plt.subplots()
    sns.lineplot(x="Date", y="Total", data=ventas_diarias, ax=ax1)
    fig1.patch.set_facecolor('none') # Fondo transparente de la figura
    ax1.set_facecolor('none')  # Fondo transparente del área del gráfico
    ax1.set_ylabel('Total $')
    ax1.set_xlabel('Fecha')
    ax1.tick_params("x", rotation=90)
    st.pyplot(fig1)
    st.write("*Muestra la variación de las ventas totales durante el período seleccionado, lo que permite identificar tendencias estacionales y detectar peaks o caídas en la actividad comercial.*")

with col2:
    st.subheader("Ingresos por Línea de Producto y Género")
    ingresos_linea_genero = df_filtered.groupby(["Product line", "Gender"])["Total"].sum().reset_index()
    # Crear gráfico de barras
    fig2 = px.bar(
        ingresos_linea_genero,
        x="Product line",
        y="Total",
        color="Gender",
        barmode="group",  # Agrupar barras por categoría
        labels={"Gender": "Género", "Product line": "Línea de Producto"},
        color_discrete_sequence=custom_palette
    )
    # Personalizar los ejes
    fig2.update_layout(
        xaxis_title="Línea de Producto",
        yaxis_title="Ingresos Totales"
    )
    # Mostrar en Streamlit
    st.plotly_chart(fig2)
    st.write("*Visualiza la distribución de los ingresos por línea de producto, diferenciando por género del cliente, lo que facilita la comparación del aporte de cada categoría según el perfil del consumidor.*")

# Crear columnas (Tercera fila)
col3, col4 = st.columns(2)
with col3:
    st.subheader("Distribución de las Calificaciones de Clientes")
    fig3, ax3 = plt.subplots()
    sns.histplot(df_filtered["Rating"], bins=10, kde=True, ax=ax3)
    ax3.set_ylabel("Frecuencia")
    ax3.set_xlabel("Calificaciones de Clientes")
    fig3.patch.set_facecolor('none') # Fondo transparente de la figura
    ax3.set_facecolor('none')  # Fondo transparente del área del gráfico
    st.pyplot(fig3)
    st.write("*Representa la distribución de las calificaciones de satisfacción de los clientes, permitiendo observar la tendencia central, la dispersión y la concentración de las evaluaciones sobre el servicio recibido.*")

with col4:
    st.subheader("Comparación del Gasto por Tipo de Cliente")
    fig4, ax4 = plt.subplots()
    sns.boxplot(x="Customer type", y="Total", hue="Customer type", data=df_filtered, ax=ax4)
    ax4.set_ylabel("Gasto Total")
    ax4.set_xlabel("Tipo de Cliente")
    fig4.patch.set_facecolor('none') # Fondo transparente de la figura
    ax4.set_facecolor('none')  # Fondo transparente del área del gráfico
    st.pyplot(fig4)
    st.write("*Compara el gasto total entre tipos de cliente (miembros y normales), mostrando la mediana, la distribución de los datos y posibles valores atípicos, útil para evaluar diferencias en comportamiento de compra.*")

# Crear columnas (Cuarta fila)
col5, col6 = st.columns(2)
with col5:
    st.subheader("Relación entre Costo y Ganancia Bruta según Línea de Producto")
    fig5 = px.scatter(
        df_filtered,
        x="cogs",
        y="gross income",
        color="Product line",
        labels={"Product line": "Línea de Producto", "cogs": "Costo", "gross income": "Ganancia bruta"},
        color_discrete_sequence=custom_palette
        )
    # Personalizar los ejes
    fig5.update_layout(
        xaxis_title="Costo",
        yaxis_title="Ganancia Bruta"
    )
    # Mostrar en Streamlit
    st.plotly_chart(fig5)
    st.write("*Visualiza la relación entre el costo y la ganancia bruta según la línea de producto, permitiendo identificar patrones lineales y analizar la eficiencia en la generación de utilidades.*")

with col6:
    st.subheader("Frecuencia de Métodos de Pago")
    fig6 = px.histogram(
        df_filtered, 
        x="Payment", 
        color="Payment",
        labels={"Payment": "Método de Pago"},
        color_discrete_sequence=custom_palette
        )
    # Personalizar los ejes
    fig6.update_layout(
        xaxis_title="Métodos de Pago",
        yaxis_title="Frecuencia",
        showlegend=False
    )
    # Mostrar en Streamlit
    st.plotly_chart(fig6)
    st.write("*Muestra la frecuencia de uso de los distintos métodos de pago, lo que permite identificar cuál es el más utilizado y detectar posibles preferencias entre los clientes.*")

# Quinta fila
st.subheader("Ingreso Bruto por Sucursal y Línea de Producto")
sunburst_df = df_filtered.groupby(['Branch', 'Product line'])['gross income'].sum().reset_index()
fig8 = px.sunburst(sunburst_df, path=['Branch', 'Product line'], values='gross income',  labels={"Branch": "Sucursal", "gross income": "Ingreso bruto", "Product line": "Línea de Producto"}, color_discrete_sequence=custom_palette)
# Ajustar tamaño de la figura
fig8.update_layout(width=800, height=800)  
# Mostrar en Streamlit
st.plotly_chart(fig8)
st.write("*Presenta el ingreso bruto generado por cada línea de producto en cada sucursal, facilitando la comparación entre tiendas y el análisis del aporte individual de cada categoría al total de ingresos.*")


# Pie de página
st.markdown("---")
st.caption("Análisis de Datos de una Cadena de Supermercados | Datos: data.csv | Grupo:53")

