import os
import io
from django.core.files.storage import Storage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from google.auth.transport.requests import Request  # Добавьте этот импорт
from django.conf import settings

class GoogleDriveStorage(Storage):
    def __init__(self):
        self.credentials = self._get_credentials()
        self.service = build('drive', 'v3', credentials=self.credentials)
        self.folder_id = settings.GOOGLE_DRIVE_FOLDER_ID

    def _get_credentials(self):
        # Создаем объект учетных данных
        creds = Credentials(
            token=None,  # Изначально нет токена
            refresh_token=settings.GOOGLE_DRIVE_REFRESH_TOKEN,
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            token_uri='https://oauth2.googleapis.com/token'
        )
         # Автообновление токена
        if creds.expired:
            try:
                creds.refresh(Request())
                print("Токен успешно обновлён!")
            except Exception as e:
                print(f"Ошибка обновления токена: {e}")
    
        return creds
        

    def _get_or_create_folder(self, folder_name, parent_id=None):
        """Создает или возвращает папку в Google Drive"""
        query = f"mimeType='application/vnd.google-apps.folder' and trashed=false and name='{folder_name}'"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        if items:
            return items[0]['id']

        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id] if parent_id else []
        }
        folder = self.service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')

    def _open(self, name, mode='rb'):
        """Открывает файл с Google Drive"""
        file_id = self._get_file_id(name)
        if not file_id:
            raise FileNotFoundError(f"File {name} not found in Google Drive")
        
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        fh.seek(0)
        return fh

    def _save(self, name, content):
        """Сохраняет файл в Google Drive"""
        path_parts = name.split('/')
        parent_id = self.folder_id

        # Создаем структуру папок
        for folder_name in path_parts[:-1]:
            if folder_name:  # Пропускаем пустые части пути
                parent_id = self._get_or_create_folder(folder_name, parent_id)

        filename = path_parts[-1]
        file_metadata = {
            'name': filename,
            'parents': [parent_id]
        }

        # Определяем MIME-тип
        from mimetypes import guess_type
        mime_type, _ = guess_type(filename)
        mime_type = mime_type or 'application/octet-stream'

        # Перемотка файла на начало
        if hasattr(content, 'seek'):
            content.seek(0)
        
        if hasattr(content, 'seek'):
            content.seek(0)

        media = MediaIoBaseUpload(
            content,
            mimetype=mime_type,
            resumable=True
        )
        # Обновляем или создаем файл
        existing_file_id = self._get_file_id(name)
        if existing_file_id:
            self.service.files().update(
                fileId=existing_file_id,
                media_body=media
            ).execute()
        else:
            self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

        return name

    def _get_file_id(self, name):
        try:
            path_parts = name.split('/')
            current_id = self.folder_id
        
        # Экранируем специальные символы в имени файла
            def escape_query(s):
                return s.replace("'", "\\'").replace("\\", "\\\\")
        
        # Ищем каждую папку в пути
            for part in path_parts[:-1]:
                if not part:
                    continue
                
                query = (
                    "mimeType='application/vnd.google-apps.folder' and "
                    f"name='{escape_query(part)}' and "
                    f"'{current_id}' in parents and "
                    "trashed=false"
                )
                results = self.service.files().list(
                    q=query, 
                    fields="files(id, name)",
                    pageSize=1
                ).execute()
                folders = results.get('files', [])
                if not folders:
                    return None
                current_id = folders[0]['id']

        # Ищем сам файл
            filename = path_parts[-1]
            query = (
                f"name='{escape_query(filename)}' and "
                f"'{current_id}' in parents and "
                "trashed=false"
            )
            results = self.service.files().list(
                q=query, 
                fields="files(id)",
                pageSize=1
            ).execute()
            files = results.get('files', [])
            return files[0]['id'] if files else None
        
        except Exception as e:
            print(f"Error in _get_file_id: {str(e)}")
            return None

    def exists(self, name):
        return self._get_file_id(name) is not None

    def url(self, name):
        file_id = self._get_file_id(name)
        if not file_id:
            return ''
    
    # Для изображений
        if name.split('.')[-1].lower() in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            return f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"
    # Для других файлов
        return f"https://drive.google.com/uc?id={file_id}&export=download"
