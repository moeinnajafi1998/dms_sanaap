from rest_framework import serializers

from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        exclude = ["file",]
        read_only_fields = ('owner', 'created_at', 'updated_at')

class DocumentCreateSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True, required=True)
    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = ('owner', 'created_at', 'updated_at')