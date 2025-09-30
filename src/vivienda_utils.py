import pandas as pd

def calcular_tipo_vivienda(df_filtrado):
    df_filtrado['PONDERA'] = pd.to_numeric(df_filtrado['PONDERA'], errors='coerce')
    df_filtrado = df_filtrado.dropna(subset=['PONDERA'])
    tipo_vivienda = (
        df_filtrado
        .groupby('IV1')['PONDERA']
        .sum()
        .sort_values(ascending=False)
    )
    tipo_vivienda_pct = tipo_vivienda / tipo_vivienda.sum() * 100
    etiquetas = [f"{nombre}: {porc:.1f}%" for nombre, porc in zip(tipo_vivienda_pct.index, tipo_vivienda_pct.values)]
    return tipo_vivienda_pct, etiquetas

def calcular_material_pisos(df_filtrado):
    df_filtrado['PONDERA'] = pd.to_numeric(df_filtrado['PONDERA'], errors='coerce')
    df_filtrado = df_filtrado.dropna(subset=['PONDERA'])
    agrupado = df_filtrado.groupby(['AGLOMERADO', 'IV3'])['PONDERA'].sum().reset_index()
    idx_max = agrupado.groupby('AGLOMERADO')['PONDERA'].idxmax()
    material_pisos = agrupado.loc[idx_max, ['AGLOMERADO', 'IV3']].copy()
    tabla = material_pisos.rename(columns={'IV3': 'Material predominante'})
    return tabla

def calcular_banio(df_filtrado):
    df_filtrado['PONDERA'] = pd.to_numeric(df_filtrado['PONDERA'], errors='coerce')
    df_filtrado = df_filtrado.dropna(subset=['PONDERA'])
    resultados = []
    for aglo in df_filtrado['AGLOMERADO'].dropna().unique():
        viviendas_aglo = df_filtrado[df_filtrado['AGLOMERADO'] == aglo]
        total_ponderado = viviendas_aglo['PONDERA'].sum()
        con_banio_dentro = viviendas_aglo[(viviendas_aglo['IV8'] == '1') & (viviendas_aglo['IV9'] == '1')]
        con_banio_ponderado = con_banio_dentro['PONDERA'].sum()
        porcentaje = (con_banio_ponderado / total_ponderado) * 100 if total_ponderado > 0 else 0
        resultados.append({
            'Aglomerado': aglo,
            'Porcentaje con baño dentro del hogar': f"{porcentaje:.2f}%"
        })
    return resultados

def calcular_evolucion_tenencia(df_filtrado):
    aglomerados = sorted(df_filtrado['AGLOMERADO'].unique())
    tipos_tenencia = sorted(df_filtrado['II7'].dropna().unique())
    return df_filtrado, aglomerados, tipos_tenencia

def calcular_viviendas_villa(df_filtrado):
    df_filtrado['PONDERA'] = pd.to_numeric(df_filtrado['PONDERA'], errors='coerce')
    df_filtrado = df_filtrado.dropna(subset=['PONDERA'])
    resultados = []
    for aglo in df_filtrado['AGLOMERADO'].dropna().unique():
        datos_aglo = df_filtrado[df_filtrado['AGLOMERADO'] == aglo]
        total_viviendas = datos_aglo['PONDERA'].sum()
        viviendas_villa = datos_aglo[datos_aglo['IV12_3'] == '1']['PONDERA'].sum()
        porcentaje = (viviendas_villa / total_viviendas) * 100 if total_viviendas > 0 else 0
        resultados.append({
            'Aglomerado': aglo,
            'Cantidad en villa': int(round(viviendas_villa)),
            'Porcentaje': f"{porcentaje:.2f}%"
        })
    return pd.DataFrame(resultados).sort_values(by='Cantidad en villa', ascending=False)

def calcular_habitabilidad(df_filtrado):
    habitabilidad = df_filtrado.groupby(['AGLOMERADO', 'CONDICION_DE_HABITABILIDAD']).size().unstack().fillna(0)
    habitabilidad_pct = habitabilidad.div(habitabilidad.sum(axis=1), axis=0) * 100
    habitabilidad_pct = habitabilidad_pct.fillna(0)
    habitabilidad_pct_fmt = habitabilidad_pct.applymap(lambda x: f"{x:.2f}%")
    return habitabilidad_pct_fmt.reset_index(), habitabilidad_pct.reset_index()