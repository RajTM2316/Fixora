from django.shortcuts import render
from django.conf import settings
from .models import Payment
from .utils import client


def create_payment(request):

    amount = 50000

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    payment = Payment.objects.create(
        amount=amount/100,
        description="Fixora Service Payment",
        razorpay_order_id=order["id"]
    )

    return render(request, "payments/payment.html", {
        "order": order,
        "key": settings.RAZORPAY_KEY_ID
    })