import streamlit as st
import pandas as pd
import io
import plotly.graph_objects as go

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Simulador Electoral Avanzado",
    page_icon="🗳️",
    layout="wide"
)

# --- Colores de Partidos ---
COLOR_PDC = '#FF7F0E' # Naranja
COLOR_LIBRE = '#D62728' # Rojo
COLOR_NULO = 'grey'
COLOR_BLANCO = 'lightgrey'


# --- Carga y Preparación de Datos ---
csv_data = """Partido,Votos 1ra vuelta
UNIDAD NAL.,1039426
MAS,166917
F P,86154
A P B,347574
SUMATE,76349
A D N,439388
Nulo,1325596
"""
df_transfer = pd.read_csv(io.StringIO(csv_data))

# Votos base de los finalistas
votos_base_pdc = 1717432
votos_base_libre = 1430176
votos_base_nulos = 0
votos_base_blancos = 0

# --- Barra Lateral con Controles Interactivos Avanzados ---
st.sidebar.header("⚙️ Simulación de Transferencia")
st.sidebar.write("Ajuste la distribución de votos para cada partido de origen.")

transfer_results = {}

for index, row in df_transfer.iterrows():
    partido = row['Partido']
    votos_origen = row['Votos 1ra vuelta']
    
    with st.sidebar.expander(f"**{partido}** ({votos_origen:,} votos)"):
        # Sliders inteligentes que ajustan su máximo dinámicamente
        pct_pdc = st.slider(f"% a PDC 🟠", 0, 100, 40, key=f"{partido}_pdc")
        
        max_libre = 100 - pct_pdc
        pct_libre = st.slider(f"% a LIBRE 🔴", 0, max_libre, 30, key=f"{partido}_libre")
        
        max_blanco = 100 - pct_pdc - pct_libre
        pct_blanco = st.slider(f"% a Blanco", 0, max_blanco, 10, key=f"{partido}_blanco")
        
        # El porcentaje a Nulo se calcula automáticamente
        pct_nulo = 100 - pct_pdc - pct_libre - pct_blanco
        st.write(f"**% a Nulo (auto): {pct_nulo}%**")
        
        transfer_results[partido] = {
            'pdc': pct_pdc / 100.0,
            'libre': pct_libre / 100.0,
            'nulo': pct_nulo / 100.0,
            'blanco': pct_blanco / 100.0
        }

# --- Lógica de Cálculo ---
# (La lógica no cambia, solo las variables que alimentan el cálculo)
votos_transferidos_a_pdc = 0
votos_transferidos_a_libre = 0
votos_transferidos_a_nulos = 0
votos_transferidos_a_blancos = 0
desglose_data = []

for partido, percentages in transfer_results.items():
    votos_origen = df_transfer.loc[df_transfer['Partido'] == partido, 'Votos 1ra vuelta'].iloc[0]
    
    votos_a_pdc = votos_origen * percentages['pdc']
    votos_a_libre = votos_origen * percentages['libre']
    votos_a_nulo = votos_origen * percentages['nulo']
    votos_a_blanco = votos_origen * percentages['blanco']
    
    votos_transferidos_a_pdc += votos_a_pdc
    votos_transferidos_a_libre += votos_a_libre
    votos_transferidos_a_nulos += votos_a_nulo
    votos_transferidos_a_blancos += votos_a_blanco
    
    desglose_data.append({
        'Partido Origen': partido,
        'Votos a PDC 🟠': int(votos_a_pdc),
        'Votos a LIBRE 🔴': int(votos_a_libre),
        'Votos a Nulo': int(votos_a_nulo),
        'Votos a Blanco': int(votos_a_blanco)
    })

# Totales finales
total_pdc = votos_base_pdc + votos_transferidos_a_pdc
total_libre = votos_base_libre + votos_transferidos_a_libre
total_nulos = votos_base_nulos + votos_transferidos_a_nulos
total_blancos = votos_base_blancos + votos_transferidos_a_blancos

votos_validos = total_pdc + total_libre

# --- Panel Principal: Visualización de Resultados ---
st.title("🗳️ Simulador Electoral Avanzado - 2da Vuelta")
st.markdown("---")

st.header("Resultados sobre Votos Válidos")
col1, col2, col3 = st.columns(3)

if votos_validos > 0:
    pct_final_pdc = (total_pdc / votos_validos) * 100
    pct_final_libre = (total_libre / votos_validos) * 100
    ganador = "PDC 🟠" if total_pdc > total_libre else "LIBRE 🔴"
    diferencia = abs(total_pdc - total_libre)
else:
    pct_final_pdc, pct_final_libre, ganador, diferencia = 0, 0, "Indefinido", 0

with col1:
    st.metric(label="Votos Proyectados PDC 🟠", value=f"{int(total_pdc):,}", help=f"{pct_final_pdc:.2f}% de votos válidos")
with col2:
    st.metric(label="Votos Proyectados LIBRE 🔴", value=f"{int(total_libre):,}", help=f"{pct_final_libre:.2f}% de votos válidos")
with col3:
    st.metric(label="Diferencia de Votos", value=f"{int(diferencia):,}", delta=ganador)

# Gráfico de Resultados Válidos con Colores
fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(name='PDC', x=['PDC'], y=[total_pdc], text=f"{pct_final_pdc:.1f}%", textposition='auto', marker_color=COLOR_PDC))
fig_bar.add_trace(go.Bar(name='LIBRE', x=['LIBRE'], y=[total_libre], text=f"{pct_final_libre:.1f}%", textposition='auto', marker_color=COLOR_LIBRE))
fig_bar.update_layout(title_text='<b>Resultado Final sobre Votos Válidos</b>', yaxis_title='Cantidad de Votos', showlegend=False)
st.plotly_chart(fig_bar, use_container_width=True)


st.markdown("---")
st.header("Distribución del Voto Total Emitido")

kpi1, kpi2 = st.columns(2)
kpi1.metric(label="Votos Nulos Proyectados", value=f"{int(total_nulos):,}")
kpi2.metric(label="Votos Blancos Proyectados", value=f"{int(total_blancos):,}")

# Gráfico de Anillo del Voto Total con Colores
labels = ['PDC 🟠', 'LIBRE 🔴', 'Nulos', 'Blancos']
values = [total_pdc, total_libre, total_nulos, total_blancos]
fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4,
                                 marker_colors=[COLOR_PDC, COLOR_LIBRE, COLOR_NULO, COLOR_BLANCO])])
fig_pie.update_layout(title_text='<b>Desglose del Voto Total Emitido en la Simulación</b>')
st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")
st.header("Detalle de Transferencia de Votos por Origen")
df_desglose = pd.DataFrame(desglose_data)
st.dataframe(df_desglose.style.format(formatter={
    'Votos a PDC 🟠': '{:,.0f}',
    'Votos a LIBRE 🔴': '{:,.0f}',
    'Votos a Nulo': '{:,.0f}',
    'Votos a Blanco': '{:,.0f}'
}))