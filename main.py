#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script principal para el procesamiento de datos financieros.

Este script coordina el flujo de trabajo completo:
1. Descarga de archivos adjuntos de correos electrónicos
2. Carga de archivos
3. Extracción y análisis de datos financieros
4. Generación de informes
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Importar los módulos del paquete processors
import processors

# Cargar variables de entorno
load_dotenv()

DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER')
REPORTS_FOLDER = os.getenv('REPORTS_FOLDER', 'reports')

def main():
    """
    Función principal que coordina el flujo de trabajo.
    """
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description='Procesador de datos financieros')
    parser.add_argument('--debug', action='store_true', help='Modo debug (fuerza la descarga de correos)')
    parser.add_argument('--no-email', action='store_true', help='No descargar correos, usar archivos existentes')
    parser.add_argument('--output', type=str, default=REPORTS_FOLDER, help='Carpeta de salida para los informes')
    parser.add_argument('--excel', action='store_true', help='Exportar también a Excel')
    
    # Parsear los argumentos
    args = parser.parse_args()
    
    # Crear la carpeta de informes si no existe
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    
    # Paso 1: Descargar archivos adjuntos de correos electrónicos
    if args.debug:
        print("Modo debug activado. Limpiando correos descargados...")
        processors.clean_downloaded_emails()
        downloaded_files = processors.download_attachments(force_download=True)
    elif not args.no_email:
        print("Descargando archivos adjuntos de correos electrónicos...")
        downloaded_files = processors.download_attachments()
    else:
        print("Usando archivos existentes...")
        downloaded_files = processors.get_available_files(DOWNLOAD_FOLDER)
    
    print(f"Archivos disponibles: {downloaded_files}")
    
    if not downloaded_files:
        print("No hay archivos para procesar.")
        return
    
    # Paso 2: Cargar archivos
    print("Cargando archivos...")
    loaded_data = processors.load_files(downloaded_files, DOWNLOAD_FOLDER)
    
    if not loaded_data:
        print("No se pudieron cargar los archivos.")
        return
    
    # Paso 3: Procesar cada archivo
    for filename, dataframe in loaded_data.items():
        print(f"\n{'='*50}")
        print(f"Procesando archivo: {filename}")
        print(f"{'='*50}")
        
        # Extraer datos financieros
        print("Extrayendo datos financieros...")
        financial_data = processors.extract_financial_data(dataframe)
        
        # Mostrar resultados de la extracción
        print(f"Se extrajeron {len(financial_data)} registros financieros.")
        
        if not financial_data:
            print("No se pudieron extraer registros financieros.")
            continue
        
        # Mostrar algunos ejemplos (primeros 3 registros)
        print("\nEjemplos de registros extraídos:")
        for i, record in enumerate(financial_data[:3]):
            print(f"{i+1}. Código: {record['codigo']}, "
                  f"Descripción: {record['descripcion'][:30]}{'...' if len(record['descripcion']) > 30 else ''}, "
                  f"Valor: ${record['valor']:,.2f}, "
                  f"Tipo: {record['tipo']}, "
                  f"Categoría: {record['categoria']}")
        
        # Analizar los datos financieros
        print("\nAnalizando datos financieros...")
        analysis_results = processors.analyze_financial_data(financial_data)
        
        # Mostrar resumen del análisis por categoría
        print("\nRESUMEN POR CATEGORÍA:")
        orden_categorias = ["animales", "praderas", "oficina", "legal", "mejoras", "otros"]
        for categoria in orden_categorias:
            if categoria in analysis_results["resumen_por_categoria"]:
                valor = analysis_results["resumen_por_categoria"][categoria]
                print(f"{categoria.capitalize()}: ${valor:,.2f}")
        
        # Paso 4: Generar informe
        print("\nGenerando informe de estado...")
        report_filename = os.path.splitext(filename)[0]
        report_path = processors.generate_report(
            financial_data, 
            analysis_results, 
            output_folder=args.output,
            filename_prefix=report_filename
        )
        
        print(f"Informe guardado en: {report_path}")
        
        # Exportar a Excel si se solicita
        if args.excel:
            print("Exportando datos a Excel...")
            excel_path = processors.export_to_excel(
                financial_data, 
                analysis_results, 
                output_folder=args.output,
                filename_prefix=report_filename
            )
            print(f"Datos exportados a: {excel_path}")
    
    print("\nProcesamiento completado.")

if __name__ == "__main__":
    main() 