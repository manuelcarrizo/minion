from git import Repo

import os
import re
from src.api.common import project_path

def exists(name):
    try:
        repo = Repo(project_path(name))
    except InvalidGitRepositoryError:
        return False
    return True

def clone(name, url):
    Repo.clone_from(url, project_path(name))

def checkout(name, branch):
    repo = Repo(project_path(name))
    git = repo.git()
    git.checkout(branch)

def branches(name):
    repo = Repo(project_path(name))
    return [re.sub('.+origin/', '', branch) for branch in repo.git.branch(['-r', '--sort', '-version:refname']).split('\n')]

def tags(name):
    repo = Repo(project_path(name))
    return [re.sub('.+origin/', '', branch) for branch in repo.git.tag(['--sort', '-version:refname']).split('\n')]

def pull(name):
    repo = Repo(project_path(name))
    repo.git.pull()

def current(name):
    repo = Repo(project_path(name))
    return repo.active_branch.name
