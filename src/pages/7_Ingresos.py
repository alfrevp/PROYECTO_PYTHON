import streamlit as st
import pandas as pd
from pathlib import Path

if "carga_realizada" not in st.session_state:
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.write("## Diríjase a la página de carga de datos para poder utilizar estas funcionalidades")
    st.stop()
    
st.title("Hogares bajo la línea de pobreza e indigencia")

# --- Carga de datos ---
ruta_carpeta = Path(__file__).parent.parent / 'recursos'
archivo_canasta = next((f for f in ruta_carpeta.glob('*.csv') if 'canasta' in f.name.lower()), None)

if archivo_canasta:
    df_canasta = pd.read_csv(archivo_canasta)
    # Parsear fechas
    df_canasta['indice_tiempo'] = pd.to_datetime(df_canasta['indice_tiempo'], errors='coerce')
    df_canasta['AÑO'] = df_canasta['indice_tiempo'].dt.year
    df_canasta['MES'] = df_canasta['indice_tiempo'].dt.month
else:
    st.error(f"No se encontró el archivo de canasta básica en {ruta_carpeta}.")
    st.stop()

# --- Interfaz ---
anios_disponibles = st.session_state["anios_disponibles"]

col1, col2 = st.columns(2)
with col1:
    anio_sel = st.selectbox("Seleccione un año:", anios_disponibles, key='cbf_anio')

with col2:
    df_hogares = pd.DataFrame(st.session_state[f"datos_hog_{anio_sel}"])
    df_hogares4 = df_hogares[df_hogares['IX_TOT'] == '4']  # Filtrar hogares con 4 integrantes
    trimestres_disponibles = sorted(df_hogares['TRIMESTRE'].unique())
    trimestre_sel = st.selectbox("Seleccione un trimestre:", trimestres_disponibles, key='cbf_trim')
    # Filtrar hogares con trimestre seleccionado
    df_hogares4 = df_hogares4[df_hogares4['TRIMESTRE'] == trimestre_sel]

# --- Cálculo automático sin botón ---
# Asegurar tipo correcto
df_hogares4['ITF'] = pd.to_numeric(df_hogares4['ITF'], errors='coerce')



# Determinar meses correspondientes al trimestre
trimestre_a_meses = {'1': [1, 2, 3], '2': [4, 5, 6], '3': [7, 8, 9], '4': [10, 11, 12]}
meses = trimestre_a_meses.get(str(trimestre_sel), [])

# Filtrar canasta y calcular promedios
anio_sel = int(anio_sel)
canasta_trim = df_canasta[
    (df_canasta['AÑO'] == anio_sel) & (df_canasta['MES'].isin(meses))
]

if canasta_trim.empty:
    st.warning("No hay datos de canasta básica para ese período.")
elif df_hogares4.empty:
    st.warning("No hay hogares de 4 integrantes para ese período.")
else:
    cbt_prom = canasta_trim['canasta_basica_total'].mean()
    cba_prom = canasta_trim['canasta_basica_alimentaria'].mean()

    total_hogares = len(df_hogares4)
    bajo_pobreza = (df_hogares4['ITF'] < cbt_prom).sum()
    bajo_indigencia = (df_hogares4['ITF'] < cba_prom).sum()

    st.info(
        f"Total de hogares de 4 integrantes: {total_hogares}\n\n"
        f"Hogares bajo la línea de pobreza: {bajo_pobreza} ({bajo_pobreza/total_hogares*100:.2f}%)\n"
        f"Hogares bajo la línea de indigencia: {bajo_indigencia} ({bajo_indigencia/total_hogares*100:.2f}%)"
    )
