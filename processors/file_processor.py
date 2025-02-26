import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER')

def load_files(downloaded_files, download_folder=None):
    """
    Carga los archivos descargados y devuelve un diccionario con los datos.
    
    Args:
        downloaded_files (list): Lista de nombres de archivos a cargar.
        download_folder (str, optional): Carpeta donde se encuentran los archivos.
            Si no se proporciona, se usa la variable de entorno DOWNLOAD_FOLDER.
            
    Returns:
        dict: Diccionario con los datos cargados (nombre_archivo -> DataFrame).
    """
    if download_folder is None:
        download_folder = DOWNLOAD_FOLDER
    
    data = {}
    
    for filename in downloaded_files:
        filepath = os.path.join(download_folder, filename)
        
        # Cargar archivos .xls y .xlsx
        if filename.endswith(('.xls', '.xlsx')):
            try:
                df = pd.read_excel(filepath)
                data[filename] = df
                print(f"Cargado: {filename} (Excel)")
            except Exception as e:
                print(f"Error al cargar {filename}: {e}")
        
        # Cargar archivos .csv
        elif filename.endswith('.csv'):
            try:
                df = pd.read_csv(filepath)
                data[filename] = df
                print(f"Cargado: {filename} (CSV)")
            except Exception as e:
                print(f"Error al cargar {filename}: {e}")

    return data

def get_available_files(download_folder=None):
    """
    Obtiene la lista de archivos disponibles en la carpeta de descargas.
    
    Args:
        download_folder (str, optional): Carpeta donde se encuentran los archivos.
            Si no se proporciona, se usa la variable de entorno DOWNLOAD_FOLDER.
            
    Returns:
        list: Lista de nombres de archivos disponibles.
    """
    if download_folder is None:
        download_folder = DOWNLOAD_FOLDER
    
    return [f for f in os.listdir(download_folder) 
            if f.endswith(('.xls', '.xlsx', '.csv'))] 