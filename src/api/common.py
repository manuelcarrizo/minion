import os
from src import settings

def project_path(name):
    return os.path.join(settings.PROJECTS_ROOT, name)
