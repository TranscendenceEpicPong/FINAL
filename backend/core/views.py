from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.middleware.csrf import get_token


@require_GET
def server_info(request):
    response = JsonResponse({
        "hostname": request.get_host(),
        "version": 1,
        "available": True,
    })
    get_token(request)
    return response
