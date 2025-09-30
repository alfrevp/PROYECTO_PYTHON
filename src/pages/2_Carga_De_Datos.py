import sys
sys.path.append('../src/')
import streamlit as st
from utils import detectar_rango_fechas_combinada, leer_archivos_combinado
import csv
from pathlib import Path
import inspect
import consultas  # Importar el archivo consultas.py
from interfacesConsultas import interfaces  # Importar las interfaces

st.set_page_config(
    page_title="Encuest.AR - EPH",
    page_icon="📊",
    layout="wide"
)

if "carga_realizada" not in st.session_state:
    st.session_state["carga_realizada"] = False

# Interfaz principal
col1, col2 = st.columns([3, 1])
with col1:
    st.title("📂 Carga de Datos")
with col2:
    actualizar = st.button("🔄 Actualizar archivos")

    if not st.session_state["carga_realizada"] or actualizar:
        with st.spinner("Actualizando datos..."):
            # Leer todos los datos disponibles nuevamente
            datos_ind, datos_hog, contenido = leer_archivos_combinado("../datos/procesado/", ["ind_", "hog_"])
            st.session_state["datos_completos_ind"] = datos_ind
            st.session_state["datos_completos_hog"] = datos_hog

            # Detectar años disponibles en los datos de individuos y hogares
            anios_ind = sorted(set(int(ind['ANO4']) for ind in datos_ind))
            anios_hog = sorted(set(int(hog['ANO4']) for hog in datos_hog))

            # Guardar los datos de individuos por año
            for anio in anios_ind:
                st.session_state[f"datos_ind_{anio}"] = [ind for ind in datos_ind if int(ind['ANO4']) == anio]
            # Guardar los datos de hogares por año
            for anio in anios_hog:
                st.session_state[f"datos_hog_{anio}"] = [hog for hog in datos_hog if int(hog['ANO4']) == anio]

        st.session_state["carga_realizada"] = True
        st.success(f"Datos cargados correctamente.\n{contenido}")

# Verificar si ya se cargaron los datos completos
if "carga_realizada" not in st.session_state:
    st.warning("No se han cargado datos. Presione '🔄 Actualizar archivos' para cargar los datos.")
else:
    # Mostrar rango de fechas disponibles
    st.subheader("Datos disponibles")
    rango = detectar_rango_fechas_combinada('../datos/procesado', ['ind_', 'hog_'])
    if rango:
        # Crear lista de años disponibles y guardarla en session_state
        años_disponibles = list(range(int(rango['F_inicio']), int(rango['F_fin']) + 1))
        st.session_state["anios_disponibles"] = años_disponibles

        st.success(
            f"El sistema contiene información desde {rango['T_inicio']} "
            f"hasta {rango['T_fin']}."
        )
    else:
        st.warning("No se encontraron datos procesados")

    # Mostrar datos completos
    st.divider()
    st.subheader("Datos completos")

    col1, col2 = st.columns(2)
    with col1:
        # Selector de año para filtrar
        anios_disponibles = sorted(set(int(hogar['ANO4']) for hogar in st.session_state["datos_completos_hog"]))
        anio_filtrado = st.selectbox(
            "Filtrar por año:",
            options=[None] + anios_disponibles,
            format_func=lambda x: "Todos" if x is None else str(x)  # Convertir a cadena para evitar errores
        )
    with col2:
        # Selector de trimestre para filtrar
        if anio_filtrado is not None:
            trimestres_disponibles = sorted(set(int(hogar['TRIMESTRE']) for hogar in st.session_state["datos_completos_hog"] if int(hogar['ANO4']) == anio_filtrado))
        else:
            trimestres_disponibles = sorted(set(int(hogar['TRIMESTRE']) for hogar in st.session_state["datos_completos_hog"]))

        trimestre_filtrado = st.selectbox(
            "Filtrar por trimestre:",
            options=[None] + trimestres_disponibles,
            format_func=lambda x: "Todos" if x is None else f"Trimestre {x}"
        )
    num_resultados = st.selectbox(
        "Resultados por página:",
        [10, 20, 50, 100],
        index=1
    )

    altura_tabla = 35 * (num_resultados + 1)

    # Inicializar estados para paginación
    for key in ["pagina_ind_completos", "pagina_hog_completos", "filtro_anio"]:        # REVISAR: se usa 'filto_anio'? parece que se usa 'anio_filtrado' en su lugar
        if key not in st.session_state:
            st.session_state[key] = 0 if key != "filtro_anio" else None

    # Filtrar INDIVIDUOS completos
    datos_ind = st.session_state["datos_completos_ind"]
    if anio_filtrado is not None:
        datos_ind = [ind for ind in datos_ind if int(ind['ANO4']) == anio_filtrado]
    if trimestre_filtrado is not None:
        datos_ind = [ind for ind in datos_ind if int(ind['TRIMESTRE']) == trimestre_filtrado]

    total_ind = len(datos_ind)
    start_ind = st.session_state.pagina_ind_completos * num_resultados
    end_ind = start_ind + num_resultados
    st.markdown("### 👤 INDIVIDUOS")
    st.dataframe(datos_ind[start_ind:end_ind], height=altura_tabla)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Anterior IND") and st.session_state.pagina_ind_completos >= 0:
            st.session_state.pagina_ind_completos -= 1
    with col2:
        if st.button("Siguiente ➡️ IND") and end_ind < total_ind:
            st.session_state.pagina_ind_completos += 1

    # Filtrar HOGARES completos
    datos_hog = st.session_state["datos_completos_hog"]
    if anio_filtrado is not None:
        datos_hog = [hog for hog in datos_hog if int(hog['ANO4']) == anio_filtrado]
    if trimestre_filtrado is not None:
        datos_hog = [hog for hog in datos_hog if int(hog['TRIMESTRE']) == trimestre_filtrado]

    total_hog = len(datos_hog)
    start_hog = st.session_state.pagina_hog_completos * num_resultados
    end_hog = start_hog + num_resultados
    st.markdown("### 🏠 HOGARES")
    st.dataframe(datos_hog[start_hog:end_hog], height=altura_tabla)

    col3, col4 = st.columns(2)
    with col3:
        if st.button("⬅️ Anterior HOG") and st.session_state.pagina_hog_completos >= 0:
            st.session_state.pagina_hog_completos -= 1
    with col4:
        if st.button("Siguiente ➡️ HOG") and end_hog < total_hog:
            st.session_state.pagina_hog_completos += 1

    # --------------------------------------------------------
    # DICCIONARIO CONSULTAS
    # --------------------------------------------------------
    configuracion_consultas = {
        "consulta1": {
            "interfaz": interfaces["consulta1"],  # Función de interfaz
            "args": [st.session_state["datos_completos_ind"]],
        },
        "consulta2": {
            "interfaz": interfaces["consulta2"],
            "args": [st.session_state["datos_completos_ind"]],
        },
        "consulta3": {
            "interfaz": interfaces["consulta3"],
            "args": [st.session_state["datos_completos_ind"]],
        },
        "consulta4": {
            "interfaz": interfaces["consulta4"],
            "args": [st.session_state["datos_completos_hog"], st.session_state["datos_completos_ind"]],
        },
        "consulta5": {
            "interfaz": interfaces["consulta5"],
            "args": [st.session_state["datos_completos_hog"]],
        },
        "consulta6": {
            "interfaz": interfaces["consulta6"],
            "args": [st.session_state["datos_completos_hog"]],
        },
        "consulta7": {
            "interfaz": interfaces["consulta7"],
            "args": [st.session_state["datos_completos_ind"]],
        },
        "consulta8": {
            "interfaz": interfaces["consulta8"],
            "args": [st.session_state["datos_completos_hog"]],
        },
        "consulta9": {
            "interfaz": interfaces["consulta9"],
            "args": [st.session_state["datos_completos_ind"]],
        },
        "consulta10": {
            "interfaz": interfaces["consulta10"],
            "args": [st.session_state["datos_completos_ind"]],
        },
        "consulta11": {
            "interfaz": interfaces["consulta11"],
            "args": [st.session_state["datos_completos_hog"]],
        },
        "consulta12": {
            "interfaz": interfaces["consulta12"],
            "args": [st.session_state["datos_completos_hog"], st.session_state["datos_completos_ind"]],
        },
        "consulta13": {
            "interfaz": interfaces["consulta13"],
            "args": [st.session_state["datos_completos_hog"], st.session_state["datos_completos_ind"]],
        },
    }

    # ---------------------------------------------------------
    # DICCIONARIO CONSULTAS
    # ---------------------------------------------------------

    # Mostrar consultas al final de la página
    st.divider()
    st.markdown("## 🔍 Consultas disponibles")

    # Obtener todas las funciones del archivo consultas.py
    funciones_consultas = [
        (name, func) for name, func in inspect.getmembers(consultas, inspect.isfunction)
    ]

    # Crear un menú dinámico con las consultas
    opciones = sorted([f"{name}: {func.__doc__}" for name, func in funciones_consultas],
        key=lambda x: int(x.split(":")[0].replace("consulta", "").strip())
    )
    opcion_seleccionada = st.selectbox("",opciones)

    # Mostrar la interfaz correspondiente a la consulta seleccionada
    consulta_seleccionada = opcion_seleccionada.split(":")[0]
    if consulta_seleccionada in configuracion_consultas:
        config = configuracion_consultas[consulta_seleccionada]
        config["interfaz"](*config["args"])  # Llamar a la interfaz con los argumentos necesarios
    else:
        st.warning("No hay una interfaz definida para esta consulta.")
