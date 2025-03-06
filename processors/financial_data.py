import pandas as pd
import numpy as np
import logging

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
        # print("El DataFrame no tiene suficientes columnas para extraer los datos financieros.")
        logging.warning("El DataFrame no tiene suficientes columnas para extraer los datos financieros.")
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
    # Convertir a string si no lo son
    parent_str = str(parent_code)
    child_str = str(child_code)
    
    # Verificar que el padre sea más corto que el hijo
    if len(parent_str) >= len(child_str):
        return False
    
    # Verificar que el hijo comience con el padre
    return child_str.startswith(parent_str)

def find_ancestors(codigo, financial_data):
    """
    Encuentra todos los ancestros de un código en los datos financieros.
    
    Args:
        codigo (str): Código para el cual buscar ancestros
        financial_data (list): Lista de diccionarios con los datos financieros
        
    Returns:
        list: Lista de diccionarios con la información de los ancestros
    """
    ancestros = []
    codigo_str = str(codigo)
    
    # Buscar todos los posibles ancestros en los datos financieros
    for registro in financial_data:
        codigo_potencial_padre = str(registro["codigo"])
        
        # Verificar si este código es un ancestro del código actual
        if is_parent_code(codigo_potencial_padre, codigo_str):
            ancestros.append({
                "codigo": codigo_potencial_padre,
                "descripcion": registro["descripcion"],
                "valor": registro["valor"],
                "tipo": registro["tipo"],
                "categoria": registro["categoria"]
            })
    
    # Ordenar ancestros por longitud del código (más cortos primero)
    ancestros_ordenados = sorted(ancestros, key=lambda x: len(x["codigo"]))
    return ancestros_ordenados

def analyze_financial_data(financial_data, debug=False):
    """
    Analiza los datos financieros y genera un informe.
    
    Args:
        financial_data (list): Lista de diccionarios con los datos financieros.
        debug (bool): Si es True, muestra información adicional durante el análisis.
        
    Returns:
        dict: Resultados del análisis.
    """
    results = {
        'total_registros': len(financial_data),
        'por_categoria': {},
        'por_tipo': {},
        'jerarquia': {},
        'detalles_completos': []
    }
    
    # Procesar cada registro
    for registro in financial_data:
        if debug:
            # print(f"Procesando código: {registro['codigo']}")
            logging.debug(f"Procesando código: {registro['codigo']}")
            
        # Encontrar ancestros del código
        ancestros = find_ancestors(registro['codigo'], financial_data)
        
        if debug:
            # print(f"Ancestros encontrados: {len(ancestros)}")
            logging.debug(f"Ancestros encontrados: {len(ancestros)}")
            for ancestro in ancestros:
                # print(f"  - {ancestro['codigo']}: {ancestro['descripcion']}")
                logging.debug(f"  - {ancestro['codigo']}: {ancestro['descripcion']}")
        
        # Crear detalle básico
        detalle = {
            "codigo": registro["codigo"],
            "descripcion": registro["descripcion"],
            "valor": registro["valor"],
            "tipo": registro["tipo"],
            "categoria": registro["categoria"],
            "ancestros": ancestros
        }
        
        # Agregar el detalle a la lista de detalles completos
        results["detalles_completos"].append(detalle)
        
        # Actualizar totales y resúmenes
        tipo = registro["tipo"]
        valor = registro["valor"]
        categoria = registro["categoria"]
        
        # Sumar al total correspondiente por tipo
        if tipo == "Activo":
            results["total_activos"] = results.get("total_activos", 0) + valor
        elif tipo == "Pasivo":
            results["total_pasivos"] = results.get("total_pasivos", 0) + valor
        elif tipo == "Patrimonio":
            results["total_patrimonio"] = results.get("total_patrimonio", 0) + valor
        elif tipo == "Ingreso":
            results["total_ingresos"] = results.get("total_ingresos", 0) + valor
        elif tipo == "Gasto" or tipo == "Costo" or tipo == "Costo de producción":
            if tipo == "Gasto":
                results["total_gastos"] = results.get("total_gastos", 0) + valor
            else:
                results["total_costos"] = results.get("total_costos", 0) + valor
        
        # Agregar al resumen por tipo
        if tipo not in results["por_tipo"]:
            results["por_tipo"][tipo] = 0
        results["por_tipo"][tipo] += valor
        
        # Agregar al resumen por categoría
        if categoria not in results["por_categoria"]:
            results["por_categoria"][categoria] = 0
        results["por_categoria"][categoria] += valor
    
    # Calcular utilidad
    total_ingresos = results.get("total_ingresos", 0)
    total_gastos = results.get("total_gastos", 0)
    total_costos = results.get("total_costos", 0)
    
    results["utilidad"] = total_ingresos - total_gastos - total_costos
    
    return results

def generate_financial_report(financial_data, analysis_results=None, debug=False):
    """
    Genera un informe a partir de los datos financieros.
    
    Args:
        financial_data (list): Lista de diccionarios con los datos financieros.
        analysis_results (dict, optional): Resultados del análisis financiero.
        debug (bool): Si está en modo debug, incluye información adicional y limpia reportes anteriores.
        
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
    informe.append(f"Total Ingresos: ${analysis_results.get('total_ingresos', 0):,.2f}")
    informe.append("")
    
    # Egresos por categoría
    total_gastos = analysis_results.get('total_gastos', 0)
    total_costos = analysis_results.get('total_costos', 0)
    informe.append(f"Total Egresos: ${total_gastos + total_costos:,.2f}")
    # Ordenar categorías para que aparezcan en un orden específico
    orden_categorias = ["animales", "praderas", "oficina", "legal", "mejoras", "otros"]
    for categoria in orden_categorias:
        if categoria in analysis_results["por_categoria"]:
            valor = analysis_results["por_categoria"][categoria]
            informe.append(f"    {categoria.capitalize()}: ${valor:,.2f}")
    informe.append("")
    
    # Total utilidad
    informe.append(f"Total Utilidad: ${analysis_results['utilidad']:,.2f}")
    informe.append("")
    
    # Detalles por categoría
    informe.append("-" * 30)
    informe.append("Detalles de cada categoria.")
    informe.append("")
    
    # Agrupar detalles por categoría
    detalles_por_categoria = {}
    for detalle in analysis_results["detalles_completos"]:
        categoria = detalle["categoria"]
        if categoria not in detalles_por_categoria:
            detalles_por_categoria[categoria] = []
        detalles_por_categoria[categoria].append(detalle)
    
    # Mostrar detalles de cada categoría
    for categoria in orden_categorias:
        if categoria in detalles_por_categoria:
            informe.append(f"\n{categoria.upper()}")
            informe.append("-" * 30)
            
            # Mostrar cada detalle
            for detalle in detalles_por_categoria[categoria]:
                informe.append(f"Código: {detalle['codigo']}")
                informe.append(f"Descripción: {detalle['descripcion']}")
                informe.append(f"Valor: ${detalle['valor']:,.2f}")
                informe.append(f"Tipo: {detalle['tipo']}")
                informe.append("Ancestros:")
                
                # Verificar si el detalle tiene la clave 'ancestros'
                ancestros = detalle.get('ancestros', [])
                if ancestros:
                    for ancestro in ancestros:
                        informe.append(f" - {ancestro['codigo']}: {ancestro['descripcion']}")
                else:
                    informe.append(" - No se encontraron ancestros")
                informe.append("")
    
    # Si estamos en modo debug, agregar información adicional
    if debug:
        informe.append("\nINFORMACIÓN DE DEBUG")
        informe.append("-" * 30)
        informe.append(f"Total registros procesados: {len(financial_data)}")
        informe.append(f"Total categorías encontradas: {len(detalles_por_categoria)}")
        for categoria, detalles in detalles_por_categoria.items():
            informe.append(f"\nRegistros en categoría {categoria}: {len(detalles)}")
            for detalle in detalles:
                informe.append(f"  - {detalle['codigo']}: {detalle['descripcion']}")
    
    return "\n".join(informe)

def clean_previous_reports(debug=False):
    """
    Limpia los reportes anteriores si estamos en modo debug.
    
    Args:
        debug (bool): Si está en modo debug, limpia los reportes anteriores.
    """
    if debug:
        import os
        import glob
        
        # Buscar todos los archivos de reporte
        reportes = glob.glob("reportes/*.txt")
        
        # Eliminar cada reporte encontrado
        for reporte in reportes:
            try:
                os.remove(reporte)
                # print(f"Reporte eliminado: {reporte}")
                logging.info(f"Reporte eliminado: {reporte}")
            except Exception as e:
                # print(f"Error al eliminar {reporte}: {str(e)}")
                logging.error(f"Error al eliminar {reporte}: {str(e)}") 