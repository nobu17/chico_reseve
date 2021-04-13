from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.auth.models import AbstractUser
# Create your models here.


class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=10, default="")
    tel_number_regex = RegexValidator(regex=r'^[0-9]+$', message=("Tel Number must be entered in the format: '09012345678'. Up to 15 digits allowed."))
    tel_number = models.CharField(validators=[tel_number_regex], max_length=15, verbose_name='電話番号', default="")
    second_email = models.EmailField(default="", validators=[EmailValidator()])

    def get(id):
        return CustomUser.objects.filter(id=id).first()

    def get_no_admin_users():
        return CustomUser.objects.filter(is_superuser=False, is_staff=False).order_by('-date_joined')

    def clear_without_admin():
        CustomUser.objects.filter(is_superuser=False, is_staff=False).delete()

    def get_email(self):
        # second email is high priority
        if self.second_email:
            return self.second_email
        elif self.email:
            return self.email
        else:
            return ""

    class Meta:
        verbose_name_plural = 'CustomUser'
