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
REPORTS_FOLDER = os.getenv('REPORTS_FOLDER', 'reportes')

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stderr)
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
        
        # Paso 1: Descargar archivos adjuntos de correos electrónicos
        if args.debug:
            processors.clean_downloaded_emails()
            downloaded_files = processors.download_attachments(force_download=True)
        elif not args.no_email:
            downloaded_files = processors.download_attachments()
        else:
            downloaded_files = processors.get_available_files(DOWNLOAD_FOLDER)
        
        if not downloaded_files:
            logging.error("No hay archivos para procesar.")
            return
        
        # Paso 2: Cargar archivos
        loaded_data = processors.load_files(downloaded_files, DOWNLOAD_FOLDER)
        
        if not loaded_data:
            logging.error("No se pudieron cargar los archivos.")
            return
        
        # Paso 3: Procesar cada archivo
        for filename in loaded_data:
            # Extraer datos financieros
            financial_data = processors.extract_financial_data(loaded_data[filename])
            
            if not financial_data:
                logging.error(f"No se pudieron extraer datos de {filename}")
                continue
            
            # Analizar los datos financieros
            analysis_results = processors.analyze_financial_data(financial_data)
            
            # Generar informe
            report = generate_financial_report(financial_data, analysis_results, debug=debug_mode)
            
            # Crear directorio de reportes si no existe
            os.makedirs("reportes", exist_ok=True)
            
            # Generar nombre de archivo con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"reportes/informe_financiero_{timestamp}.txt"
            
            # Guardar informe
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report)
            
            logging.info(f"Informe guardado: {report_file}")
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 