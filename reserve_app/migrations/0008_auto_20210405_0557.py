# Generated by Django 3.1.7 on 2021-04-04 20:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reserve_app', '0007_reservemodel_canceled'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservemodel',
            name='memo',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='weeklyschedulemodel',
            name='dayofweek',
            field=models.PositiveSmallIntegerField(choices=[(6, '日曜'), (0, '月曜'), (1, '火曜'), (2, '水曜'), (3, '木曜'), (4, '金曜'), (5, '土曜')], validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(6)]),
        ),
    ]
