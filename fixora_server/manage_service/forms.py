from django import forms
from .models import Service


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["name", "description", "base_price", "service_image"]  

        widgets = {
            "name": forms.TextInput(
                attrs={"class": "w-full border rounded-lg p-2"}
            ),
            "description": forms.Textarea(
                attrs={"class": "w-full border rounded-lg p-2", "rows": 4}
            ),
            "base_price": forms.NumberInput(
                attrs={"class": "w-full border rounded-lg p-2"}
            ),
            "service_image": forms.ClearableFileInput( 
                attrs={"class": "w-full border rounded-lg p-2"}
            ),
        }