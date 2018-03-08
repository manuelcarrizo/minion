import os

import docker
from src.api.common import project_path

client = docker.from_env()

def get(name):
    for container in client.containers.list(all=True):
        if container.attrs['Config']['Image'] == name:
            return container
    return None

def start(name, tag, port):
    container = client.containers.run(name, detach=True, ports={port: None})
    return container.id

def stop(name):
    container = get(name)
    if container:
        print("stopping %s" % container.id)
        container.stop()

def images():
    pass

def build(name, tag):
    image = "minion/%s:%s" % (name, tag)
    img, logs = client.images.build(path=project_path(name), tag=image, rm=True)

    for line in logs:
        message = line.get('stream', '').strip()
        if len(message):
            print(message)