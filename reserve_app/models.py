from django.db import models
from django.db.models import Q, Count, Max
from django.core.validators import MaxValueValidator, MinValueValidator, EmailValidator
from accounts.models import CustomUser
import datetime
from . import util
# Create your models here.


MON_DAY = 0
TUES_DAY = 1
WEDNES_DAY = 2
THURS_DAY = 3
FRI_DAY = 4
SATUR_DAY = 5
SUN_DAY = 6

DAYS_OF_WEEK = (
    (SUN_DAY, '日曜'),
    (MON_DAY, '月曜'),
    (TUES_DAY, '火曜'),
    (WEDNES_DAY, '水曜'),
    (THURS_DAY, '木曜'),
    (FRI_DAY, '金曜'),
    (SATUR_DAY, '土曜'),
)

TIME_MAP_HALF_HOURS_CHOICES = (
    (datetime.time(00, 00, 00), '00:00'),
    (datetime.time(00, 30, 00), '00:30'),
    (datetime.time(1, 00, 00), '01:00'),
    (datetime.time(1, 30, 00), '01:30'),
    (datetime.time(2, 00, 00), '02:00'),
    (datetime.time(2, 30, 00), '02:30'),
    (datetime.time(3, 00, 00), '03:00'),
    (datetime.time(3, 30, 00), '03:30'),
    (datetime.time(4, 00, 00), '04:00'),
    (datetime.time(4, 30, 00), '04:30'),
    (datetime.time(5, 00, 00), '05:00'),
    (datetime.time(5, 30, 00), '05:30'),
    (datetime.time(6, 00, 00), '06:00'),
    (datetime.time(6, 30, 00), '06:30'),
    (datetime.time(7, 00, 00), '07:00'),
    (datetime.time(7, 30, 00), '07:30'),
    (datetime.time(8, 00, 00), '08:00'),
    (datetime.time(8, 30, 00), '08:30'),
    (datetime.time(9, 00, 00), '09:00'),
    (datetime.time(9, 30, 00), '09:30'),
    (datetime.time(10, 00, 00), '10:00'),
    (datetime.time(10, 30, 00), '10:30'),
    (datetime.time(11, 00, 00), '11:00'),
    (datetime.time(11, 30, 00), '11:30'),
    (datetime.time(12, 00, 00), '12:00'),
    (datetime.time(12, 30, 00), '12:30'),
    (datetime.time(13, 00, 00), '13:00'),
    (datetime.time(13, 30, 00), '13:30'),
    (datetime.time(14, 00, 00), '14:00'),
    (datetime.time(14, 30, 00), '14:30'),
    (datetime.time(15, 00, 00), '15:00'),
    (datetime.time(15, 30, 00), '15:30'),
    (datetime.time(16, 00, 00), '16:00'),
    (datetime.time(16, 30, 00), '16:30'),
    (datetime.time(17, 00, 00), '17:00'),
    (datetime.time(17, 30, 00), '17:30'),
    (datetime.time(18, 00, 00), '18:00'),
    (datetime.time(18, 30, 00), '18:30'),
    (datetime.time(19, 00, 00), '19:00'),
    (datetime.time(19, 30, 00), '19:30'),
    (datetime.time(20, 00, 00), '20:00'),
    (datetime.time(20, 30, 00), '20:30'),
    (datetime.time(21, 00, 00), '21:00'),
    (datetime.time(21, 30, 00), '21:30'),
    (datetime.time(22, 00, 00), '22:00'),
    (datetime.time(22, 30, 00), '22:30'),
    (datetime.time(23, 00, 00), '23:00'),
    (datetime.time(23, 30, 00), '23:30')
)


class WeeklyScheduleModel(models.Model):
    dayofweek = models.PositiveSmallIntegerField(choices=DAYS_OF_WEEK,
                                                 validators=[MinValueValidator(MON_DAY), MaxValueValidator(SUN_DAY)])
    start_time = models.TimeField(choices=TIME_MAP_HALF_HOURS_CHOICES)
    end_time = models.TimeField(choices=TIME_MAP_HALF_HOURS_CHOICES)

    @classmethod
    def get(cls, pk):
        return WeeklyScheduleModel.objects.filter(pk=pk).first()

    @classmethod
    def get_all(cls):
        return WeeklyScheduleModel.objects.order_by('dayofweek', 'start_time')

    @classmethod
    def get_ranges(cls, pk, dayofweek, start_time, end_time):
        return WeeklyScheduleModel.objects.filter(dayofweek=dayofweek, start_time__lt=end_time, end_time__gt=start_time).exclude(pk=pk)

    @classmethod
    def get_by_dayofweek(cls, dayofweek):
        return WeeklyScheduleModel.objects.filter(dayofweek=dayofweek).order_by('-dayofweek', 'start_time')

    @classmethod
    def get_filtered_date_by_availalble_dayofweeks(cls, filter_target_dates):
        all_day_of_weeks = WeeklyScheduleModel.objects.values_list('dayofweek', flat=True).distinct()
        all_day_of_weeks = list(all_day_of_weeks)

        result = []
        for day in filter_target_dates:
            if all_day_of_weeks.count(day.weekday()) > 0:
                result.append(day)

        return result

    @classmethod
    def create_init_data(cls):
        WeeklyScheduleModel(dayofweek=SUN_DAY, start_time=datetime.time(7, 00, 00), end_time=datetime.time(9, 30, 00)).save()
        WeeklyScheduleModel(dayofweek=SUN_DAY, start_time=datetime.time(11, 30, 00), end_time=datetime.time(15, 00, 00)).save()
        WeeklyScheduleModel(dayofweek=MON_DAY, start_time=datetime.time(11, 30, 00), end_time=datetime.time(15, 00, 00)).save()
        WeeklyScheduleModel(dayofweek=TUES_DAY, start_time=datetime.time(7, 00, 00), end_time=datetime.time(9, 30, 00)).save()
        WeeklyScheduleModel(dayofweek=TUES_DAY, start_time=datetime.time(11, 30, 00), end_time=datetime.time(15, 00, 00)).save()
        WeeklyScheduleModel(dayofweek=WEDNES_DAY, start_time=datetime.time(7, 00, 00), end_time=datetime.time(9, 30, 00)).save()
        WeeklyScheduleModel(dayofweek=WEDNES_DAY, start_time=datetime.time(11, 30, 00), end_time=datetime.time(15, 00, 00)).save()
        WeeklyScheduleModel(dayofweek=FRI_DAY, start_time=datetime.time(11, 30, 00), end_time=datetime.time(15, 00, 00)).save()
        WeeklyScheduleModel(dayofweek=FRI_DAY, start_time=datetime.time(17, 30, 00), end_time=datetime.time(21, 00, 00)).save()
        WeeklyScheduleModel(dayofweek=SATUR_DAY, start_time=datetime.time(7, 00, 00), end_time=datetime.time(9, 30, 00)).save()
        WeeklyScheduleModel(dayofweek=SATUR_DAY, start_time=datetime.time(11, 30, 00), end_time=datetime.time(15, 00, 00)).save()
        WeeklyScheduleModel(dayofweek=SATUR_DAY, start_time=datetime.time(17, 30, 00), end_time=datetime.time(21, 00, 00)).save()


class SpecialScheduleModel(models.Model):
    start_date = models.DateField()
    start_time = models.TimeField(choices=TIME_MAP_HALF_HOURS_CHOICES)
    end_time = models.TimeField(choices=TIME_MAP_HALF_HOURS_CHOICES)

    @classmethod
    def get(cls, pk):
        return SpecialScheduleModel.objects.filter(pk=pk).first()

    @classmethod
    def get_all(cls):
        return SpecialScheduleModel.objects.order_by('-start_date', 'start_time')

    @classmethod
    def get_count(cls):
        return SpecialScheduleModel.objects.count()

    @classmethod
    def get_by_date(cls, start_date):
        return SpecialScheduleModel.objects.filter(start_date=start_date).order_by('start_date', 'start_time')

    @classmethod
    def get_ranges(cls, start_date, start_time, end_time):
        return SpecialScheduleModel.objects.filter(start_date=start_date, start_time__lt=end_time, end_time__gt=start_time)

    @classmethod
    def get_ranges_by_date(cls, start_date, end_date):
        return SpecialScheduleModel.objects.filter(start_date__lte=end_date, start_date__gte=start_date)

    @classmethod
    def add_lack_date(cls, all_days, start_date, end_date):
        # get ranges
        all_special_days = SpecialScheduleModel.get_ranges_by_date(start_date, end_date)
        # get union
        unique = []
        for special_day in all_special_days:
            if special_day.start_date not in all_days:
                unique.append(special_day.start_date)

        all_days.extend(unique)
        return all_days


class SpecialHolydayModel(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    memo = models.CharField(max_length=30)

    @classmethod
    def get_all(cls):
        return SpecialHolydayModel.objects.order_by('-start_date')

    @classmethod
    def get_count(cls):
        return SpecialHolydayModel.objects.count()

    @classmethod
    def get_filtered_day(cls, filter_target_dates):
        result = []
        all_holidays = SpecialHolydayModel.get_all()
        for day in filter_target_dates:
            is_out_of_holiday = True
            for holiday in all_holidays:
                if holiday.start_date <= day and holiday.end_date >= day:
                    is_out_of_holiday = False

            if is_out_of_holiday:
                result.append(day)

        return result


class SeatModel(models.Model):
    name = models.CharField(max_length=10)
    memo = models.CharField(max_length=30)
    capacity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    minnum = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    count = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(99)])
    max_count_of_one_reserve = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(99)])

    @classmethod
    def get_all(cls):
        return SeatModel.objects.order_by('-pk')

    @classmethod
    def get(cls, pk):
        return SeatModel.objects.filter(pk=pk).first()

    def get_max_number_of_one_reserve(self):
        return self.max_count_of_one_reserve * self.capacity

    def get_use_seat_count(self, reserve_number):
        # round up is needed
        return -(-reserve_number // self.capacity)

    @classmethod
    def create_init_data(cls):
        SeatModel(name="カウンター席", memo="1人がけの席です。", capacity=1, minnum=1, count=6, max_count_of_one_reserve=6).save()
        SeatModel(name="テーブル席", memo="２人がけの席です。", capacity=2, minnum=2, count=2, max_count_of_one_reserve=2).save()
        SeatModel(name="テーブル席", memo="3~4人がけの席です。", capacity=4, minnum=3, count=1, max_count_of_one_reserve=1).save()


class ReserveModel(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    seat = models.ForeignKey(SeatModel, on_delete=models.CASCADE)
    seat_used_number = models.PositiveSmallIntegerField()
    start_date = models.DateField()
    start_time = models.TimeField()
    number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(6)])
    memo = models.CharField(max_length=500)
    full_name = models.CharField(max_length=30)
    tel = models.CharField(max_length=15)
    email = models.EmailField(default='', validators=[EmailValidator()])
    canceled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def can_cancel(self):
        if self.canceled:
            return False
        # now = datetime.datetime.now()
        # model_date = util.DateTimeUtil.get_datetime(self.start_date, self.start_time)
        # return now <= model_date
        return True

    @classmethod
    def get_by_pk(cls, reserve_pk):
        return ReserveModel.objects.filter(pk=reserve_pk).first()

    @classmethod
    def get_all_by_date(cls):
        return ReserveModel.objects.order_by('-start_date', '-start_time')

    @classmethod
    def get_all_by_created(cls):
        return ReserveModel.objects.order_by('-created_at')

    @classmethod
    def get_by_date(cls, start_date):
        return ReserveModel.objects.filter(start_date=start_date).order_by('-start_time')

    @classmethod
    def get_available_by_date(cls, start_date):
        return ReserveModel.objects.filter(canceled=False, start_date=start_date).order_by('-start_time')

    @classmethod
    def get_by_date_ranges(cls, start_date, end_date):
        return ReserveModel.objects.filter(canceled=False, start_date__gte=start_date, start_date__lte=end_date).order_by('-start_date', '-start_time')

    @classmethod
    def get_user_all_reserve(cls, user_id):
        return ReserveModel.objects.filter(user=user_id).order_by('-start_date', '-start_time')

    @classmethod
    def get_reserves_day_of_week(cls, start_date, day_of_week, start_time, end_time):
        return ReserveModel.objects.filter(canceled=False, start_date__gte=start_date, start_date__iso_week_day=day_of_week, start_time__gte=start_time, start_time__lte=end_time)

    @classmethod
    def get_reserve_count_by_date(cls, date):
        return ReserveModel.objects.filter(canceled=False, start_date=date).count()

    @classmethod
    def get_user_canceled_count(cls, user_id, check_start_date):
        return ReserveModel.objects.filter(canceled=True, user=user_id, start_date__gte=check_start_date).count()

    @classmethod
    def get_canceled_reserves_group_by_user(cls, check_start_date):
        return ReserveModel.objects.filter(canceled=True, start_date__gte=check_start_date).select_related().values('user', 'user__is_superuser', 'user__is_staff', 'user__username', 'user__tel_number', 'user__tel_number', 'user__email', 'user__second_email').annotate(count=Count('user')).order_by('-count')

    @classmethod
    def exists_user_reserve(cls, user_id):
        now = datetime.datetime.now()
        today_date = now.date()
        offset_time = util.TimeUtil.sub_minutes(now.time(), 10)
        return ReserveModel.objects.filter(user=user_id, canceled=False).filter(Q(start_date__gt=today_date) | Q(start_date=today_date, start_time__gte=offset_time)).exists()

    @classmethod
    def exists_user_availalbe_reserve(cls, user_id, reserve_pk):
        now = datetime.datetime.now()
        today_date = now.date()
        # 30 minutes before is available reserve
        offset_time = util.TimeUtil.sub_minutes(now.time(), 30)
        return ReserveModel.objects.filter(pk=reserve_pk, user=user_id, canceled=False).filter(Q(start_date__gt=today_date) | Q(start_date=today_date, start_time__gte=offset_time)).exists()

    @classmethod
    def exists_reserve(cls, start_date, end_date):
        return ReserveModel.objects.filter(canceled=False, start_date__gte=start_date, start_date__lte=end_date).exists()

    @classmethod
    def get_user_availalbe_reserve(cls, user_id, reserve_pk):
        now = datetime.datetime.now()
        today_date = now.date()
        # 30 minutes before is available reserve
        offset_time = util.TimeUtil.sub_minutes(now.time(), 30)
        return ReserveModel.objects.filter(pk=reserve_pk, user=user_id, canceled=False).filter(Q(start_date__gte=today_date) | Q(start_date=today_date, start_time__gte=offset_time)).first()

    @classmethod
    def get_user_current_reserve(cls, user_id):
        now = datetime.datetime.now()
        today_date = now.date()
        # 30 minutes after form current is available reserve
        offset_time = util.TimeUtil.sub_minutes(now.time(), 30)
        return ReserveModel.objects.filter(user=user_id, canceled=False).filter(Q(start_date__gt=today_date) | Q(start_date=today_date, start_time__gte=offset_time))

    @classmethod
    def get_reserve_sum_by_user(cls):
        return ReserveModel.objects.filter(canceled=False).select_related().values('user', 'user__username', 'user__tel_number', 'user__tel_number', 'user__email', 'user__second_email').annotate(count=Count('user'), last_start_date=Max('start_date')).order_by('-count')

    @classmethod
    def update_canceled(cls, reserve_pk, value):
        reserve = ReserveModel.objects.filter(pk=reserve_pk).first()
        reserve.canceled = value
        reserve.save()
        return reserve

    @classmethod
    def delete_canceled_reserve(cls, user_id):
        return ReserveModel.objects.filter(canceled=True, user=user_id).delete()


class CommonSettingModel(models.Model):
    key = models.CharField(max_length=30)
    value = models.CharField(max_length=5000)

    @classmethod
    def get_value(cls, key):
        return CommonSettingModel.objects.filter(key=key).first()

    @classmethod
    def set_value(cls, key, value):
        model = CommonSettingModel.get_value(key)
        if model is None:
            model = CommonSettingModel()

        model.key = key
        model.value = value
        print("valueeee", key, value)
        model.save()
