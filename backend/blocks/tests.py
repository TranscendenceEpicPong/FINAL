from django.test import TestCase
from core.models import EpicPongUser as User
from .service import BlockService
from .models import Blocks
from .status import StatusAdding, StatusRemoving
from friends.models import Friends

# Create your tests here.
