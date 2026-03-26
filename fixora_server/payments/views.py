from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Payment
from .utils import client
from manage_service.models import ServiceRequest
from manage_user.models import Profile


@login_required
def create_payment(request, request_id):
    profile = get_object_or_404(Profile, user=request.user)
    service_request = get_object_or_404(
        ServiceRequest,
        id=request_id,
        customer=profile,
        status='COMPLETED',
        payment_done=False
    )

    amount_inr = service_request.provider_service.service.base_price
    amount_paise = int(amount_inr * 100)

    order = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1
    })

    Payment.objects.update_or_create(
        service_request=service_request,
        defaults={
            "amount": amount_inr,
            "description": f"Payment for {service_request.provider_service.service.name}",
            "razorpay_order_id": order["id"],
            "status": "created"
        }
    )

    return render(request, "payments/payment.html", {
        "order": order,
        "key": settings.RAZORPAY_KEY_ID,
        "amount": amount_paise,
        "service_request": service_request,
    })


@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        payment_id = request.POST.get("razorpay_payment_id")
        order_id = request.POST.get("razorpay_order_id")
        signature = request.POST.get("razorpay_signature")

        params_dict = {
            "razorpay_payment_id": payment_id,
            "razorpay_order_id": order_id,
            "razorpay_signature": signature,
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            payment = Payment.objects.get(razorpay_order_id=order_id)
            payment.razorpay_payment_id = payment_id
            payment.razorpay_signature = signature
            payment.status = "paid"
            payment.save()

            # Mark the service request payment as done
            service_request = payment.service_request
            service_request.payment_done = True
            service_request.save()

            # Redirect to feedback page
            return redirect("manage_service:complete_service", request_id=service_request.id)

        except Exception as e:
            print("Verification error:", e)
            return render(request, "payments/failure.html")

    return render(request, "payments/failure.html")