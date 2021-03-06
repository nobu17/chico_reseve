# Generated by Django 3.1.7 on 2021-03-10 14:52

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='full_name',
            field=models.CharField(default='', max_length=10),
        ),
        migrations.AddField(
            model_name='customuser',
            name='tel_number',
            field=models.CharField(default='', max_length=15, validators=[django.core.validators.RegexValidator(message="Tel Number must be entered in the format: '09012345678'. Up to 15 digits allowed.", regex='^[0-9]+$')], verbose_name='電話番号'),
        ),
    ]
