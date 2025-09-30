import pandas as pd
import matplotlib.pyplot as plt

def obtener_anios_trimestres_disponibles(df):
    df["ANO4"] = pd.to_numeric(df["ANO4"], errors="coerce")
    df["TRIMESTRE"] = pd.to_numeric(df["TRIMESTRE"], errors="coerce")
    anios = sorted(df["ANO4"].dropna().unique().astype(int))
    trimestres = sorted(df["TRIMESTRE"].dropna().unique().astype(int))
    return anios, trimestres

def filtrar_por_anio_trimestre(df, anio, trimestre):
    df["ANO4"] = pd.to_numeric(df["ANO4"], errors="coerce")
    df["TRIMESTRE"] = pd.to_numeric(df["TRIMESTRE"], errors="coerce")
    return df[(df["ANO4"] == anio) & (df["TRIMESTRE"] == trimestre)]

# punto 1
def graf_distribucion_edad_sexo(df, anio, trimestre):
    """ Genera un grafico de barras para mostrar la distribucion de sexo
    por edades (de 10 en 10). """
    # filtrar datos
    df_filtrado = filtrar_por_anio_trimestre(df, anio, trimestre)
    if df_filtrado.empty:
        return None, "No hay datos disponibles para el año y trimestre seleccionados."

    bins = list(range(0, 100, 10)) + [150]
    labels = [f"{i}-{i+9}" for i in range(0, 90, 10)] + ["90+"]

    df_filtrado = df_filtrado.copy()    # para evitar SettingWithCopyWarning
    df_filtrado["grupo_edad"] = pd.cut(df_filtrado["CH06"], bins=bins, labels=labels, right=False)
    df_filtrado["sexo"] = df_filtrado["CH04"].map({"1": "Varón", "2": "Mujer"}).fillna("Otro")

    tabla = df_filtrado.groupby(["grupo_edad", "sexo"], observed=True)["PONDERA"].sum().unstack(fill_value=0)    # observed para evitar FutureWarning de pandas

    fig, ax = plt.subplots(figsize=(10, 6))
    tabla.plot(kind="bar", ax=ax, color=["#d62728", "#1f77b4"])
    ax.set_title(f"Distribución por grupos de edad y sexo - {anio} T{trimestre}")
    ax.set_xlabel("Grupo de edad")
    ax.set_ylabel("Población estimada (millones)")
    ax.legend(title="Sexo")

    # prueba mostrar num sobre cada barra
    for contenedor in ax.containers:
        labels = [f"{v/1e6:.1f}M" if v > 0 else "" for v in contenedor.datavalues]
        ax.bar_label(contenedor, labels=labels, label_type="edge", fontsize=8, padding=2)

    return fig, None

# punto 2
def edad_promedio_por_aglomerado(df):
    """ Calcula la edad promedio por aglomerado para el último año y trimestre disponibles.
    Retorna un DataFrame con columnas: aglomerado, edad_promedio. """
    ultimo_anio = df["ANO4"].max()
    ultimo_trimestre = df[df["ANO4"] == ultimo_anio]["TRIMESTRE"].max()

    df_filtrado = df[(df["ANO4"] == ultimo_anio) & (df["TRIMESTRE"] == ultimo_trimestre)]

    resultado = df_filtrado.groupby("AGLOMERADO").apply(
        lambda x: (x["CH06"] * x["PONDERA"]).sum() / x["PONDERA"].sum()
    ).reset_index(name="Edad Promedio")

    resultado["Edad Promedio"] = resultado["Edad Promedio"].round(2)

    resultado = resultado[["AGLOMERADO", "Edad Promedio"]]

    return resultado, ultimo_anio, ultimo_trimestre


# punto 4

def media_mediana_edad_por_anio_trimestre(df):
    """ Calcula la media y mediana de edad por año y trimestre.
    Retorna DataFrame con columnas año, trimestre, media y mediana de edad. """
    df = df.copy()
    
    grouped = df.groupby(['ANO4', 'TRIMESTRE'])
    
    media = grouped.apply(lambda x: (x['CH06'] * x['PONDERA']).sum() / x['PONDERA'].sum())
    media.name = 'media_edad'
    
    # para mediana: ordenar edades, acumular personas y buscar valor donde la suma alcanza 50%
    def mediana_ponderada(subdf):
        subdf_sorted = subdf.sort_values('CH06')
        cumsum = subdf_sorted['PONDERA'].cumsum()
        cutoff = subdf_sorted['PONDERA'].sum() / 2
        mediana = subdf_sorted.loc[cumsum >= cutoff, 'CH06'].iloc[0]
        return mediana
    
    mediana = grouped.apply(mediana_ponderada)
    mediana.name = 'mediana_edad'
    
    result = pd.concat([media, mediana], axis=1).reset_index()
    
    #  redondear
    result['media_edad'] = result['media_edad'].round(2)
    result['mediana_edad'] = result['mediana_edad'].round(2)

    # asegurar orden en que se muestra año/trimestre
    result = result.sort_values(['ANO4', 'TRIMESTRE']).reset_index(drop=True)

    result = result.rename(columns={
        'ANO4': 'Año',
        'TRIMESTRE': 'Trimestre',
        'media_edad': 'Media de Edad',
        'mediana_edad': 'Mediana de Edad'
    })
    
    return result


# punto 3
# punto 3
def evolucion_dependencia_demografica(df, cod_aglo):
    """
    Calcula la evolución de la dependencia demográfica para un aglomerado dado.
    Devuelve un DataFrame con columnas año, trimestre y dependencia demográfica.
    """
    df = df.copy()
    
    # filtrar por aglomerado
    df = df[df["AGLOMERADO"] == cod_aglo]

    # clasificar edades
    df["grupo_etario"] = pd.cut(df["CH06"], bins=[-1, 14, 64, float('inf')], labels=["dependiente_joven", "activa", "dependiente_mayor"])
    
    # agrupar por año, trimestre y grupo
    grupal = df.groupby(["ANO4", "TRIMESTRE", "grupo_etario"], observed=True)["PONDERA"].sum().unstack(fill_value=0).reset_index()   # oberved para evitar FutureWarning

    # calcular dependencia
    grupal["Dependencia Demográfica"] = ((grupal["dependiente_joven"] + grupal["dependiente_mayor"]) / grupal["activa"]) * 100

    # eenombrar columnas para presentación
    grupal = grupal.rename(columns={"ANO4": "Año", "TRIMESTRE": "Trimestre"})
    resultado = grupal[["Año", "Trimestre", "Dependencia Demográfica"]].sort_values(["Año", "Trimestre"]).reset_index(drop=True)

    # eedondear
    resultado["Dependencia Demográfica"] = resultado["Dependencia Demográfica"].round(2)

    return resultado