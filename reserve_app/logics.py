from . import models
from . import util
from django.core.mail import send_mail


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


class SendEmail:
    def __init__(self):
        admin_mails = CommonSetting.get_admin_mails()
        self.__admin_emails = [mail.strip() for mail in admin_mails.split(",")]
        self.__from_email = CommonSetting.get_send_from_mail()

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
        message = self.__create_reserve_common_message_for_user(message, reserve_model)
        message += CommonSetting.get_reserve_complete_user_message()
        # send to user
        self.__send_email(subject, message, self.__from_email, [reserve_model.email])

        # send to admins
        subject = "予約通知"
        message = "新規予約が追加されました。\n"
        message += "予約内容は以下の通りです。\n\n\n"
        message = self.__create_reserve_common_message_for_admin(message, reserve_model)
        # send to admin
        self.__send_email(subject, message, self.__from_email, self.__admin_emails)

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
        message = self.__create_reserve_common_message_for_user(message, reserve_model)
        message += CommonSetting.get_reserve_cancel_user_message()
        # send to user
        self.__send_email(subject, message, self.__from_email, [reserve_model.email])

        # send to admins
        subject = "予約キャンセル通知"
        message = "予約がキャンセルされました。\n"
        message += "予約内容は以下の通りです。\n\n\n"
        message = self.__create_reserve_common_message_for_admin(message, reserve_model)
        # send to admin
        self.__send_email(subject, message, self.__from_email, self.__admin_emails)

    def __send_email(self, subject, message, from_email, to_emails):
        try:
            send_mail(subject, message, from_email, to_emails)
        except Exception as e:
            print("mail send failed:", e)

    def __create_reserve_common_message_for_user(self, message, reserve_model):
        message += "○予約日時\n"
        message += f"{util.DateTimeUtil.get_str(reserve_model.start_date, reserve_model.start_time)}\n\n"
        message += "○予約人数\n"
        message += f"{reserve_model.number} 名\n\n"
        message += "○席\n"
        message += f"{reserve_model.seat.name}\n\n"
        return message

    def __create_common_inquire_message(self, message):
        message += "本メールは送信専用です。"
        return message

    def __create_reserve_common_message_for_admin(self, message, reserve_model):
        message += "○予約日時\n"
        message += f"{util.DateTimeUtil.get_str(reserve_model.start_date, reserve_model.start_time)}\n\n"
        message += "○予約人数\n"
        message += f"{reserve_model.number} 名\n\n"
        message += "○席\n"
        message += f"{reserve_model.seat.name}\n\n"
        message += "○ユーザー名\n"
        message += f"{reserve_model.full_name}\n\n"
        message += "○連絡先\n"
        message += f"{reserve_model.tel}\n"
        message += f"{reserve_model.email}\n\n"
        return message


class CommonSetting:
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
