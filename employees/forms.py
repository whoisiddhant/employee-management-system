
from django import forms
from django.contrib.auth.models import User
from .models import Employee
from django.contrib.auth.password_validation import validate_password


class EmployeeForm(forms.ModelForm):

    username = forms.CharField(max_length=150)

    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Temporary Password"
    )

    class Meta:
        model = Employee
        fields = [
            'full_name',
            'email',
            'phone',
            'department',
            'position'
        ]

    def clean_username(self):
        username = self.cleaned_data['username']

        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")

        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        validate_password(password)
        return password


class EmployeeUpdateForm(forms.ModelForm):

    username = forms.CharField(max_length=150)

    class Meta:
        model = Employee
        fields = [
            'full_name',
            'email',
            'phone',
            'department',
            'position'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            self.fields['username'].initial = self.instance.user.username

    def clean_username(self):
        username = self.cleaned_data['username']

        existing_user = User.objects.filter(
          username__iexact=username
        ).exclude(pk=self.instance.user_id).first()
            
        

        if existing_user:
            raise forms.ValidationError("This username is already taken.")

        return username
