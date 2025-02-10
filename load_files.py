import os
import pandas as pd
from dotenv import load_dotenv
import mail

load_dotenv()

DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER')

def load_files(downloaded_files, download_folder):
    """Carga los archivos descargados y devuelve un diccionario con los datos."""
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

if __name__ == '__main__':
    # Suponiendo que tienes la lista de archivos descargados y la carpeta de descarga
    downloaded_files = mail.download_attachments()
    download_folder = DOWNLOAD_FOLDER

    # Cargar los archivos
    loaded_data = load_files(downloaded_files, download_folder)
    print("Datos cargados:", loaded_data)