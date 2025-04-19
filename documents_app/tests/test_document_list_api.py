# python manage.py test documents_app.tests.test_document_list_api

from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from django.urls import reverse
from documents_app.models import Document

User = get_user_model()

class DocumentListViewTest(APITestCase):
    def setUp(self):
        # Ensure groups exist
        self.admin_group, _ = Group.objects.get_or_create(name='admin')
        self.viewer_group, _ = Group.objects.get_or_create(name='viewer')
        self.editor_group, _ = Group.objects.get_or_create(name='editor')

        # Users
        self.admin_user = User.objects.create_user(username='admin', password='adminpass')
        self.viewer_user = User.objects.create_user(username='viewer', password='viewerpass')
        self.editor_user = User.objects.create_user(username='editor', password='editorpass')

        self.admin_user.groups.add(self.admin_group)
        self.viewer_user.groups.add(self.viewer_group)
        self.editor_user.groups.add(self.editor_group)

        # Documents
        self.doc1 = Document.objects.create(owner=self.admin_user, title='Admin Doc')
        self.doc2 = Document.objects.create(owner=self.viewer_user, title='Viewer Doc')

        self.url = reverse('document-list')

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

    def test_admin_can_see_all_documents(self):
        self.authenticate(self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_viewer_sees_only_their_documents(self):
        self.authenticate(self.viewer_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Viewer Doc')

    def test_editor_is_forbidden(self):
        self.authenticate(self.editor_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_owner(self):
        self.authenticate(self.admin_user)
        response = self.client.get(self.url, {'owner': self.viewer_user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Viewer Doc')

    def test_filter_by_title(self):
        self.authenticate(self.admin_user)
        response = self.client.get(self.url, {'title': 'Admin Doc'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['owner'], self.admin_user.id)

    def test_pagination_fields_exist(self):
        self.authenticate(self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for field in ['total_items', 'total_pages', 'current_page', 'results']:
            self.assertIn(field, response.data)

    def test_unauthenticated_user_cannot_access_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
