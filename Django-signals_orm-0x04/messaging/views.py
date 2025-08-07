from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
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