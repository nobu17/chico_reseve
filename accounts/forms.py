from django import forms
from allauth.socialaccount.forms import SignupForm


class CustomSignupForm(SignupForm):
    def validate_unique_email(self, value):
        try:
            return super(SignupForm, self).validate_unique_email(value)
        except forms.ValidationError:
            raise forms.ValidationError("既に同じメールアドレスが登録済みです。別のメールアドレスを登録お願いします。")
