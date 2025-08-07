from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.db.models import Prefetch, Q
from .models import ThreadedMessage


# Cached view with 60 seconds timeout
@cache_page(60)
@login_required
def cached_message_list(request):
    """
    Cached view that displays a list of messages in conversations.
    Task 5: Set up basic caching with 60 seconds timeout.
    """
    messages = ThreadedMessage.objects.select_related('sender', 'receiver').filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).order_by('-timestamp')
    
    return render(request, 'chats/message_list.html', {
        'messages': messages
    })


# Optimized threaded conversations with prefetch_related and select_related
@login_required
def optimized_threaded_view(request):
    """
    View that implements threaded conversations with optimized queries
    using prefetch_related and select_related to reduce database queries.
    """
    # Optimize queries for messages and their replies
    root_messages = ThreadedMessage.objects.select_related(
        'sender', 'receiver'
    ).prefetch_related(
        Prefetch(
            'replies',
            queryset=ThreadedMessage.objects.select_related(
                'sender', 'receiver'
            ).prefetch_related(
                'replies__sender', 'replies__receiver'
            ).order_by('timestamp')
        )
    ).filter(
        parent_message__isnull=True,  # Only root messages
        receiver=request.user
    ).order_by('-timestamp')
    
    return render(request, 'chats/threaded_conversations.html', {
        'root_messages': root_messages
    })


# Recursive query implementation
@login_required
def message_thread_detail(request, message_id):
    """
    Display a complete message thread using recursive ORM queries.
    """
    message = get_object_or_404(ThreadedMessage, id=message_id)
    thread_root = message.get_thread_root()
    
    # Get the complete thread structure using recursive queries
    thread_data = build_thread_structure(thread_root)
    
    return render(request, 'chats/thread_detail.html', {
        'thread_root': thread_root,
        'thread_data': thread_data,
        'participants': thread_root.get_thread_participants()
    })


def build_thread_structure(root_message):
    """
    Recursive function to build thread structure using Django ORM.
    Task 3: Implement recursive query to fetch all replies and display in threaded format.
    """
    def get_nested_replies(message):
        replies_data = []
        direct_replies = message.replies.select_related('sender', 'receiver').order_by('timestamp')
        
        for reply in direct_replies:
            reply_data = {
                'message': reply,
                'replies': get_nested_replies(reply),  # Recursive call
                'depth': reply.thread_depth
            }
            replies_data.append(reply_data)
        
        return replies_data
    
    return {
        'message': root_message,
        'replies': get_nested_replies(root_message),
        'depth': 0
    }
