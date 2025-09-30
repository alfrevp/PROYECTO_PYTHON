# empleo_utils.py
import pandas as pd


def calcular_estudios_desocupados(df):
    df['PONDERA'] = pd.to_numeric(df['PONDERA'], errors='coerce')
    df = df.dropna(subset=['PONDERA'])
    df_filtrado = df[(df['ESTADO'] == '2')]
    if df_filtrado.empty:
        return None
    return (
        df_filtrado.groupby('NIVEL_ED_str')['PONDERA']
        .sum()
        .sort_values(ascending=False)
    )


def calcular_tasas_empleo_desempleo(df):
    df = df[df['ESTADO'].isin(['1', '2'])]
    df['PONDERA'] = pd.to_numeric(df['PONDERA'], errors='coerce')
    df = df.dropna(subset=['PONDERA'])
    resumen = (
        df.groupby(['ANO4', 'TRIMESTRE', 'ESTADO'])['PONDERA']
        .sum(min_count=1)
        .unstack(fill_value=0)
    )
    ocupados = resumen.get('1', pd.Series(0, index=resumen.index))
    desocupados = resumen.get('2', pd.Series(0, index=resumen.index))
    total_activos = ocupados + desocupados
    tasas_empleo = (ocupados / total_activos * 100).fillna(0)
    tasas_desempleo = (desocupados / total_activos * 100).fillna(0)
    return tasas_empleo, tasas_desempleo, resumen.index


def calcular_distribucion_empleo(df):
    df = df[df['ESTADO'] == '1']
    df['PONDERA'] = pd.to_numeric(df['PONDERA'], errors='coerce')
    df = df.dropna(subset=['PONDERA'])
    resultados = []
    for aglo, grupo in df.groupby('AGLOMERADO'):
        # Sumar ponderaciones por tipo de empleo
        total = grupo['PONDERA'].sum()
        estatal = grupo.loc[grupo['PP04A'] == '1', 'PONDERA'].sum()
        privado = grupo.loc[grupo['PP04A'] == '2', 'PONDERA'].sum()
        otro = grupo.loc[grupo['PP04A'] == '3', 'PONDERA'].sum()
        #Porcentajes
        estatal_pct = (estatal / total * 100) if total > 0 else 0
        privado_pct = (privado / total * 100) if total > 0 else 0
        otro_pct = (otro / total * 100) if total > 0 else 0
        resultados.append({
            'Aglomerado': aglo,
            'Total ocupados': total,
            'Estatal (%)': f"{estatal_pct:.2f}%",
            'Privado (%)': f"{privado_pct:.2f}%",
            'Otro (%)': f"{otro_pct:.2f}%"
        })
    return pd.DataFrame(resultados)


def calcular_variacion_mapa(df_min, df_max, coordenadas, opcion_tasa):
    aglomerados = pd.concat([df_min, df_max])['AGLOMERADO'].unique()
    resultados = []
    for aglo in aglomerados:
        ini = df_min[df_min['AGLOMERADO'] == aglo]
        fin = df_max[df_max['AGLOMERADO'] == aglo]
        for df in [ini, fin]:
            df['PONDERA'] = pd.to_numeric(df['PONDERA'], errors='coerce')
            df.dropna(subset=['PONDERA'], inplace=True)
        o_ini = ini.loc[ini['ESTADO'] == '1', 'PONDERA'].sum()
        d_ini = ini.loc[ini['ESTADO'] == '2', 'PONDERA'].sum()
        t_ini = o_ini + d_ini
        o_fin = fin.loc[fin['ESTADO'] == '1', 'PONDERA'].sum()
        d_fin = fin.loc[fin['ESTADO'] == '2', 'PONDERA'].sum()
        t_fin = o_fin + d_fin
        tasa_ini = (o_ini / t_ini * 100) if opcion_tasa == 'Tasa de empleo' else (d_ini / t_ini * 100)
        tasa_fin = (o_fin / t_fin * 100) if opcion_tasa == 'Tasa de empleo' else (d_fin / t_fin * 100)
        variacion = tasa_fin - tasa_ini
        coords = coordenadas.get(str(aglo), {}).get('coordenadas', [0, 0])
        resultados.append({
            'aglomerado': aglo,
            'variacion': variacion,
            'coordenadas': coords
        })
    return resultados
