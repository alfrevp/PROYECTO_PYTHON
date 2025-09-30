import sys
sys.path.append('../src/')
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Encuest.AR - EPH",
    page_icon="📊",
    layout="wide"
)

# Título y descripción
st.title("Encuest.AR 📊")
st.markdown("""
**Visualización interactiva de la Encuesta Permanente de Hogares (EPH)**

La EPH es un programa nacional que recoge información sobre:
- Características demográficas
- Condiciones laborales
- Niveles educativos
- Situación habitacional

*Datos oficiales del INDEC (Instituto Nacional de Estadística y Censos)*
""")

# Sección de instrucciones (para etapa 2)
st.divider()
st.subheader("Instrucciones de uso")
st.write("""
1. Navega entre las páginas usando el menú lateral
2. En **Carga de datos** verifica el rango temporal disponible
3. En **Características Demográficas** encontrarás información general sobre la población
4. En **Características De Vivienda** información sobre los tipos de vivienda 
5. En **Actividad Y Empleo** datos sobre trabajo
6. En **Educación** se podrán visualizar temas referidos al nivel educativo de cada persona
7. En **Ingresos** información ecnómica y estimaciones de acuerdo a la canasta básica familiar
""")
