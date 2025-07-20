# from django.shortcuts import render

# create your views here.
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer, 
    ConversationSerializer, 
    ConversationListSerializer,
    MessageSerializer, 
    MessageCreateSerializer
)


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and creating conversations
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['participants__first_name', 'participants__last_name']
    
    def get_queryset(self):
        """
        Return conversations where the current user is a participant
        """
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants', 'messages__sender')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'list':
            return ConversationListSerializer
        elif self.action == 'create':
            return ConversationSerializer
        return ConversationSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new conversation
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        
        # return the created conversation with full details
        response_serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """
        Add a participant to an existing conversation
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.add(user)
            return Response(
                {'message': f'User {user.full_name} added to conversation'}, 
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """
        Remove a participant from an existing conversation
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
            if user in conversation.participants.all():
                conversation.participants.remove(user)
                return Response(
                    {'message': f'User {user.full_name} removed from conversation'}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'User is not a participant in this conversation'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and creating messages
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return messages from conversations where the current user is a participant
        """
        user_conversations = Conversation.objects.filter(participants=self.request.user)
        return Message.objects.filter(
            conversation__in=user_conversations
        ).select_related('sender', 'conversation')
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Send a message to an existing conversation
        """
        # check if user is participant in the conversation
        conversation_id = request.data.get('conversation')
        if conversation_id:
            try:
                conversation = Conversation.objects.get(conversation_id=conversation_id)
                if request.user not in conversation.participants.all():
                    return Response(
                        {'error': 'You are not a participant in this conversation'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Conversation.DoesNotExist:
                return Response(
                    {'error': 'Conversation not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        
        # return the created message with full details
        response_serializer = MessageSerializer(message, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def by_conversation(self, request):
        """
        Get all messages for a specific conversation
        """
        conversation_id = request.query_params.get('conversation_id')
        if not conversation_id:
            return Response(
                {'error': 'conversation_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
            if request.user not in conversation.participants.all():
                return Response(
                    {'error': 'You are not a participant in this conversation'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            messages = self.get_queryset().filter(conversation=conversation)
            serializer = MessageSerializer(messages, many=True, context={'request': request})
            return Response(serializer.data)
            
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
