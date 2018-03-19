import os
from rest_framework import serializers
from src.api.models import Project, Port, Volume

from src.api import git_adapter
from src.api import common

class PortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Port
        fields = ('project', 'host', 'container', 'protocol')

class VolumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Volume
        fields = ('id', 'project', 'path',)
    
    def create(self, validated_data):
        volume = Volume.objects.create(**validated_data)

        volume_path = common.volumes_path(volume.project.lower()) + volume.path
        os.makedirs(volume_path, exist_ok=True)

        return volume

class ProjectSerializer(serializers.ModelSerializer):
    ports = PortSerializer(many=True)
    volumes = VolumeSerializer(many=True)
    class Meta:
        model = Project
        depth = 1
        fields = ('id', 'name', 'url', 'image', 'ports', 'volumes')

    def create(self, validated_data):
        ports_data = validated_data.pop('ports')
        volumes_data = validated_data.pop('volumes')

        project = Project.objects.create(**validated_data)

        for port_data in ports_data:
            Port.objects.create(project=project, **port_data)

        for volume_data in volumes_data:
            Volume.objects.create(project=project, **volume_data)

        common.background_task(git_adapter.clone, project.lower(), project.url)

        return project
    

