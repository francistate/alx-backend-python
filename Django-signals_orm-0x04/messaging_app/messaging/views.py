from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.db.models import Prefetch
from .models import Message, Notification, MessageHistory


# Delete User View
@login_required
@require_http_methods(["DELETE", "POST"])
def delete_user(request):
    """
    View that allows a user to delete their account.
    The post_delete signal will handle cleanup of related data.
    """
    user = request.user
    
    try:
        # Delete the user - signals will handle related data cleanup
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'User account deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Optimized Threaded Conversations View
@login_required
@cache_page(60)  # Task 5: Cache for 60 seconds
def threaded_conversations(request):
    """
    View that implements threaded conversations with optimized queries
    using prefetch_related and select_related.
    """
    # Optimize queries for messages and their replies
    messages = Message.objects.select_related('sender', 'receiver').prefetch_related(
        Prefetch(
            'replies',
            queryset=Message.objects.select_related('sender', 'receiver').order_by('timestamp')
        )
    ).filter(
        parent_message__isnull=True,  # Only root messages
        receiver=request.user
    ).order_by('-timestamp')
    
    # Convert to list for template rendering
    threaded_data = []
    for message in messages:
        threaded_data.append({
            'message': message,
            'replies': list(message.replies.all()),
            'reply_count': message.get_replies_count()
        })
    
    return render(request, 'messaging/threaded_conversations.html', {
        'threaded_conversations': threaded_data
    })


# Unread Messages View using Custom Manager
@login_required
def unread_messages(request):
    """
    View that displays only unread messages using the custom UnreadMessagesManager.
    Optimized with .only() to retrieve only necessary fields.
    """
    unread_messages = Message.unread.unread_for_user(request.user)
    
    return render(request, 'messaging/unread_messages.html', {
        'unread_messages': unread_messages,
        'count': unread_messages.count()
    })


# Cached Message List View
@cache_page(60)  # Cache for 60 seconds
@login_required
def message_list(request):
    """
    View that displays a list of messages in a conversation with caching.
    """
    messages = Message.objects.select_related('sender', 'receiver').filter(
        receiver=request.user
    ).order_by('-timestamp')
    
    return render(request, 'messaging/message_list.html', {
        'messages': messages
    })


# View for message history
@login_required
def message_history(request, message_id):
    """
    View to display message edit history.
    """
    message = get_object_or_404(Message, id=message_id, receiver=request.user)
    history = MessageHistory.objects.filter(message=message).order_by('-edited_at')
    
    return render(request, 'messaging/message_history.html', {
        'message': message,
        'history': history
    })


# Recursive query implementation for threaded conversations
def get_message_thread(message_id):
    """
    Recursive function to get all replies to a message using Django ORM.
    """
    def get_replies(message):
        replies = []
        direct_replies = Message.objects.select_related('sender', 'receiver').filter(
            parent_message=message
        ).order_by('timestamp')
        
        for reply in direct_replies:
            reply_data = {
                'message': reply,
                'replies': get_replies(reply)  # Recursive call
            }
            replies.append(reply_data)
        
        return replies
    
    root_message = get_object_or_404(Message, id=message_id)
    return {
        'message': root_message,
        'replies': get_replies(root_message)
    }
