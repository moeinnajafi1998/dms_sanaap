# python manage.py test documents_app.tests.test_document_delete_api

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
        # Create users: owner and admin
        self.owner = User.objects.create_user(username='owner', password='pass')
        self.admin = User.objects.create_user(username='admin', password='pass')
        self.admin.groups.create(name='admin')

        # Create a document to delete
        self.doc = Document.objects.create(
            title='Document to delete',
            description='Description of the document',
            owner=self.owner,
            file='documents/to-delete.txt'  # mock this for the test if needed
        )

        # URL for the delete endpoint
        self.url = reverse('document-delete', kwargs={'pk': self.doc.pk})

    def authenticate(self, user):
        """Authenticate a user by JWT token"""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

    @mock.patch('documents_app.views.default_storage')
    def test_admin_can_delete_document(self, mock_storage):
        """Test that an admin can delete a document"""
        self.authenticate(self.admin)

        # Mock the behavior of file deletion
        mock_storage.delete.return_value = True

        # Perform the delete request
        response = self.client.delete(self.url)

        # Assert that the delete method was called on the file storage
        mock_storage.delete.assert_called_once_with(self.doc.file.name)

        # Assert that the status code is 204 (successful delete)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_admin_cannot_delete_document(self):
        """Test that a non-admin user (the owner) cannot delete the document"""
        self.authenticate(self.owner)  # Owner is not an admin
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_delete_document(self):
        """Test that an unauthenticated user cannot delete a document"""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
