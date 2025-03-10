import imaplib
import email
from dotenv import load_dotenv
from email.header import decode_header
import os
import logging

# Configuración
# load config from dotenv
load_dotenv()

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
IMAP_SERVER = os.getenv('IMAP_SERVER')
DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER')
SEARCH_CRITERIA = os.getenv('SEARCH_CRITERIA')
DOWNLOADED_EMAILS_FILE = 'downloaded_emails.txt'
SUPPORTED_EXTENSIONS = ('.xlsx', '.xls', '.csv')

def clean_filename(filename):
    """Limpia el nombre del archivo."""
    if isinstance(filename, bytes):
        filename = filename.decode()
    return "".join(c if c.isalnum() or c in ['.', '_', '-'] else "_" for c in filename)

def clean_downloaded_emails():
    """Limpia el registro de correos descargados."""
    try:
        if os.path.exists(DOWNLOADED_EMAILS_FILE):
            os.remove(DOWNLOADED_EMAILS_FILE)
            # print("Registro de correos descargados eliminado.")
    except Exception as e:
        # print(f"Error al limpiar el registro de correos: {e}")
        logging.error(f"Error al limpiar el registro de correos: {e}")

def download_attachments(force_download=False):
    """
    Conecta a Gmail y descarga archivos adjuntos y devuelve una lista de los archivos descargados.
    
    Args:
        force_download (bool): Si es True, fuerza la descarga incluso si ya existen.
        
    Returns:
        list: Lista de nombres de archivos descargados.
    """
    # print("Iniciando descarga de correos...")
    logging.info("Iniciando descarga de correos...")
    downloaded_files = []  # Lista para almacenar los nombres de los archivos descargados
    
    # Si se fuerza la descarga, limpiar el registro de correos descargados
    if force_download:
        clean_downloaded_emails()
    
    # Conectar al servidor IMAP
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)  # Codificar a UTF-8
    mail.select('inbox')  # Selecciona la bandeja de entrada
    
    # Leer los IDs de correos ya descargados
    downloaded_ids = set()
    if os.path.exists(DOWNLOADED_EMAILS_FILE):
        with open(DOWNLOADED_EMAILS_FILE, 'r') as log_file:
            downloaded_ids = set(line.strip() for line in log_file)

    # Buscar correos que coincidan con el filtro
    status, messages = mail.search(None, SEARCH_CRITERIA)
    if status != 'OK':
        # print("No se encontraron correos.")
        logging.info("No se encontraron correos.")
        return []
    
    # Obtener la lista de IDs de los correos
    email_ids = messages[0].split()

    if not email_ids:
        # print("No se encontraron correos con archivos adjuntos.")
        logging.info("No se encontraron correos con archivos adjuntos.")
        return []

    # Crear la carpeta para los archivos adjuntos
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    # Recorrer los correos
    for email_id in email_ids:
        email_id_str = email_id.decode()  # Decodificar el ID a cadena
        if email_id_str in downloaded_ids and not force_download:
            # print(f"Correo {email_id_str} ya descargado. Saltando...")
            logging.info(f"Correo {email_id_str} ya descargado. Saltando...")
            continue  # Saltar correos ya descargados

        status, msg_data = mail.fetch(email_id, '(RFC822)')  # Obtener el correo completo
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                # Recorrer las partes del correo
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue

                    # Obtener el nombre del archivo adjunto
                    filename = part.get_filename()
                    if filename:
                        # Decodificar el nombre del archivo si está en formato MIME
                        decoded_header = decode_header(filename)
                        filename = ''.join(
                            str(t[0], t[1] if t[1] else 'utf-8') if isinstance(t[0], bytes) else t[0]
                            for t in decoded_header
                        )
                        
                        # Verificar si el tipo de archivo es soportado
                        if not any(filename.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                            # print(f"Archivo {filename} no es un tipo soportado. Saltando...")
                            logging.info(f"Archivo {filename} no es un tipo soportado. Saltando...")
                            continue

                        # Limpiar el nombre del archivo
                        filename = clean_filename(filename)
                        filepath = os.path.join(DOWNLOAD_FOLDER, filename)

                        # Guardar el archivo adjunto
                        with open(filepath, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                        # print(f"Descargado: {filename}")
                        logging.info(f"Descargado: {filename}")
                        downloaded_files.append(filename)  # Agregar el nombre del archivo a la lista

        # Registrar el ID del correo descargado
        with open(DOWNLOADED_EMAILS_FILE, 'a') as log_file:
            log_file.write(f"{email_id_str}\n")  # Escribir el ID como cadena

    # Cerrar la conexión
    mail.logout()
    # print(f"Archivos descargados: {downloaded_files}")
    logging.info(f"Archivos descargados: {downloaded_files}")
    return downloaded_files  # Devolver la lista de archivos descargados

if __name__ == '__main__':
    downloaded_files = download_attachments()
    print(f"Archivos descargados: {downloaded_files}")