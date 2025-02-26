"""
Paquete de procesadores para el análisis de datos financieros.

Este paquete contiene módulos para procesar correos electrónicos,
cargar archivos, extraer y analizar datos financieros, y generar informes.
"""

from processors.email_processor import download_attachments, clean_downloaded_emails
from processors.file_processor import load_files, get_available_files
from processors.financial_data import extract_financial_data, analyze_financial_data, clasificar_cuenta, clasificar_categoria
from processors.report_generator import generate_report, export_to_excel

__all__ = [
    'download_attachments',
    'clean_downloaded_emails',
    'load_files',
    'get_available_files',
    'extract_financial_data',
    'analyze_financial_data',
    'clasificar_cuenta',
    'clasificar_categoria',
    'generate_report',
    'export_to_excel'
] 