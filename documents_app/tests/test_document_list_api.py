# python manage.py test documents_app.tests.test_document_list_api

from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from documents_app.models import Document
from rest_framework import status
from django.urls import reverse

User = get_user_model()

class DocumentListViewTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(username='admin', password='adminpass')
        self.editor_user = User.objects.create_user(username='editor', password='editorpass')

        # Assign group names (you must have these groups created in test or fixtures)
        self.admin_user.groups.create(name='admin')
        self.editor_user.groups.create(name='editor')

        # Create documents
        self.doc1 = Document.objects.create(owner=self.admin_user, title='Admin Doc')
        self.doc2 = Document.objects.create(owner=self.editor_user, title='Editor Doc')

    def authenticate(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

    def test_admin_sees_all_documents(self):
        self.authenticate(self.admin_user)
        response = self.client.get(reverse('document-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_editor_sees_own_documents_only(self):
        self.authenticate(self.editor_user)
        response = self.client.get(reverse('document-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Editor Doc')

    def test_filter_by_owner(self):
        self.authenticate(self.admin_user)
        response = self.client.get(reverse('document-list'), {'owner': self.editor_user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_pagination_structure(self):
        self.authenticate(self.admin_user)
        response = self.client.get(reverse('document-list'))
        self.assertIn('total_items', response.data)
        self.assertIn('total_pages', response.data)
        self.assertIn('current_page', response.data)
