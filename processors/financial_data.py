import pandas as pd
import numpy as np

# Diccionario de categorías con sus códigos parciales (prefijos)
# Basado en la estructura de cuentas contables colombianas y adaptado a las categorías solicitadas
CATEGORIAS = {
    "animales": ["1240", "1241", "1242", "1243", "1244", "1245", "5240", "5241", "5242", "5243", "5244", "5245"],
    "praderas": ["1230", "1231", "1232", "1233", "5230", "5231", "5232", "5233"],
    "oficina": ["1524", "1528", "5110", "5111", "5112", "5113", "5114", "5115", "5116", "5117", "5118"],
    "legal": ["2365", "2367", "2368", "2370", "2380", "5195", "5196", "5197", "5198", "5199"],
    "mejoras": ["1504", "1508", "1516", "1520", "1540", "1560", "1562", "1564", "5140", "5145", "5150", "5155"],
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
    
    # Buscar coincidencias con los prefijos de cada categoría
    for categoria, prefijos in CATEGORIAS.items():
        for prefijo in prefijos:
            if codigo_str.startswith(prefijo):
                return categoria
    
    # Si hay palabras clave en la descripción, usar eso como pista adicional
    if descripcion:
        descripcion_lower = descripcion.lower()
        if any(keyword in descripcion_lower for keyword in ["animal", "ganado", "bovino", "porcino", "avícola", "veterinaria"]):
            return "animales"
        elif any(keyword in descripcion_lower for keyword in ["pradera", "pasto", "forraje", "cultivo", "siembra", "agrícola"]):
            return "praderas"
        elif any(keyword in descripcion_lower for keyword in ["oficina", "administrativo", "papelería", "computador", "software", "mueble"]):
            return "oficina"
        elif any(keyword in descripcion_lower for keyword in ["legal", "impuesto", "tributo", "fiscal", "abogado", "notaría"]):
            return "legal"
        elif any(keyword in descripcion_lower for keyword in ["mejora", "construcción", "edificio", "infraestructura", "maquinaria"]):
            return "mejoras"
    
    # Si no hay coincidencias, asignar a "otros"
    return "otros"

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
    
    # Calcular totales por tipo y categoría
    for registro in financial_data:
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
    informe.append("INFORME FINANCIERO")
    informe.append("=" * 50)
    informe.append("")
    
    # Resumen general
    informe.append("RESUMEN GENERAL")
    informe.append("-" * 30)
    informe.append(f"Total Activos: ${analysis_results['total_activos']:,.2f}")
    informe.append(f"Total Pasivos: ${analysis_results['total_pasivos']:,.2f}")
    informe.append(f"Total Patrimonio: ${analysis_results['total_patrimonio']:,.2f}")
    informe.append(f"Total Ingresos: ${analysis_results['total_ingresos']:,.2f}")
    informe.append(f"Total Gastos: ${analysis_results['total_gastos']:,.2f}")
    informe.append(f"Total Costos: ${analysis_results['total_costos']:,.2f}")
    informe.append(f"Utilidad: ${analysis_results['utilidad']:,.2f}")
    informe.append("")
    
    # Indicadores financieros
    informe.append("INDICADORES FINANCIEROS")
    informe.append("-" * 30)
    informe.append(f"Endeudamiento: {analysis_results['indicadores']['endeudamiento']:.2%}")
    informe.append(f"Liquidez: {analysis_results['indicadores']['liquidez']:.2f}")
    informe.append("")
    
    # Resumen por categoría
    informe.append("RESUMEN POR CATEGORÍA")
    informe.append("-" * 30)
    # Ordenar categorías para que aparezcan en un orden específico
    orden_categorias = ["animales", "praderas", "oficina", "legal", "mejoras", "otros"]
    for categoria in orden_categorias:
        if categoria in analysis_results["resumen_por_categoria"]:
            valor = analysis_results["resumen_por_categoria"][categoria]
            informe.append(f"{categoria.capitalize()}: ${valor:,.2f}")
    informe.append("")
    
    # Resumen por tipo
    informe.append("RESUMEN POR TIPO")
    informe.append("-" * 30)
    for tipo, valor in analysis_results["resumen_por_tipo"].items():
        informe.append(f"{tipo}: ${valor:,.2f}")
    
    return "\n".join(informe) 