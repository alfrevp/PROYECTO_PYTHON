# Proyecto Integrador – Python

Este proyecto fue desarrollado como trabajo integrador dentro del **Seminario de Python** de la Facultad de Informática de la UNLP, año 2025.  
El objetivo principal es procesar y analizar datos de encuestas de hogares mediante Python, implementando limpieza de datos, cálculos estadísticos y visualizaciones interactivas.
El código refleja la lógica y metodología utilizada en el trabajo integrador, sin incluir archivos pesados ni datos privados.
Para la descarga de los datasets, ir a "Microdatos y Documentos 2016-2025" en el siguiente link: https://www.indec.gob.ar/indec/web/Institucional-Indec-BasesDeDatos

////////////////////////////////

# Encuest.AR 📊

**Encuest.AR** es una aplicación interactiva desarrollada en Python con Streamlit para la visualización y análisis de datos de la Encuesta Permanente de Hogares (EPH) del INDEC. Este proyecto permite explorar información demográfica, laboral, educativa y habitacional de manera dinámica y accesible.

## Características principales

- **Carga de datos**: Permite cargar y verificar el rango temporal de los datos disponibles.
- **Consultas interactivas**: Incluye múltiples consultas predefinidas para analizar los datos de hogares e individuos.
- **Visualización de resultados**: Presenta los resultados en tablas y gráficos interactivos.
- **Filtros avanzados**: Filtra los datos por año, trimestre y otras características relevantes.

## Consultas Disponibles

* Consulta 1: Porcentaje de personas mayores a 6 años capaces e incapaces de leer y escribir por año (último trimestre).
* Consulta 2: Porcentaje de personas no nacidas en Argentina con nivel universitario o superior.
* Consulta 3: Año, trimestre y porcentaje con menor desocupación.
* Consulta 4: Ranking de los 5 aglomerados con mayor porcentaje de hogares con 2+ ocupantes con estudios universitarios o superiores finalizados.
* Consulta 5: Porcentaje de viviendas ocupadas por sus propietarios por aglomerado.
* Consulta 6: Aglomerado con mayor cantidad de viviendas con más de 2 ocupantes y sin baño.
* Consulta 7: Porcentaje de personas con nivel universitario o superior por aglomerado.
* Consulta 8: Regiones en orden descendente según porcentaje de inquilinos.
* Consulta 9: Tabla con cantidad de personas mayores de edad por nivel de estudios.
* Consulta 10: Comparación de porcentaje de personas mayores de edad con secundario incompleto entre dos aglomerados.
* Consulta 11: Aglomerados con mayor y menor porcentaje de viviendas de "Material precario" en el último trimestre del año seleccionado.
* Consulta 12: Porcentaje de jubilados que viven en viviendas con condición insuficiente por aglomerado (último trimestre).
* Consulta 13: Cantidad de personas con nivel universitario que viven en viviendas con condición insuficiente (último trimestre del año seleccionado).

## Estructura del proyecto

```
Integrador
| README.md
| requisitos.txt
| LICENSE
|
+---datos
| |---procesado
|
+---Notebooks
| Prueba.ipynb
| Res-hogar.ipynb
| Res-individuo.ipynb
|
---src
| aglomerados_coordenadas.json
| app.py
| consultas.py
| demografia_utils.py
| educacion_utils.py
| interfacesConsultas.py
| utils.py
| mapeos.py
|
+---pages
| 2_Carga_De_Datos.py
| 3_Caracteristicas_Demograficas.py
| 4_Caracteristicas_De_Vivienda.py
| 5_Actividad_Y_Empleo.py
| 6_Educacion.py
| 7_Ingresos.py
|
---recursos
| aglomerados_coordenadas.json
| canasta.csv
```
## Requisitos

- Python 3.8 o superior
- Librerías especificadas en `requisitos.txt`

## Instalación

1. Clonar este repositorio:
   ```
   git clone https://gitlab.catedras.linti.unlp.edu.ar/python-2025/proyectos/grupo29/code
   cd Integrador
   ```
2. Crear un entorno virtual y activarlo
   ```
   python -m venv .venv
   .venv\Scripts\activate  # En Windows
   source .venv/bin/activate  # En Linux/Mac
   ```

3. Instalar dependencias
   ```
   pip install -r requisitos.txt
   ```
## Archivos necesarios

*Archivos de entrada*
* **Archivos de datos crudos:** Los archivos deben estar en la carpeta `datos/` y seguir el formato esperado (Los nombres de los archivos son los que tienen "por defecto" al extraerlos desde los comprimidos .zip al descargar la información desde la página)
* * usu_hogar_T[...].txt
* * usu_individual_T[...].txt

*Archivos generados*
* **Archivos procesados:** Los cuadernos Jupyter generan archivos procesados en la carpeta `datos/procesado/` con los prefijos ind_AXXXX_TY y ind_AXXXX_TY. Siendo XXXX el año e Y el trimestre.

## GUIA DE USO (seguir los pasos en orden para el correcto funcionamiento)

1. Procesamiento de datos con Jupyter Notebooks
Antes de utilizar la aplicación, es necesario procesar los datos utilizando los cuadernos Jupyter disponibles en la carpeta Notebooks/:

**Res-individuo.ipynb:** Procesa los datos de individuos, generando archivos procesados en la carpeta `datos/procesado/`.
**Res-hogar.ipynb:** Procesa los datos de hogares, generando archivos procesados en la carpeta `datos/procesado/`.

*Para ejecutar los cuadernos:*
* 1. Abrir una terminal e ir hasta la carpeta `Notebooks/`.
* 2. Iniciar Jupyter Notebook:
   ```
   jupyter notebook
   ```
* 3. Abrir y ejecutar los cuadernos `Res-individuo.ypynb` y `Res-hogar.ypynb` en orden.

2. Ejecutar la aplicación
   ```
   streamlit run src/app.py
   ```
3. Ingrsar a la página de **Carga de Datos**, para la primer carga automática de archivos. En caso de actualizar el contenido de la carpeta de datos, presionar el botón "🔄 Actualizar archivos" para cargar los nuevos.

 **IMPORTANTE: es necesario cargar los archivos en la pagina 2 para poder utilizar las siguientes

4. En el menu lateral, puede cambiar entre las diferentes paginas para la visualizacion de datos:
   * Caracteristicas Demograficas
   * Características de Vivienda
   * Actividad y Empleo
   * Educación
   * Ingresos

## NOTA SOBRE FUNCIONAMIENTO
* Al pasar entre las diferentes páginas de las tablas (pagina 2), es probable que sea necesario presionar los botones 2 veces.
* Dentro de la carpeta src/recursos deben estar los archivos .csv de la canasta básica (puede tener cualquier nombre siempre y cuando contenga el string "canasta" en él) y coordenadas de los aglomerados
