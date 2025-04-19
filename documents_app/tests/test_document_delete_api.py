from unittest import mock
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from documents_app.models import Document

User = get_user_model()

class DocumentDestroyViewTest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='pass')
        self.admin = User.objects.create_user(username='admin', password='pass')
        self.admin.groups.create(name='admin')

        self.doc = Document.objects.create(
            title='Document to delete',
            description='Description of the document',
            owner=self.owner,
            file='documents/to-delete.txt'
        )

        self.url = reverse('document-delete', kwargs={'pk': self.doc.pk})

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

    @mock.patch('documents_app.views.Minio')
    def test_admin_can_delete_document(self, mock_minio):
        self.authenticate(self.admin)
        
        # Mock Minio client behavior
        mock_minio_client = mock.Mock()
        mock_minio.return_value = mock_minio_client
        
        # Simulate deletion
        response = self.client.delete(self.url)

        # Assert the file was removed from Minio
        mock_minio_client.remove_object.assert_called_once_with(
            "auto-generated-bucket-media-files", 
            'documents/to-delete.txt'
        )

        # Assert status code is 204 (no content, successful delete)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_admin_cannot_delete_document(self):
        self.authenticate(self.owner)  # The owner is not an admin
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_delete_document(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
