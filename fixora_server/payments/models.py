from django.db import models

class Payment(models.Model):

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    description = models.CharField(max_length=255)

    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)

    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)

    razorpay_signature = models.CharField(max_length=500, blank=True, null=True)

    status = models.CharField(
    max_length=50,
    choices=[
        ("created", "Created"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ],
    default="created"
)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.razorpay_order_id} - Amount {self.amount}"

class Invoice(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50, unique=True)
    issued_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} for Payment ID {self.payment.id}"

class Refund(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refund of {self.refund_amount} for Payment ID {self.payment.id}"

class PaymentMethod(models.Model):
    method_name = models.CharField(max_length=100)
    details = models.TextField()

    def __str__(self):
        return self.method_name

class Transaction(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50)
    processed_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.transaction_id} - Status: {self.status}"

class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.code})"
