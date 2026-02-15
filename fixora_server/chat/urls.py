from django.urls import path
from . import views

urlpatterns = [
    path('<int:request_id>/', views.direct_chat, name='direct_chat'),
]
