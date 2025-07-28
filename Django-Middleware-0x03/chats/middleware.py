import logging
import time
from datetime import datetime, time as dt_time
from collections import defaultdict
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        logging.basicConfig(
            filename='requests.log',
            level=logging.INFO,
            format='%(message)s'
        )

    def __call__(self, request):
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        logger.info(log_message)
        
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_time = datetime.now().time()
        start_time = dt_time(21, 0)  # 9 PM
        end_time = dt_time(6, 0)     # 6 AM
        
        # Check if current time is between 9 PM and 6 AM (allowed hours)
        if not (current_time >= start_time or current_time <= end_time):
            return HttpResponseForbidden("Access denied. Chat is only available between 9 PM and 6 AM.")
        
        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_message_count = defaultdict(list)
        self.rate_limit = 5  # 5 messages per minute
        self.time_window = 60  # 60 seconds

    def __call__(self, request):
        if request.method == 'POST':
            client_ip = self.get_client_ip(request)
            current_time = time.time()
            
            # Clean old timestamps
            self.ip_message_count[client_ip] = [
                timestamp for timestamp in self.ip_message_count[client_ip]
                if current_time - timestamp < self.time_window
            ]
            
            # Check if rate limit exceeded
            if len(self.ip_message_count[client_ip]) >= self.rate_limit:
                return JsonResponse(
                    {'error': 'Rate limit exceeded. You can only send 5 messages per minute.'},
                    status=429
                )
            
            # Add current timestamp
            self.ip_message_count[client_ip].append(current_time)
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RolepermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_role = getattr(request.user, 'role', None)
            if user_role not in ['admin', 'moderator']:
                return HttpResponseForbidden("Access denied. Admin or moderator role required.")
        else:
            return HttpResponseForbidden("Access denied. Authentication required.")
        
        response = self.get_response(request)
        return response