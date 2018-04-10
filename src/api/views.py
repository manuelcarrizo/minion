import http
import shutil

from django.conf import settings

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

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            shutil.rmtree(common.project_path(instance.lower()))
            self.perform_destroy(instance)
        except Exception as e:
            pass
        
        return Response(status=http_status.HTTP_204_NO_CONTENT)

    @detail_route(methods=["get", "post"])
    def status(self, request, pk=None):
        project = Project.objects.get(pk=pk)
        name = project.lower()

        if request.method == 'GET':
            # only get the running container
            container = docker_adapter.get(name, project.image, False)
            if container:
                return Response(container.status.upper())
            else:
                return Response('OFF')
        elif request.method == 'POST':
            command = request.data.get('command', None)
            tag = request.data.get('tag', project.image)

            if command == 'start':
                id = docker_adapter.start(project)
                return Response(id)
            elif command == 'stop':
                docker_adapter.stop(name, tag)
                return Response("Stopping %s" % name)
            elif command == 'restart':
                docker_adapter.stop(name, tag)
                id = docker_adapter.start(project)
                return Response(id)
            else:
                return Response('command is required', status=http_status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def build(self, request, pk=None):
        project = Project.objects.get(pk=pk)
        name = project.lower()

        print("about to build", request.data)

        branch = request.data.get('branch', None)
        tag = request.data.get('tag', None)

        git_adapter.pull(name)

        ref = branch or tag
        if ref:
            git_adapter.checkout(name, ref)
        else:
            return Response('Unknown branch or tag', status=http_status.HTTP_400_BAD_REQUEST)

        common.background_task(docker_adapter.build, name, ref)

        return Response("Building %s" % ref)

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

    @detail_route(methods=['get'])
    def endpoint(self, request, pk=None):
        project = Project.objects.get(pk=pk)

        port = project.ports.all()[:1].get()
        return Response("%s:%d" % (settings.SERVER_NAME, port.host))
    
    @detail_route(methods=['get'])
    def tags(self, request, pk=None):
        project = Project.objects.get(pk=pk)

        return Response(docker_adapter.images(project.lower()))

    @detail_route(methods=['post'])
    def deploy(self, request, pk=None):
        project = Project.objects.get(pk=pk)
        name = project.lower()

        tag = request.data.get('tag', None)

        if tag:
            print("deploying", name, 'from', project.image, 'to', tag)
            docker_adapter.stop(name, project.image)
            
            project.image = tag
            project.save()

            docker_adapter.start(project)

            return Response('Success')
        else:
            return Response('tag is required', status=http_status.HTTP_400_BAD_REQUEST)

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

