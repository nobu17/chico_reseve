from . import const
from . import models
from . import util
import locale
import datetime
from django.db import connection
from django.core.mail import EmailMessage


class ReserveDuplicateCheck:
    """This class is responsible for checking reservation of user not to reserve multiplly
    """

    def __init__(self, user):
        self.__user = user

    def is_availalble_reserve(self):
        # if user is administraotr, not check duplication
        if self.__user.is_superuser:
            return True
        if self.__user.id:
            if not models.ReserveModel.exists_user_reserve(self.__user.id):
                return True
        return False

    def get_duplicated_error_message(self):
        return "既に予約済みです。同時に予約できるのは１件のみです。"


class WeeklyScheduleCheck:
    """This class is responsible for checking weekly schedule
    """

    def is_reservation_exists(self, weekly_schedule_pk):
        """check reservation is exists or not

        Args:
            weekly_schedule_pk ([int]): [weeklyschedule pk]

        Returns:
            [bool]: [reservation is exists or not]
        """
        now_date = datetime.datetime.now().date()
        schedule = models.WeeklyScheduleModel.get(weekly_schedule_pk)
        if schedule is not None:
            # python weeekday and model weekday is mismatch (+1 to adjust)
            exists_reserves = models.ReserveModel.get_reserves_day_of_week(now_date, (schedule.dayofweek + 1), schedule.start_time, schedule.end_time)
            # if exists reserves are not match new schedule, it is error
            for reserve in exists_reserves:
                if util.DateTimeUtil.is_match(reserve.start_date, reserve.start_time, schedule.dayofweek, schedule.start_time, schedule.end_time):
                    return True

        return False

    def vlidate(self, schedule_pk, start_time, end_time, day_of_week):
        """is valid time or not

        Args:
            schedule_pk ([int]): [week schedule pk]
            start_time ([time]): [start time]
            end_time ([time]): [end time]
            day_of_week ([int]): [day of week]

        Returns:
            [tuple(bool, string)]: [(time is valid),(error message)]
        """
        if start_time >= end_time:
            return (False, "開始時刻は終了時刻より過去にする必要があります。")

        if end_time < (util.TimeUtil.add_minutes(start_time, const.RESERVE_MINUTES_OFFSET)):
            return (False, f'開始時刻と終了時刻の感覚が短すぎます。{const.RESERVE_MINUTES_OFFSET}分以上必要です。')

        ranges = models.WeeklyScheduleModel.get_ranges(schedule_pk, day_of_week, start_time, end_time)
        if ranges.count() > 0:
            return (False, "重複したスケジュールが存在します。")

        # check reserve
        # old schedule should not have reserve
        now_date = datetime.datetime.now().date()
        old = models.WeeklyScheduleModel.get(schedule_pk)
        if old is not None:
            # python weeekday and model weekday is mismatch (+1 to adjust)
            exists_reserves = models.ReserveModel.get_reserves_day_of_week(now_date, (old.dayofweek + 1), old.start_time, old.end_time)
            # if exists reserves are not match new schedule, it is error
            for reserve in exists_reserves:
                if not util.DateTimeUtil.is_match(reserve.start_date, reserve.start_time, day_of_week, start_time, end_time):
                    return (False, "変更するとこの予約が維持できません。" + util.DateTimeUtil.get_str(reserve.start_date, reserve.start_time))

        return (True, "")


class SpecialScheduleCheck:
    """This class is responsible for checking special schedule
    """

    def is_reservation_exists(self, special_schedule_pk):
        """check reservation is exists or not

        Args:
            special_schedule_pk ([int]): [special_schedule_pk pk]

        Returns:
            [bool]: [reservation is exists or not]
        """
        schedule = models.SpecialScheduleModel.get(special_schedule_pk)

        if schedule is not None:
            # if schedule is past, not check anything
            if schedule.start_date < datetime.datetime.now().date():
                return False

            exists_reserves = models.ReserveModel.get_by_date(schedule.start_date)
            for reserve in exists_reserves:
                reserve_end_time = util.TimeUtil.add_minutes(reserve.start_time, const.RESERVE_MINUTES_OFFSET)
                if util.TimeUtil.is_range(schedule.start_time, schedule.end_time, reserve.start_time, reserve_end_time):
                    return True

        return False

    def validate(self, start_date, start_time, end_time):
        """is valid schedule or not

        Args:
            start_date ([date]): [start_date]
            start_time ([time]): [start time]
            end_time ([time]): [end time]

        Returns:
            [tuple(bool, string)]: [(time is valid),(error message)]
        """
        now_date = datetime.datetime.now().date()
        if now_date >= start_date:
            return (False, "開始日付は明日以降のみ指定可能です。")

        if start_time >= end_time:
            return (False, "開始時刻は終了時刻より過去にする必要があります。")

        if end_time < (util.TimeUtil.add_minutes(start_time, const.RESERVE_MINUTES_OFFSET)):
            return (False, f'開始時刻と終了時刻の間隔が短すぎます。{const.RESERVE_MINUTES_OFFSET}分以上必要です。')

        # ranges = models.WeeklyScheduleModel.get_ranges(-1, start_date.weekday(), start_time, end_time)
        # if ranges.count() > 0:
        #     return (False, "通常予定に重複したスケジュールが存在します。")

        ranges = models.SpecialScheduleModel.get_ranges(start_date, start_time, end_time)
        if ranges.count() > 0:
            return (False, "重複したスケジュールが存在します。")

        return (True, "")


class UserBanCheck:
    """This class is responsible for checking user banned or not
    """

    def __init__(self, user):
        self.__user = user

    def is_banned(self):
        # super user can not be banned
        if self._is_staff_or_admin():
            return False
        if self.__user.id:
            threthold_date = util.DateUtil.get_date_from_now(-const.BANNED_CHECK_PERIOD_OF_DAYS)
            canceld_count = models.ReserveModel.get_user_canceled_count(self.__user.id, threthold_date)
            if canceld_count >= const.BANNED_THRETHOLD_OF_CANCEL:
                return True
        return False

    def get_user_banned_message(self):
        return "一定数のキャンセルを行ったため、予約不可能です。お手数ですがContactメニューから管理者に連絡をお願いいたします。"

    def delete_banned_data(self):
        if not self._is_staff_or_admin():
            models.ReserveModel.delete_canceled_reserve(self.__user.id)

    def get_banned_users(self):
        threthold_date = util.DateUtil.get_date_from_now(-const.BANNED_CHECK_PERIOD_OF_DAYS)
        # filter admins or not over thretholds
        cancels = models.ReserveModel.get_canceled_reserves_group_by_user(threthold_date).filter(user__is_staff=False, user__is_superuser=False, count__gte=const.BANNED_THRETHOLD_OF_CANCEL)
        return cancels

    def _is_staff_or_admin(self):
        if self.__user.is_superuser or self.__user.is_staff:
            return True
        return False


class ReserveCalendar:
    """This class is responsible for manuplating calendar logics
    """

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


class SendEmail:
    """This class is responsible for send email to admins or user
    """

    def __init__(self):
        admin_mails = CommonSetting.get_admin_mails()
        self._admin_emails = [mail.strip() for mail in admin_mails.split(",")]
        self._from_email = CommonSetting.get_send_from_mail()

    def send_reserve_complete(self, reserve_model):
        """
        send email about reserve is completed to user
        send email about reserve is added to admin
        """
        if (reserve_model is None):
            raise Exception("reserve model error")

        subject = "予約完了しました。(CHICO★SPICE)"
        message = "CHICO★SPICEの店舗予約が完了しました。\n"
        message += "予約内容は以下の通りです。\n\n\n"
        message = self._create_reserve_common_message_for_user(message, reserve_model)
        message += CommonSetting.get_reserve_complete_user_message()
        # send to user
        self._send_email(subject, message, self._from_email, [reserve_model.email], self._admin_emails)

    def send_cancel_completed(self, reserve_model):
        """
        send email about cancel is completed to user
        send email about cancel is added to admin
        """
        if (reserve_model is None):
            raise Exception("reserve model error")

        subject = "予約をキャンセルしました。(CHICO★SPICE)"
        message = "CHICO★SPICEの店舗予約をキャンセルしました。\n"
        message += "キャンセル内容は以下の通りです。\n\n\n"
        message = self._create_reserve_common_message_for_user(message, reserve_model)
        message += CommonSetting.get_reserve_cancel_user_message()
        self._send_email(subject, message, self._from_email, [reserve_model.email], self._admin_emails)

    def send_update_completed(self, reserve_model):
        """
        send email about update is completed to user
        send email about update is added to admin
        """
        if (reserve_model is None):
            raise Exception("reserve model error")

        subject = "予約情報更新しました。(CHICO★SPICE)"
        message = "CHICO★SPICEの店舗予約の情報更新が完了しました。\n"
        message += "予約内容は以下の通りです。\n\n\n"
        message = self._create_reserve_common_message_for_user(message, reserve_model)
        message += CommonSetting.get_reserve_complete_user_message()
        self._send_email(subject, message, self._from_email, [reserve_model.email], self._admin_emails)

    def _send_email(self, subject, message, from_email, to_emails, bcc):
        try:
            email = EmailMessage(subject, message, from_email, to_emails, bcc)
            email.send()
        except Exception as e:
            print("mail send failed:", e)

    def _create_reserve_common_message_for_user(self, message, reserve_model):
        message += "○予約日時\n"
        message += f"{util.DateTimeUtil.get_str(reserve_model.start_date, reserve_model.start_time)}\n\n"
        message += "○予約人数\n"
        message += f"{reserve_model.number} 名\n\n"
        message += "○席\n"
        message += f"{reserve_model.seat.name}\n\n"
        message += "○メモ等確認事項\n"
        message += f"{reserve_model.memo}\n\n"
        return message


class CommonSetting:
    """This class is responsible for adding or updating common settings
    """
    __send_from_mail_key = "send_from_mail"
    __admin_mails_key = "admin_mails"
    __reserve_complete_user_message_key = "reserve_complete_user_message"
    __reserve_cancel_user_message_key = "reserve_cancel_user_message"

    @classmethod
    def get_send_from_mail(cls):
        return cls.__get_value(cls.__send_from_mail_key, "no-replay@chico.com")

    @classmethod
    def set_send_from_mail(cls, value):
        models.CommonSettingModel.set_value(cls.__send_from_mail_key, value)

    @classmethod
    def get_reserve_complete_user_message(cls):
        return cls.__get_value(cls.__reserve_complete_user_message_key, "")

    @classmethod
    def set_reserve_complete_user_message(cls, value):
        models.CommonSettingModel.set_value(cls.__reserve_complete_user_message_key, value)

    @classmethod
    def get_reserve_cancel_user_message(cls):
        return cls.__get_value(cls.__reserve_cancel_user_message_key, "")

    @classmethod
    def set_reserve_cancel_user_message(cls, value):
        models.CommonSettingModel.set_value(cls.__reserve_cancel_user_message_key, value)

    @classmethod
    def get_admin_mails(cls):
        return cls.__get_value(cls.__admin_mails_key, "no-replay@chico.com")

    @classmethod
    def set_admin_mails(cls, value):
        models.CommonSettingModel.set_value(cls.__admin_mails_key, value)

    @classmethod
    def __get_value(cls, key, default_value):
        result = models.CommonSettingModel.get_value(key)
        if result is None:
            return default_value
        return result.value


class ReserveCalcLogic:
    """
    calcurating the resevation core logic (remain seat info and king, availalble time to reserve)
    """

    def __init__(self, select_date, reserve_number, max_days, duration_minutes, is_admin):
        self.__reserve_number = reserve_number
        self.__max_days = max_days
        self.__duration_minutes = duration_minutes
        # if seelct_date is none set tomorrow and then it is checked by calc_select_dates methods
        # admin can reserve today
        start_offset_days = 0 if is_admin else const.OFFSET_DAYS_START_RESERVE
        self.__select_date = util.DateUtil.get_date(select_date, self.__max_days, start_offset_days)
        self.__is_admin = is_admin

    def calc_info(self):
        """
        calculating selectable dates, times, seats
        """
        self._calc_select_dates()
        self._calc_reserve_time_list()
        self._calc_seat_remain()

    def _calc_select_dates(self):
        """
        set availalbe dates of reserve
        """
        select_dates = []
        # get reservable all days from current date + offset (day) (not using selected_date)
        # admin can reserve today
        start_offset_days = 0 if self.__is_admin else const.OFFSET_DAYS_START_RESERVE
        base_date = datetime.datetime.now().date() + datetime.timedelta(days=start_offset_days)
        all_days = util.DateUtil.get_ranges(base_date, self.__max_days)
        # filter actual days by available schedules
        filtered_days = models.WeeklyScheduleModel.get_filtered_date_by_availalble_dayofweeks(all_days)
        # add special schedule
        filtered_days = models.SpecialScheduleModel.add_lack_date(filtered_days, all_days[0], all_days[-1])
        # filter special holiday
        filtered_days = models.SpecialHolydayModel.get_filtered_day(filtered_days)
        for dt in filtered_days:
            select_dates.append(dt)

        self.__select_dates = select_dates
        # get difference as disabled days
        self.__disabled_select_dates = util.ListUtil.list_difference(all_days, filtered_days)

        # select_date is setted without selectable at init, so if it is not match list, select again
        if (self.__select_date not in self.__select_dates) and (len(self.__select_dates) > 0):
            self.__select_date = self.__select_dates[0]

    def get_select_date(self):
        return self.__select_date

    def get_disabled_select_date(self):
        return self.__disabled_select_dates

    def get_select_dates(self):
        return self.__select_dates

    def get_select_dates_choices(self):
        # locale.setlocale(locale.LC_ALL, '')
        locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
        choices = []
        for dt in self.__select_dates:
            frm = dt.strftime('%Y/%m/%d (%A)')
            choices.append((dt, frm))
        return choices

    def _calc_reserve_time_list(self):
        """
        set availalble times of resereve from store's schedule
        """
        # week_of_day = 1
        week_of_day = self.__select_date.weekday()
        self.__reserve_time_list = []
        # special schedules
        specials = models.SpecialScheduleModel.get_by_date(self.__select_date)
        # if exists special holuday, ignore existing weekly schedule
        if len(specials) > 0:
            schedules = specials
        else:
            # get available time schedules by selected date' dayofweek
            schedules = list(models.WeeklyScheduleModel.get_by_dayofweek(week_of_day))

        # for special in specials:
        #    schedules.append(special)

        # divide the schedule by segument of time
        for schedule in schedules:
            # actual end_time is needed to concern offsets
            end_time = util.TimeUtil.add_minutes(schedule.end_time, -const.RESERVE_MINUTES_OFFSET)
            time_results = util.TimeUtil.get_ranges(schedule.start_time, end_time, self.__duration_minutes)
            for time_result in time_results:
                self.__reserve_time_list.append(time_result)
                # self.__reserve_time_list.append((time_result, time_result.strftime('%H:%M')))
        self.__reserve_time_list.sort()

    def get_reserve_time_list_choices(self):
        """
        get availalble times of resereve with seat reservable status
        """
        choices = []
        all_seat_status = self.get_all_seat_states()
        for time_result in self.__reserve_time_list:
            frm = time_result.strftime('%H:%M')
            # get seat stutas
            can_reserve = all_seat_status[frm]["can_reserve"]
            if can_reserve:
                frm += '\n○'
            else:
                frm += '\n×'

            choices.append((time_result, frm))
        return choices

    def get_all_seats_for_choice(self):
        selectable_seats = []
        all_seats = models.SeatModel.get_all()
        for seat in all_seats:
            selectable_seats.append((seat.pk, seat.name))
        return selectable_seats

    def get_all_seats_info(self):
        selectable_seats = {}
        all_seats = models.SeatModel.get_all()
        for seat in all_seats:
            selectable_seats[seat.pk] = {"name": seat.name, "memo": seat.memo}
        return selectable_seats

    def _calc_seat_remain(self):
        self.__seat_remain_info = []
        # get seat infomation
        seats = models.SeatModel.get_all()
        # ToDo:need to concern no seats case
        # create a remain model
        for time in self.__reserve_time_list:
            self.__seat_remain_info.append(SeatRemainInformation(time, self.__duration_minutes, seats))

        print('before seatinfo')
        self.print_test()

        # get reserves and calc reamin seat number
        reserves = models.ReserveModel.get_by_date(self.__select_date)
        for reserve in reserves:
            for remain in self.__seat_remain_info:
                # decreasing seat count if match the time
                remain.decrease_seat_remain(reserve)

        print('after seatinfo')
        self.print_test()

        # set seat_state by reserve number
        for seat in self.__seat_remain_info:
            seat.set_state_by_reserve_number(self.__reserve_number)

    def get_seat_remain_info(self):
        return self.__seat_remain_info

    def print_test(self):
        for seat in self.__seat_remain_info:
            print(seat)

    def get_all_seat_states(self):
        result = {}
        for seat in self.__seat_remain_info:
            # seat.set_state_by_reserve_number(self.__reserve_number)
            temp = seat.get_seat_state(self.__reserve_number)
            # key:starttime, value: {seatstate}
            result[temp[0]] = temp[1]

        return result

    def check_availalbe_reserve(self, start_time):
        # check select date reserve condition
        seat_states = self.get_all_seat_states()
        return seat_states[start_time.strftime('%H:%M')]


class SeatRemainInformation:
    # seat stock is keyvalye (key;seatid, value:amount of stock)
    def __init__(self, start_time, duration_minutes, seats):
        self.start_time = start_time
        self.duration_minutes = duration_minutes
        self.end_time = util.TimeUtil.add_minutes(start_time, duration_minutes)
        self.seats = seats
        self.disabled_seats_ids = []
        # init seat remains
        self.seat_remains = {}
        for seat in seats:
            self.seat_remains[seat.pk] = {'seat_count': seat.count, 'seat_capacity': seat.capacity}

    def decrease_seat_remain(self, reserve_data):
        # define end time form reservation start time
        reserve_end_time = util.TimeUtil.add_minutes(reserve_data.start_time, const.RESERVE_MINUTES_OFFSET)
        # if reservation is match the time, decreasing the specified seat number
        if self.start_time >= reserve_data.start_time and reserve_end_time >= self.end_time:
            self.seat_remains[reserve_data.seat.pk]['seat_count'] -= reserve_data.seat_used_number

    def set_state_by_reserve_number(self, reserve_number):
        self.disabled_seats_ids = []
        # min check
        for seat in self.seats:
            # check min requirement
            if seat.minnum > reserve_number:
                self.disabled_seats_ids.append(seat.pk)
            # check max availalbe
            elif seat.get_max_number_of_one_reserve() < reserve_number:
                self.disabled_seats_ids.append(seat.pk)

    # get seat state (key:start_time, value{can_reserve:Bool, seat_status:{pk, Bool}})
    def get_seat_state(self, reserve_number):
        result = {}
        print("disabled_seats_ids", self.disabled_seats_ids)
        for pk, info in self.seat_remains.items():
            # if disabled always False
            if pk in self.disabled_seats_ids:
                result[pk] = False
            # if over seat capacity is over reserve, available to be reserve
            elif (((info['seat_capacity'] * info['seat_count']) - reserve_number) >= 0):
                result[pk] = True
            else:
                result[pk] = False

        all_seat_state = False
        for _, seat_state in result.items():
            if seat_state:
                all_seat_state = True

        summary = {
            'can_reserve': all_seat_state,
            'seat_status': result
        }

        return (self.start_time.strftime('%H:%M'), summary)

    def __str__(self):
        temp = "start_time:" + self.start_time.strftime('%H:%M') + ' '

        for k, v in self.seat_remains.items():
            temp += "Seat" + str(k) + ":" + str(v) + ' '

        return temp


class DebugData:
    def __init__(self, mode):
        self._mode = mode

    def do_task(self):
        """clear reservation records
        """
        if self._mode == "delete_reserve":
            cursor = connection.cursor()
            cursor.execute("TRUNCATE TABLE `reserve_app_reservemodel`")
            return True
        elif self._mode == "delete_user":
            models.CustomUser.clear_without_admin()
            return True
        elif self._mode == "init_store_schedule":
            cursor = connection.cursor()
            cursor.execute("TRUNCATE TABLE `reserve_app_weeklyschedulemodel`")
            models.WeeklyScheduleModel.create_init_data()
            return True
        elif self._mode == "init_seat_and_reserve":
            cursor = connection.cursor()
            # at first clear reserve
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            cursor.execute("TRUNCATE TABLE `reserve_app_reservemodel`")
            cursor.execute("TRUNCATE TABLE `reserve_app_seatmodel`")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            models.SeatModel.create_init_data()
            return True
        else:
            return False
