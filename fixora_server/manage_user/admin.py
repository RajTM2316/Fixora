from django.contrib.admin import AdminSite
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.db.models import Sum

from manage_user.models import Profile, Address
from manage_service.models import ServiceRequest, Category
from payments.models import Payment, Refund


class FixoraAdminSite(AdminSite):
    site_header = "Fixora Admin"
    site_title = "Fixora Panel"
    index_title = "Dashboard"

    # =========================
    # Custom Logout
    # =========================
    def logout(self, request, extra_context=None):
        logout(request)
        return redirect('/admin/login/')

    # =========================
    # Custom Dashboard
    # =========================
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}

        # =========================
        # USER STATS
        # =========================
        total_customers = Profile.objects.filter(role="customer").count()
        total_providers = Profile.objects.filter(role="provider").count()

        # =========================
        # CATEGORY STATS
        # =========================
        total_categories = Category.objects.count()
        active_categories = Category.objects.filter(is_active=True).count()

        # =========================
        # SERVICE REQUEST STATS
        # =========================
        total_requests = ServiceRequest.objects.count()
        pending_requests = ServiceRequest.objects.filter(status="PENDING").count()
        completed_requests = ServiceRequest.objects.filter(status="COMPLETED").count()
        cancelled_requests = ServiceRequest.objects.filter(status="CANCELLED").count()

        # =========================
        # PAYMENT STATS
        # =========================
        total_payments = Payment.objects.aggregate(
            total=Sum("amount")
        )["total"] or 0

        total_refunds = Refund.objects.aggregate(
            total=Sum("refund_amount")
        )["total"] or 0

        net_revenue = total_payments - total_refunds

        # =========================
        # BUSINESS METRICS
        # =========================
        cancel_rate = 0
        completion_rate = 0

        if total_requests > 0:
            cancel_rate = round((cancelled_requests / total_requests) * 100, 2)
            completion_rate = round((completed_requests / total_requests) * 100, 2)

        # =========================
        # RECENT ACTIVITY
        # =========================
        recent_requests = (
            ServiceRequest.objects
            .select_related("customer__user", "provider_service__provider__user")
            .order_by("-request_date")[:5]
        )

        # =========================
        # CONTEXT UPDATE
        # =========================
        extra_context.update({
            # Users
            "total_customers": total_customers,
            "total_providers": total_providers,

            # Categories
            "total_categories": total_categories,
            "active_categories": active_categories,

            # Requests
            "total_requests": total_requests,
            "pending_requests": pending_requests,
            "completed_requests": completed_requests,
            "cancelled_requests": cancelled_requests,

            # Payments
            "total_payments": total_payments,
            "total_refunds": total_refunds,
            "net_revenue": net_revenue,

            # Business Metrics
            "cancel_rate": cancel_rate,
            "completion_rate": completion_rate,

            # Recent
            "recent_requests": recent_requests,
        })

        return super().index(request, extra_context)


# =========================
# Create custom admin instance
# =========================
custom_admin_site = FixoraAdminSite(name='fixora_admin')

# =========================
# Register models
# =========================
custom_admin_site.register(Profile)
custom_admin_site.register(Address)
custom_admin_site.register(Category)