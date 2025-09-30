# Código para implementar las consultas de la Sección B

def consulta1(datos_individuos):
    """
    Porcentaje de personas mayores a 6 años capaces e incapaces de leer y escribir por año (último trimestre)
    """
    resultados = {}

    # Filtrar datos del último trimestre (trimestre "4")
    datos_ultimo_trimestre = [ind for ind in datos_individuos if ind['TRIMESTRE'] == '4' and int(ind['CH06']) > 6]

    # Agrupar por año y calcular totales
    grupos = {}
    for ind in datos_ultimo_trimestre:
        ano = ind['ANO4']
        if ano not in grupos:
            grupos[ano] = {'total': 0, 'lee_escribe': 0}
        
        grupos[ano]['total'] += int(ind['PONDERA'])
        if ind['CH09'] == '1':  # Sí sabe leer y escribir
            grupos[ano]['lee_escribe'] += int(ind['PONDERA'])

    # Calcular porcentajes para cada año
    for ano, valores in grupos.items():
        total = valores['total']
        lee_escribe = valores['lee_escribe']
        resultados[ano] = {
            'trimestre': '4',
            'porcentaje_lee_escribe': (lee_escribe / total) * 100 if total > 0 else 0,
            'porcentaje_no_lee_escribe': 100 - (lee_escribe / total) * 100 if total > 0 else 0
        }

    # Ordenar por año
    return dict(sorted(resultados.items()))

def consulta2(datos_individuos, ano, trimestre): 
    """
    Porcentaje de personas no nacidas en Argentina con nivel universitario o superior
    """
    total_extranjeros = 0
    extranjeros_universitarios = 0
    
    for ind in datos_individuos:
        if ind['ANO4'] == str(ano) and ind['TRIMESTRE'] == str(trimestre):            # NOTA: ano y trimestre a string porque siempre retornaba 0
            if ind['CH15'] == '4' or ind['CH15'] == '5':  # No nacido en Argentina
                total_extranjeros += int(ind['PONDERA'])
                if ind['UNIVERSITARIO'] == '1':  # universitario completo
                    extranjeros_universitarios += int(ind['PONDERA'])

    return (extranjeros_universitarios / total_extranjeros) * 100 if total_extranjeros > 0 else 0


def consulta3(datos_individuos):
    """
    Año, trimestre y porcentaje con menor desocupación
    """
    desocupacion_por_periodo = {}
    
    for ind in datos_individuos:
        key = (ind['ANO4'], ind['TRIMESTRE'])
        if key not in desocupacion_por_periodo:
            desocupacion_por_periodo[key] = {'total': 0, 'desocupados': 0}
        
        desocupacion_por_periodo[key]['total'] += int(ind['PONDERA'])
        if ind['ESTADO'] == '2':  # Desocupado
            desocupacion_por_periodo[key]['desocupados'] += int(ind['PONDERA'])
    
    # Calcular porcentaje de desocupación para cada período
    porcentajes = {}
    for periodo, valores in desocupacion_por_periodo.items():
        porcentajes[periodo] = (valores['desocupados'] / valores['total']) * 100 if valores['total'] > 0 else 0
    
    # Encontrar el período con menor desocupación
    periodo_menor_desocupacion, menor_porcentaje = min(porcentajes.items(), key=lambda x: x[1])
    ano, trimestre = periodo_menor_desocupacion
    
    return ano, trimestre, menor_porcentaje

def consulta4(datos_hogares, datos_individuos):
    """
    Ranking de los 5 aglomerados con mayor porcentaje de hogares con 2+ ocupantes 
    con estudios universitarios o superiores finalizados (archivos más recientes)
    """
    # Encontrar el período más reciente
    max_ano = max(ind['ANO4'] for ind in datos_individuos)
    max_trimestre = max(ind['TRIMESTRE'] for ind in datos_individuos if ind['ANO4'] == max_ano)
    
    # Procesar individuos universitarios
    universitarios_por_hogar = {}
    for ind in datos_individuos:
        if ind['ANO4'] == max_ano and ind['TRIMESTRE'] == max_trimestre:
            if ind['NIVEL_ED'] == '6':  # Superior o universitario completo
                if ind['CODUSU'] not in universitarios_por_hogar:
                    universitarios_por_hogar[ind['CODUSU']] = 0
                universitarios_por_hogar[ind['CODUSU']] += 1
    
    # Procesar hogares con 2+ universitarios
    aglomerados = {}
    for hogar in datos_hogares:
        if hogar['ANO4'] == max_ano and hogar['TRIMESTRE'] == max_trimestre:
            aglo = hogar['AGLOMERADO']
            if aglo not in aglomerados:
                aglomerados[aglo] = {'total_hogares': 0, 'hogares_2mas_uni': 0}
            
            aglomerados[aglo]['total_hogares'] += 1
            if hogar['CODUSU'] in universitarios_por_hogar and universitarios_por_hogar[hogar['CODUSU']] >= 2:
                aglomerados[aglo]['hogares_2mas_uni'] += 1
    
    # Calcular porcentajes
    ranking = []
    for aglo, valores in aglomerados.items():
        porcentaje = (valores['hogares_2mas_uni'] / valores['total_hogares']) * 100 if valores['total_hogares'] > 0 else 0
        ranking.append((aglo, porcentaje))
    
    # Ordenar y devolver top 5
    return sorted(ranking, key=lambda x: x[1], reverse=True)[:5]

def consulta5(datos_hogares):
    """
    Porcentaje de viviendas ocupadas por sus propietarios por aglomerado
    """
    resultados = {}
    
    for hogar in datos_hogares:
        aglo = hogar['AGLOMERADO']
        if aglo not in resultados:
            resultados[aglo] = {'total': 0, 'propietarios': 0}
        
        resultados[aglo]['total'] += 1
        if hogar['II7'] in ('1', '2'):  # Propietario de la vivienda y del terreno
            resultados[aglo]['propietarios'] += 1
    
    # Calcular porcentajes
    porcentajes = {}
    for aglo, valores in resultados.items():
        porcentajes[aglo] = (valores['propietarios'] / valores['total']) * 100 if valores['total'] > 0 else 0
    
    return porcentajes

def consulta6(datos_hogares):
    """
    Aglomerado con mayor cantidad de viviendas con más de 2 ocupantes y sin baño
    """
    conteo = {}
    
    for hogar in datos_hogares:
        if int(hogar['IX_TOT']) > 2 and hogar['IV8'] == '2':  # Más de 2 ocupantes y sin baño
            aglo = hogar['AGLOMERADO']
            conteo[aglo] = conteo.get(aglo, 0) + 1
    
    if not conteo:
        return None, 0
    
    max_aglo = max(conteo.items(), key=lambda x: x[1])
    return max_aglo

def consulta7(datos_individuos):
    """
    Porcentaje de personas con nivel universitario o superior por aglomerado
    """
    resultados = {}
    
    for ind in datos_individuos:
        aglo = ind['AGLOMERADO']
        if aglo not in resultados:
            resultados[aglo] = {'total': 0, 'universitarios': 0}
        
        resultados[aglo]['total'] += int(ind['PONDERA'])
        if ind['NIVEL_ED'] == '6':  # Superior o universitario completo
            resultados[aglo]['universitarios'] += int(ind['PONDERA'])
    
    # Calcular porcentajes
    porcentajes = {}
    for aglo, valores in resultados.items():
        porcentajes[aglo] = (valores['universitarios'] / valores['total']) * 100 if valores['total'] > 0 else 0
    
    return porcentajes

def consulta8(datos_hogares):
    """
    Regiones en orden descendente según porcentaje de inquilinos
    """
    regiones = {}
    
    for hogar in datos_hogares:
        region = hogar['REGION']
        if region not in regiones:
            regiones[region] = {'total': 0, 'inquilinos': 0}
        
        regiones[region]['total'] += 1
        if hogar['II7'] == '3':  # Inquilino
            regiones[region]['inquilinos'] += 1
    
    # Calcular porcentajes y ordenar
    porcentajes = []
    for region, valores in regiones.items():
        porcentaje = (valores['inquilinos'] / valores['total']) * 100 if valores['total'] > 0 else 0
        porcentajes.append((region, porcentaje))
    
    return sorted(porcentajes, key=lambda x: x[1], reverse=True)

def consulta9(datos_individuos, aglomerado):
    """
    Tabla con cantidad de personas mayores de edad por nivel de estudios
    """
    resultados = {}
    
    for ind in datos_individuos:
        if int(ind['AGLOMERADO']) == aglomerado and int(ind['CH06']) > 17:  # Mayores de edad
            key = (ind['ANO4'], ind['TRIMESTRE'])
            if key not in resultados:
                resultados[key] = {
                    'Primario incompleto': 0,
                    'Primario completo': 0,
                    'Secundario incompleto': 0,
                    'Secundario completo': 0,
                    'Superior|universitario incompleto': 0,
                    'Superior|universitario completo': 0,
                    'Sin instrucción': 0,
                    'No sabe|No responde': 0,
                }
            
            nivel = ind['NIVEL_ED_str']
            if nivel in resultados[key]:
                resultados[key][nivel] += int(ind['PONDERA'])
            elif "Superior" in nivel or "universitario" in nivel:
                resultados[key]['Superior o universitario'] += int(ind['PONDERA'])
    
    # Convertir a lista ordenada
    tabla = []
    for (ano, trimestre), niveles in sorted(resultados.items()):
        fila = {
            'Año': ano,
            'Trimestre': trimestre,
            **niveles
        }
        tabla.append(fila)
    
    return tabla

def consulta10(datos_individuos, aglo_a, aglo_b):
    """
    Tabla con porcentaje de personas mayores de edad con secundario incompleto
    para dos aglomerados seleccionados
    """
    resultados = {}
    
    for ind in datos_individuos:
        if int(ind['CH06']) > 17:  # Mayores de edad
            aglo = int(ind['AGLOMERADO'])
            if aglo in (aglo_a, aglo_b):
                key = (ind['ANO4'], ind['TRIMESTRE'])
                if key not in resultados:
                    resultados[key] = {
                        aglo_a: {'total': 0, 'sec_incompleto': 0},
                        aglo_b: {'total': 0, 'sec_incompleto': 0}
                    }
                
                resultados[key][aglo]['total'] += int(ind['PONDERA'])
                if ind['NIVEL_ED_str'] == 'Secundario incompleto':
                    resultados[key][aglo]['sec_incompleto'] += int(ind['PONDERA'])
    
    # Calcular porcentajes y preparar tabla
    tabla = []
    for (ano, trimestre), valores in sorted(resultados.items()):
        porcentaje_a = (valores[aglo_a]['sec_incompleto'] / valores[aglo_a]['total']) * 100 if valores[aglo_a]['total'] > 0 else 0
        porcentaje_b = (valores[aglo_b]['sec_incompleto'] / valores[aglo_b]['total']) * 100 if valores[aglo_b]['total'] > 0 else 0
        
        fila = {
            'Año': ano,
            'Trimestre': trimestre,
            aglo_a: f"{porcentaje_a:.1f}%",
            aglo_b: f"{porcentaje_b:.1f}%"
        }
        tabla.append(fila)
    
    return tabla

def consulta11(datos_hogares, ano):
    """
    Aglomerados con mayor y menor porcentaje de viviendas de "Material precario"
    en el último trimestre del año seleccionado
    """
    # Encontrar el último trimestre presente en el año seleccionado
    trimestres = [hogar['TRIMESTRE'] for hogar in datos_hogares if int(hogar['ANO4']) == ano]
    if not trimestres:
        return None, None  # No hay datos para el año seleccionado

    ultimo_trimestre = max(trimestres)

    # Procesar datos para el último trimestre encontrado
    aglomerados = {}
    for hogar in datos_hogares:
        if int(hogar['ANO4']) == ano and hogar['TRIMESTRE'] == ultimo_trimestre:
            aglo = hogar['AGLOMERADO']
            if aglo not in aglomerados:
                aglomerados[aglo] = {'total': 0, 'precario': 0}
            
            aglomerados[aglo]['total'] += 1
            if hogar['MATERIAL_TECHUMBRE'] == 'Material precario':
                aglomerados[aglo]['precario'] += 1
    
    # Calcular porcentajes
    porcentajes = {}
    for aglo, valores in aglomerados.items():
        porcentajes[aglo] = (valores['precario'] / valores['total']) * 100 if valores['total'] > 0 else 0
    
    if not porcentajes:
        return None, None  # No hay datos para calcular porcentajes

    # Encontrar aglomerados con mayor y menor porcentaje
    max_aglo = max(porcentajes.items(), key=lambda x: x[1])
    min_aglo = min(porcentajes.items(), key=lambda x: x[1])
    
    return max_aglo, min_aglo

def consulta12(datos_hogares, datos_individuos):            # REVISAR: devuelve 0 para todos -> revisar cuantos "insuficiente" hay en dataset (alfre)
    """
    Porcentaje de jubilados que viven en viviendas con condición insuficiente
    por aglomerado (último trimestre)
    """
    # Encontrar el período más reciente
    max_ano = max(ind['ANO4'] for ind in datos_individuos)
    max_trimestre = max(ind['TRIMESTRE'] for ind in datos_individuos if ind['ANO4'] == max_ano)
    
    # Identificar jubilados
    jubilados = set()
    for ind in datos_individuos:
        if ind['ANO4'] == max_ano and ind['TRIMESTRE'] == max_trimestre:
            if ind['CAT_INAC'] == '1': # Jubilado/Pensionado
                jubilados.add(ind['CODUSU'])
    
    # Procesar hogares con condición insuficiente
    resultados = {}
    for hogar in datos_hogares:
        if hogar['ANO4'] == max_ano and hogar['TRIMESTRE'] == max_trimestre:
            aglo = hogar['AGLOMERADO']
            if aglo not in resultados:
                resultados[aglo] = {'total_jubilados': 0, 'jubilados_insuficiente': 0}

            if hogar['CODUSU'] in jubilados:
                resultados[aglo]['total_jubilados'] += 1
                if hogar['CONDICION_DE_HABITABILIDAD'] == 'Insuficiente':
                    resultados[aglo]['jubilados_insuficiente'] += 1
    
    # Calcular porcentajes
    porcentajes = {}
    for aglo, valores in resultados.items():
        porcentajes[aglo] = (valores['jubilados_insuficiente'] / valores['total_jubilados']) * 100 if valores['total_jubilados'] > 0 else 0
    
    return porcentajes, max_ano, max_trimestre

def consulta13(datos_hogares, datos_individuos, ano):            # REVISAR: devuelve 0 para todos -> parece que en el dataset pocos cumplen condicion "insuficiente"  (alfre)
    """
    Cantidad de personas con nivel universitario que viven en viviendas con
    condición insuficiente (último trimestre del año seleccionado)
    """
    # Encontrar el último trimestre para el año dado
    ultimo_trimestre = max([h['TRIMESTRE'] for h in datos_hogares if int(h['ANO4']) == ano])       # int(h['TRIMESTRE']) ?   (alfre)
    
    # Identificar viviendas con condición insuficiente
    hogares_insuficientes = set()
    for hogar in datos_hogares:
        if int(hogar['ANO4']) == ano and hogar['TRIMESTRE'] == ultimo_trimestre:
            if hogar['CONDICION_DE_HABITABILIDAD'] == 'Insuficiente':
                hogares_insuficientes.add(hogar['CODUSU'])
    
    # Contar universitarios en esas viviendas
    total = 0
    for ind in datos_individuos:
        if int(ind['ANO4']) == ano and ind['TRIMESTRE'] == ultimo_trimestre:
            if ind['CODUSU'] in hogares_insuficientes:
                if ind['NIVEL_ED'] in ('5','6'):  # Superior o universitario completo
                    total += int(ind['PONDERA'])
    return total