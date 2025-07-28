from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    
    # override the default id field with UUID
    user_id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        db_index=True
    )
    
    # required fields from specification
    first_name = models.CharField(max_length=150, null=False, blank=False)
    last_name = models.CharField(max_length=150, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)

    phone_number = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(
        max_length=10, 
        choices=ROLE_CHOICES, 
        null=False, 
        blank=False,
        default='guest'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        # db_table = 'chats_user'
        indexes = [
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    # if required
    # @property
    # def password_hash(self):
    #     return self.password


class Conversation(models.Model):
    """
    Conversation model that tracks which users are involved in a conversation
    """
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    # many-to-many relationship with User for participants
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        blank=False
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chats_conversation'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        participant_names = ", ".join([user.full_name for user in self.participants.all()[:3]])
        if self.participants.count() > 3:
            participant_names += f" and {self.participants.count() - 3} others"
        return f"Conversation: {participant_names}"
    
    @property
    def participant_count(self):
        return self.participants.count()
    
    def get_latest_message(self):
        return self.messages.first()  # assuming messages are ordered by sent_at desc


class Message(models.Model):
    """
    Message model containing the sender, conversation and message content
    """
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True
    )
    
    # foreign key to User (sender)
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        null=False
    )
    
    # foreign key to conversation
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
        null=False
    )
    
    message_body = models.TextField(null=False, blank=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chats_message'
        ordering = ['-sent_at']  # latest messages first
        indexes = [
            models.Index(fields=['sent_at']),
            models.Index(fields=['sender']),
            models.Index(fields=['conversation']),
        ]
    
    def __str__(self):
        preview = self.message_body[:50] + "..." if len(self.message_body) > 50 else self.message_body
        return f"{self.sender.full_name}: {preview}"
