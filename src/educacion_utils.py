import pandas as pd
import numpy as np
from mapeos import MAPEO_NIVEL

# punto 1
def contar_personas_por_nivel(df_ind, anio):
            
    df_filtrado = df_ind[df_ind["ANO4"] == anio].copy()
    df_filtrado["Nivel educativo"] = df_filtrado["NIVEL_ED"].astype(str).map(MAPEO_NIVEL).fillna("Otro/no definido")
    
    resultado = df_filtrado.groupby("Nivel educativo")["PONDERA"].sum().reset_index()
    resultado = resultado.rename(columns={"PONDERA": "Cantidad"})
    resultado = resultado.sort_values(by="Cantidad", ascending=False)
    
    return resultado


# punto 2
def nivel_mas_comun_por_grupo_edad(df_ind, grupos_edad):
    df_ind = df_ind.copy()
    df_ind["NIVEL_ED"] = pd.to_numeric(df_ind["NIVEL_ED"], errors="coerce").astype("Int64")
    df_ind["Nivel educativo"] = df_ind["NIVEL_ED"].map(MAPEO_NIVEL).fillna("Otro/no definido")

    resultados = []

    for (edad_min, edad_max) in grupos_edad:
        if edad_max is None:
            df_grupo = df_ind[df_ind["CH06"] >= edad_min]
            grupo_nombre = f"{edad_min}+"
        else:
            df_grupo = df_ind[(df_ind["CH06"] >= edad_min) & (df_ind["CH06"] < edad_max)]
            grupo_nombre = f"{edad_min}-{edad_max}"

        if df_grupo.empty:
            resultados.append({"Grupo etario": grupo_nombre, "Nivel más común": "Sin datos"})
            continue

        suma_niveles = df_grupo.groupby("Nivel educativo")["PONDERA"].sum()
        nivel_top = suma_niveles.idxmax()
        resultados.append({"Grupo etario": grupo_nombre, "Nivel más común": nivel_top})

    return pd.DataFrame(resultados)


# punto 4
def porcentaje_alfabetizacion_por_anio(df_ind):
    df = df_ind.copy()
    df = df[df["CH06"] > 6]  # mayores de 6

    total = df.groupby("ANO4")["PONDERA"].sum()
    sabe = df[df["CH09"] == 1].groupby("ANO4")["PONDERA"].sum()
    no_sabe = df[df["CH09"] == 2].groupby("ANO4")["PONDERA"].sum()

    agrupado = pd.DataFrame({
        "Total": total,
        "Sabe leer/escribir": sabe,
        "No sabe leer/escribir": no_sabe
    }).reset_index()

    agrupado.replace(0, np.nan, inplace=True)

    agrupado["Sabe"] = (agrupado["Sabe leer/escribir"] / agrupado["Total"] * 100).round(2)
    agrupado["No sabe"] = (agrupado["No sabe leer/escribir"] / agrupado["Total"] * 100).round(2)

    return agrupado[["ANO4", "Sabe", "No sabe"]].sort_values("ANO4")

