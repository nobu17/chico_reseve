from . import models
from . import util


class ReserveDuplicateCheck:
    def __init__(self, user):
        self.__user = user

    def is_availalble_reserve(self):
        if self.__user.id:
            if not models.ReserveModel.exists_user_reserve(self.__user.id):
                return True
        return False


class ReserveCalendar:
    def __init__(self, base_date):
        self.__base_date = base_date
        self.__calc_range_date()

    def __calc_range_date(self):
        # define range is +- 1 month
        start_and_end_dates = util.DateUtil.get_start_and_end(self.__base_date, 1, 1)
        self.__start_and_end_dates = list(map((lambda n: n.strftime('%Y-%m-%d')), start_and_end_dates))
        # holidaysho
        holidays = []
        holiday_records = models.SpecialHolydayModel.get_all()
        for holiday in holiday_records:
            print(holiday.start_date, holiday.end_date)
            dates = util.DateUtil.get_date_ranges(holiday.start_date, holiday.end_date)
            holidays.extend(dates)

        self.__holidays = list(map((lambda n: n.strftime('%Y-%m-%d')), holidays))

        # self.__holidays
        # get disabled weekdays from schedule
        self.__disabled_day_of_weeks = []
        all_schedules = models.WeeklyScheduleModel.get_all()

        for day_of_week, _ in models.DAYS_OF_WEEK:
            if not any(day_of_week == sche.dayofweek for sche in all_schedules):
                # this day of week value will be refined becasue, js calendar dayofweek define is different
                self.__disabled_day_of_weeks.append(day_of_week)

        # get reserves
        reserves_by_date = {}
        reserves = list(models.ReserveModel.get_by_date_ranges(start_and_end_dates[0], start_and_end_dates[1]))
        for reserve in reserves:
            str_date = reserve.start_date.strftime('%Y-%m-%d')
            val = reserves_by_date.get(str_date)
            if val is None:
                val = []
            val.append(reserve)
            reserves_by_date[str_date] = val

        self.__reserves_by_date = reserves_by_date

        # create date list for display calendar
        self.__reserves_date_list = []
        for date in reserves_by_date:
            self.__reserves_date_list.append({
                'name': 'reserve',
                'date': date
            })

    def get_start_and_end_dates(self):
        return self.__start_and_end_dates

    def get_holidays(self):
        return self.__holidays

    def get_disabled_day_of_weeks(self):
        return self.__disabled_day_of_weeks

    def get_reserves_by_date(self):
        return self.__reserves_by_date

    def get_reserves_date_list(self):
        return self.__reserves_date_list
