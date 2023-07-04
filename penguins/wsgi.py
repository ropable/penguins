"""
WSGI config for penguins project.
It exposes the WSGI callable as a module-level variable named ``application``
"""
import os
from pathlib import Path

d = Path(__file__).resolve().parents[1]
dot_env = os.path.join(str(d), '.env')
if os.path.exists(dot_env):
    from dotenv import load_dotenv
    load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'penguins.settings')
from django.core.wsgi import get_wsgi_application
from dj_static import Cling, MediaCling

application = Cling(MediaCling(get_wsgi_application()))
