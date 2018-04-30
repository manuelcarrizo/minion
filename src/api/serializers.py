import os
from rest_framework import serializers
from src.api.models import Project, Port, Volume, EnvVar

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
        # sanitize
        validated_data['path'] = os.path.normpath("/" + validated_data['path']).replace("//", "/").replace(" ", "_")
        volume = Volume.objects.create(**validated_data)

        volume_path = common.volumes_path(volume.project.lower()) + volume.path
        os.makedirs(volume_path, exist_ok=True)

        return volume

class EnvVarSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnvVar
        fields = ('project', 'key', 'value')

    def create(self, validated_data):
        validated_data['key'] = validated_data['key'].replace(" ", "_")
        return EnvVar.objects.create(**validated_data)

class ProjectSerializer(serializers.ModelSerializer):
    ports = PortSerializer(many=True, required=False)
    volumes = VolumeSerializer(many=True, required=False)
    class Meta:
        model = Project
        depth = 1
        fields = ('id', 'name', 'url', 'image', 'ports', 'volumes', 'envvars')

    def create(self, validated_data):
        # sanitize name
        validated_data['name'] = validated_data['name'].replace(" ", "_")

        ports_data = validated_data.pop('ports', [])
        volumes_data = validated_data.pop('volumes', [])
        envvars_data = validated_data.pop('envvars', [])

        project = Project.objects.create(**validated_data)

        for ports in ports_data:
            Port.objects.create(project=project, **ports)

        for volumes in volumes_data:
            Volume.objects.create(project=project, **volumes)
        
        for envvars in envvars_data:
            EnvVar.objects.create(project=project, **envvars)

        common.background_task(git_adapter.clone, project.lower(), project.url)

        return project
    

