from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Conversation, Message


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'role', 'created_at')
        }),
    )
    readonly_fields = ('user_id', 'created_at')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('conversation_id', 'participant_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('participants__email', 'participants__first_name', 'participants__last_name')
    filter_horizontal = ('participants',)
    readonly_fields = ('conversation_id', 'created_at')
    
    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'sender', 'conversation', 'message_preview', 'sent_at')
    list_filter = ('sent_at',)
    search_fields = ('sender__email', 'message_body')
    readonly_fields = ('message_id', 'sent_at')
    
    def message_preview(self, obj):
        return obj.message_body[:50] + "..." if len(obj.message_body) > 50 else obj.message_body
    message_preview.short_description = 'Message Preview'
