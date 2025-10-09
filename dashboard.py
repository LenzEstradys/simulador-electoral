import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
from pywaffle import Waffle

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Simulador Electoral Definitivo",
    page_icon="🏆",
    layout="wide"
)

# --- Colores de Partidos ---
COLOR_PDC = '#FF7F0E' # Naranja
COLOR_LIBRE = '#D62728' # Rojo
COLOR_NULO = 'grey'
COLOR_BLANCO = 'lightgrey'

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
total_votantes_1ra_vuelta = df_transfer['Votos 1ra vuelta'].sum()

# LOS VOTOS BASE AHORA SON 0, TODO SE CALCULA POR TRANSFERENCIA
votos_base_pdc, votos_base_libre, votos_base_nulos, votos_base_blancos = 0, 0, 0, 0

# --- Barra Lateral con Controles Interactivos ---
st.sidebar.header("🏆 Simulación de Transferencia Total")
st.sidebar.write("Escriba el % para cada categoría.")

transfer_results = {}

for index, row in df_transfer.iterrows():
    partido = row['Partido']
    votos_origen = row['Votos 1ra vuelta']
    
    with st.sidebar.expander(f"**Votantes de '{partido}'** ({votos_origen:,})"):
        # Lógica para votantes de PDC
        if partido == 'PDC':
            pct_pdc = st.number_input(f"% Retención (a PDC 🟠)", 0, 100, 80, key=f"{partido}_pdc")
            max_libre = 100 - pct_pdc
            pct_libre = st.number_input(f"% Fuga a LIBRE 🔴", 0, max_libre, min(5, max_libre), key=f"{partido}_libre")
            max_nulo = 100 - pct_pdc - pct_libre
            pct_nulo = st.number_input(f"% Fuga a Nulo", 0, max_nulo, min(10, max_nulo), key=f"{partido}_nulo")
            pct_blanco = 100 - pct_pdc - pct_libre - pct_nulo
            st.markdown(f"**% Fuga a Blanco (auto): `{pct_blanco}`%**")
        
        # Lógica para votantes de LIBRE
        elif partido == 'LIBRE':
            pct_libre = st.number_input(f"% Retención (a LIBRE 🔴)", 0, 100, 85, key=f"{partido}_libre")
            max_pdc = 100 - pct_libre
            pct_pdc = st.number_input(f"% Fuga a PDC 🟠", 0, max_pdc, min(5, max_pdc), key=f"{partido}_pdc")
            max_nulo = 100 - pct_libre - pct_pdc
            pct_nulo = st.number_input(f"% Fuga a Nulo", 0, max_nulo, min(5, max_nulo), key=f"{partido}_nulo")
            pct_blanco = 100 - pct_libre - pct_pdc - pct_nulo
            st.markdown(f"**% Fuga a Blanco (auto): `{pct_blanco}`%**")

        # Lógica para los demás
        else:
            pct_pdc = st.number_input(f"% a PDC 🟠", 0, 100, 40, key=f"{partido}_pdc")
            max_libre = 100 - pct_pdc
            pct_libre = st.number_input(f"% a LIBRE 🔴", 0, max_libre, min(30, max_libre), key=f"{partido}_libre")
            max_nulo = 100 - pct_pdc - pct_libre
            pct_nulo = st.number_input(f"% a Nulo", 0, max_nulo, min(20, max_nulo), key=f"{partido}_nulo")
            pct_blanco = 100 - pct_pdc - pct_libre - pct_nulo
            st.markdown(f"**% a Blanco (auto): `{pct_blanco}`%**")
        
        transfer_results[partido] = {'pdc': pct_pdc/100, 'libre': pct_libre/100, 'nulo': pct_nulo/100, 'blanco': pct_blanco/100}

# --- Lógica de Cálculo ---
total_pdc, total_libre, total_nulos, total_blancos = 0, 0, 0, 0
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

total_proyectado_2da_vuelta = total_pdc + total_libre + total_nulos + total_blancos
votos_validos = total_pdc + total_libre

# --- Panel Principal: Visualización de Resultados ---
st.title("🏆 Simulador Electoral Definitivo - 2da Vuelta")

# --- PANEL DE VERIFICACIÓN DE TOTALES ---
st.info(f"""
**Verificación de Votos:**
- **Total Votantes 1ra Vuelta:** `{int(total_votantes_1ra_vuelta):,}`
- **Total Proyectado 2da Vuelta:** `{int(total_proyectado_2da_vuelta):,}`
""", icon="✅")
st.markdown("---")

# --- SECCIÓN DE RESULTADOS VÁLIDOS ---
st.header("Resultados sobre Votos Válidos")
col1, col2, col3 = st.columns(3)

if votos_validos > 0:
    pct_final_pdc = (total_pdc / votos_validos) * 100
    pct_final_libre = (total_libre / votos_validos) * 100
    ganador_str = "PDC 🟠" if total_pdc > total_libre else "LIBRE 🔴"
    diferencia = abs(total_pdc - total_libre)
else:
    pct_final_pdc, pct_final_libre, ganador_str, diferencia = 0, 0, "Indefinido", 0

with col1: st.metric(label="Votos Válidos PDC 🟠", value=f"{int(total_pdc):,}", help=f"{pct_final_pdc:.2f}% de votos válidos")
with col2: st.metric(label="Votos Válidos LIBRE 🔴", value=f"{int(total_libre):,}", help=f"{pct_final_libre:.2f}% de votos válidos")
with col3: st.metric(label="Diferencia de Votos", value=f"{int(diferencia):,}", delta=ganador_str)
st.markdown("---")

# --- SECCIÓN DE DISTRIBUCIÓN TOTAL ---
st.header("Distribución del Voto Total Emitido")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(label="Total Votos PDC 🟠", value=f"{int(total_pdc):,}")
kpi2.metric(label="Total Votos LIBRE 🔴", value=f"{int(total_libre):,}")
kpi3.metric(label="Total Votos Nulos", value=f"{int(total_nulos):,}")
kpi4.metric(label="Total Votos Blancos", value=f"{int(total_blancos):,}")

# --- GRÁFICO DE PERSONITAS (WAFFLE CHART) ---
data_waffle = {
    'PDC 🟠': total_pdc,
    'LIBRE 🔴': total_libre,
    'Nulos': total_nulos,
    'Blancos': total_blancos
}
# Asignación de corona
if ganador_str == "PDC 🟠":
    data_waffle = {'👑 PDC 🟠': total_pdc, 'LIBRE 🔴': total_libre, 'Nulos': total_nulos, 'Blancos': total_blancos}
    waffle_colors = [COLOR_PDC, COLOR_LIBRE, COLOR_NULO, COLOR_BLANCO]
else:
    data_waffle = {'PDC 🟠': total_pdc, '👑 LIBRE 🔴': total_libre, 'Nulos': total_nulos, 'Blancos': total_blancos}
    waffle_colors = [COLOR_PDC, COLOR_LIBRE, COLOR_NULO, COLOR_BLANCO]

fig_waffle = plt.figure(
    FigureClass=Waffle,
    rows=10,
    values=data_waffle,
    colors=waffle_colors,
    legend={'loc': 'upper left', 'bbox_to_anchor': (1, 1)},
    icons='child', 
    font_size=20, 
    icon_style='solid'
)
st.pyplot(fig_waffle)
st.markdown("---")

# --- SECCIÓN DE DESGLOSE ---
st.header("Detalle de Transferencia de Votos por Origen")
df_desglose = pd.DataFrame(desglose_data).set_index('Partido Origen')
st.dataframe(df_desglose.style.format(formatter={'Votos a PDC 🟠': '{:,.0f}', 'Votos a LIBRE 🔴': '{:,.0f}', 'Votos a Nulo': '{:,.0f}', 'Votos a Blanco': '{:,.0f}'}))