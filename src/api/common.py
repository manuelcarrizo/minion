import os
import threading

from src import settings

def project_path(name):
    return os.path.join(settings.PROJECTS_ROOT, name)

def background_task(worker, *args):
    print("Running", worker, "with args", args)
    t = threading.Thread(target=worker, args=args, daemon=True)
    t.start()