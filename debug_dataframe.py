import os
from dotenv import load_dotenv
import load_files
import pandas as pd

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
        print(f"\n{'='*50}")
        print(f"Archivo: {filename}")
        print(f"{'='*50}")
        
        # Mostrar información básica
        print(f"Forma del DataFrame: {df.shape}")
        print(f"Columnas: {df.columns.tolist()}")
        
        # Mostrar los primeros registros
        print("\nPrimeros 10 registros:")
        print(df.head(10))
        
        # Mostrar tipos de datos
        print("\nTipos de datos:")
        print(df.dtypes)
        
        # Verificar valores nulos
        print("\nValores nulos por columna:")
        print(df.isnull().sum())
        
        # Mostrar algunos registros específicos para entender mejor la estructura
        print("\nRegistros con valores en la columna 'Unnamed: 0':")
        if 'Unnamed: 0' in df.columns:
            sample = df[df['Unnamed: 0'].notna()].head(5)
            print(sample)
        
        # Mostrar registros que podrían contener códigos financieros
        print("\nRegistros que podrían contener códigos financieros:")
        # Buscar columnas que podrían contener códigos
        for col in df.columns:
            sample = df[df[col].astype(str).str.match(r'^\d+$', na=False)].head(5)
            if not sample.empty:
                print(f"Columna: {col}")
                print(sample)

if __name__ == "__main__":
    main() 