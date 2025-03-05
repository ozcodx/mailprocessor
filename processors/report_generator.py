import os
import pandas as pd
from datetime import datetime

def generate_report(financial_data, analysis_results, output_folder=None, filename_prefix="informe"):
    """
    Genera un informe de estado financiero y lo guarda en un archivo.
    
    Args:
        financial_data (list): Lista de diccionarios con los datos financieros.
        analysis_results (dict): Resultados del análisis financiero.
        output_folder (str, optional): Carpeta donde se guardará el informe.
            Si no se proporciona, se guarda en la carpeta actual.
        filename_prefix (str, optional): Prefijo para el nombre del archivo.
            
    Returns:
        str: Ruta del archivo generado.
    """
    if not financial_data:
        print("No hay datos para generar el informe.")
        return None
    
    # Crear el informe
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
            
            # Ordenar registros por código
            registros = sorted(datos_por_categoria[categoria], key=lambda x: x["codigo"])
            
            # Mostrar cada registro
            for registro in registros:
                informe.append(f"Código: {registro['codigo']}")
                informe.append(f"Descripción: {registro['descripcion']}")
                informe.append(f"Valor: ${registro['valor']:,.2f}")
                informe.append(f"Tipo: {registro['tipo']}")
                informe.append("")
    
    # Guardar el informe en un archivo
    if output_folder is None:
        output_folder = "."
    
    # Crear la carpeta si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Generar nombre de archivo con fecha y hora
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.txt"
    filepath = os.path.join(output_folder, filename)
    
    # Escribir el informe en el archivo
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(informe))
    
    return filepath

def export_to_excel(financial_data, analysis_results, output_folder=None, filename_prefix="datos_financieros"):
    """
    Exporta los datos financieros a un archivo Excel.
    
    Args:
        financial_data (list): Lista de diccionarios con los datos financieros.
        analysis_results (dict): Resultados del análisis financiero.
        output_folder (str, optional): Carpeta donde se guardará el archivo.
            Si no se proporciona, se guarda en la carpeta actual.
        filename_prefix (str, optional): Prefijo para el nombre del archivo.
            
    Returns:
        str: Ruta del archivo generado.
    """
    if not financial_data:
        print("No hay datos para exportar.")
        return None
    
    # Crear DataFrame con los datos financieros
    df = pd.DataFrame(financial_data)
    
    # Crear DataFrame con el resumen por categoría
    categorias = []
    valores = []
    for categoria, valor in analysis_results["resumen_por_categoria"].items():
        categorias.append(categoria)
        valores.append(valor)
    
    df_resumen = pd.DataFrame({
        "Categoría": categorias,
        "Valor": valores
    })
    
    # Crear DataFrame con el resumen general
    resumen_general = {
        "Concepto": ["Total Activos", "Total Pasivos", "Total Patrimonio", "Total Ingresos", 
                    "Total Gastos", "Total Costos", "Utilidad"],
        "Valor": [
            analysis_results["total_activos"],
            analysis_results["total_pasivos"],
            analysis_results["total_patrimonio"],
            analysis_results["total_ingresos"],
            analysis_results["total_gastos"],
            analysis_results["total_costos"],
            analysis_results["utilidad"]
        ]
    }
    df_general = pd.DataFrame(resumen_general)
    
    # Guardar en Excel
    if output_folder is None:
        output_folder = "."
    
    # Crear la carpeta si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Generar nombre de archivo con fecha y hora
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.xlsx"
    filepath = os.path.join(output_folder, filename)
    
    # Crear un escritor de Excel
    with pd.ExcelWriter(filepath, engine="xlsxwriter") as writer:
        # Escribir los DataFrames en diferentes hojas
        df.to_excel(writer, sheet_name="Datos Detallados", index=False)
        df_resumen.to_excel(writer, sheet_name="Resumen por Categoría", index=False)
        df_general.to_excel(writer, sheet_name="Resumen General", index=False)
    
    return filepath 