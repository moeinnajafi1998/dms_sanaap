from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from ...models import Document  # اگر اسم اپت documents نیست تغییر بده

class Command(BaseCommand):
    help = "Create default user roles: admin, editor, viewer"

    def handle(self, *args, **kwargs):
        # ابتدا بررسی کنیم قبلا ساخته نشده باشن
        roles = ['admin', 'editor', 'viewer']
        for role in roles:
            group, created = Group.objects.get_or_create(name=role)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Group '{role}' created."))
            else:
                self.stdout.write(self.style.WARNING(f"Group '{role}' already exists."))

        # گرفتن پرمیشن‌های مربوط به مدل Document
        content_type = ContentType.objects.get_for_model(Document)

        all_permissions = Permission.objects.filter(content_type=content_type)

        # تخصیص پرمیشن‌ها به هر نقش:
        # Admin: همه‌چیز
        Group.objects.get(name='admin').permissions.set(all_permissions)

        # Editor: فقط add و change
        editor_perms = all_permissions.filter(codename__in=['add_document', 'change_document'])
        Group.objects.get(name='editor').permissions.set(editor_perms)

        # Viewer: فقط view
        viewer_perms = all_permissions.filter(codename__in=['view_document'])
        Group.objects.get(name='viewer').permissions.set(viewer_perms)

        self.stdout.write(self.style.SUCCESS("Permissions assigned successfully."))
