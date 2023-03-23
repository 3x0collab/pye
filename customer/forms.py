from django import forms
from django.contrib.auth.models import User
from . import models


class CustomerUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['username','password']
        widgets = {
        'password': forms.PasswordInput()
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model=models.Customer
        fields=['email']



class CodeForm(forms.ModelForm):
    class Meta:
        model = models.Transformer
        fields = ('code', 'name',"description","is_public")
        widgets = {
                "code": forms.Textarea(),
            }