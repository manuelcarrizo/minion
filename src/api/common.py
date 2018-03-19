import os
import threading

from django.conf import settings

def project_path(name):
    return os.path.join(settings.PROJECTS_ROOT, 'src', name)

def volumes_path(name):
    return os.path.join(settings.PROJECTS_ROOT, 'volumes', name)

def background_task(worker, *args):
    t = threading.Thread(target=worker, args=args, daemon=True)
    t.start()