from django.urls import path
from .views import *

urlpatterns = [
    path('documents/', DocumentListView.as_view(), name='document-list'),
    path('documents/create/', DocumentCreateView.as_view(), name='document-create'),
    path('documents/<int:pk>/', DocumentRetrieveView.as_view(), name='document-retrieve'),
    path('documents/<int:pk>/update/', DocumentUpdateView.as_view(), name='document-update'),
    path('documents/<int:pk>/delete/', DocumentDestroyView.as_view(), name='document-delete'),
    path('documents/<int:document_id>/generate-url/', GenerateDocumentURLView.as_view(), name='generate-document-url'),

]
