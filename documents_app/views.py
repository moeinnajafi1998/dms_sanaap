from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.core.files.storage import default_storage

from .models import Document
from .serializers import DocumentSerializer,DocumentCreateUpdateSerializer
from .permissions import IsOwnerOrAdminOrEditor, IsAdmin,IsEditor
from .pagination import DocumentPagination


class DocumentListView(generics.ListAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrEditor]
    pagination_class = DocumentPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ['owner', 'title']  
    # ordering_fields = ['created_at', 'title'] 

    def get_queryset(self):
        user = self.request.user
        queryset = Document.objects.all()

        if user.groups.filter(name='admin').exists():
            return queryset
        return queryset.filter(owner=user)


class DocumentCreateView(generics.CreateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrEditor]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class DocumentRetrieveView(generics.RetrieveAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

class DocumentUpdateView(generics.UpdateAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrEditor]

    def perform_update(self, serializer):
        serializer.save()


class DocumentDestroyView(generics.DestroyAPIView):
    queryset = Document.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def perform_destroy(self, instance):
        file_name = instance.file.name
        if file_name and default_storage.exists(file_name):
            default_storage.delete(file_name)
        super().perform_destroy(instance)

class GenerateDocumentURLView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, document_id):
        try:
            document = Document.objects.get(id=document_id)
            file = document.file
            url = default_storage.url(file.name)
            return Response({"url": url})
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=404)
