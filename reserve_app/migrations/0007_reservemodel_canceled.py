# Generated by Django 3.1.7 on 2021-03-24 11:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reserve_app', '0006_auto_20210321_2150'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservemodel',
            name='canceled',
            field=models.BooleanField(default=False),
        ),
    ]
