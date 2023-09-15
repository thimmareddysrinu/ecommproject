from django import forms
from . models import Order, Customer
from django.contrib.auth.models import User


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["name", "address", "email", "mobile", "paymentmethod" ]


class CustomerregisForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.CharField(widget=forms.EmailInput())

    class Meta:
        model = Customer
        fields = ["username","email", "password",  "fullname", "adress"]

    def clean_username(self):
        uname = self.cleaned_data.get("username")
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError("if username already exists")
        return uname


class CustomerloginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput())
    password = forms.CharField(widget=forms.PasswordInput())

class ForgotPasswordForm(forms.Form):
    email= forms.CharField(widget=forms.EmailInput(attrs={
        "class":"form-control",
        "placeholder":"enter email used in the customer account"
    }))
    def clean_email(self):
        e = self.cleaned_data.get("email")
        if Customer.objects.filter(user__email=e).exists():
            pass
        else:
            raise forms.ValidationError("customer with this account/email does not exists ")
        return e
 
class PasswordResetForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'autocomplete': 'new-password',
        'placeholder': 'Enter New Password',
    }), label="New Password")
    confirm_new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'autocomplete': 'new-password',
        'placeholder': 'Confirm New Password',
    }), label="Confirm New Password")

    def clean_confirm_new_password(self):
        new_password = self.cleaned_data.get("new_password")
        confirm_new_password = self.cleaned_data.get("confirm_new_password")
        if new_password != confirm_new_password:
            raise forms.ValidationError(
                "New Passwords did not match!")
        return confirm_new_password
