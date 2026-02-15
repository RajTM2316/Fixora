from django.contrib import admin
from .models import Category, Service, ProviderService, ServiceRequest


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'description')
    list_filter = ('name',)
    search_fields = ('name',)
    list_per_page = 10


admin.site.register(Category, CategoryAdmin)
admin.site.register(Service)
admin.site.register(ProviderService)
admin.site.register(ServiceRequest)
