import os
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.credentials import Credentials
from django.core.wsgi import get_wsgi_application
import mimetypes

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
application = get_wsgi_application()

from django.conf import settings

GOOGLE_DRIVE_FOLDER_ID = settings.GOOGLE_DRIVE_FOLDER_ID  # ID целевой папки на Drive

# OAuth
SCOPES = ['https://www.googleapis.com/auth/drive.file']
TOKEN_FILE = 'token.json'

# Локальная папка с медиа
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')


def authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    else:
        raise ValueError("Не найден token.json. Сначала авторизуйтесь через Google API.")
    return creds


def get_or_create_folder(service, folder_name, parent_id=None):
    """Создаёт или возвращает папку на Google Drive"""
    query = f"mimeType='application/vnd.google-apps.folder' and trashed=false and name='{folder_name}'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    
    if items:
        return items[0]['id']

    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id] if parent_id else []
    }
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    return folder.get('id')


def upload_file(service, local_path, parent_id):
    """Загружает файл в указанную папку на Drive"""
    filename = os.path.basename(local_path)
    
    if os.path.getsize(local_path) == 0:
        print(f"Пропущен пустой файл: {filename}")
        return

    mime_type, _ = mimetypes.guess_type(local_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'

    file_metadata = {
        'name': filename,
        'parents': [parent_id]
    }
    
    with open(local_path, 'rb') as f:
        media = MediaIoBaseUpload(f, mimetype=mime_type, resumable=True)
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"Загружен: {filename} в папку {parent_id}")


def upload_folder(service, local_folder, parent_id):
    """Рекурсивно создает структуру папок и загружает файлы"""
    for entry in os.scandir(local_folder):
        if entry.is_dir():
            # Создаем/получаем папку на Drive
            folder_name = os.path.basename(entry.path)
            drive_folder_id = get_or_create_folder(service, folder_name, parent_id)
            print(f"Обрабатывается папка: {entry.path} -> Drive ID: {drive_folder_id}")
            # Рекурсивная обработка вложенной папки
            upload_folder(service, entry.path, drive_folder_id)
        elif entry.is_file():
            # Загрузка файла в текущую папку Drive
            upload_file(service, entry.path, parent_id)


if __name__ == "__main__":
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    
    print(f"Начало загрузки. Корневая папка на Drive: {GOOGLE_DRIVE_FOLDER_ID}")
    upload_folder(service, MEDIA_ROOT, GOOGLE_DRIVE_FOLDER_ID)
    print("Все файлы и папки загружены с сохранением структуры!")