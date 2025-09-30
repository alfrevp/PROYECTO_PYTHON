import pandas as pd
import streamlit as st
from demografia_utils import *
import altair as alt
from mapeos import MAPEO_AGLOMERADO

st.set_page_config(
    page_title="Encuest.AR - Características Demográficas",
    page_icon="👥",
    layout="wide"
)

if "carga_realizada" not in st.session_state:
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.markdown("## Diríjase a la página de carga de datos para poder utilizar estas funcionalidades")
    st.stop()

datos = st.session_state["datos_completos_ind"]
df = pd.DataFrame(datos)

st.title("👥Características Demográficas")
st.divider()
# asegurar tipos correctos (año, trimestre, sexo, edad, ponderacion y cod aglomerado)
df["ANO4"] = pd.to_numeric(df["ANO4"], errors="coerce")
df["TRIMESTRE"] = pd.to_numeric(df["TRIMESTRE"], errors="coerce")
df["CH04"] = df["CH04"].astype(str)
df["CH06"] = pd.to_numeric(df["CH06"], errors="coerce")
df["PONDERA"] = pd.to_numeric(df["PONDERA"], errors="coerce")
df["AGLOMERADO"] = df["AGLOMERADO"].astype(str).map(MAPEO_AGLOMERADO)

# --- INCISO 1 ---
st.subheader("Distribución de personas por edad y sexo")
anios, _ = obtener_anios_trimestres_disponibles(df)

col1, col2 = st.columns([1, 3])
with col1:
    anio = st.selectbox(
        "Seleccioná un año:",
        options=[None] + anios,
        format_func=lambda x: "Seleccionar..." if x is None else str(x)
    )
    trimestres = sorted(df[df["ANO4"] == anio]["TRIMESTRE"].dropna().unique().astype(int)) if anio else []
    trimestre = st.selectbox(
        "Seleccioná un trimestre:",
        options=[None] + trimestres,
        format_func=lambda x: "Seleccionar..." if x is None else f"T{x}"
    )
    mostrar = st.button("📊 Mostrar gráfico")
with col2:
    if mostrar and anio is not None and trimestre is not None:
        fig, error = graf_distribucion_edad_sexo(df, anio, trimestre)
        if error:
            st.error(error)
        else:
            st.pyplot(fig)
    elif mostrar:
        st.warning("Por favor seleccioná un año y trimestre.")

st.divider()

# --- INCISO 2 ---
st.subheader("Edad promedio por aglomerado")

if st.button("Mostrar edad promedio por aglomerado"):
    df_edad_prom, anio, trimestre = edad_promedio_por_aglomerado(df)

    # Crear la etiqueta combinada para el gráfico
    #df_edad_prom["aglomerado_label"] = df_edad_prom["Código"].astype(str) + " - " + df_edad_prom["Aglomerado"]

    st.write(f"Datos correspondientes al año {anio} - trimestre {trimestre} (último trimestre almacenado en el sistema) :")
    
    # mostrar tabla (3 columnas para simular el centrado en la pagina)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.dataframe(df_edad_prom)

    # grafico    -> NOTA: mejorar visualmente
    chart = alt.Chart(df_edad_prom).mark_bar().encode(
        x=alt.X('AGLOMERADO:N', title="Aglomerado"),
        y=alt.Y('Edad Promedio:Q', title="Edad Promedio"),
        tooltip=['AGLOMERADO', alt.Tooltip('Edad Promedio', format=".2f")]
    ).properties(
        width=700,
        height=400,
    )
    st.altair_chart(chart, use_container_width=True)

st.divider()

# --- INCISO 3 ---
st.subheader("Evolución de la dependencia demográfica por aglomerado:")

# Mostrar opciones
opciones_aglomerados = [f"{nombre}" for cod, nombre in sorted(MAPEO_AGLOMERADO.items())]

col1, col2 = st.columns([3, 1])
with col1:
    seleccion = st.selectbox("Seleccioná un aglomerado:", opciones_aglomerados)
with col2:
    st.write("")
    st.write("")   # muy cavernicola pero para que quede mas alineado
    mostrar = st.button("Mostrar evolución")
        
if mostrar:
    df_dep = evolucion_dependencia_demografica(df, seleccion)
    
    # Crear una nueva columna con año y trimestre combinados
    df_dep["Periodo"] = df_dep["Año"].astype(str) + " - T" + df_dep["Trimestre"].astype(str)

    # Crear el gráfico
    chart = alt.Chart(df_dep).mark_line(point=True).encode(
        x=alt.X('Periodo:N', title='Periodo', sort=None),
        y=alt.Y('Dependencia Demográfica:Q', title='Dependencia Demográfica (%)', scale=alt.Scale(domain=[0, 100])),
        tooltip=['Año', 'Trimestre', alt.Tooltip('Dependencia Demográfica', format='.2f')]
    ).properties(
        width=700,
        height=400,
        title="Evolución de la dependencia demográfica"
    )

    st.altair_chart(chart, use_container_width=True)

st.divider()

# --- INCISO 4 ---

st.subheader("Media y mediana de edad por año y trimestre")

df_media_mediana = media_mediana_edad_por_anio_trimestre(df)
df_media_mediana["Año"] = df_media_mediana["Año"].astype(str)    # muestro como string para que no le ponga "," al num

# mostrar tabla (3 columnas para simular el centrado en la pagina)
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.dataframe(df_media_mediana)

# grafico evolutivo

df_media_mediana["Periodo"] = df_media_mediana["Año"] + " - T" + df_media_mediana["Trimestre"].astype(str)

df_media_mediana_fold = df_media_mediana.melt(id_vars=['Periodo'], value_vars=['Media de Edad', 'Mediana de Edad'], var_name='Tipo', value_name='Edad')

chart = alt.Chart(df_media_mediana_fold).mark_line(point=True).encode(
    x=alt.X('Periodo:N', title='Periodo'),
    y=alt.Y('Edad:Q', title='Edad', scale=alt.Scale(domain=[25, 40])),
    color='Tipo:N',
    strokeDash='Tipo:N',
    tooltip=['Periodo', 'Tipo', 'Edad']
).properties(
    width=700,
    height=400,
    title="Evolución de la media y mediana de edad por año y trimestre:"
).configure_view(
    fill="#0B011DA9",        # fondo del área del gráfico
    stroke='transparent'   # sin borde
)

st.altair_chart(chart, use_container_width=True)