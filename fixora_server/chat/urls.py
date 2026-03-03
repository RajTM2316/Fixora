from django.urls import path
from . import views
app_name = 'chat'
urlpatterns = [
    path('<int:request_id>/', views.direct_chat, name='direct_chat'),
]
