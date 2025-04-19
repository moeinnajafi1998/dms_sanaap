# python manage.py test documents_app.tests.test_document_retrieve_api

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from documents_app.models import Document

User = get_user_model()

class DocumentRetrieveViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.other_user = User.objects.create_user(username='otheruser', password='password456')

        self.document = Document.objects.create(
            title='Sample Document',
            description='Just a test.',
            owner=self.user
        )

        self.retrieve_url = reverse('document-retrieve', kwargs={'pk': self.document.pk})

    def authenticate(self, user=None):
        user = user or self.user
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

    def test_retrieve_document_authenticated(self):
        self.authenticate()
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.document.title)

    def test_retrieve_document_unauthenticated(self):
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_nonexistent_document(self):
        self.authenticate()
        bad_url = reverse('document-retrieve', kwargs={'pk': 9999})
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
