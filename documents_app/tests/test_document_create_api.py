# python manage.py test documents_app.tests.test_document_create_api

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group
from documents_app.models import Document

User = get_user_model()

class DocumentCreateViewTest(APITestCase):
    def setUp(self):
        Group.objects.get_or_create(name='editor')
        Group.objects.get_or_create(name='admin')

        self.user = User.objects.create_user(username='testuser', password='password123')
        self.user.groups.add(Group.objects.get(name='editor'))  # Optional group role

        self.create_url = reverse('document-create')

    def authenticate(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

    def test_create_document_authenticated(self):
        self.authenticate()
        data = {
            "title": "Test Document",
            "description": "This is a test document."
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(Document.objects.first().owner, self.user)

    def test_create_document_unauthenticated(self):
        data = {
            "title": "Should Fail",
            "description": "Unauthorized"
        }
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
