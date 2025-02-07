import imaplib
import email
from dotenv import load_dotenv
from email.header import decode_header
import os

# Configuración
# load config from dotenv
load_dotenv()

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
IMAP_SERVER = os.getenv('IMAP_SERVER')
DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER')
SEARCH_CRITERIA = os.getenv('SEARCH_CRITERIA')

def clean_filename(filename):
    """Limpia el nombre del archivo."""
    if isinstance(filename, bytes):
        filename = filename.decode()
    return "".join(c if c.isalnum() or c in ['.', '_', '-'] else "_" for c in filename)

def download_attachments():
    """Conecta a Gmail y descarga archivos adjuntos y devuelve una lista de los archivos descargados."""
    print("Iniciando descarga de correos...")
    downloaded_files = []  # Lista para almacenar los nombres de los archivos descargados
    # Conectar al servidor IMAP
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)  # Codificar a UTF-8
    mail.select('inbox')  # Selecciona la bandeja de entrada
    
    # Leer los IDs de correos ya descargados
    downloaded_ids = set()
    if os.path.exists('downloaded_emails.txt'):
        with open('downloaded_emails.txt', 'r') as log_file:
            downloaded_ids = set(line.strip() for line in log_file)

    # Buscar correos que coincidan con el filtro
    status, messages = mail.search(None, SEARCH_CRITERIA)
    if status != 'OK':
        print("No se encontraron correos.")
        return []
    
    # Obtener la lista de IDs de los correos
    email_ids = messages[0].split()

    if not email_ids:
        print("No se encontraron correos con archivos adjuntos.")
        return []

    # Crear la carpeta para los archivos adjuntos
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)

    # Recorrer los correos
    for email_id in email_ids:
        email_id_str = email_id.decode()  # Decodificar el ID a cadena
        if email_id_str in downloaded_ids:
            print(f"Correo {email_id_str} ya descargado. Saltando...")
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
                        filename = clean_filename(filename)
                        filepath = os.path.join(DOWNLOAD_FOLDER, filename)

                        # Guardar el archivo adjunto
                        with open(filepath, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                        print(f"Descargado: {filename}")
                        downloaded_files.append(filename)  # Agregar el nombre del archivo a la lista

        # Registrar el ID del correo descargado
        with open('downloaded_emails.txt', 'a') as log_file:
            log_file.write(f"{email_id_str}\n")  # Escribir el ID como cadena

    # Cerrar la conexión
    mail.logout()
    return downloaded_files  # Devolver la lista de archivos descargados

if __name__ == '__main__':
    downloaded_files = download_attachments()
    print(f"Archivos descargados: {downloaded_files}")