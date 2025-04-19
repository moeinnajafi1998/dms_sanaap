# python manage.py test documents_app.tests.test_document_retrieve_api

from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import Group
from documents_app.models import Document

User = get_user_model()

class DocumentRetrieveViewTest(APITestCase):
    def setUp(self):
        # Create groups
        self.admin_group, _ = Group.objects.get_or_create(name='admin')
        self.editor_group, _ = Group.objects.get_or_create(name='editor')
        self.viewer_group, _ = Group.objects.get_or_create(name='viewer')

        # Create users
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.other_user = User.objects.create_user(username='otheruser', password='password456')
        self.admin_user = User.objects.create_user(username='admin', password='adminpass')
        self.editor_user = User.objects.create_user(username='editor', password='editorpass')
        self.viewer_user = User.objects.create_user(username='viewer', password='viewerpass')

        self.admin_user.groups.add(self.admin_group)
        self.editor_user.groups.add(self.editor_group)
        self.viewer_user.groups.add(self.viewer_group)

        # Create a document owned by `self.user`
        self.document = Document.objects.create(
            title='Sample Document',
            description='Just a test.',
            owner=self.user
        )

        self.retrieve_url = reverse('document-retrieve', kwargs={'pk': self.document.pk})

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

    def test_retrieve_document_as_viewer(self):
        """Viewer group can retrieve the document"""
        self.authenticate(self.viewer_user)
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.document.title)

    def test_retrieve_document_as_admin(self):
        """Admin group can retrieve the document"""
        self.authenticate(self.admin_user)
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_document_as_editor_forbidden(self):
        """Editor group is not allowed to retrieve"""
        self.authenticate(self.editor_user)
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_document_authenticated_owner_forbidden(self):
        """Being the owner is not enough (not in viewer/admin group)"""
        self.authenticate(self.user)
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_document_unauthenticated(self):
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_document_not_owner_and_not_in_group(self):
        """User not owner, not in viewer/admin"""
        self.authenticate(self.other_user)
        response = self.client.get(self.retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_nonexistent_document(self):
        self.authenticate(self.viewer_user)
        bad_url = reverse('document-retrieve', kwargs={'pk': 9999})
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
