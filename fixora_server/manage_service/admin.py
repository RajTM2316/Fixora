from django.contrib import admin
from .models import Category
# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'description')
    list_filter = ('name',)
    search_fields = ('name',)
    list_per_page = 10

admin.site.register(Category, CategoryAdmin)