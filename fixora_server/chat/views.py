from django.contrib.auth.views import login_required
from django.shortcuts import render, get_object_or_404
from manage_service.models import ServiceRequest

@login_required
def direct_chat(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)

    return render(request, 'chat/direct_chat.html', {
        'service_request': service_request,
    })
