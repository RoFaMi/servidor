from django.urls import path
from . import views
from .views import google_login, google_callback

urlpatterns = [
    path('', google_login, name='google_login'),  # Hacer de google_login la página principal
    path('auth/callback/', google_callback, name='google_callback'),
    path('chat/', views.chat_view, name='chat'),  # Mover el chat a otra ruta (opcional)
    path('api/send_notification/', views.send_notification, name='send_notification'),
    path('send_message/', views.send_message, name='send_message'),
]
