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

def payment_success(request):

    payment_id = request.POST.get("razorpay_payment_id")
    order_id = request.POST.get("razorpay_order_id")
    signature = request.POST.get("razorpay_signature")

    params_dict = {
        "razorpay_payment_id": payment_id,
        "razorpay_order_id": order_id,
        "razorpay_signature": signature
    }

    try:

        client.utility.verify_payment_signature(params_dict)

        payment = Payment.objects.get(razorpay_order_id=order_id)

        payment.razorpay_payment_id = payment_id
        payment.razorpay_signature = signature
        payment.status = "paid"

        payment.save()

        return render(request, "payments/success.html")

    except:

        return render(request, "payments/failure.html")