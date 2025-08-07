from django.contrib import admin
from .models import Message, Notification, MessageHistory


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model."""
    list_display = ['sender', 'receiver', 'content_preview', 'timestamp', 'edited', 'read']
    list_filter = ['edited', 'read', 'timestamp']
    search_fields = ['sender__username', 'receiver__username', 'content']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model."""
    list_display = ['user', 'notification_type', 'content_preview', 'created_at', 'read']
    list_filter = ['notification_type', 'read', 'created_at']
    search_fields = ['user__username', 'content']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    """Admin interface for MessageHistory model."""
    list_display = ['message', 'old_content_preview', 'edited_at', 'edited_by']
    list_filter = ['edited_at']
    search_fields = ['message__content', 'old_content', 'edited_by__username']
    date_hierarchy = 'edited_at'
    ordering = ['-edited_at']
    
    def old_content_preview(self, obj):
        return obj.old_content[:50] + "..." if len(obj.old_content) > 50 else obj.old_content
    old_content_preview.short_description = 'Old Content Preview'
