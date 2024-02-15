from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from .form import BlocksAddForm, BlocksDeleteForm
from .models import Blocks
from core.models import EpicPongUser as User
from .status import StatusAdding, StatusRemoving
from .service import BlockService
from django.core.serializers import serialize
import json
from backend.settings import env
import jwt

# Create your views here.
@require_http_methods("GET")
def index(request):
    owner_id = jwt.decode(request.COOKIES.get('authorization'), env('JWT_SECRET'), algorithms=['HS256']).get('id')
    owner = User.objects.get(id=owner_id)
    raw_blocks = Blocks.objects.filter(user=owner).values()
    blocks = []
    for raw_block in raw_blocks:
        user = User.objects.get(id=raw_block.get("block_id"))
        blocks.append({
            'id': user.id,
            'username': user.username,
        })

    return JsonResponse(blocks, safe=False, status=200)