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
    image = "minion/%s:%s" % (name, tag)
    container = client.containers.run(image, detach=True, ports={port: None})
    return container.id

def stop(name):
    container = get(name)
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

def base_url(name, port):
    container = get(name)
    docker_port = "%d/tcp" % port

    try:
        entry = container.attrs['NetworkSettings']['Ports'][docker_port][0]

        ret = entry['HostIp'] + ":" + entry['HostPort']
    except:
        ret = None

    return ret