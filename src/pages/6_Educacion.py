import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from educacion_utils import *
import altair as alt
from consultas import consulta4
from mapeos import MAPEO_AGLOMERADO

st.set_page_config(
    page_title="Encuest.AR - Educacion",
    page_icon="🎓",
    layout="wide"
)

if "carga_realizada" not in st.session_state:
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.markdown("## Diríjase a la página de carga de datos para poder utilizar estas funcionalidades")
    st.stop()

datos = st.session_state["datos_completos_ind"]
df_ind = pd.DataFrame(datos)
st.title("🎓Educación")

# asegurar tipos correctos 
df_ind["ANO4"] = pd.to_numeric(df_ind["ANO4"], errors="coerce")
df_ind["TRIMESTRE"] = pd.to_numeric(df_ind["TRIMESTRE"], errors="coerce")
df_ind["PONDERA"] = pd.to_numeric(df_ind["PONDERA"], errors="coerce")
df_ind["CH06"] = pd.to_numeric(df_ind["CH06"], errors="coerce")  # edad
df_ind["CH09"] = pd.to_numeric(df_ind["CH09"], errors="coerce")  # sabe leer y escribir


st.divider() 
# --- INCISO 1 ----
st.subheader("Máximo nivel alcanzado por año (cant personas)")

anio = st.selectbox("Seleccione el año:", sorted(df_ind["ANO4"].unique()))

df_niveles = contar_personas_por_nivel(df_ind, anio)

# grafico
fig, ax = plt.subplots(figsize=(6, 3.5))
fig.patch.set_facecolor("#18031F") 
ax.set_facecolor("#18031F")
bars = ax.barh(df_niveles["Nivel educativo"], df_niveles["Cantidad"], color="#66B2FF", edgecolor="none", alpha=0.85)
for bar in bars:
    width = bar.get_width()
    ax.text(
        width + max(df_niveles["Cantidad"]) * 0.01,
        bar.get_y() + bar.get_height() / 2,
        f"{int(width):,}".replace(",", "."),
        va="center",
        fontsize=8,
        fontweight="normal",
        fontfamily='serif',
        color="white"
    )

ax.set_xlabel("Cantidad de personas", fontsize=10, fontweight="normal", fontfamily='serif', color="white")
ax.set_title(f"Máximo nivel educativo alcanzado - {anio}", fontsize=12, fontweight="normal", fontfamily='serif', pad=10, color="white")
ax.invert_yaxis()
for spine in ax.spines.values():
    spine.set_visible(False)
ax.spines["bottom"].set_visible(True)
ax.spines["bottom"].set_color("#4F709C")
ax.spines["bottom"].set_linewidth(1)
ax.yaxis.set_ticks_position('none')
ax.xaxis.set_ticks_position('bottom')
ax.tick_params(axis='y', labelsize=8, colors='white')
for label in ax.get_yticklabels():
    label.set_fontweight('normal')
    label.set_fontfamily('serif')
ax.tick_params(axis='x', colors='white')

# ocultar etiquetas y marcas del eje X
ax.tick_params(axis='x', labelbottom=False, which='both', length=0)
ax.grid(False)

plt.subplots_adjust(left=0.15, right=0.95, top=0.9, bottom=0.15)
st.pyplot(fig)

st.divider()

# --- INCISO 2 ---
st.subheader("Nivel educativo más común por grupo etario")

grupos_posibles = [
    (20, 30),
    (30, 40),
    (40, 50),
    (50, 60),
    (60, None)
]
nombres_grupos = ["20-30", "30-40", "40-50", "50-60", "60+"]

seleccion = st.multiselect(
    "Seleccione grupos etarios a mostrar:",
    nombres_grupos,
    default=[]
)

if seleccion:
    grupos_seleccionados = [grupos_posibles[nombres_grupos.index(g)] for g in seleccion]
    df_nivel_comun = nivel_mas_comun_por_grupo_edad(df_ind, grupos_seleccionados)
    
    tabla_html = df_nivel_comun.to_html(index=False)
    tabla_html_centrada = f"""
    <div style="display: flex; justify-content: center;">
        {tabla_html}
    </div>
    """
    st.markdown(tabla_html_centrada, unsafe_allow_html=True)
else:
    st.info("Por favor, seleccioná al menos un grupo etario para mostrar los resultados.")


st.divider()

# --- INCISO 3 ---
st.subheader("Ranking de 5 aglomerados con mayor porcentaje de hogares con 2+ universitarios:")

if st.button("Mostrar ranking"):
    ranking = consulta4(st.session_state["datos_completos_hog"], st.session_state["datos_completos_ind"])
    df_ranking = pd.DataFrame(ranking, columns=["AGLOMERADO", "Porcentaje"])

    df_ranking["Nombre aglomerado"] = df_ranking["AGLOMERADO"].map(lambda x: MAPEO_AGLOMERADO.get(int(x), None))
    df_ranking = df_ranking[["Nombre aglomerado", "Porcentaje"]]
    df_ranking["Porcentaje"] = df_ranking["Porcentaje"].round(2)   # redondeo

    col1, col2 = st.columns(2)
    with col1:
        tabla_html = df_ranking.to_html(index=False)
        st.markdown(tabla_html, unsafe_allow_html=True)
    with col2:
        import io
        csv_buffer = io.StringIO()
        df_ranking.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        st.download_button(
            label="Descargar CSV",
            data=csv_data,
            file_name="ranking_5_aglomerados.csv",
            mime="text/csv",
        )

st.divider()

# --- INCISO 4 --- 
st.subheader("Porcentaje de alfabetización (mayores a 6 años)")

df_alfabetismo = porcentaje_alfabetizacion_por_anio(df_ind)

df_stack = df_alfabetismo.melt(id_vars=["ANO4"], value_vars=["Sabe", "No sabe"], var_name="Estado", value_name="Porcentaje")

grafico_barras = alt.Chart(df_stack).mark_bar().encode(
    x=alt.X("ANO4:O", title="Año", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("Porcentaje:Q", stack="normalize", axis=alt.Axis(format='%')),
    color=alt.Color("Estado:N", scale=alt.Scale(scheme="tableau10")),
    tooltip=[alt.Tooltip("Estado:N"), alt.Tooltip("Porcentaje:Q", format=".2f")]
).properties(
    width=700,
    height=400,
    title="Personas que saben y no saben leer/escribir (por año) :"
)

st.altair_chart(grafico_barras, use_container_width=True)