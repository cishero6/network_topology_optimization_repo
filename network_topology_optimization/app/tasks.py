from celery import shared_task
from app.core.pipeline_manager import PipelineManager
from app.core.storage_manager import StorageManager
from app.models import Query

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def process_pipeline_task(self, query_id: str):
    """Фоновая задача обработки файлов"""
    try:
        query = Query.objects.get(query_id=query_id)
        storage = StorageManager()
        
        # Получаем пути к сохраненным файлам
        file1_path = storage.get_file_path(query.original_file1.name)
        file2_path = storage.get_file_path(query.original_file2.name)
        
        # Запускаем обработку
        PipelineManager().process(query_id, file1_path, file2_path)
        
    except Exception as e:
        Query.objects.filter(query_id=query_id).update(status='FAILED')
        raise self.retry(exc=e, max_retries=3)