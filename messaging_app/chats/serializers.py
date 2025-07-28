from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'first_name', 'last_name', 'email', 
            'phone_number', 'role', 'created_at', 'full_name'
        ]
        read_only_fields = ['user_id', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate_email(self, value):
        """
        Custom validation for email field
        """
        queryset = User.objects.filter(email=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model
    """
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True, required=False)
    conversation_id = serializers.UUIDField(source='conversation.conversation_id', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'sender_id', 'conversation', 'conversation_id',
            'message_body', 'sent_at'
        ]
        read_only_fields = ['message_id', 'sent_at']
    
    def create(self, validated_data):
        # set sender from request user if not provided
        if 'sender_id' not in validated_data:
            validated_data['sender'] = self.context['request'].user
        else:
            sender_id = validated_data.pop('sender_id')
            try:
                validated_data['sender'] = User.objects.get(user_id=sender_id)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid sender_id")
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
            'messages', 'created_at', 'participant_count', 'latest_message'
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
            if participants.count() != len(participant_ids):
                raise serializers.ValidationError("One or more participant IDs are invalid.")
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
    message_body = serializers.CharField(max_length=1000)
    
    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'conversation', 
                  'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sender', 'sent_at']
    
    def validate_message_body(self, value):
        """
        Custom validation for message body
        """
        if not value.strip():
            raise serializers.ValidationError("Message body cannot be empty.")
        return value.strip()
    
    def create(self, validated_data):
        # automatically set sender to current user
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)