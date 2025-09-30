from pathlib import Path
import csv
from typing import List, Dict
import time
import streamlit as st

# Comparador de rango
def en_rango(anio, trim, desde, hasta):
    return (anio, trim) >= desde and (anio, trim) <= hasta

# Lector filtrado por rango con una única barra de progreso
def leer_archivos_combinado(directorio, prefijos):
    """
    Lee todos los archivos disponibles en el directorio con los prefijos especificados
    y devuelve los datos completos sin filtrar por rango.

    Args:
        directorio (str): Ruta del directorio donde se encuentran los archivos.
        prefijos (list): Lista de prefijos para identificar los archivos.

    Returns:
        tuple: Dos listas (datos de individuos y hogares) y un string indicando la cronología.
    """
    datos = {"ind_": [], "hog_": []}
    archivos = []
    fechas_ind = set()  # Fechas presentes en los datos de individuos
    fechas_hog = set()  # Fechas presentes en los datos de hogares

    for prefijo in prefijos:
        archivos.extend([(prefijo, a) for a in Path(directorio).iterdir() if a.name.startswith(prefijo)])
    
    total_archivos = len(archivos)
    progress_bar = st.progress(0)  # Crear barra de progreso
    progress_text = st.empty()  # Contenedor para el texto del porcentaje

    for i, (prefijo, archivo) in enumerate(archivos):
        with archivo.open('r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    datos[prefijo].append(row)
                    # Agregar la fecha (año y trimestre) al conjunto de fechas
                    if prefijo == "ind_":
                        fechas_ind.add((int(row['ANO4']), int(row['TRIMESTRE'])))
                    elif prefijo == "hog_":
                        fechas_hog.add((int(row['ANO4']), int(row['TRIMESTRE'])))
                except:
                    continue

        # Actualizar barra de progreso
        porcentaje = int(((i + 1) / total_archivos) * 100)
        progress_bar.progress((i + 1) / total_archivos)
        progress_text.markdown(f"**{porcentaje}% completado**")

    # Ocultar barra de progreso al finalizar
    progress_bar.empty()
    progress_text.empty()

    # Verificar cronología para individuos y hogares
    def verificar_cronologia(fechas):
        if not fechas:
            return "CRONOLOGÍA INCOMPLETA: No se encontraron fechas en los datos", []

        fechas_ordenadas = sorted(fechas)  # Ordenar las fechas por año y trimestre
        cronologia_completa = True
        faltantes = []

        # Verificar continuidad de las fechas
        for i in range(len(fechas_ordenadas) - 1):
            actual = fechas_ordenadas[i]
            siguiente = fechas_ordenadas[i + 1]

            # Calcular el siguiente trimestre esperado
            if actual[1] == 4:  # Si es el último trimestre del año
                esperado = (actual[0] + 1, 1)  # Primer trimestre del siguiente año
            else:
                esperado = (actual[0], actual[1] + 1)  # Siguiente trimestre del mismo año

            if siguiente != esperado:
                cronologia_completa = False
                faltantes.append(esperado)

        # Generar el mensaje de cronología
        if cronologia_completa:
            return "CRONOLOGÍA COMPLETA", []
        else:
            return "CRONOLOGÍA INCOMPLETA", faltantes

    # Verificar cronología para individuos
    cronologia_ind, faltantes_ind = verificar_cronologia(fechas_ind)
    # Verificar cronología para hogares
    cronologia_hog, faltantes_hog = verificar_cronologia(fechas_hog)

    # Generar mensaje final
    mensaje = ""
    if cronologia_ind == "CRONOLOGÍA COMPLETA":
        mensaje += "CRONOLOGÍA COMPLETA DE INDIVIDUOS\n"
    else:
        faltantes_ind_str = ", ".join([f"T{trim} - {ano}" for ano, trim in faltantes_ind])
        mensaje += f"CRONOLOGÍA INCOMPLETA DE INDIVIDUOS: Faltan datos para {faltantes_ind_str}\n"

    if cronologia_hog == "CRONOLOGÍA COMPLETA":
        mensaje += "CRONOLOGÍA COMPLETA DE HOGARES\n"
    else:
        faltantes_hog_str = ", ".join([f"T{trim} - {ano}" for ano, trim in faltantes_hog])
        mensaje += f"CRONOLOGÍA INCOMPLETA DE HOGARES: Faltan datos para {faltantes_hog_str}"

    return datos["ind_"], datos["hog_"], mensaje

# Función para detectar rango de fechas en múltiples archivos
def detectar_rango_fechas_combinada(directorio, prefijos):
    fechas = []
    try:
        archivos = []
        for prefijo in prefijos:
            archivos.extend([archivo for archivo in Path(directorio).iterdir() if archivo.name.startswith(prefijo)])
        
        if not archivos:
            st.warning(f"No se encontraron archivos con los prefijos {prefijos} en {directorio}")
            return None

        progress_bar = st.progress(0)
        progress_text = st.empty()
        total_archivos = len(archivos)

        for i, archivo in enumerate(archivos):
            with archivo.open('r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ano = int(row['ANO4'])
                    trimestre = int(row['TRIMESTRE'])
                    fechas.append((ano, trimestre))
                    break

            porcentaje = int(((i + 1) / total_archivos) * 100)
            progress_bar.progress((i + 1) / total_archivos)
            progress_text.markdown(f"**{porcentaje}% completado**")

        time.sleep(0.5)
        progress_bar.empty()
        progress_text.empty()

    except FileNotFoundError:
        st.error(f"Directorio no encontrado: {directorio}")
        return None

    if not fechas:
        return None

    min_ano, min_trim = min(fechas)
    max_ano, max_trim = max(fechas)

    return {
        'T_inicio': f"T{min_trim:1d}/{min_ano}", 'F_inicio': f"{min_ano}",
        'T_fin': f"T{max_trim:1d}/{max_ano}", 'F_fin': f"{max_ano}"
    }

def configurar_ruta_datos(ruta: str) -> None:
    """Configura la ruta donde se encuentran los archivos de datos"""
    global DATA_PATH
    DATA_PATH = ruta

def cargar_datos(tipo: str) -> List[Dict]:
    """
    Carga todos los archivos de individuos o hogares y los combina
    en una lista de diccionarios.

    Args -> tipo: 'individuo' o 'hogar'
    """

    datos_combinados = []
    total = 0
    data_path = Path(DATA_PATH)
    archivos_encontrados = False  # Bandera para verificar si se encontraron archivos

    for archivo in data_path.iterdir():
        if tipo in archivo.name.lower() and archivo.suffix == '.txt':
            archivos_encontrados = True
            with archivo.open('r') as f:
                lector = csv.DictReader(f, delimiter=';')
                datos_combinados.extend(list(lector))
                total+= 1
    
    print(f"Se han cargado {total} archivos de tipo '{tipo}' desde la ruta '{DATA_PATH}'.")
    if not archivos_encontrados:
        print(f"Error: No se encontraron archivos del tipo '{tipo}' en la ruta '{DATA_PATH}'.")
    
    return datos_combinados