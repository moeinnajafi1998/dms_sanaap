from rest_framework import serializers

from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        exclude = ["file",]
        read_only_fields = ('owner', 'created_at', 'updated_at')