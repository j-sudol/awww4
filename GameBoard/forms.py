from django import forms
from .models import Board

class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['board_name', 'rows', 'columns']
        widgets = {
            'rows': forms.NumberInput(attrs={'id': 'rows'}),
            'columns': forms.NumberInput(attrs={'id': 'columns'}),
        }