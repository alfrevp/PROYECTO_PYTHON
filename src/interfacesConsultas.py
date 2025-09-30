import streamlit as st
import consultas  # Importar el archivo consultas.py

# Definir las interfaces para cada consulta
def interfaz_c1(datos_ind):
    if st.button("Ejecutar Consulta 1"):
        resultado = consultas.consulta1(datos_ind)
        # Convertir el resultado en una lista de diccionarios para mostrarlo como tabla
        tabla_resultado = [
            {
                "Año": ano,
                "Lee y Escribe": f"{valores['porcentaje_lee_escribe']:.2f}%",
                "Caso Contrario": f"{valores['porcentaje_no_lee_escribe']:.2f}%"
            }
            for ano, valores in resultado.items()
        ]
        
        # Mostrar la tabla
        st.dataframe(tabla_resultado, use_container_width=True)

def interfaz_c2(datos_individuos):    
    # Extraer años y trimestres de los datos
    anios = sorted(set(int(ind['ANO4']) for ind in datos_individuos))
    trimestres = sorted(set(int(ind['TRIMESTRE']) for ind in datos_individuos))
    
    # Selectores para año y trimestre
    anio_seleccionado = st.selectbox("Seleccione un año:", anios)
    trimestre_seleccionado = st.selectbox("Seleccione un trimestre:", trimestres)
    
    if st.button("Ejecutar Consulta 2"):
        # Ejecutar la consulta con el año y trimestre seleccionados
        resultado = consultas.consulta2(datos_individuos, anio_seleccionado, trimestre_seleccionado)
        
        # Mostrar el resultado
        st.write("### Resultados de la Consulta 2")
        st.write(f"Porcentaje: {resultado:.2f}%")

def interfaz_c3(datos_individuos):
    if st.button("Ejecutar Consulta 3"):
        # Ejecutar la consulta
        resultado = consultas.consulta3(datos_individuos)
        
        tabla_resultado = [
            {
                "Año": resultado[0],
                "Trimestre": resultado[1],
                "Porcentaje de Desocupación": f"{resultado[2]:.2f}%"
            }
        ]
        st.dataframe(tabla_resultado)

def interfaz_c4(datos_hogares, datos_individuos):    
    if st.button("Ejecutar Consulta 4"):
        # Ejecutar la consulta
        resultado = consultas.consulta4(datos_hogares, datos_individuos)
        
        # Convertir el resultado en una tabla
        tabla_resultado = [
            {
                "Ranking": idx + 1,
                "Aglomerado": aglomerado,
                "Porcentaje de Hogares con 2+ Universitarios": f"{porcentaje:.2f}%"
            }
            for idx, (aglomerado, porcentaje) in enumerate(resultado)
        ]
        
        # Mostrar la tabla
        st.write("### Resultados de la Consulta 4")
        st.dataframe(tabla_resultado, use_container_width=True) 

def interfaz_c5(datos_hogares):
    if st.button("Ejecutar Consulta 5"):
        resultado = consultas.consulta5(datos_hogares)
        tabla_resultado = [
            {
                "Aglomerado": aglomerado,
                "Porcentaje de Hogares con 2+ Universitarios": f"{porcentaje:.2f}%"
            }
            for aglomerado, porcentaje in resultado.items()
        ]
        st.dataframe(tabla_resultado)

def interfaz_c6(datos_hogares):
    if st.button("Ejecutar Consulta 6"):
        resultado = consultas.consulta6(datos_hogares)
        st.write(f"Aglomerado {resultado[0]}, con {resultado[1]} viviendas")

def interfaz_c7(datos_individuos):
    if st.button("Ejecutar Consulta 7"):
        resultado = consultas.consulta7(datos_individuos)
        tabla_resultado = [
            {
                "Aglomerado": aglomerado,
                "Porcentaje": f"{porcentaje:.2f}%"
            }
            for aglomerado, porcentaje in resultado.items()
        ]
        st.dataframe(tabla_resultado)

def interfaz_c8(datos_hogares):    
    if st.button("Ejecutar Consulta 8"):
        # Ejecutar la consulta
        resultado = consultas.consulta8(datos_hogares)
        tabla_resultado = [
            {
                "Región": region,
                "Porcentaje de Inquilinos": f"{porcentaje:.2f}%"
            }
            for region, porcentaje in resultado
        ]
        st.dataframe(tabla_resultado, use_container_width=True)

def interfaz_c9(datos_individuos):
    aglomerados = sorted(set(int(ind['AGLOMERADO']) for ind in datos_individuos))
    aglomerado_seleccionado = st.selectbox("Seleccione un aglomerado:", aglomerados)
    if st.button("Ejecutar Consulta 9"):
        resultado = consultas.consulta9(datos_individuos, aglomerado_seleccionado)

        st.write(f"### Resultados para el aglomerado {aglomerado_seleccionado}")
        st.dataframe(resultado, use_container_width=True)

def interfaz_c10(datos_individuos):
    aglomerados = sorted(set(int(ind['AGLOMERADO']) for ind in datos_individuos))
    aglo1 = st.selectbox("Seleccione un aglomerado:", aglomerados)
    aglo2 = st.selectbox("Seleccione otro aglomerado:", aglomerados)
    if st.button("Ejecutar Consulta 10"):
        if aglo1 == aglo2:
            st.warning("Seleccione dos aglomerados diferentes.")
        else:
            st.dataframe(consultas.consulta10(datos_individuos, aglo1, aglo2), use_container_width=True)

def interfaz_c11(datos_hogares):
    
    # Selector de año
    anios = sorted(set(int(hogar['ANO4']) for hogar in datos_hogares))
    anio_seleccionado = st.selectbox("Seleccione un año:", anios)
    
    if st.button("Ejecutar Consulta 11"):
        # Ejecutar la consulta
        resultado = consultas.consulta11(datos_hogares, anio_seleccionado)
        
        if resultado is None or resultado[0] is None or resultado[1] is None:
            st.warning("No hay datos suficientes para el año seleccionado.")
        else:
            max_aglo, min_aglo = resultado
            
            # Crear tabla con los resultados
            tabla_resultado = [
                {
                    "Descripción": "Mayor porcentaje",
                    "Aglomerado": max_aglo[0],
                    "Porcentaje": f"{max_aglo[1]:.2f}%"
                },
                {
                    "Descripción": "Menor porcentaje",
                    "Aglomerado": min_aglo[0],
                    "Porcentaje": f"{min_aglo[1]:.2f}%"
                }
            ]
            st.dataframe(tabla_resultado, use_container_width=True)

def interfaz_c12(datos_hogares, datos_individuos):
    if st.button("Ejecutar Consulta 12"):
        # Ejecutar la consulta
        resultado, max_ano, max_trimestre = consultas.consulta12(datos_hogares, datos_individuos)

        tabla_resultado = [
            {
                "Aglomerado": aglomerado,
                "Porcentaje": f"{porcentaje:.2f}%"
            }
            for aglomerado, porcentaje in resultado.items()
        ]
        st.write(f"Resultados para el año {max_ano} y trimestre {max_trimestre}")
        st.dataframe(tabla_resultado, use_container_width=True)

def interfaz_c13(datos_hogares, datos_individuos):
    anios = sorted(set(int(ind['ANO4']) for ind in datos_hogares))
    anio_seleccionado = st.selectbox("Seleccione un año:", anios)
    if st.button("Ejecutar Consulta 13"):
        resultado = consultas.consulta13(datos_hogares, datos_individuos, anio_seleccionado)
        st.write(f"Resultado para el año {anio_seleccionado}: {resultado}")


# Diccionario de interfaces
interfaces = {
    "consulta1": interfaz_c1,
    "consulta2": interfaz_c2,
    "consulta3": interfaz_c3,
    "consulta4": interfaz_c4,
    "consulta5": interfaz_c5,
    "consulta6": interfaz_c6,
    "consulta7": interfaz_c7,
    "consulta8": interfaz_c8,
    "consulta9": interfaz_c9,
    "consulta10": interfaz_c10,
    "consulta11": interfaz_c11,
    "consulta12": interfaz_c12,
    "consulta13": interfaz_c13,
}