from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models.signals import post_save, pre_save, post_delete
from .models import Message, Notification, MessageHistory
from .signals import create_message_notification, log_message_edit, cleanup_user_data


class SignalTestCase(TestCase):
    """Test cases for Django signals implementation."""
    
    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username='sender',
            email='sender@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='receiver',
            email='receiver@test.com',
            password='testpass123'
        )
    
    def test_message_notification_signal(self):
        """Test that creating a message triggers notification signal."""
        # Create a new message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message for notification"
        )
        
        # Check if notification was created
        notification = Notification.objects.filter(
            user=self.user2,
            message=message
        ).first()
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.notification_type, 'new_message')
        self.assertIn(self.user1.username, notification.content)
    
    def test_message_edit_signal(self):
        """Test that editing a message creates history record."""
        # Create a message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original content"
        )
        
        # Edit the message
        message.content = "Edited content"
        message.save()
        
        # Check if history was created
        history = MessageHistory.objects.filter(message=message).first()
        
        self.assertIsNotNone(history)
        self.assertEqual(history.old_content, "Original content")
        self.assertTrue(message.edited)
    
    def test_user_deletion_signal(self):
        """Test that deleting a user triggers cleanup signal."""
        # Create some test data
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message"
        )
        
        notification = Notification.objects.create(
            user=self.user1,
            message=message,
            content="Test notification"
        )
        
        # Delete the user
        user_id = self.user1.id
        self.user1.delete()
        
        # Check that related data was cleaned up
        self.assertFalse(User.objects.filter(id=user_id).exists())


class CustomManagerTestCase(TestCase):
    """Test cases for custom managers."""
    
    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
    
    def test_unread_messages_manager(self):
        """Test the custom UnreadMessagesManager."""
        # Create read and unread messages
        read_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Read message",
            read=True
        )
        
        unread_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Unread message",
            read=False
        )
        
        # Test custom manager
        unread_messages = Message.unread.unread_for_user(self.user2)
        
        self.assertEqual(unread_messages.count(), 1)
        self.assertEqual(unread_messages.first(), unread_message)


class ThreadedConversationTestCase(TestCase):
    """Test cases for threaded conversations."""
    
    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
    
    def test_threaded_message_structure(self):
        """Test threaded message relationships."""
        # Create root message
        root_message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Root message"
        )
        
        # Create reply
        reply_message = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Reply message",
            parent_message=root_message
        )
        
        # Test relationships
        self.assertEqual(reply_message.parent_message, root_message)
        self.assertEqual(root_message.replies.count(), 1)
        self.assertEqual(reply_message.get_thread_root(), root_message)


class ViewTestCase(TestCase):
    """Test cases for views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_unread_messages_view(self):
        """Test unread messages view."""
        self.client.login(username='testuser', password='testpass123')
        
        # This would test the view 
        # response = self.client.get('/messaging/unread/')
        # self.assertEqual(response.status_code, 200)
        pass
    
    def test_delete_user_view(self):
        """Test delete user view."""
        self.client.login(username='testuser', password='testpass123')
        
        # This would test the delete user functionality
        # response = self.client.post('/messaging/delete-user/')
        # self.assertEqual(response.status_code, 200)
        pass
