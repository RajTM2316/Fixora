from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.conf import settings
from .models import Payment
from .utils import client


def create_payment(request):

    amount = 50000  # ₹500 in paise

    order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": 1
    })

    Payment.objects.create(
        amount=amount / 100,
        description="Fixora Service Payment",
        razorpay_order_id=order["id"],
        status="created"
    )

    return render(request, "payments/payment.html", {
        "order": order,
        "key": settings.RAZORPAY_KEY_ID
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

        except Exception as e:

            print("Verification error:", e)

            return render(request, "payments/failure.html")

    return render(request, "payments/failure.html")


    