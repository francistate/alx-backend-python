from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'user_id', 'first_name', 'last_name', 'email', 
            'phone_number', 'role', 'created_at', 'full_name'
        ]
        read_only_fields = ['user_id', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model
    """
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True, required=False)
    
    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'sender_id', 
            'conversation', 'message_body', 'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at']
    
    def create(self, validated_data):
        # set sender from request user if not provided
        if 'sender_id' not in validated_data:
            validated_data['sender'] = self.context['request'].user
        else:
            validated_data['sender_id'] = validated_data.pop('sender_id')
        return super().create(validated_data)


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model with nested messages
    """
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    messages = MessageSerializer(many=True, read_only=True)
    participant_count = serializers.ReadOnlyField()
    latest_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'participant_ids', 
            'messages', 'created_at', 'participant_count', 
            'latest_message'
        ]
        read_only_fields = ['conversation_id', 'created_at']
    
    def get_latest_message(self, obj):
        """
        Get the latest message in the conversation
        """
        latest_message = obj.get_latest_message()
        if latest_message:
            return MessageSerializer(latest_message).data
        return None
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create(**validated_data)
        
        # add participants
        if participant_ids:
            participants = User.objects.filter(user_id__in=participant_ids)
            conversation.participants.set(participants)
        
        # add current user as participant if not already included
        current_user = self.context['request'].user
        if current_user not in conversation.participants.all():
            conversation.participants.add(current_user)
        
        return conversation


class ConversationListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing conversations (without all messages)
    """
    participants = UserSerializer(many=True, read_only=True)
    participant_count = serializers.ReadOnlyField()
    latest_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'participants', 'created_at', 
            'participant_count', 'latest_message'
        ]
        read_only_fields = ['conversation_id', 'created_at']
    
    def get_latest_message(self, obj):
        """
        Get the latest message in the conversation
        """
        latest_message = obj.get_latest_message()
        if latest_message:
            return {
                'message_id': latest_message.message_id,
                'message_body': latest_message.message_body,
                'sender': latest_message.sender.full_name,
                'sent_at': latest_message.sent_at
            }
        return None


class MessageCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating messages
    """
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'conversation', 
                  'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sender', 'sent_at']
    
    def create(self, validated_data):
        # automatically set sender to current user
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)