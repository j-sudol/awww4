from django import forms
from django.contrib.auth.models import User
from backgrounds.models import Background
from routes.models import Route
from routes.models import RoutePoint

class addRouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['name', 'background']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Route Name'}),
            'background': forms.Select(attrs={'class': 'form-control'}),
        }

# class addRoutePointForm(forms.ModelForm):
#     class Meta:
#         model = RoutePoint
#         fields = ['x',]
#         widgets = {
#             'name': forms.TextInput(attrs={'placeholder': 'Point Name'}),
#             'background': forms.Select(attrs={'class': 'form-control'}),
#             'order': forms.NumberInput(attrs={'placeholder': 'Order'}),
#         }