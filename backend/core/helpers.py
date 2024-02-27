from django.http import JsonResponse

def get_cookie(request, name):
    return request.COOKIES.get(name)

def get_response(response, safe=False):
    return JsonResponse(response, safe=safe, status=response['status'])