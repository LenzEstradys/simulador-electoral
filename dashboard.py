import streamlit as st
import pandas as pd
import io
import plotly.graph_objects as go

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Simulador Electoral 2da Vuelta",
    page_icon="🗳️",
    layout="wide"
)

# --- Carga y Preparación de Datos ---
# Datos iniciales del archivo del usuario
csv_data = """Partido,Votos 1ra vuelta
UNIDAD NAL.,1039426
MAS,166917
F P,86154
A P B,347574
SUMATE,76349
A D N,439388
A P,0
Blancos,0
Nulo,1325596
"""
df_transfer = pd.read_csv(io.StringIO(csv_data))

# Votos base de los finalistas
votos_base_pdc = 1717432
votos_base_libre = 1430176

# Porcentajes iniciales definidos por el usuario
initial_percentages = {
    'UNIDAD NAL.': 50,
    'MAS': 50,
    'F P': 50,
    'A P B': 50,
    'SUMATE': 50,
    'A D N': 40,
    'A P': 50,
    'Blancos': 50,
    'Nulo': 70
}

# --- Barra Lateral con Controles Interactivos ---
st.sidebar.header("⚙️ Ajustar Transferencia de Votos")
st.sidebar.write("Mueva los sliders para simular diferentes escenarios de transferencia de votos hacia PDC.")

transfer_percentages = {}
for index, row in df_transfer.iterrows():
    partido = row['Partido']
    votos = row['Votos 1ra vuelta']
    if votos > 0: # Solo mostrar sliders para partidos con votos
        # Usamos el diccionario de valores iniciales para el 'value' del slider
        pct = st.sidebar.slider(
            f"% de '{partido}' a PDC",
            min_value=0,
            max_value=100,
            value=initial_percentages.get(partido, 50), # Usa el valor inicial, o 50 si no está
            step=1
        )
        transfer_percentages[partido] = pct / 100.0

# --- Lógica de Cálculo ---
votos_transferidos_a_pdc = 0
votos_transferidos_a_libre = 0

# Crear una lista para el desglose detallado
desglose_data = []

for partido, pct_a_pdc in transfer_percentages.items():
    votos_origen = df_transfer[df_transfer['Partido'] == partido]['Votos 1ra vuelta'].iloc[0]
    
    votos_a_pdc = votos_origen * pct_a_pdc
    votos_a_libre = votos_origen * (1 - pct_a_pdc)
    
    votos_transferidos_a_pdc += votos_a_pdc
    votos_transferidos_a_libre += votos_a_libre
    
    desglose_data.append({
        'Partido Origen': partido,
        'Votos Aportados a PDC': int(votos_a_pdc),
        'Votos Aportados a LIBRE': int(votos_a_libre)
    })

# Totales finales
total_pdc = votos_base_pdc + votos_transferidos_a_pdc
total_libre = votos_base_libre + votos_transferidos_a_libre

# --- Panel Principal: Visualización de Resultados ---
st.title("🗳️ Simulador de Resultados Electorales - 2da Vuelta")
st.markdown("---")

# KPIs principales en columnas
col1, col2, col3 = st.columns(3)
ganador = "PDC" if total_pdc > total_libre else "LIBRE"
diferencia = abs(total_pdc - total_libre)

with col1:
    st.metric(label="Votos Proyectados PDC", value=f"{int(total_pdc):,}")

with col2:
    st.metric(label="Votos Proyectados LIBRE", value=f"{int(total_libre):,}")

with col3:
    st.metric(label="Diferencia de Votos", value=f"{int(diferencia):,}", delta=ganador)


st.markdown("---")

# Gráficos en columnas
col_chart1, col_chart2 = st.columns([2, 1])

with col_chart1:
    # Gráfico de Barras
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name='PDC', x=['PDC'], y=[total_pdc], marker_color='#1f77b4'))
    fig_bar.add_trace(go.Bar(name='LIBRE', x=['LIBRE'], y=[total_libre], marker_color='#ff7f0e'))
    fig_bar.update_layout(title_text='<b>Resultado Final Proyectado</b>', yaxis_title='Cantidad de Votos')
    st.plotly_chart(fig_bar, use_container_width=True)

with col_chart2:
    # Gráfico de Anillo
    labels = ['PDC', 'LIBRE']
    values = [total_pdc, total_libre]
    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, marker_colors=['#1f77b4', '#ff7f0e'])])
    fig_pie.update_layout(title_text='<b>Distribución del Voto (%)</b>', showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# Tabla de Desglose
st.header("Detalle de Transferencia de Votos")
df_desglose = pd.DataFrame(desglose_data)
st.dataframe(df_desglose.style.format({
    'Votos Aportados a PDC': '{:,.0f}',
    'Votos Aportados a LIBRE': '{:,.0f}'
}))