import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def download_attachments(force_download=False):
    """
    Descarga los archivos adjuntos de los correos electrónicos.
    
    Args:
        force_download (bool): Si es True, fuerza la descarga incluso si ya existen.
        
    Returns:
        list: Lista de nombres de archivos descargados.
    """
    try:
        # Importar el módulo mail.py que está en la raíz del proyecto
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import mail
        
        # Llamar a la función de descarga de mail.py
        downloaded_files = mail.download_attachments(force_download)
        return downloaded_files
    except Exception as e:
        print(f"Error al descargar archivos adjuntos: {e}")
        return []

def clean_downloaded_emails():
    """
    Limpia los correos descargados (para modo debug).
    
    Returns:
        bool: True si se limpiaron correctamente, False en caso contrario.
    """
    try:
        # Importar el módulo mail.py que está en la raíz del proyecto
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        import mail
        
        # Llamar a una función para limpiar los correos (si existe)
        if hasattr(mail, 'clean_downloaded_emails'):
            mail.clean_downloaded_emails()
            return True
        else:
            print("La función clean_downloaded_emails no está disponible en el módulo mail.")
            return False
    except Exception as e:
        print(f"Error al limpiar correos descargados: {e}")
        return False 