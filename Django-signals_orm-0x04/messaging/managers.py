from django.db import models


class UnreadMessagesManager(models.Manager):
    """
    Custom manager to filter unread messages for a specific user.
    Task 4: Implement custom manager that filters unread messages for a specific user.
    """
    
    def unread_for_user(self, user):
        """
        Return unread messages for a specific user.
        Uses .only() to retrieve only necessary fields for optimization.
        """
        return self.filter(receiver=user, read=False).only(
            'id', 'sender', 'content', 'timestamp', 'read'
        ).select_related('sender')
    
    def unread_count_for_user(self, user):
        """Return count of unread messages for a specific user."""
        return self.filter(receiver=user, read=False).count()
    
    def mark_as_read_for_user(self, user, message_ids=None):
        """
        Mark messages as read for a specific user.
        If message_ids is provided, mark only those messages.
        Otherwise, mark all unread messages for the user.
        """
        queryset = self.filter(receiver=user, read=False)
        
        if message_ids:
            queryset = queryset.filter(id__in=message_ids)
        
        return queryset.update(read=True)
    
    def unread_by_sender(self, receiver, sender):
        """Get unread messages from a specific sender to a specific receiver."""
        return self.filter(
            receiver=receiver, 
            sender=sender, 
            read=False
        ).only('id', 'content', 'timestamp', 'read')
    
    def get_queryset(self):
        """
        Override get_queryset to return only unread messages by default.
        This makes the manager always filter for unread messages.
        """
        return super().get_queryset().filter(read=False)