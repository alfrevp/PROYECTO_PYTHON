# principal.py
import streamlit as st
import pandas as pd
import json
import os
import folium
from streamlit_folium import folium_static
from empleo_utils import *
from mapeos import MAPEO_AGLOMERADO
import altair as alt

if "carga_realizada" not in st.session_state:
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.write("## Diríjase a la página de carga de datos para poder utilizar estas funcionalidades")
    st.stop()

st.title("Actividad y Empleo")

df_individuos = pd.DataFrame(st.session_state["datos_completos_ind"])
df_individuos["AGLOMERADO"] = df_individuos["AGLOMERADO"].astype(str).map(MAPEO_AGLOMERADO)

# 1.5.1
st.subheader("Personas desocupadas por nivel de estudios")
anios = st.session_state["anios_disponibles"]
col1, col2 = st.columns(2)
with col1:
    anio_sel = st.selectbox("Seleccione un año:", anios, key='empleo_año')
with col2:
    df_anio = st.session_state[f"datos_ind_{anio_sel}"]
    trimestres = sorted(set(ind['TRIMESTRE'] for ind in df_anio))
    trim_sel = st.selectbox("Seleccione un trimestre:", trimestres, key='empleo_trim')

if st.button("Mostrar resultados", key='empleo_btn1'):
    df = pd.DataFrame(df_anio)
    df = df[df['TRIMESTRE'] == trim_sel]
    resultado = calcular_estudios_desocupados(df)
    if resultado is not None:
        st.bar_chart(resultado)
    else:
        st.warning("No hay personas desocupadas para la selección realizada.")

# 1.5.2 y 1.5.3
st.subheader("Evolución de la tasa de empleo y desempleo")
aglos = df_individuos['AGLOMERADO'].unique()
aglo_sel = st.selectbox("Filtrar por aglomerado (opcional):", ['Todos'] + list(aglos), key='empleo_aglo_comb')
if st.button("Mostrar evolución empleo/desempleo", key='empleo_btn_comb'):
    df_filt = df_individuos if aglo_sel == 'Todos' else df_individuos[df_individuos['AGLOMERADO'] == aglo_sel]
    tasas_empleo, tasas_desempleo, index = calcular_tasas_empleo_desempleo(df_filt)
    df_tasas = pd.DataFrame({
        'Tasa de empleo': tasas_empleo,
        'Tasa de desempleo': tasas_desempleo
    }, index=index).reset_index()
    df_tasas['Periodo'] = 'A' + df_tasas['ANO4'].astype(str) + '_T' + df_tasas['TRIMESTRE'].astype(str)
    df_tasas.set_index('Periodo', inplace=True)
    
    chart = alt.Chart(df_tasas.reset_index()).mark_line(point=True).encode(
        x=alt.X('Periodo:N', title='Periodo'),
        y=alt.Y('Tasa de empleo:Q', title='Tasa de empleo (%)'),
        color=alt.value('#1f77b4')
    ).properties(
        width=700,
        height=300  # <-- aquí ajustas la altura
    )

    chart2 = alt.Chart(df_tasas.reset_index()).mark_line(point=True, color='red').encode(
        x=alt.X('Periodo:N', title='Periodo'),
        y=alt.Y('Tasa de desempleo:Q', title='Tasa de desempleo (%)'),
    )

    st.altair_chart(chart + chart2, use_container_width=True)

# 1.5.4
st.subheader("Distribución del empleo por tipo")
df_resultado = calcular_distribucion_empleo(df_individuos)
st.dataframe(df_resultado, hide_index=True)

# 1.5.5
st.subheader("Mapa de variación de tasas de empleo/desempleo")
opcion_tasa = st.radio("Seleccione qué tasa visualizar:", ('Tasa de empleo', 'Tasa de desempleo'), key='tasa_mapa_final')
anio_ini = min(st.session_state["anios_disponibles"])
anio_fin = max(st.session_state["anios_disponibles"])
df_ini = pd.DataFrame(st.session_state[f"datos_ind_{anio_ini}"])
df_fin = pd.DataFrame(st.session_state[f"datos_ind_{anio_fin}"])
ruta = os.path.join(os.path.dirname(__file__), '..','recursos', 'aglomerados_coordenadas.json')
with open(ruta, encoding='utf-8') as f:
    coords = json.load(f)
resultados = calcular_variacion_mapa(df_ini, df_fin, coords, opcion_tasa)
m = folium.Map(location=[-34.6037, -58.3816], zoom_start=5)
for r in resultados:
    color = 'green' if (opcion_tasa == 'Tasa de empleo' and r['variacion'] > 0) or (opcion_tasa == 'Tasa de desempleo' and r['variacion'] < 0) else 'red'
    folium.CircleMarker(
        location=r['coordenadas'],
        radius=5,
        color=color,
        fill=True,
        fill_color=color,
        popup=f"Aglomerado {r['aglomerado']}: Variación {r['variacion']:.1f}%"
    ).add_to(m)
folium_static(m)
