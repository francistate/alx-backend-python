from rest_framework import permissions
from .models import Conversation, Message


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user is a participant of the conversation or message's conversation
        """
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()
        
        elif isinstance(obj, Message):
            return request.user in obj.conversation.participants.all()
        
        return False


class IsOwnerOrParticipant(permissions.BasePermission):
    """
    Custom permission that allows:
    - Message owners to edit/delete their own messages
    - Conversation participants to view messages
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Check permissions based on the HTTP method and object type
        """
        if isinstance(obj, Message):
            # For messages, check if user is participant in conversation
            is_participant = request.user in obj.conversation.participants.all()
            
            # For safe methods (GET, HEAD, OPTIONS), allow if participant
            if request.method in permissions.SAFE_METHODS:
                return is_participant
            
            # For unsafe methods (POST, PUT, PATCH, DELETE), allow if owner or participant
            return is_participant and (obj.sender == request.user or request.method == 'POST')
        
        elif isinstance(obj, Conversation):
            # For conversations, user must be a participant
            return request.user in obj.participants.all()
        
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated
        """
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """
        Read permissions for any participant,
        Write permissions only for the owner.
        """
        # Read permissions for safe methods
        if request.method in permissions.SAFE_METHODS:
            if isinstance(obj, Message):
                return request.user in obj.conversation.participants.all()
            elif isinstance(obj, Conversation):
                return request.user in obj.participants.all()
        
        # Write permissions only for owner
        if isinstance(obj, Message):
            return obj.sender == request.user
        
        return False


class IsAuthenticatedAndParticipant(permissions.BasePermission):
    """
    Permission that combines authentication check with conversation participation
    """
    
    def has_permission(self, request, view):
        """
        Check if user is authenticated
        """
        if not (request.user and request.user.is_authenticated):
            return False
        
        # For list views, check if user has access to any conversations
        if view.action in ['list', 'create']:
            return True
        
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check object-level permissions
        """
        if isinstance(obj, Conversation):
            return request.user in obj.participants.all()
        
        elif isinstance(obj, Message):
            return request.user in obj.conversation.participants.all()
        
        return False