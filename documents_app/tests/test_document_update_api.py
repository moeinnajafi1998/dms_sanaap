import io
from unittest import mock
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from documents_app.models import Document

User = get_user_model()

class DocumentUpdateViewTest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='pass')
        self.other_user = User.objects.create_user(username='other', password='pass')
        self.admin = User.objects.create_user(username='admin', password='pass')
        self.admin.groups.create(name='admin')

        self.doc = Document.objects.create(
            title='Old Title',
            description='Old description',
            owner=self.owner,
            file='documents/oldfile.txt'
        )

        self.url = reverse('document-update', kwargs={'pk': self.doc.pk})

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

    @mock.patch('documents_app.views.Minio')
    def test_owner_can_update_with_file(self, mock_minio):
        self.authenticate(self.owner)

        new_file = SimpleUploadedFile('newfile.txt', b'updated content', content_type='text/plain')

        data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'file': new_file
        }

        response = self.client.patch(self.url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Title')

    def test_unauthenticated_user_cannot_update(self):
        response = self.client.patch(self.url, {'title': 'New title'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_owner_non_admin_cannot_update(self):
        self.authenticate(self.other_user)
        response = self.client.patch(self.url, {'title': 'Hack title'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch('documents_app.views.Minio')
    def test_admin_can_update(self, mock_minio):
        self.authenticate(self.admin)
        response = self.client.patch(self.url, {'title': 'Admin updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Admin updated')
