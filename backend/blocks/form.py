from django import forms
from .models import Blocks

class BlocksAddForm(forms.ModelForm):
    username = forms.CharField(min_length=4, max_length=150)

    class Meta:
        model = Blocks
        fields = ['username']

class BlocksDeleteForm(BlocksAddForm):
    pass