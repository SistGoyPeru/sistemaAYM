"""
Archivo ASGI para el proyecto Django sistemaAyM.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistemaAyM.settings')

application = get_asgi_application()
