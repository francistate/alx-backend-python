from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory


# Signal for User Notifications
@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Signal that listens for new messages and automatically creates a
    notification for the receiving user.
    """
    if created:
        # Determine notification type based on whether it's a reply
        notification_type = 'message_reply' if instance.parent_message else 'new_message'
        
        # Create notification content
        if instance.parent_message:
            content = f"{instance.sender.username} replied to your message: {instance.content[:100]}..."
        else:
            content = f"New message from {instance.sender.username}: {instance.content[:100]}..."
        
        # Create the notification
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            notification_type=notification_type,
            content=content
        )


# Signal for Logging Message Edits
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Signal that uses pre_save to log the old content of a message 
    into a separate MessageHistory model before it's updated.
    """
    if instance.pk:  # Only for existing messages (updates, not creates)
        try:
            # Get the old version of the message
            old_message = Message.objects.get(pk=instance.pk)
            
            # Check if the content has actually changed
            if old_message.content != instance.content:
                # Create history record with old content
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content,
                    edited_by=instance.sender  # Assuming sender is the editor
                )
                
                # Mark message as edited
                instance.edited = True
        except Message.DoesNotExist:
            # This shouldn't happen but just in case
            pass


# Signal for Deleting User-Related Data
@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Signal that automatically cleans up related data when a user deletes their account.
    This includes messages, notifications, and message histories.
    """
    # Delete all messages sent by the user
    Message.objects.filter(sender=instance).delete()
    
    # Delete all messages received by the user
    Message.objects.filter(receiver=instance).delete()
    
    # Delete all notifications for the user
    Notification.objects.filter(user=instance).delete()
    
    # Delete all message edit histories by the user
    MessageHistory.objects.filter(edited_by=instance).delete()
    
    # Note: CASCADE relationships will handle most of this automatically,
    # but this signal provides explicit control and can be extended for custom logic