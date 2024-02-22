from django.http import JsonResponse

def get_cookie(request, name):
    return request.COOKIES.get(name)

def get_response(response):
    return JsonResponse(response, status=response['status'])