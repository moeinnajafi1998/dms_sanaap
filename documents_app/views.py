from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from minio import Minio
from datetime import timedelta
import uuid
from minio.error import S3Error
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

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
        instance = self.get_object()
        old_file_name = instance.file.name

        uploaded_file = self.request.FILES.get('file', None)

        if uploaded_file:
            new_file_name = f"{uuid.uuid4().hex}_{uploaded_file.name}"
            object_name = f"documents/{new_file_name}"

            minio_client = Minio(
                "127.0.0.1:9000",
                access_key="minioadmin",
                secret_key="minioadmin",
                secure=False
            )

            try:
                minio_client.put_object(
                    "auto-generated-bucket-media-files",
                    object_name,
                    uploaded_file.file,
                    length=uploaded_file.size,
                    content_type=uploaded_file.content_type
                )

                try:
                    minio_client.remove_object(
                        "auto-generated-bucket-media-files",
                        old_file_name 
                    )
                except S3Error as e:
                    print(e)

                serializer.save(file=object_name)

            except Exception as e:
                print(e)

        else:
            serializer.save()



class DocumentDestroyView(generics.DestroyAPIView):
    queryset = Document.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def perform_destroy(self, instance):
        file_name = instance.file.name  
        minio_client = Minio(
            "127.0.0.1:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )

        try:
            minio_client.remove_object(
                "auto-generated-bucket-media-files",  
                file_name                             
            )
            print(file_name) 
        except S3Error as e:
            print(e)

        super().perform_destroy(instance)


class GenerateDocumentURLView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, document_id):
        minio_client = Minio(
            "127.0.0.1:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False
        )

        try:
            document = Document.objects.get(id=document_id)
            file_name = document.file.name

            expiration = timedelta(seconds=3600)  # 1 hour expiration

            # Generate pre-signed URL with expiration time
            url = minio_client.presigned_get_object("auto-generated-bucket-media-files",file_name, expires=expiration)
            return Response({"url": url})
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=404)
