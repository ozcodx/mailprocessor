import os
import pandas as pd
from dotenv import load_dotenv
import mail
import logging

load_dotenv()

DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER')

def load_file(filename):
    """
    Carga un archivo Excel o CSV y devuelve un DataFrame.
    
    Args:
        filename (str): Ruta del archivo a cargar.
        
    Returns:
        pandas.DataFrame: DataFrame con los datos cargados.
    """
    try:
        if filename.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(filename)
            logging.info(f"Cargado: {filename} (Excel)")
            return df
    except Exception as e:
        logging.error(f"Error al cargar {filename}: {e}")
        return None
    
    try:
        if filename.lower().endswith('.csv'):
            df = pd.read_csv(filename)
            logging.info(f"Cargado: {filename} (CSV)")
            return df
    except Exception as e:
        logging.error(f"Error al cargar {filename}: {e}")
        return None

def load_files(folder_path):
    """
    Carga todos los archivos Excel y CSV de una carpeta.
    
    Args:
        folder_path (str): Ruta de la carpeta a procesar.
        
    Returns:
        dict: Diccionario con los DataFrames cargados.
    """
    loaded_data = {}
    
    # Verificar que la carpeta existe
    if not os.path.exists(folder_path):
        return loaded_data
    
    # Listar archivos en la carpeta
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            filepath = os.path.join(folder_path, filename)
            df = load_file(filepath)
            if df is not None:
                loaded_data[filename] = df
    
    logging.info(f"Datos cargados: {len(loaded_data)} archivos")
    return loaded_data

if __name__ == '__main__':
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Descargar archivos adjuntos
    download_folder = DOWNLOAD_FOLDER
    downloaded_files = mail.download_attachments()
    
    # Cargar los archivos
    loaded_data = load_files(download_folder)
    # print("Datos cargados:", loaded_data)
    logging.info(f"Datos cargados: {len(loaded_data) if loaded_data else 0} archivos")