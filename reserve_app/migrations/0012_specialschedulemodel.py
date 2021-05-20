# Generated by Django 3.1.7 on 2021-05-19 22:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reserve_app', '0011_commonsettingmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpecialScheduleModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('start_time', models.TimeField(choices=[(datetime.time(0, 0), '00:00'), (datetime.time(0, 30), '00:30'), (datetime.time(1, 0), '01:00'), (datetime.time(1, 30), '01:30'), (datetime.time(2, 0), '02:00'), (datetime.time(2, 30), '02:30'), (datetime.time(3, 0), '03:00'), (datetime.time(3, 30), '03:30'), (datetime.time(4, 0), '04:00'), (datetime.time(4, 30), '04:30'), (datetime.time(5, 0), '05:00'), (datetime.time(5, 30), '05:30'), (datetime.time(6, 0), '06:00'), (datetime.time(6, 30), '06:30'), (datetime.time(7, 0), '07:00'), (datetime.time(7, 30), '07:30'), (datetime.time(8, 0), '08:00'), (datetime.time(8, 30), '08:30'), (datetime.time(9, 0), '09:00'), (datetime.time(9, 30), '09:30'), (datetime.time(10, 0), '10:00'), (datetime.time(10, 30), '10:30'), (datetime.time(11, 0), '11:00'), (datetime.time(11, 30), '11:30'), (datetime.time(12, 0), '12:00'), (datetime.time(12, 30), '12:30'), (datetime.time(13, 0), '13:00'), (datetime.time(13, 30), '13:30'), (datetime.time(14, 0), '14:00'), (datetime.time(14, 30), '14:30'), (datetime.time(15, 0), '15:00'), (datetime.time(15, 30), '15:30'), (datetime.time(16, 0), '16:00'), (datetime.time(16, 30), '16:30'), (datetime.time(17, 0), '17:00'), (datetime.time(17, 30), '17:30'), (datetime.time(18, 0), '18:00'), (datetime.time(18, 30), '18:30'), (datetime.time(19, 0), '19:00'), (datetime.time(19, 30), '19:30'), (datetime.time(20, 0), '20:00'), (datetime.time(20, 30), '20:30'), (datetime.time(21, 0), '21:00'), (datetime.time(21, 30), '21:30'), (datetime.time(22, 0), '22:00'), (datetime.time(22, 30), '22:30'), (datetime.time(23, 0), '23:00'), (datetime.time(23, 30), '23:30')])),
                ('end_time', models.TimeField(choices=[(datetime.time(0, 0), '00:00'), (datetime.time(0, 30), '00:30'), (datetime.time(1, 0), '01:00'), (datetime.time(1, 30), '01:30'), (datetime.time(2, 0), '02:00'), (datetime.time(2, 30), '02:30'), (datetime.time(3, 0), '03:00'), (datetime.time(3, 30), '03:30'), (datetime.time(4, 0), '04:00'), (datetime.time(4, 30), '04:30'), (datetime.time(5, 0), '05:00'), (datetime.time(5, 30), '05:30'), (datetime.time(6, 0), '06:00'), (datetime.time(6, 30), '06:30'), (datetime.time(7, 0), '07:00'), (datetime.time(7, 30), '07:30'), (datetime.time(8, 0), '08:00'), (datetime.time(8, 30), '08:30'), (datetime.time(9, 0), '09:00'), (datetime.time(9, 30), '09:30'), (datetime.time(10, 0), '10:00'), (datetime.time(10, 30), '10:30'), (datetime.time(11, 0), '11:00'), (datetime.time(11, 30), '11:30'), (datetime.time(12, 0), '12:00'), (datetime.time(12, 30), '12:30'), (datetime.time(13, 0), '13:00'), (datetime.time(13, 30), '13:30'), (datetime.time(14, 0), '14:00'), (datetime.time(14, 30), '14:30'), (datetime.time(15, 0), '15:00'), (datetime.time(15, 30), '15:30'), (datetime.time(16, 0), '16:00'), (datetime.time(16, 30), '16:30'), (datetime.time(17, 0), '17:00'), (datetime.time(17, 30), '17:30'), (datetime.time(18, 0), '18:00'), (datetime.time(18, 30), '18:30'), (datetime.time(19, 0), '19:00'), (datetime.time(19, 30), '19:30'), (datetime.time(20, 0), '20:00'), (datetime.time(20, 30), '20:30'), (datetime.time(21, 0), '21:00'), (datetime.time(21, 30), '21:30'), (datetime.time(22, 0), '22:00'), (datetime.time(22, 30), '22:30'), (datetime.time(23, 0), '23:00'), (datetime.time(23, 30), '23:30')])),
            ],
        ),
    ]
