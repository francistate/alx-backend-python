from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class UnreadMessagesManager(models.Manager):
    """Custom manager to filter unread messages for a specific user."""
    
    def unread_for_user(self, user):
        """Return unread messages for a specific user."""
        return self.filter(receiver=user, read=False).only(
            'id', 'sender', 'content', 'timestamp', 'read'
        )


class Message(models.Model):
    """
    Message model with fields for sender, receiver, content, timestamp,
    and additional fields for threaded conversations and read status.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='received_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Field to track if message has been edited
    edited = models.BooleanField(default=False)
    
    # Self-referential foreign key for threaded conversations
    parent_message = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies'
    )
    
    # Field to track read status
    read = models.BooleanField(default=False)
    
    # Custom managers
    objects = models.Manager()  # Default manager
    unread = UnreadMessagesManager()  # Custom manager for unread messages
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sender', 'timestamp']),
            models.Index(fields=['receiver', 'read']),
            models.Index(fields=['parent_message']),
        ]
    
    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}: {self.content[:50]}..."
    
    def get_thread_root(self):
        """Get the root message of the thread."""
        if self.parent_message:
            return self.parent_message.get_thread_root()
        return self
    
    def get_replies_count(self):
        """Get count of replies to this message."""
        return self.replies.count()


class Notification(models.Model):
    """
    Notification model to store notifications linked to User and Message models.
    """
    NOTIFICATION_TYPES = [
        ('new_message', 'New Message'),
        ('message_reply', 'Message Reply'),
        ('message_edited', 'Message Edited'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    message = models.ForeignKey(
        Message, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES, 
        default='new_message'
    )
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.notification_type}"


class MessageHistory(models.Model):
    """
    Model to store edit history of messages.
    Task 1: Store old content before message is updated.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(
        Message, 
        on_delete=models.CASCADE, 
        related_name='edit_history'
    )
    old_content = models.TextField()
    edited_at = models.DateTimeField(default=timezone.now)
    edited_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='message_edits'
    )
    
    class Meta:
        ordering = ['-edited_at']
        indexes = [
            models.Index(fields=['message', 'edited_at']),
        ]
    
    def __str__(self):
        return f"Edit history for message {self.message.id} at {self.edited_at}"
