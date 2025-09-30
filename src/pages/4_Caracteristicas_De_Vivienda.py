import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mapeos import *
from vivienda_utils import *

if "carga_realizada" not in st.session_state:
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.markdown("## Diríjase a la página de carga de datos para poder utilizar estas funcionalidades")
    st.stop()

anios_disponibles = st.session_state["anios_disponibles"]
anio_seleccionado = st.selectbox(
    "Seleccione un año para explorar las características habitacionales:",
    ['Todos'] + list(anios_disponibles)
)

st.title(f"Características de la Vivienda - {anio_seleccionado}")
# Preparacion de datos
df_filtrado = pd.DataFrame(st.session_state[f"datos_hog_{anio_seleccionado}"] if anio_seleccionado != 'Todos' else st.session_state["datos_completos_hog"])
df_filtrado["AGLOMERADO"] = df_filtrado["AGLOMERADO"].astype(str).map(MAPEO_AGLOMERADO)
df_filtrado["IV1"] = df_filtrado["IV1"].astype(str).map(MAPEO_IV1)
df_filtrado["IV3"] = df_filtrado["IV3"].astype(str).map(MAPEO_MATERIAL)
df_filtrado['II7'] = df_filtrado['II7'].astype(str).map(MAPEO_TENENCIA)

# 1.4.1 Cantidad total de viviendas
st.subheader("Cantidad total de viviendas")
st.write(f"Total de viviendas encuestadas: {len(df_filtrado):,}")

# 1.4.2 Gráfico de torta - Tipo de vivienda
st.subheader("Tipo de vivienda")
if not df_filtrado.empty:
    tipo_vivienda_pct, etiquetas = calcular_tipo_vivienda(df_filtrado)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            fig, ax = plt.subplots(figsize=(4, 4), facecolor='white')
            wedges, _ = ax.pie(
                tipo_vivienda_pct,
                startangle=90,
                counterclock=False
            )
            ax.legend(wedges, etiquetas, title="Tipo de vivienda", loc="center left", bbox_to_anchor=(1, 0.5))
            st.pyplot(fig)
else:
    st.warning("No hay datos para el año seleccionado")

# 1.4.3 Material predominante en pisos por aglomerado
st.subheader("Material predominante en pisos por aglomerado")
if not df_filtrado.empty:
    tabla = calcular_material_pisos(df_filtrado)
    st.dataframe(tabla, hide_index=True)
else:
    st.warning("No hay datos para el año seleccionado")

# 1.4.4 Proporción de viviendas con baño dentro del hogar
st.subheader("Viviendas con baño dentro del hogar")
if not df_filtrado.empty:
    resultados = calcular_banio(df_filtrado)
    st.dataframe(resultados)
else:
    st.warning("No hay datos para el año seleccionado")

# 1.4.5 Evolución del régimen de tenencia para un aglomerado específico y año
st.subheader("Evolución del régimen de tenencia:")
df_filtrado, aglomerados, tipos_tenencia = calcular_evolucion_tenencia(df_filtrado)
col1, col2 = st.columns(2)
with col1:
    aglo_seleccionado = st.selectbox("Seleccione un aglomerado:", aglomerados)
with col2:
    tenencias_seleccionadas = st.multiselect(
        "Seleccione tipo(s) de tenencia:", tipos_tenencia, default=tipos_tenencia
    )
if st.button("Mostrar evolución"):
    df_filtrado145 = df_filtrado[
        (df_filtrado['AGLOMERADO'] == aglo_seleccionado) &
        (df_filtrado['II7'].isin(tenencias_seleccionadas))
    ]
    if not df_filtrado145.empty:
        evolucion = (df_filtrado145.groupby(['TRIMESTRE', 'II7'])['PONDERA'].sum().unstack(fill_value=0).sort_index())
        st.line_chart(evolucion)
        st.write("Eje horizontal: Trimestre")
    else:
        st.warning("No hay datos para la selección realizada.")

# 1.4.6 Viviendas en villa de emergencia
st.subheader("Viviendas en villa de emergencia por aglomerado")
if not df_filtrado.empty:
    resultados_df = calcular_viviendas_villa(df_filtrado)
    st.dataframe(resultados_df, hide_index=True)
else:
    st.warning("No hay datos para el año seleccionado")

# 1.4.7 Condición de habitabilidad
st.subheader("Condición de habitabilidad")
if not df_filtrado.empty:
    habitabilidad_pct_fmt, habitabilidad_pct = calcular_habitabilidad(df_filtrado)
    st.dataframe(habitabilidad_pct_fmt, hide_index=True)
    st.download_button(
        label="Descargar CSV",
        data=habitabilidad_pct.to_csv(index=False).encode('utf-8'),
        file_name='condicion_habitabilidad.csv',
        mime='text/csv'
    )
else:
    st.warning("No hay datos para el año seleccionado")

