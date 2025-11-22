from django.contrib import admin
from .models import TODO


@admin.register(TODO)
class TODOAdmin(admin.ModelAdmin):
    list_display = ('title', 'due_date', 'is_resolved', 'created_at', 'updated_at')
    list_filter = ('is_resolved', 'due_date', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('TODO Information', {
            'fields': ('title', 'description')
        }),
        ('Status & Dates', {
            'fields': ('is_resolved', 'due_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
