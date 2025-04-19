# python manage.py test documents_app.tests.test_document_update_api

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Document  # adjust path if needed
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class DocumentUpdateAPITestCase(APITestCase):
    def setUp(self):
        # Create groups
        self.admin_group = Group.objects.create(name='admin')
        self.editor_group = Group.objects.create(name='editor')

        # Create users
        self.admin_user = User.objects.create_user(username='admin', password='pass123')
        self.editor_user = User.objects.create_user(username='editor', password='pass123')
        self.regular_user = User.objects.create_user(username='user', password='pass123')

        # Assign groups
        self.admin_user.groups.add(self.admin_group)
        self.editor_user.groups.add(self.editor_group)

        # Create document
        self.document = Document.objects.create(
            title='Test Document',
            description='Original description',
            file=SimpleUploadedFile("file.txt", b"file_content"),
            owner=self.admin_user
        )

        self.update_url = reverse('document-update', kwargs={'pk': self.document.pk})  # adjust name if needed

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    def test_admin_user_can_update_document(self):
        self.authenticate(self.admin_user)
        data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'file': SimpleUploadedFile("newfile.txt", b"new file content"),
            'owner': self.admin_user.pk
        }
        response = self.client.put(self.update_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.document.refresh_from_db()
        self.assertEqual(self.document.title, 'Updated Title')

    def test_editor_user_can_update_document(self):
        self.authenticate(self.editor_user)
        data = {
            'title': 'Editor Updated',
            'description': 'Changed by editor',
            'file': SimpleUploadedFile("editorfile.txt", b"editor content"),
            'owner': self.admin_user.pk
        }
        response = self.client.put(self.update_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_cannot_update_document(self):
        self.authenticate(self.regular_user)
        data = {
            'title': 'Hacker Title',
            'description': 'I should not be allowed',
            'file': SimpleUploadedFile("badfile.txt", b"bad content"),
            'owner': self.admin_user.pk
        }
        response = self.client.put(self.update_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_update_document(self):
        data = {
            'title': 'Anonymous Edit',
            'description': 'No login',
            'file': SimpleUploadedFile("anon.txt", b"anon content"),
            'owner': self.admin_user.pk
        }
        response = self.client.put(self.update_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)