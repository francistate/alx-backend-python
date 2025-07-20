from django.urls import path, include
from rest_framework import routers
from .views import ConversationViewSet, MessageViewSet

# create a router and register our viewsets with it
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# the API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]