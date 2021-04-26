from django import forms
from django.core.validators import RegexValidator, EmailValidator
import datetime
from . import models
from . import exceptions
from . import const
from . import util
from . import logics

TELLNUMBER_REGEX = RegexValidator(regex=r'^[0-9]+$', message=("電話番号は数値のみ入力可能です。例：09012345678"))


class CommonSettingsModelForm(forms.Form):
    admin_mails = forms.CharField(
        label='管理メール通知アドレス',
        max_length=500,
        required=True,
        help_text="カンマ区切りで複数可能。500文字まで",
    )
    send_from_mail = forms.CharField(
        label='自動送信メールのFromアドレス',
        max_length=50,
        required=True,
        help_text="50文字まで",
    )
    reserve_complete_user_message_key = forms.CharField(
        label='予約完了時の店舗からのメッセージ',
        max_length=1000,
        required=True,
        help_text="1000文字まで",
        widget=forms.Textarea(attrs={'class': 'textarea', 'rows': '5'})
    )

    def load(self):
        self.fields['admin_mails'].initial = logics.CommonSetting.get_admin_mails()
        self.fields['send_from_mail'].initial = logics.CommonSetting.get_send_from_mail()
        self.fields['reserve_complete_user_message_key'].initial = logics.CommonSetting.get_reserve_complete_user_message()

    def save(self):
        logics.CommonSetting.set_admin_mails(self.cleaned_data['admin_mails'].strip())
        logics.CommonSetting.set_send_from_mail(self.cleaned_data['send_from_mail'].strip())
        logics.CommonSetting.set_reserve_complete_user_message(self.cleaned_data['reserve_complete_user_message_key'].strip())


class SpecialHolydayModelForm(forms.ModelForm):
    field_order = ['memo', 'start_date', 'end_date']

    class Meta:
        model = models.SpecialHolydayModel
        fields = {'memo', 'start_date', 'end_date'}
        labels = {
            'memo': '名称',
        }

    start_date = forms.DateField(
        label="開始日",
        widget=forms.DateInput(attrs={"type": "date"})
    )

    end_date = forms.DateField(
        label="終了日",
        widget=forms.DateInput(attrs={"type": "date"})
    )

    def can_add_data(self):
        count = models.SpecialHolydayModel.get_count()
        return count < const.MAX_HOLIDAY_COUNT

    def clean(self):
        start_date = self.cleaned_data['start_date']
        end_date = self.cleaned_data['end_date']

        if start_date > end_date:
            raise forms.ValidationError("開始日時は終了日時と同日か過去にする必要があります。")

        # check reserve
        if models.ReserveModel.exists_reserve(start_date, end_date):
            raise forms.ValidationError("指定した範囲内に既に予約が存在するため、休日設定できません。")

        return self.cleaned_data


class WeeklyScheduleModelForm(forms.ModelForm):
    field_order = ['dayofweek', 'start_time', 'end_time']

    class Meta:
        model = models.WeeklyScheduleModel
        fields = {'dayofweek', 'start_time', 'end_time'}
        labels = {
            'dayofweek': '曜日',
            'start_time': '開始時刻',
            'end_time': '終了時刻'
        }

    def clean(self):
        dayofweek = self.cleaned_data['dayofweek']
        start_time = self.cleaned_data['start_time']
        end_time = self.cleaned_data['end_time']

        if start_time >= end_time:
            raise forms.ValidationError("開始時刻は終了時刻より過去にする必要があります。")

        if end_time < (util.TimeUtil.add_minutes(start_time, const.RESERVE_MINUTES_OFFSET)):
            raise forms.ValidationError(f'開始時刻と終了時刻の感覚が短すぎます。{const.RESERVE_MINUTES_OFFSET}分以上必要です。')

        ranges = models.WeeklyScheduleModel.get_ranges(self.instance.pk, dayofweek, start_time, end_time)
        if ranges.count() > 0:
            raise forms.ValidationError("重複したスケジュールが存在します。")

        # check reserve
        # old schedule should not have reserve
        now_date = datetime.datetime.now().date()
        old = models.WeeklyScheduleModel.get(self.instance.pk)
        if old is not None:
            # python weeekday and model weekday is mismatch (+1 to adjust)
            exists_reserves = models.ReserveModel.get_reserves_day_of_week(now_date, (old.dayofweek + 1), old.start_time, old.end_time)
            # if exists reserves are not match new schedule, it is error
            for reserve in exists_reserves:
                if not util.DateTimeUtil.is_match(reserve.start_date, reserve.start_time, dayofweek, start_time, end_time):
                    raise forms.ValidationError("変更するとこの予約が維持できません。" + util.DateTimeUtil.get_str(reserve.start_date, reserve.start_time))

        return self.cleaned_data


class SeatModelForm(forms.ModelForm):
    field_order = ['name', 'memo', 'count', 'capacity', 'minnum', 'max_count_of_one_reserve']

    class Meta:
        model = models.SeatModel
        fields = {'name', 'memo', 'count', 'capacity', 'minnum', 'max_count_of_one_reserve'}
        labels = {
            'name': '名前',
            'memo': '説明',
            'count': '席数',
            'capacity': '収容人数',
            'minnum': '必要人数/予約',
            'max_count_of_one_reserve': '使用可能数/予約'
        }
        help_texts = {
            'name': '10文字まで',
            'memo': '30文字まで',
        }


ONE = 1
TWO = 2
THREE = 3
FOUR = 4
FIVE = 5
SIX = 6

RESERVATION_NUMBER = (
    (ONE, '1名'),
    (TWO, '2名'),
    (THREE, '3名'),
    (FOUR, '4名'),
    (FIVE, '5名'),
    (SIX, '6名'),
)


class ReserveForm(forms.Form):

    full_name = forms.CharField(
        label='代表者氏名',
        max_length=10,
        required=True,
        help_text="10文字まで",
    )

    tel = forms.CharField(
        label='電話番号',
        max_length=15,
        required=True,
        validators=[TELLNUMBER_REGEX]
    )

    email = forms.EmailField(
        label='メールアドレス',
        required=True,
        validators=[EmailValidator]
    )

    memo = forms.CharField(
        label='メモ等確認事項',
        max_length=500,
        required=False,
        help_text="500文字まで",
        widget=forms.Textarea(attrs={'class': 'textarea', 'rows': '5'})
    )

    number = forms.ChoiceField(
        label='予約人数',
        required=True,
        choices=RESERVATION_NUMBER
    )

    start_date = forms.ChoiceField(
        label='予約日',
        required=True,
        disabled=False,
    )

    selected_time = forms.ChoiceField(
        label='予約時間',
        required=True,
        disabled=False,
        widget=forms.RadioSelect(attrs={'class': 'select_time'})
    )

    selected_seat = forms.ChoiceField(
        label='座席',
        required=True,
        disabled=False,
        widget=forms.RadioSelect(attrs={'class': 'select_seat'})
    )

    def load_userinfo(self, user_pk):
        user = models.CustomUser.get(user_pk)
        self.fields['full_name'].initial = user.full_name
        self.fields['tel'].initial = user.tel_number
        self.fields['email'].initial = user.get_email()

    def init_field(self, number, select_date, select_dates, selected_times, selected_seats):
        self.fields['number'].initial = number
        self.fields['start_date'].choices = select_dates
        self.fields['start_date'].initial = select_date
        self.fields['selected_time'].choices = selected_times
        self.fields['selected_seat'].choices = selected_seats


class ReserveConfirmForm(forms.Form):
    field_order = ['number', 'start_date', 'selected_time', 'selected_seat', 'full_name', 'tel', 'email', 'memo']

    full_name = forms.CharField(
        label='代表者氏名',
        max_length=10,
        required=True,
    )

    tel = forms.CharField(
        label='電話番号',
        max_length=15,
        required=True,
        validators=[TELLNUMBER_REGEX]
    )

    email = forms.EmailField(
        label='メールアドレス',
        required=True,
        validators=[EmailValidator]
    )

    memo = forms.CharField(
        label='メモ等確認事項',
        max_length=500,
        required=False,
    )

    number = forms.IntegerField(
        label='予約人数',
        required=True
    )

    start_date = forms.DateField(
        label='予約日',
        required=True
    )

    selected_time = forms.TimeField(
        label='予約時間',
        required=True,
    )

    selected_seat = forms.CharField(
        label='座席',
        required=True,
    )

    def get_selected_seat_display(self):
        seat = models.SeatModel.get(self.cleaned_data["selected_seat"])
        return seat.name

    def load_for_cancl_admin(self, reserve_pk):
        data = models.ReserveModel.get_by_pk(reserve_pk)
        self.__set_fields(data)

    def load_for_cancel(self, user, reserve_pk):
        if not models.ReserveModel.exists_user_availalbe_reserve(user.id, reserve_pk):
            raise exceptions.NotExistsReserveError("該当の予約は存在しません")
        data = models.ReserveModel.get_user_availalbe_reserve(user, reserve_pk)
        self.__set_fields(data)

    def __set_fields(self, data):
        self.fields['start_date'].initial = data.start_date
        self.fields['selected_time'].initial = data.start_time
        self.fields['number'].initial = data.number
        self.fields['full_name'].initial = data.full_name
        self.fields['tel'].initial = data.tel
        self.fields['email'].initial = data.email
        self.fields['memo'].initial = data.memo
        self.fields['selected_seat'].initial = data.seat.pk

    def cancel(self, user, reserve_pk):
        if not models.ReserveModel.exists_user_availalbe_reserve(user.id, reserve_pk):
            raise exceptions.NotExistsReserveError("該当の予約は存在しません")
        try:
            return models.ReserveModel.update_canceled(reserve_pk, True)
        except Exception as e:
            print(e)
            raise exceptions.CancelFailedError("キャンセルの処理に失敗しました。お手数ですが再度お試しください。")

    def cancel_admin(self, reserve_pk):
        try:
            return models.ReserveModel.update_canceled(reserve_pk, True)
        except Exception as e:
            print(e)
            raise exceptions.CancelFailedError("キャンセルの処理に失敗しました。お手数ですが再度お試しください。")

    def save(self, user):
        # if already reserved, refused (To do: neeed check canel and already passed schedule)
        if models.ReserveModel.exists_user_reserve(user.id):
            raise exceptions.ReserveCanNotSaveError("既に予約済みです。同時に予約できるのは１件のみです。")

        # creating reserve model
        reserve = models.ReserveModel()
        reserve.start_date = self.cleaned_data['start_date']
        reserve.start_time = self.cleaned_data['selected_time']
        reserve.number = self.cleaned_data['number']
        reserve.memo = self.cleaned_data['memo']
        reserve.full_name = self.cleaned_data['full_name']
        reserve.tel = self.cleaned_data['tel']
        reserve.email = self.cleaned_data['email']

        seat_pk = self.cleaned_data['selected_seat']
        seat = models.SeatModel.get(seat_pk)
        reserve.seat = seat
        # calc seat used number
        reserve.seat_used_number = seat.get_use_seat_count(reserve.number)

        user = models.CustomUser(id=user.id)
        reserve.user = user
        reserve.save()

        # update user information
        update_target_user = models.CustomUser.get(user.id)
        update_target_user.full_name = reserve.full_name
        update_target_user.tel_number = reserve.tel
        update_target_user.second_email = reserve.email
        update_target_user.save()

        return reserve
