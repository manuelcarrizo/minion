import os

from django.conf import settings
import docker
from src.api.common import project_path, volumes_path

client = docker.from_env()

def get(name, tag='latest', all=True):
    image = "minion/%s:%s" % (name, tag)
    for container in client.containers.list(all=all):
        if container.attrs['Config']['Image'] == image:
            return container
    return None

def start(project):
    image = "minion/%s:%s" % (project.lower(), project.image)
    ports = { '%d/%s' % (p.container, p.protocol ): p.host for p in project.ports.all() }
    volumes = {'%s%s' % (volumes_path(project.lower()), v.path):
                    {'bind': v.path, 'mode': 'rw'} for v in project.volumes.all() }

    container = client.containers.run(image, detach=True, stdout=True, stderr=True, ports=ports, volumes=volumes)
    return container.id

def stop(name, tag='latest'):
    container = get(name, tag)
    if container:
        print("stopping %s" % container.id)
        container.stop()

def images(name):
    filter = "minion/%s" % name
    repotags = [i.attrs['RepoTags'] for i in client.images.list()]
    return [item.split(':')[1] for items in repotags for item in items if item.startswith(filter)]

def build(name, tag):
    try:
        print("docker_adapter.build")
        image = "minion/%s:%s" % (name, tag)
        img, logs = client.images.build(path=project_path(name), tag=image, rm=True)

        print("docker_adapter.build about to read logs")
        for line in logs:
            print(line)
            message = line.get('stream', '').strip()
            if len(message):
                print(message)
    except Exception as e:
        print("error", e)

def base_url(name, image, port):
    container = get(name, image, False)
    docker_port = "%d/%s" % (port.container, port.protocol)

    try:
        entry = container.attrs['NetworkSettings']['Ports'][docker_port][0]

        ret = entry['HostIp'] + ":" + entry['HostPort']
    except:
        ret = None

    return ret
