from django.contrib import admin

from .models import Document

class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at', 'updated_at')  
    list_filter = ('owner', 'created_at')  
    search_fields = ('title', 'description')  
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')  
    fields = ('title', 'description', 'file', 'owner')  
    save_on_top = True  

admin.site.register(Document, DocumentAdmin)

