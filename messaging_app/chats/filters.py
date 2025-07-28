import django_filters
from django.db import models
from django_filters import rest_framework as filters
from .models import Message, Conversation, User


class MessageFilter(filters.FilterSet):
    """
    Filter class for Message model to retrieve messages within time range
    and by conversation participants
    """
    # Date range filtering for messages
    sent_after = filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    sent_before = filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    sent_at_range = filters.DateFromToRangeFilter(field_name='sent_at')
    
    # Filter by sender
    sender_email = filters.CharFilter(field_name='sender__email', lookup_expr='icontains')
    sender_name = filters.CharFilter(method='filter_by_sender_name')
    
    # Filter by conversation
    conversation_id = filters.UUIDFilter(field_name='conversation__conversation_id')
    
    # Search in message content
    message_contains = filters.CharFilter(field_name='message_body', lookup_expr='icontains')
    
    class Meta:
        model = Message
        fields = {
            'sent_at': ['exact', 'gte', 'lte'],
            'message_body': ['icontains'],
            'conversation': ['exact'],
            'sender': ['exact'],
        }
    
    def filter_by_sender_name(self, queryset, name, value):
        """
        Filter messages by sender's first name or last name
        """
        return queryset.filter(
            models.Q(sender__first_name__icontains=value) |
            models.Q(sender__last_name__icontains=value)
        )


class ConversationFilter(filters.FilterSet):
    """
    Filter class for Conversation model to retrieve conversations with specific users
    """
    # Filter by participant email
    participant_email = filters.CharFilter(method='filter_by_participant_email')
    participant_name = filters.CharFilter(method='filter_by_participant_name')
    
    # Filter by creation date
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    created_at_range = filters.DateFromToRangeFilter(field_name='created_at')
    
    # Filter by number of participants
    min_participants = filters.NumberFilter(method='filter_by_min_participants')
    max_participants = filters.NumberFilter(method='filter_by_max_participants')
    
    class Meta:
        model = Conversation
        fields = {
            'created_at': ['exact', 'gte', 'lte'],
        }
    
    def filter_by_participant_email(self, queryset, name, value):
        """
        Filter conversations by participant email
        """
        return queryset.filter(participants__email__icontains=value).distinct()
    
    def filter_by_participant_name(self, queryset, name, value):
        """
        Filter conversations by participant name (first or last name)
        """
        return queryset.filter(
            models.Q(participants__first_name__icontains=value) |
            models.Q(participants__last_name__icontains=value)
        ).distinct()
    
    def filter_by_min_participants(self, queryset, name, value):
        """
        Filter conversations with minimum number of participants
        """
        return queryset.annotate(
            participant_count=models.Count('participants')
        ).filter(participant_count__gte=value)
    
    def filter_by_max_participants(self, queryset, name, value):
        """
        Filter conversations with maximum number of participants
        """
        return queryset.annotate(
            participant_count=models.Count('participants')
        ).filter(participant_count__lte=value)


class UserFilter(filters.FilterSet):
    """
    Filter class for User model
    """
    # Basic text search
    name = filters.CharFilter(method='filter_by_name')
    email = filters.CharFilter(field_name='email', lookup_expr='icontains')
    role = filters.ChoiceFilter(choices=[
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ])
    
    # Date filtering
    joined_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    joined_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = User
        fields = {
            'role': ['exact'],
            'is_active': ['exact'],
            'created_at': ['exact', 'gte', 'lte'],
        }
    
    def filter_by_name(self, queryset, name, value):
        """
        Filter users by first name or last name
        """
        return queryset.filter(
            models.Q(first_name__icontains=value) |
            models.Q(last_name__icontains=value)
        )