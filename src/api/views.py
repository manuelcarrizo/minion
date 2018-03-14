import http
import shutil

from rest_framework import status as http_status
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from src.api import common

from src.api.models import Project, Port, Volume
from src.api.serializers import ProjectSerializer, PortSerializer, VolumeSerializer

import src.api.docker_adapter as docker_adapter
import src.api.git_adapter as git_adapter

class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows projects to be viewed or edited.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    @detail_route(methods=["get", "post"])
    def status(self, request, pk=None):
        project = Project.objects.get(pk=pk)
        name = project.lower()

        if request.method == 'GET':
            container = docker_adapter.get(name)
            print(container)
            return Response(container.status)
        elif request.method == 'POST':
            command = request.data.get('command', None)
            if command == 'start':
                tag = request.data.get('tag', 'latest')
                id = docker_adapter.start(name, tag, project.port)
                return Response(id)
            elif command == 'stop':
                res = docker_adapter.stop(name)
                return Response(res)
            else:
                return Response('command is required', status=http_status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def build(self, request, pk=None):
        project = Project.objects.get(pk=pk)
        name = project.lower()
        branch = request.data.get('branch', git_adapter.current(name))

        if branch != git_adapter.current(name):
            print("Switching to branch", branch)
            git_adapter.checkout(name, branch)

        git_adapter.pull(name)
        common.background_task(docker_adapter.build, name, branch)

        return Response("Building %s" % branch)

    @detail_route(methods=['post'])
    def reset(self, request, pk=None):
        project = Project.objects.get(pk=pk)
        name = project.lower()

        try:
            shutil.rmtree(common.project_path(name))
        except FileNotFoundError:
            pass
        git_adapter.clone(name, project.url)

        return Response('Success')

    @detail_route(methods=['get'])
    def branches(self, request, pk=None):
        project = Project.objects.get(pk=pk)

        return Response(git_adapter.branches(project.lower()))

    @detail_route(methods=['get'])
    def releases(self, request, pk=None):
        project = Project.objects.get(pk=pk)

        return Response(git_adapter.tags(project.lower()))

    def endpoint_url(self, name, port):
        return docker_adapter.base_url(name, port)

    @detail_route(methods=['get'])
    def endpoint(self, request, pk=None):
        project = Project.objects.get(pk=pk)

        return Response(self.endpoint_url(project.lower(), project.port))
    
    @detail_route(methods=['get'])
    def tags(self, request, pk=None):
        project = Project.objects.get(pk=pk)

        return Response(docker_adapter.images(project.lower()))


"""
    @detail_route(methods=['get'])
    def ping(self, request, pk=None):
        project = Project.objects.get(pk=pk)
        name = project.lower()

        endpoint = self.endpoint_url(project.lower(), project.port)

        try:
            print("getting", endpoint, project.pingpath)
            conn = http.client.HTTPConnection(endpoint)
            conn.request("HEAD", project.pingpath)
            response = conn.getresponse()
            print(response.reason, response.read())
            return Response(response.status)
        except Exception as e:
            print(e)
            return Response("Could not ping application")
"""

class PortViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ports to be viewed or edited.
    """
    queryset = Port.objects.all()
    serializer_class = PortSerializer

class VolumeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows volumes to be viewed or edited.
    """
    queryset = Volume.objects.all()
    serializer_class = VolumeSerializer

