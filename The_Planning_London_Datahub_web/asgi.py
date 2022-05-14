# mysite/asgi.py
import os

import django
from channels.http import AsgiHandler
from channels.routing import ProtocolTypeRouter
from . import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings)
# django.setup()

application = ProtocolTypeRouter({
  "http": AsgiHandler(),
  # Just HTTP for now. (We can add other protocols later.)
})