import uuid
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from app.core.interfaces import IStorageManager
from app.core.storage_manager import StorageManager
from app.tasks import process_pipeline_task
from app.models import Query

class QueryManager:
    def __init__(self, storage: IStorageManager):
        self.storage = storage  # Зависимость получаем извне

    def create_query(self, file1, file2) -> str:
        """Создание нового запроса"""
        query_id = uuid.uuid4()
        
        try:
            self._validate_files(file1, file2)
            file1_path = self._save_file(file1, query_id, 'original_1')
            file2_path = self._save_file(file2, query_id, 'original_2')
            
            Query.objects.create(
                query_id=query_id,
                original_file1=file1_path,
                original_file2=file2_path,
                status='PENDING'
            )
            
            return str(query_id)
            
        except Exception as e:
            self.set_status(query_id, 'FAILED')
            raise

    def set_status(self, query_id: str, status: str):
        """Обновление статуса запроса"""
        try:
            Query.objects.filter(query_id=query_id).update(status=status)
        except ObjectDoesNotExist:
            pass

    def get_status(self, query_id: str) -> dict:
        """Получение текущего статуса"""
        try:
            query = Query.objects.get(query_id=query_id)
            return {'status': query.status}
        except ObjectDoesNotExist:
            return {'error': 'Query not found'}

    def _validate_files(self, *files):
        """Проверка формата и размера файлов"""
        allowed_extensions = {'.xxx'}  # Заменить на актуальные расширения
        max_size = 10 * 1024 * 1024  # 10MB
        
        for file in files:
            if not file.name.endswith(tuple(allowed_extensions)):
                raise ValidationError("Invalid file format")
            if file.size > max_size:
                raise ValidationError("File size exceeds limit")

    def _save_file(self, file, query_id: str, prefix: str) -> str:
        """Сохранение файла через StorageManager"""
        filename = f"{query_id}_{prefix}.{file.name.split('.')[-1]}"
        return self.storage.save_uploaded_file(file, filename)

    def _start_processing(self, query_id: str):
        process_pipeline_task.delay(str(query_id))