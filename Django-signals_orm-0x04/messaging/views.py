from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.db.models import Q, Prefetch
from .models import Message, Notification, MessageHistory
import json


@login_required
@require_POST
def delete_user(request):
    """
    View that allows a user to delete their account.
    This will trigger the post_delete signal to clean up related data.
    """
    if request.method == 'POST':
        try:
            # Get the current user
            user = request.user
            
            # Log the user out before deletion
            logout(request)
            
            # Delete the user account
            # This will trigger the post_delete signal which handles cleanup
            user.delete()
            
            # Add success message
            messages.success(request, 'Your account has been successfully deleted.')
            
            # Return JSON response for AJAX requests
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': 'Account deleted successfully'
                })
            
            # Redirect to home page for regular requests
            return redirect('home')
            
        except Exception as e:
            # Handle any errors
            error_message = f'Error deleting account: {str(e)}'
            
            # Return JSON response for AJAX requests
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': False,
                    'error': error_message
                })
            
            messages.error(request, error_message)
            return redirect('profile')  # Redirect back to profile page
    
    # If not POST request, redirect to profile
    return redirect('profile')


@login_required
def confirm_delete_user(request):
    """
    View to show confirmation page before deleting user account.
    """
    return render(request, 'messaging/confirm_delete_user.html', {
        'user': request.user
    })


# Task 3: Optimized threaded conversations with prefetch_related and select_related
@login_required
def optimized_threaded_conversations(request):
    """
    Use prefetch_related and select_related to optimize querying of messages and 
    their replies, reducing the number of database queries.
    """
    messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).select_related('sender', 'receiver').prefetch_related(
        Prefetch(
            'replies',
            queryset=Message.objects.select_related('sender', 'receiver')
        )
    ).order_by('-timestamp')
    
    return render(request, 'messaging/threaded_conversations.html', {
        'messages': messages
    })


# Task 3: Recursive query using Django's ORM to fetch all replies
@login_required
def threaded_message_detail(request, message_id):
    """
    Recursive query using Django's ORM to fetch all replies to a message 
    and display them in a threaded format in the user interface.
    """
    message = get_object_or_404(Message, id=message_id)
    
    # Get all messages in the thread using recursive approach
    def get_thread_messages(root_message):
        messages = Message.objects.filter(parent_message=root_message).select_related('sender', 'receiver')
        thread_data = []
        for msg in messages:
            thread_data.append({
                'message': msg,
                'replies': get_thread_messages(msg)
            })
        return thread_data
    
    thread_messages = get_thread_messages(message)
    
    return render(request, 'messaging/thread_detail.html', {
        'root_message': message,
        'thread_messages': thread_messages
    })


# Task 4: Use custom manager to display unread messages
@login_required
def unread_messages_inbox(request):
    """
    Use this manager in your views to display only unread messages in a user's inbox.
    """
    unread_messages = Message.unread.unread_for_user(request.user)
    
    return render(request, 'messaging/unread_inbox.html', {
        'unread_messages': unread_messages
    })


# Task 4: Optimized query with .only() to retrieve only necessary fields
@login_required
def optimized_message_list(request):
    """
    Optimize this query with .only() to retrieve only necessary fields.
    """
    messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).only('id', 'content', 'timestamp', 'read').select_related('sender', 'receiver')
    
    return render(request, 'messaging/optimized_messages.html', {
        'messages': messages
    })


# Task 5: Cached view with cache_page and 60 seconds timeout
@cache_page(60)
@login_required
def cached_message_list(request):
    """
    Use cache_page in your views to cache the view that displays a list of messages 
    in a conversation with a 60 seconds cache timeout.
    """
    messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).select_related('sender', 'receiver').order_by('-timestamp')
    
    return render(request, 'messaging/cached_messages.html', {
        'messages': messages
    })