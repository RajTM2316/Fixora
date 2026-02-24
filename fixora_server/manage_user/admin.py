from django.contrib.admin import AdminSite
from django.contrib.auth import logout
from django.shortcuts import redirect
from .models import Profile, Address


class FixoraAdminSite(AdminSite):
    site_header = "Fixora Control Panel"
    site_title = "Fixora Admin"
    index_title = "Welcome to Fixora Admin"

    def logout(self, request, extra_context=None):
        logout(request)
        return redirect('/admin/login/')


# Create custom admin instance
custom_admin_site = FixoraAdminSite(name='fixora_admin')

# Register models here
custom_admin_site.register(Profile)
custom_admin_site.register(Address)