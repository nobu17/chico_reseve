import datetime
import calendar
import locale
from dateutil.relativedelta import relativedelta


class DateTimeUtil:
    @staticmethod
    def get_datetime(date, time):
        return datetime.datetime(year=date.year, month=date.month, day=date.day, hour=time.hour, minute=time.minute, second=time.second)

    @staticmethod
    def is_match(check_date, check_time, day_of_week, start_time, end_time):
        if check_date.weekday() != day_of_week:
            return False
        if check_time < start_time:
            return False
        if check_time > end_time:
            return False
        return True

    @staticmethod
    def get_str(date, time):
        locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
        return date.strftime('%Y年%m月%d日(%A) ') + time.strftime('%H:%M')


class TimeUtil:
    @staticmethod
    def get_ranges(start_time, end_time, duration_minutes):
        results = []
        tempDate = datetime.date.today()
        tempDuration = 0
        basetime = datetime.time(start_time.hour, start_time.minute, 00)
        dt = datetime.datetime.combine(tempDate, basetime) + datetime.timedelta(minutes=tempDuration)

        while (dt.time() <= end_time):
            results.append(dt.time())
            tempDuration += duration_minutes
            dt = datetime.datetime.combine(tempDate, basetime) + datetime.timedelta(minutes=tempDuration)

        return results

    @staticmethod
    def add_minutes(time, minutes):
        tempDate = datetime.date.today()
        basetime = datetime.time(time.hour, time.minute, 00)
        dt = datetime.datetime.combine(tempDate, basetime) + datetime.timedelta(minutes=minutes)
        return dt.time()

    @staticmethod
    def sub_minutes(time, minutes):
        tempDate = datetime.date.today()
        basetime = datetime.time(time.hour, time.minute, 00)
        dt = datetime.datetime.combine(tempDate, basetime) - datetime.timedelta(minutes=minutes)
        return dt.time()


class DateUtil:
    @staticmethod
    def get_ranges(start_date, days):
        results = []
        limit = start_date + datetime.timedelta(days=days)
        dt = start_date

        while(dt <= limit):
            results.append(dt)
            dt = dt + datetime.timedelta(days=1)

        return results

    @staticmethod
    def get_date(date, max_days, offset_days):
        result = None
        now = datetime.datetime.now().date()
        base_day = now + datetime.timedelta(days=offset_days)
        if date is None:
            result = base_day
        elif isinstance(date, datetime.datetime):
            result = date.date()
        elif isinstance(date, datetime.date):
            result = date
        else:
            raise Exception("not support date format")

        if result <= base_day:
            return base_day
        else:
            limit = now + datetime.timedelta(max_days)
            if limit < result:
                return base_day

        return result

    @staticmethod
    def get_months_date(base_date, start_offset_month, end_offset_month):
        start_date = base_date + relativedelta(months=(-start_offset_month))
        end_date = base_date + relativedelta(months=end_offset_month)
        start = datetime.date(start_date.year, start_date.month, 1)
        end = datetime.date(end_date.year, end_date.month, calendar.monthrange(end_date.year, end_date.month)[1])
        delta = end - start

        result = []
        for i in range(delta.days + 1):
            result.append((start + datetime.timedelta(days=i)))

        return result

    @staticmethod
    def get_start_and_end(base_date, start_offset_month, end_offset_month):
        start_date = base_date + relativedelta(months=(-start_offset_month))
        end_date = base_date + relativedelta(months=end_offset_month)
        start = datetime.date(start_date.year, start_date.month, 1)
        end = datetime.date(end_date.year, end_date.month, calendar.monthrange(end_date.year, end_date.month)[1])

        result = [start, end]

        return result

    @staticmethod
    def parse(date):
        result = None
        if isinstance(date, datetime.datetime):
            result = date.date()
        elif isinstance(date, datetime.date):
            result = date
        elif isinstance(date, str):
            result = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        else:
            raise Exception("not support date format")

        return result

    @staticmethod
    def get_date_from_now(offset_days):
        now = datetime.datetime.now().date()
        return now + datetime.timedelta(days=offset_days)

    @staticmethod
    def get_date_ranges(start_date, end_date):
        result = []
        # to include start
        start = start_date + datetime.timedelta(days=-1)
        for n in range((end_date - start).days):
            result.append(start_date + datetime.timedelta(n))

        return result


class NumberUtil:
    @staticmethod
    def getNumber(number, default, max, min):
        if number is None:
            return default
        elif number > max:
            return default
        elif number <= min:
            return default

        return number


class ListUtil:
    @staticmethod
    def list_difference(list1, list2):
        result = list1.copy()
        for value in list2:
            if value in result:
                result.remove(value)

        return result
