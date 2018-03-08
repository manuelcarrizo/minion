from rest_framework import serializers
from src.api.models import Project

from src.api import git_adapter

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name', 'url', 'port')

    def create(self, validated_data):
        obj = Project.objects.create(**validated_data)
        obj.save()

        git_adapter.clone(obj.name, obj.url)

        return obj
