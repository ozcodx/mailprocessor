import pandas as pd
import numpy as np

# Diccionario de categorías con sus IDs principales
# Los IDs más cortos definen las categorías principales
CATEGORIAS = {
    "animales": ["1445"],  # Semovientes
    "praderas": ["1504"],  # Terrenos
    "oficina": ["2335"],   # Costos y gastos por pagar
    "legal": ["2365", "2370", "25"],  # Retenciones, aportes y beneficios a empleados
    "mejoras": ["1520", "1524", "1540", "1592"],  # Maquinaria, equipo, flota y depreciación
    "otros": []  # Categoría por defecto para códigos que no coinciden con ninguna otra categoría
}

def extract_financial_data(dataframe):
    """
    Extrae los datos financieros de un DataFrame con la estructura específica del Estado de Situación Financiera.
    
    Args:
        dataframe (pd.DataFrame): DataFrame que contiene los datos financieros.
        
    Returns:
        list: Lista de diccionarios con los campos 'codigo', 'descripcion', 'valor', 'tipo' y 'categoria'.
    """
    # Lista para almacenar los resultados
    financial_data = []
    
    # Verificar que el DataFrame tenga al menos 3 columnas
    if dataframe.shape[1] < 3:
        print("El DataFrame no tiene suficientes columnas para extraer los datos financieros.")
        return financial_data
    
    # Obtener los nombres de las columnas
    columns = dataframe.columns.tolist()
    
    # Buscar la fila que contiene los encabezados reales
    header_row_idx = None
    for idx, row in dataframe.iterrows():
        if isinstance(row[columns[0]], str) and "Código cuenta contable" in row[columns[0]]:
            header_row_idx = idx
            break
    
    # Si no se encuentra la fila de encabezados, intentar con otra estrategia
    if header_row_idx is None:
        # Buscar filas que parecen contener códigos de cuenta (números)
        for idx, row in dataframe.iterrows():
            if isinstance(row[columns[0]], str) and row[columns[0]].isdigit():
                # Encontramos una fila con un código de cuenta
                header_row_idx = idx - 1  # Asumimos que la fila anterior es el encabezado
                break
    
    # Si aún no encontramos encabezados, usar la fila 7 (basado en la salida de depuración)
    if header_row_idx is None:
        header_row_idx = 7
    
    # Iterar sobre las filas del DataFrame a partir de la fila después del encabezado
    for idx in range(header_row_idx + 1, len(dataframe)):
        row = dataframe.iloc[idx]
        
        # Extraer los valores de las columnas
        codigo = row[columns[0]]
        descripcion = row[columns[1]] if len(columns) > 1 else None
        valor = row[columns[2]] if len(columns) > 2 else None
        
        # Verificar que el código y el valor no estén vacíos
        if pd.notna(codigo) and pd.notna(valor):
            # Convertir el código a string si no lo es
            if not isinstance(codigo, str):
                codigo = str(codigo)
            
            # Convertir el valor a float si es posible
            try:
                if isinstance(valor, str):
                    # Eliminar posibles caracteres no numéricos (excepto el punto decimal)
                    valor = ''.join(c for c in valor if c.isdigit() or c == '.')
                valor = float(valor)
            except (ValueError, TypeError):
                # Si no se puede convertir a float, continuar con el siguiente registro
                continue
            
            # Determinar el tipo de cuenta basado en el código
            tipo = clasificar_cuenta(codigo, descripcion)
            
            # Determinar la categoría basada en el código
            categoria = clasificar_categoria(codigo, descripcion)
            
            # Agregar el registro a la lista de resultados
            financial_data.append({
                'codigo': codigo,
                'descripcion': descripcion if pd.notna(descripcion) else '',
                'valor': valor,
                'tipo': tipo,
                'categoria': categoria
            })
    
    return financial_data

def clasificar_cuenta(codigo, descripcion):
    """
    Clasifica una cuenta contable según su código.
    
    Args:
        codigo (str): Código de la cuenta contable.
        descripcion (str): Descripción de la cuenta contable.
        
    Returns:
        str: Tipo de cuenta (Activo, Pasivo, Patrimonio, Ingreso, Gasto, Costo).
    """
    if not codigo:
        return "No clasificado"
    
    # Convertir a string si no lo es
    codigo_str = str(codigo)
    
    # Clasificación basada en el primer dígito del código
    primer_digito = codigo_str[0] if codigo_str else ''
    
    if primer_digito == '1':
        return "Activo"
    elif primer_digito == '2':
        return "Pasivo"
    elif primer_digito == '3':
        return "Patrimonio"
    elif primer_digito == '4':
        return "Ingreso"
    elif primer_digito == '5':
        return "Gasto"
    elif primer_digito == '6':
        return "Costo"
    elif primer_digito == '7':
        return "Costo de producción"
    elif primer_digito == '8':
        return "Cuentas de orden deudoras"
    elif primer_digito == '9':
        return "Cuentas de orden acreedoras"
    else:
        return "No clasificado"

def clasificar_categoria(codigo, descripcion):
    """
    Clasifica una cuenta contable según su código en una de las categorías definidas.
    Usa la jerarquía de IDs para determinar la categoría.
    
    Args:
        codigo (str): Código de la cuenta contable.
        descripcion (str): Descripción de la cuenta contable.
        
    Returns:
        str: Categoría (animales, praderas, oficina, legal, mejoras, otros).
    """
    if not codigo:
        return "otros"
    
    # Convertir a string si no lo es
    codigo_str = str(codigo)
    
    # Ignorar códigos que empiezan por 3 (patrimonio)
    if codigo_str.startswith('3'):
        return "otros"
    
    # Buscar coincidencias con los IDs principales de cada categoría
    for categoria, ids_principales in CATEGORIAS.items():
        for id_principal in ids_principales:
            # Si el código actual es un ancestro del ID principal
            if codigo_str.startswith(id_principal):
                return categoria
    
    # Si no hay coincidencias, asignar a "otros"
    return "otros"

def is_parent_code(parent_code, child_code):
    """
    Determina si un código es padre de otro basado en la longitud y prefijo.
    
    Args:
        parent_code (str): Código potencial padre
        child_code (str): Código potencial hijo
        
    Returns:
        bool: True si parent_code es padre de child_code
    """
    return len(parent_code) < len(child_code) and child_code.startswith(parent_code)

def analyze_financial_data(financial_data):
    """
    Realiza un análisis básico de los datos financieros.
    
    Args:
        financial_data (list): Lista de diccionarios con los datos financieros.
        
    Returns:
        dict: Diccionario con los resultados del análisis.
    """
    if not financial_data:
        return {"error": "No hay datos para analizar"}
    
    # Inicializar resultados
    resultados = {
        "total_activos": 0,
        "total_pasivos": 0,
        "total_patrimonio": 0,
        "total_ingresos": 0,
        "total_gastos": 0,
        "total_costos": 0,
        "resumen_por_tipo": {},
        "resumen_por_categoria": {},
        "indicadores": {}
    }
    
    # Crear una lista de códigos ordenados por longitud (más largos primero)
    codigos_ordenados = sorted(
        [(r["codigo"], r) for r in financial_data],
        key=lambda x: len(x[0]),
        reverse=True
    )
    
    # Conjunto para rastrear códigos que ya han sido procesados
    codigos_procesados = set()
    
    # Procesar cada código, empezando por los más largos
    for codigo, registro in codigos_ordenados:
        if codigo in codigos_procesados:
            continue
            
        # Verificar si este código es hijo de algún código ya procesado
        es_hijo = False
        for codigo_procesado in codigos_procesados:
            if is_parent_code(codigo_procesado, codigo):
                es_hijo = True
                break
        
        if es_hijo:
            continue
            
        # Si llegamos aquí, el código no es hijo de ningún código procesado
        codigos_procesados.add(codigo)
        
        tipo = registro["tipo"]
        valor = registro["valor"]
        categoria = registro["categoria"]
        
        # Sumar al total correspondiente por tipo
        if tipo == "Activo":
            resultados["total_activos"] += valor
        elif tipo == "Pasivo":
            resultados["total_pasivos"] += valor
        elif tipo == "Patrimonio":
            resultados["total_patrimonio"] += valor
        elif tipo == "Ingreso":
            resultados["total_ingresos"] += valor
        elif tipo == "Gasto" or tipo == "Costo" or tipo == "Costo de producción":
            if tipo == "Gasto":
                resultados["total_gastos"] += valor
            else:
                resultados["total_costos"] += valor
        
        # Agregar al resumen por tipo
        if tipo not in resultados["resumen_por_tipo"]:
            resultados["resumen_por_tipo"][tipo] = 0
        resultados["resumen_por_tipo"][tipo] += valor
        
        # Agregar al resumen por categoría
        if categoria not in resultados["resumen_por_categoria"]:
            resultados["resumen_por_categoria"][categoria] = 0
        resultados["resumen_por_categoria"][categoria] += valor
    
    # Calcular indicadores financieros básicos
    if resultados["total_pasivos"] > 0:
        resultados["indicadores"]["endeudamiento"] = resultados["total_pasivos"] / (resultados["total_activos"] if resultados["total_activos"] > 0 else 1)
    else:
        resultados["indicadores"]["endeudamiento"] = 0
    
    resultados["indicadores"]["liquidez"] = resultados["total_activos"] / (resultados["total_pasivos"] if resultados["total_pasivos"] > 0 else 1)
    
    # Calcular utilidad
    resultados["utilidad"] = resultados["total_ingresos"] - resultados["total_gastos"] - resultados["total_costos"]
    
    return resultados

def generate_financial_report(financial_data, analysis_results=None):
    """
    Genera un informe a partir de los datos financieros.
    
    Args:
        financial_data (list): Lista de diccionarios con los datos financieros.
        analysis_results (dict, optional): Resultados del análisis financiero.
        
    Returns:
        str: Informe generado.
    """
    if not financial_data:
        return "No hay datos para generar el informe."
    
    # Si no se proporcionan resultados de análisis, generarlos
    if analysis_results is None:
        analysis_results = analyze_financial_data(financial_data)
    
    # Generar el informe
    informe = []
    informe.append("INFORME DE ESTADO FINANCIERO")
    informe.append("-" * 30)
    informe.append("")
    
    # Resumen general
    informe.append(f"Total Ingresos: ${analysis_results['total_ingresos']:,.2f}")
    informe.append("")
    
    # Egresos por categoría
    informe.append(f"Total Egresos: ${analysis_results['total_gastos'] + analysis_results['total_costos']:,.2f}")
    # Ordenar categorías para que aparezcan en un orden específico
    orden_categorias = ["animales", "praderas", "oficina", "legal", "mejoras", "otros"]
    for categoria in orden_categorias:
        if categoria in analysis_results["resumen_por_categoria"]:
            valor = analysis_results["resumen_por_categoria"][categoria]
            informe.append(f"    {categoria.capitalize()}: ${valor:,.2f}")
    informe.append("")
    
    # Total utilidad
    informe.append(f"Total Utilidad: ${analysis_results['utilidad']:,.2f}")
    informe.append("")
    
    # Detalles por categoría
    informe.append("-" * 30)
    informe.append("Detalles de cada categoria.")
    informe.append("")
    
    # Agrupar datos por categoría
    datos_por_categoria = {}
    for registro in financial_data:
        categoria = registro["categoria"]
        if categoria not in datos_por_categoria:
            datos_por_categoria[categoria] = []
        datos_por_categoria[categoria].append(registro)
    
    # Mostrar detalles de cada categoría
    for categoria in orden_categorias:
        if categoria in datos_por_categoria:
            informe.append(f"\n{categoria.upper()}")
            informe.append("-" * 30)
            
            # Ordenar registros por longitud del código (más largos primero)
            registros = sorted(datos_por_categoria[categoria], 
                             key=lambda x: len(x["codigo"]), 
                             reverse=True)
            
            # Conjunto para rastrear códigos que ya han sido procesados
            codigos_procesados = set()
            
            # Mostrar solo los registros con códigos finales
            for registro in registros:
                codigo = registro["codigo"]
                
                # Verificar si este código es hijo de algún código ya procesado
                es_hijo = False
                for codigo_procesado in codigos_procesados:
                    if is_parent_code(codigo_procesado, codigo):
                        es_hijo = True
                        break
                
                if es_hijo:
                    continue
                
                # Si llegamos aquí, el código no es hijo de ningún código procesado
                codigos_procesados.add(codigo)
                
                informe.append(f"Código: {codigo}")
                informe.append(f"Descripción: {registro['descripcion']}")
                informe.append(f"Valor: ${registro['valor']:,.2f}")
                informe.append(f"Tipo: {registro['tipo']}")
                informe.append("")
    
    return "\n".join(informe) 