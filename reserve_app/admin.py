from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.SpecialHolydayModel)
admin.site.register(models.WeeklyScheduleModel)
admin.site.register(models.SeatModel)
