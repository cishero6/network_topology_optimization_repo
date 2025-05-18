import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from app.core.factories import ProdFactory
from app.core.query_manager import QueryManager
from app.models import Query

logger = logging.getLogger(__name__)

@csrf_exempt
def api_request(request):
    """Обработка запроса на создание задачи"""
    try:
        query_manager = QueryManager(ProdFactory.create_storage())

        if request.method != 'POST':
            return JsonResponse({'error': 'Method not allowed'}, status=405)
            
        if len(request.FILES) != 2:
            return JsonResponse({'error': 'Exactly 2 files required'}, status=400)

        files = list(request.FILES.values())
        query_id = query_manager.create_query(files[0], files[1])
        return JsonResponse({'queryId': query_id})

    except ValidationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.error(f"API Request error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def api_check(request):
    """Проверка статуса задачи"""
    try:
        query_manager = QueryManager(ProdFactory.create_storage())

        query_id = request.GET.get('queryId')
        if not query_id:
            return JsonResponse({'error': 'queryId parameter required'}, status=400)
        
        status_info = query_manager.get_status(query_id)
        return JsonResponse(status_info)
        
    except Query.DoesNotExist:
        return JsonResponse({'error': 'Invalid queryId'}, status=404)
    except Exception as e:
        logger.error(f"API Check error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)

def api_get(request):
    """Получение результатов задачи"""
    try:
        query_id = request.GET.get('queryId')
        if not query_id:
            return JsonResponse({'error': 'queryId parameter required'}, status=400)

        query = Query.objects.get(query_id=query_id)
        if query.status != 'COMPLETED':
            return JsonResponse({'error': 'Processing not completed'}, status=400)

        return JsonResponse({
            'stage1_result': query.stage1_result.url,
            'stage2_result': query.stage2_result.url
        })
        
    except Query.DoesNotExist:
        return JsonResponse({'error': 'Invalid queryId'}, status=404)
    except Exception as e:
        logger.error(f"API Get error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)