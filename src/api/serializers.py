from rest_framework import serializers
from src.api.models import Project, Port, Volume

from src.api import git_adapter

class PortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Port
        fields = ('id', 'number')

class VolumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Volume
        fields = ('id', 'path')
class ProjectSerializer(serializers.ModelSerializer):
    ports = PortSerializer(many=True)
    volumes = VolumeSerializer(many=True)
    class Meta:
        model = Project
        depth = 1
        fields = ('id', 'name', 'url', 'image', 'ports', 'volumes')

    # def create(self, validated_data):
    #     print("creating project")
    #     print("data", validated_data)
    #     obj = Project.objects.create(**validated_data)
    #     obj.save()

    #     print("cloning", obj.url)
    #     git_adapter.clone(obj.name, obj.url)

    #     return obj
