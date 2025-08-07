from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class ThreadedMessage(models.Model):
    """
    Task 3: Model specifically for threaded conversations
    with optimized parent_message relationship
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='threaded_sent_messages'
    )
    receiver = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='threaded_received_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Self-referential foreign key for threaded conversations
    parent_message = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies',
        db_index=True  # Optimize for queries
    )
    
    # Track thread depth for optimization
    thread_depth = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sender', 'timestamp']),
            models.Index(fields=['receiver', 'timestamp']),
            models.Index(fields=['parent_message', 'timestamp']),
            models.Index(fields=['thread_depth']),
        ]
    
    def save(self, *args, **kwargs):
        """Override save to automatically set thread_depth."""
        if self.parent_message:
            self.thread_depth = self.parent_message.thread_depth + 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        depth_indicator = "  " * self.thread_depth + "└─ " if self.thread_depth > 0 else ""
        return f"{depth_indicator}Message from {self.sender.username}: {self.content[:50]}..."
    
    def get_thread_root(self):
        """Get the root message of the thread."""
        if self.parent_message:
            return self.parent_message.get_thread_root()
        return self
    
    def get_all_replies(self):
        """Get all replies in this thread recursively."""
        replies = []
        direct_replies = self.replies.select_related('sender', 'receiver').order_by('timestamp')
        
        for reply in direct_replies:
            replies.append(reply)
            replies.extend(reply.get_all_replies())
        
        return replies
    
    def get_thread_participants(self):
        """Get all users who participated in this thread."""
        thread_root = self.get_thread_root()
        all_messages = [thread_root] + thread_root.get_all_replies()
        
        participants = set()
        for message in all_messages:
            participants.add(message.sender)
            participants.add(message.receiver)
        
        return list(participants)
