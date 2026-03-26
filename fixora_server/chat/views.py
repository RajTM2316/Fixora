from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from manage_service.models import ServiceRequest
from manage_user.models import Profile

@login_required
def direct_chat(request, request_id):
    service_request = get_object_or_404(
        ServiceRequest.objects.select_related(
            "customer__user",
            "provider_service__provider__user",
        ),
        id=request_id
    )

    profile = get_object_or_404(Profile, user=request.user)

    # Determine who the current user is talking TO
    if profile.role == "customer":
        other_user = service_request.provider_service.provider.user if service_request.provider_service else None
        other_role = "Provider"
    else:
        other_user = service_request.customer.user
        other_role = "Customer"

    return render(request, 'chat/direct_chat.html', {
        'service_request': service_request,
        'other_user': other_user,    # the User object of the other person
        'other_role': other_role,    # "Provider" or "Customer"
    })