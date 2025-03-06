import os
from dotenv import load_dotenv
import load_files
import pandas as pd
import logging

# Cargar variables de entorno
load_dotenv()

DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER')

def main():
    """
    Función para depurar y mostrar la estructura del DataFrame.
    """
    # Obtener la lista de archivos en la carpeta de descargas
    downloaded_files = [f for f in os.listdir(DOWNLOAD_FOLDER) 
                       if f.endswith(('.xls', '.xlsx', '.csv'))]
    
    # Cargar los archivos
    loaded_data = load_files.load_files(downloaded_files, DOWNLOAD_FOLDER)
    
    # Examinar cada DataFrame
    for filename, df in loaded_data.items():
        debug_dataframe(df, filename)

def debug_dataframe(df, filename=None):
    """
    Muestra información de depuración sobre un DataFrame.
    
    Args:
        df (pandas.DataFrame): DataFrame a depurar.
        filename (str, optional): Nombre del archivo de origen.
    """
    # Verificar si hay una columna 'Unnamed: 0'
    if 'Unnamed: 0' in df.columns:
        sample = df[['Unnamed: 0']].head(5)
    
    # Buscar columnas que podrían contener códigos financieros
    for col in df.columns:
        if df[col].dtype == 'object':
            sample = df[df[col].str.contains(r'^\d+$', na=False)].head(5)
            if not sample.empty:
                pass
    
    logging.info(f"Depuración completada para DataFrame {filename if filename else ''} de forma {df.shape}")

if __name__ == "__main__":
    main() 