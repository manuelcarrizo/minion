from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from src.api.models import Project
from src.api.serializers import ProjectSerializer

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

    @detail_route(methods=['post'])
    def build(self, request, pk=None):
        project = Project.objects.get(pk=pk)
        name = project.lower()
        branch = request.data.get('branch', git_adapter.current(name))

        if branch != git_adapter.current(name):
            git_adapter.checkout(name, branch)

        git_adapter.pull(name)
        docker_adapter.build(name, branch)

        return Response("Building %s" % branch)