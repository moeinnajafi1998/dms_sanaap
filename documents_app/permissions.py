from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='admin').exists()

class IsEditor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='editor').exists()

class IsViewer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='viewer').exists()

class IsOwnerOrAdminOrEditor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name='admin').exists():
            return True
        if request.user.groups.filter(name='editor').exists():
            return True
        return obj.owner == request.user

class IsAdminOrEditor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name__in=['admin', 'editor']).exists()

class IsViewerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.groups.filter(name='admin').exists():
            return True
        return request.user.groups.filter(name='viewer').exists()