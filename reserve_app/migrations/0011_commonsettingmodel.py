# Generated by Django 3.1.7 on 2021-04-25 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reserve_app', '0010_reservemodel_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommonSettingModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=30)),
                ('value', models.CharField(max_length=5000)),
            ],
        ),
    ]