# python manage.py test documents_app.tests.test_document_create_api

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group
from documents_app.models import Document
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class DocumentCreateViewTest(APITestCase):
    def setUp(self):
        # Create groups if they don't exist
        Group.objects.get_or_create(name='editor')
        Group.objects.get_or_create(name='admin')

        # Create a user and add them to the 'editor' group
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.user.groups.add(Group.objects.get(name='editor'))

        # Define the URL for document creation
        self.create_url = reverse('document-create')  # Make sure this name matches your urls.py

    def authenticate(self):
        """Helper method to authenticate the test client using JWT"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

    def test_create_document_authenticated(self):
        """Authenticated user can successfully create a document with a file"""
        self.authenticate()

        # Create a dummy file to upload
        file = SimpleUploadedFile("testfile.txt", b"This is a test file.", content_type="text/plain")

        data = {
            "title": "Test Document",
            "description": "This is a test document.",
            "file": file
        }

        response = self.client.post(self.create_url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(Document.objects.first().owner, self.user)

    def test_create_document_unauthenticated(self):
        """Unauthenticated users should not be able to create documents"""
        file = SimpleUploadedFile("unauth.txt", b"Unauthorized file content.", content_type="text/plain")

        data = {
            "title": "Should Fail",
            "description": "Unauthorized",
            "file": file
        }

        response = self.client.post(self.create_url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Document.objects.count(), 0)
