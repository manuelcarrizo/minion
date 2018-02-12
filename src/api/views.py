from rest_framework import viewsets

from src.api.models import Project
from src.api.serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


