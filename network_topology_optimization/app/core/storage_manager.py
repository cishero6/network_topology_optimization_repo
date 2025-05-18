import fnmatch
import os
import logging
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.conf import settings

from app.core.interfaces import IStorageManager

logger = logging.getLogger(__name__)

class StorageManager(IStorageManager):
    def __init__(self):
        # Инициализация хранилищ для разных типов файлов
        self.uploads_storage = FileSystemStorage(
            location=os.path.join(settings.MEDIA_ROOT, 'uploads')
        )
        self.results_storage = FileSystemStorage(
            location=os.path.join(settings.MEDIA_ROOT, 'results')
        )

    def save_uploaded_file(self, file, query_id: str) -> str:
        """Сохранение исходного файла от клиента"""
        try:
            filename = self._generate_filename(query_id, file.name, 'upload')
            return self.uploads_storage.save(filename, file)
        except Exception as e:
            logger.error(f"Failed to save uploaded file: {str(e)}")
            raise

    def save_final_result(self, content: bytes, query_id: str) -> str:
        """Сохранение финального результата"""
        try:
            filename = self._generate_filename(query_id, 'final', 'bin')
            return self.results_storage.save(filename, ContentFile(content))
        except Exception as e:
            logger.error(f"Failed to save final result: {str(e)}")
            raise

    def cleanup_query_files(self, query_id: str):
        """Очистка всех временных файлов запроса"""
        def delete_matching_files(storage, pattern):
            for filename in storage.listdir('')[1]:
                if filename.startswith(query_id):
                    storage.delete(filename)
        
        try:
            delete_matching_files(self.uploads_storage, f"{query_id}_*")
        except Exception as e:
            logger.error(f"Cleanup failed for {query_id}: {str(e)}")
            raise

    def get_result_url(self, query_id: str, stage: int) -> str:
        """Генерация URL для скачивания результата"""
        filename = f"{query_id}_final_stage{stage}.bin"
        return self.results_storage.url(filename)

    def _generate_filename(self, query_id: str, base_name: str, ext: str) -> str:
        """Генерация уникального имени файла с микросекундным timestamp"""
        from time import time
        timestamp = int(time() * 1000000)  # Микросекунды для гарантии уникальности
        return f"{query_id}_{base_name}_{timestamp}.{ext}"

    def _delete_by_pattern(self, storage, pattern: str):
        """Удаление файлов по паттерну"""
        for filename in storage.listdir('')[1]:
            if fnmatch.fnmatch(filename, pattern):
                storage.delete(filename)