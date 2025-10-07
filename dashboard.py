import streamlit as st
import pandas as pd
import io
import plotly.graph_objects as go

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Simulador Electoral Definitivo",
    page_icon="🏆",
    layout="wide"
)

# --- Colores de Partidos ---
COLOR_PDC = '#FF7F0E' # Naranja
COLOR_LIBRE = '#D62728' # Rojo
COLOR_PDC_LIGHT = '#FFDAB9' # Naranja claro (Durazno)
COLOR_LIBRE_LIGHT = '#F08080' # Rojo claro (Coral)


# --- Carga y Preparación de Datos ---
csv_data = """Partido,Votos 1ra vuelta
PDC,1717432
LIBRE,1430176
UNIDAD NAL.,1039426
MAS,166917
F P,86154
A P B,347574
SUMATE,76349
A D N,439388
Nulo,1325596
"""
df_transfer = pd.read_csv(io.StringIO(csv_data))

# LOS VOTOS BASE AHORA SON 0, TODO SE CALCULA POR TRANSFERENCIA
votos_base_pdc = 0
votos_base_libre = 0
votos_base_nulos = 0
votos_base_blancos = 0

# --- Barra Lateral con Controles Interactivos ---
st.sidebar.header("🏆 Simulación de Transferencia Total")
st.sidebar.write("Ajuste la distribución para TODOS los votantes de la 1ra vuelta.")

transfer_results = {}

for index, row in df_transfer.iterrows():
    partido = row['Partido']
    votos_origen = row['Votos 1ra vuelta']
    
    with st.sidebar.expander(f"**Votantes de '{partido}'** ({votos_origen:,})"):
        if partido == 'PDC':
            pct_pdc = st.slider(f"% Retención (se quedan en PDC 🟠)", 0, 100, 80, key=f"{partido}_pdc")
            max_libre = 100 - pct_pdc
            pct_libre = st.slider(f"% Fuga a LIBRE 🔴", 0, max_libre, 5, key=f"{partido}_libre")
            max_nulo = 100 - pct_pdc - pct_libre
            pct_nulo = st.slider(f"% Fuga a Nulo", 0, max_nulo, 10, key=f"{partido}_nulo")
            pct_blanco = 100 - pct_pdc - pct_libre - pct_nulo
            st.write(f"**% Fuga a Blanco (auto): {pct_blanco}%**")
        
        elif partido == 'LIBRE':
            pct_libre = st.slider(f"% Retención (se quedan en LIBRE 🔴)", 0, 100, 85, key=f"{partido}_libre")
            max_pdc = 100 - pct_libre
            pct_pdc = st.slider(f"% Fuga a PDC 🟠", 0, max_pdc, 5, key=f"{partido}_pdc")
            max_nulo = 100 - pct_libre - pct_pdc
            pct_nulo = st.slider(f"% Fuga a Nulo", 0, max_nulo, 5, key=f"{partido}_nulo")
            pct_blanco = 100 - pct_libre - pct_pdc - pct_nulo
            st.write(f"**% Fuga a Blanco (auto): {pct_blanco}%**")

        else:
            pct_pdc = st.slider(f"% a PDC 🟠", 0, 100, 40, key=f"{partido}_pdc")
            max_libre = 100 - pct_pdc
            pct_libre = st.slider(f"% a LIBRE 🔴", 0, max_libre, 30, key=f"{partido}_libre")
            max_nulo = 100 - pct_pdc - pct_libre
            pct_nulo = st.slider(f"% a Nulo", 0, max_nulo, 20, key=f"{partido}_nulo")
            pct_blanco = 100 - pct_pdc - pct_libre - pct_nulo
            st.write(f"**% a Blanco (auto): {pct_blanco}%**")
        
        transfer_results[partido] = {
            'pdc': pct_pdc / 100.0,
            'libre': pct_libre / 100.0,
            'nulo': pct_nulo / 100.0,
            'blanco': pct_blanco / 100.0
        }

# --- Lógica de Cálculo ---
total_pdc = votos_base_pdc
total_libre = votos_base_libre
total_nulos = votos_base_nulos
total_blancos = votos_base_blancos
desglose_data = []

for partido, percentages in transfer_results.items():
    votos_origen = df_transfer.loc[df_transfer['Partido'] == partido, 'Votos 1ra vuelta'].iloc[0]
    votos_a_pdc = votos_origen * percentages['pdc']
    votos_a_libre = votos_origen * percentages['libre']
    votos_a_nulo = votos_origen * percentages['nulo']
    votos_a_blanco = votos_origen * percentages['blanco']
    
    total_pdc += votos_a_pdc
    total_libre += votos_a_libre
    total_nulos += votos_a_nulo
    total_blancos += votos_a_blanco
    
    desglose_data.append({'Partido Origen': partido, 'Votos a PDC 🟠': int(votos_a_pdc), 'Votos a LIBRE 🔴': int(votos_a_libre), 'Votos a Nulo': int(votos_a_nulo), 'Votos a Blanco': int(votos_a_blanco)})

votos_validos = total_pdc + total_libre

# --- Panel Principal: Visualización de Resultados ---
st.title("🏆 Simulador Electoral Definitivo - 2da Vuelta")
st.markdown("---")

st.header("Resultados sobre Votos Válidos")
# Esta sección se mantiene para mostrar el % y la diferencia de la competencia directa
col1, col2, col3 = st.columns(3)

if votos_validos > 0:
    pct_final_pdc = (total_pdc / votos_validos) * 100
    pct_final_libre = (total_libre / votos_validos) * 100
    ganador_str = "PDC 🟠" if total_pdc > total_libre else "LIBRE 🔴"
    diferencia = abs(total_pdc - total_libre)
else:
    pct_final_pdc, pct_final_libre, ganador_str, diferencia = 0, 0, "Indefinido", 0

# Se mantienen los 3 KPIs de la competencia directa
with col1:
    st.metric(label="Votos Válidos PDC 🟠", value=f"{int(total_pdc):,}", help=f"{pct_final_pdc:.2f}% de votos válidos")
with col2:
    st.metric(label="Votos Válidos LIBRE 🔴", value=f"{int(total_libre):,}", help=f"{pct_final_libre:.2f}% de votos válidos")
with col3:
    st.metric(label="Diferencia de Votos", value=f"{int(diferencia):,}", delta=ganador_str)

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(name='PDC', x=['PDC'], y=[total_pdc], text=f"{pct_final_pdc:.1f}%", textposition='auto', marker_color=COLOR_PDC))
fig_bar.add_trace(go.Bar(name='LIBRE', x=['LIBRE'], y=[total_libre], text=f"{pct_final_libre:.1f}%", textposition='auto', marker_color=COLOR_LIBRE))
fig_bar.update_layout(title_text='<b>Resultado Final sobre Votos Válidos</b>', yaxis_title='Cantidad de Votos', showlegend=False)
st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
st.header("Distribución del Voto Total Emitido")

# --- SECCIÓN CORREGIDA ---
# Ahora se usan 4 columnas para mostrar todos los totales juntos
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(label="Total Votos PDC 🟠", value=f"{int(total_pdc):,}")
kpi2.metric(label="Total Votos LIBRE 🔴", value=f"{int(total_libre):,}")
kpi3.metric(label="Total Votos Nulos", value=f"{int(total_nulos):,}")
kpi4.metric(label="Total Votos Blancos", value=f"{int(total_blancos):,}")


# --- LÓGICA DEL GRÁFICO FINAL MEJORADO ---
labels_pie = ['PDC 🟠', 'LIBRE 🔴', 'Nulos', 'Blancos']
values_pie = [total_pdc, total_libre, total_nulos, total_blancos]
pull_pie = [0, 0, 0, 0] 

if total_pdc > total_libre:
    labels_pie[0] = f"👑 {labels_pie[0]}"
    pull_pie[0] = 0.1 
    pie_colors = [COLOR_PDC, COLOR_LIBRE, COLOR_PDC_LIGHT, COLOR_LIBRE_LIGHT]
elif total_libre > total_pdc:
    labels_pie[1] = f"👑 {labels_pie[1]}"
    pull_pie[1] = 0.1
    pie_colors = [COLOR_PDC, COLOR_LIBRE, COLOR_LIBRE_LIGHT, COLOR_PDC_LIGHT]
else:
    pie_colors = [COLOR_PDC, COLOR_LIBRE, 'grey', 'lightgrey']

fig_pie = go.Figure(data=[go.Pie(
    labels=labels_pie, 
    values=values_pie, 
    hole=.4,
    marker_colors=pie_colors,
    pull=pull_pie,
    textinfo='percent+label',
    textfont_size=14
)])
fig_pie.update_layout(title_text='<b>Desglose del Voto Total Emitido en la Simulación</b>', showlegend=False)
st.plotly_chart(fig_pie, use_container_width=True)


st.markdown("---")
st.header("Detalle de Transferencia de Votos por Origen")
st.write("Esta tabla muestra cómo se distribuyeron los votos de CADA partido de la 1ra vuelta.")
df_desglose = pd.DataFrame(desglose_data).set_index('Partido Origen')
st.dataframe(df_desglose.style.format(formatter={'Votos a PDC 🟠': '{:,.0f}', 'Votos a LIBRE 🔴': '{:,.0f}', 'Votos a Nulo': '{:,.0f}', 'Votos a Blanco': '{:,.0f}'}))