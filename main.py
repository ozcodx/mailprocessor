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
import logging
from datetime import datetime
from processors.financial_data import analyze_financial_data, generate_financial_report, clean_previous_reports

# Importar los módulos del paquete processors
import processors

# Cargar variables de entorno
load_dotenv()

DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER')
REPORTS_FOLDER = os.getenv('REPORTS_FOLDER', 'reports')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

def main():
    """
    Función principal que coordina el flujo de trabajo.
    """
    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description='Procesador de datos financieros')
    parser.add_argument('--debug', action='store_true', help='Modo debug (fuerza la descarga de correos)')
    parser.add_argument('--no-email', action='store_true', help='No descargar correos, usar archivos existentes')
    parser.add_argument('--output', type=str, default=REPORTS_FOLDER, help='Carpeta de salida para los informes')
    
    # Parsear los argumentos
    args = parser.parse_args()
    
    # Crear la carpeta de informes si no existe
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    
    # Verificar si estamos en modo debug
    debug_mode = args.debug
    
    try:
        # Limpiar reportes anteriores si estamos en modo debug
        if debug_mode:
            clean_previous_reports(debug=True)
            logging.info("Modo debug activado - Reportes anteriores eliminados")
        
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
            
            # Analizar los datos financieros
            print("\nAnalizando datos financieros...")
            analysis_results = processors.analyze_financial_data(financial_data)
            
            # Generar informe
            print("\nGenerando informe de estado...")
            report = generate_financial_report(financial_data, analysis_results, debug=debug_mode)
            
            # Crear directorio de reportes si no existe
            os.makedirs("reportes", exist_ok=True)
            
            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"reportes/informe_financiero_{timestamp}.txt"
            
            # Guardar informe
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report)
            
            print(f"Informe guardado en: {report_file}")
            logging.info(f"Informe generado exitosamente: {report_file}")
        
    except Exception as e:
        logging.error(f"Error al procesar el archivo: {str(e)}")
        raise

if __name__ == "__main__":
    main() 