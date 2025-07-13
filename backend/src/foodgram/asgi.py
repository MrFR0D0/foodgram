import os
import sys
from pathlib import Path

from django.core.asgi import get_asgi_application

# Add the project's 'src' directory to the Python path
ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(ROOT_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodgram.settings")

application = get_asgi_application()
