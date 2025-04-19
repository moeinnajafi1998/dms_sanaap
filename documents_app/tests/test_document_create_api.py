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
        # Create groups
        self.editor_group, _ = Group.objects.get_or_create(name='editor')
        self.admin_group, _ = Group.objects.get_or_create(name='admin')
        self.viewer_group, _ = Group.objects.get_or_create(name='viewer')

        # Create users
        self.editor_user = User.objects.create_user(username='editor', password='password123')
        self.editor_user.groups.add(self.editor_group)

        self.admin_user = User.objects.create_user(username='admin', password='adminpass')
        self.admin_user.groups.add(self.admin_group)

        self.viewer_user = User.objects.create_user(username='viewer', password='viewpass')
        self.viewer_user.groups.add(self.viewer_group)

        self.create_url = reverse('document-create')

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_editor_can_create_document(self):
        self.authenticate(self.editor_user)

        file = SimpleUploadedFile("editor.txt", b"Editor file content", content_type="text/plain")
        data = {
            "title": "Editor Doc",
            "description": "By editor",
            "file": file
        }

        response = self.client.post(self.create_url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(Document.objects.first().owner, self.editor_user)

    def test_admin_can_create_document(self):
        self.authenticate(self.admin_user)

        file = SimpleUploadedFile("admin.txt", b"Admin file content", content_type="text/plain")
        data = {
            "title": "Admin Doc",
            "description": "By admin",
            "file": file
        }

        response = self.client.post(self.create_url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(Document.objects.first().owner, self.admin_user)

    def test_unauthenticated_cannot_create_document(self):
        file = SimpleUploadedFile("unauth.txt", b"Unauthorized", content_type="text/plain")
        data = {
            "title": "Unauth Doc",
            "description": "No auth",
            "file": file
        }

        response = self.client.post(self.create_url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Document.objects.count(), 0)

    def test_viewer_cannot_create_document(self):
        self.authenticate(self.viewer_user)

        file = SimpleUploadedFile("viewer.txt", b"Viewer file", content_type="text/plain")
        data = {
            "title": "Viewer Doc",
            "description": "Viewer tries",
            "file": file
        }

        response = self.client.post(self.create_url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Document.objects.count(), 0)

    def test_missing_file_field(self):
        self.authenticate(self.editor_user)

        data = {
            "title": "No file document",
            "description": "Missing file"
        }

        response = self.client.post(self.create_url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("file", response.data)

