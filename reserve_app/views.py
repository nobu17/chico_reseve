# from django.shortcuts import render
from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import connection, transaction
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from urllib.parse import urlencode
from . import exceptions
from . import models
from . import forms
from . import util
from . import const
from . import logics
from . import encode
import datetime
import json
import locale
# import pytz
# Create your views here.


class IndexView(generic.TemplateView):
    template_name = "index.html"


class Contact(generic.TemplateView):
    template_name = "contact/index.html"


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
class UserAdminIndex(generic.TemplateView):
    template_name = "useradmin/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        today_date = util.DateUtil.get_date_from_now(0)
        tomorrow_date = util.DateUtil.get_date_from_now(1)

        today_reserve_count = models.ReserveModel.get_reserve_count_by_date(today_date)
        tomorrow_reserve_count = models.ReserveModel.get_reserve_count_by_date(tomorrow_date)

        ctx['today_reserve_count'] = today_reserve_count
        ctx['tomorrow_reserve_count'] = tomorrow_reserve_count
        ctx['tomorrow_date'] = tomorrow_date.strftime('%Y-%m-%d')
        return ctx


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
class UserAdminDebug(generic.TemplateView):
    template_name = "useradmin/debug.html"

    def get(self, request, **kwargs):
        mode = self.kwargs.get('mode', '')
        if mode == "delete_reserve":
            cursor = connection.cursor()
            cursor.execute("TRUNCATE TABLE `reserve_app_reservemodel`")
            messages.success(self.request, "削除に成功しました。")
        elif mode == "delete_user":
            models.CustomUser.clear_without_admin()
            messages.success(self.request, "削除に成功しました。")

        context = {}
        return self.render_to_response(context)


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
class SepecialHolidayList(generic.ListView):
    template_name = "holidays/index.html"
    queryset = models.SpecialHolydayModel.get_all()


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
class SepecialHolidayCreate(generic.CreateView):
    template_name = "holidays/create.html"
    model = models.SpecialHolydayModel
    form_class = forms.SpecialHolydayModelForm
    success_url = reverse_lazy('holidays_list')

    def dispatch(self, request, *args, **kwargs):
        if not self.form_class().can_add_data():
            messages.error(self.request, "最大の作成数に達しました。先に削除を行ってから追加してください。", extra_tags='danger')
            return redirect("holidays_list")

        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['start_date'] = datetime.date.today()
        initial['end_date'] = datetime.date.today()
        return initial

    def form_valid(self, form):
        messages.success(self.request, "作成に成功しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "データの更新に失敗しました。", extra_tags='danger')
        return super().form_invalid(form)


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
class SepecialHolidayUpdate(generic.UpdateView):
    template_name = "holidays/update.html"
    model = models.SpecialHolydayModel
    form_class = forms.SpecialHolydayModelForm
    success_url = reverse_lazy('holidays_list')

    def form_valid(self, form):
        messages.success(self.request, "更新に成功しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "データの更新に失敗しました。", extra_tags='danger')
        return super().form_invalid(form)


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
class SepecialHolidayDelete(generic.DeleteView):
    template_name = "holidays/delete.html"
    model = models.SpecialHolydayModel
    success_url = reverse_lazy('holidays_list')

    def form_valid(self, form):
        messages.success(self.request, "削除しました。")
        return super().form_valid(form)


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
class ScheduleList(generic.ListView):
    template_name = "schedules/index.html"
    queryset = models.WeeklyScheduleModel.get_all()


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
class ScheduleCreate(generic.CreateView):
    template_name = "schedules/create.html"
    model = models.WeeklyScheduleModel
    form_class = forms.WeeklyScheduleModelForm
    success_url = reverse_lazy('schedules_list')

    def form_valid(self, form):
        messages.success(self.request, "作成に成功しました。")
        return super().form_valid(form)


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
class ScheduleUpdate(generic.UpdateView):
    template_name = "schedules/update.html"
    model = models.WeeklyScheduleModel
    form_class = forms.WeeklyScheduleModelForm
    success_url = reverse_lazy('schedules_list')

    def form_valid(self, form):
        messages.success(self.request, "更新に成功しました。")
        return super().form_valid(form)


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
class ScheduleDelete(generic.DeleteView):
    template_name = "schedules/delete.html"
    model = models.WeeklyScheduleModel
    success_url = reverse_lazy('schedules_list')


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
class AdminReserveList(generic.ListView):
    template_name = "useradmin/reserve_list.html"
    paginate_by = 10
    model = models.ReserveModel

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        mode = self.kwargs.get('mode', 'date')
        title = ""
        if mode == ('date'):
            title = '日付順'
        elif mode == ('created'):
            title = '申し込み順'
        elif mode == ('user'):
            user_id = self.kwargs.get('param', '')
            title = 'ユーザー別:' + user_id
        elif mode == ('specify_date'):
            now = datetime.datetime.now().date()
            select_date = self.kwargs.get('param', now)
            select_date = self.__get_parse_select_date(select_date)
            title = '指定日付:' + select_date.strftime('%Y/%m/%d')

        ctx['title'] = title
        return ctx

    def get_queryset(self):
        mode = self.kwargs.get('mode', 'date')
        result = None
        if mode == ('date'):
            result = models.ReserveModel.get_all_by_date()
        elif mode == ('created'):
            result = models.ReserveModel.get_all_by_created()
        elif mode == ('user'):
            user_id = self.kwargs.get('param', '')
            result = models.ReserveModel.get_user_all_reserve(user_id)
        elif mode == ('specify_date'):
            now = datetime.datetime.now().date()
            select_date = self.kwargs.get('param', now)
            select_date = self.__get_parse_select_date(select_date)
            result = models.ReserveModel.get_by_date(select_date)
        return result

    def __get_parse_select_date(self, select_date):
        try:
            return util.DateUtil.parse(select_date)
        except Exception:
            return datetime.datetime.now().date()


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
class AdminReserveCalendar(generic.TemplateView):
    template_name = "useradmin/reserve_calendar.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        select_date = self.kwargs.get('select_date')
        select_date = util.DateUtil.get_date(select_date, 30, 0)
        ctx['select_date'] = select_date
        
        logic = logics.ReserveCalendar(datetime.datetime.now().date())
        ctx['holidays'] = json.dumps(logic.get_holidays())
        ctx['disabled_day_of_weeks'] = json.dumps(logic.get_disabled_day_of_weeks())
        ctx['start_and_end_dates'] = json.dumps(logic.get_start_and_end_dates())
        ctx['reserves_by_date'] = json.dumps(logic.get_reserves_by_date(), cls=encode.ModelEncoder)
        ctx['reserves_date_list'] = json.dumps(logic.get_reserves_date_list())

        return ctx


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
class AdminReserveCancel(generic.View):
    template_name = "useradmin/reserve_cancel.html"
    model = models.ReserveModel
    form_class = forms.ReserveConfirmForm

    def get(self, request, *args, **kwargs):
        reserve_pk = self.kwargs.get('reserve_pk', '')
        backurl = request.GET.get('backurl', '/user_admin/')
        form = self.form_class()
        form.load_for_cancl_admin(reserve_pk)

        return render(request, self.template_name, {'form': form, 'reserve_pk': reserve_pk, 'backurl': backurl})

    def post(self, request, *args, **kwargs):
        reserve_pk = self.kwargs.get('reserve_pk', '')
        form = self.form_class(request.POST)
        if form.is_valid():
            user_message = ""
            try:
                form.cancel_admin(reserve_pk)
                user_message = "キャンセル完了しました。"
            except Exception as e:
                user_message = e

            redirect_url = reverse_lazy('user_admin')
            parameters = urlencode({'user_message': user_message})
            url = f'{redirect_url}?{parameters}'
            return redirect(url)

        return render(request, self.template_name, {'form': form, 'reserve_pk': reserve_pk})


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
class SeatList(generic.ListView):
    template_name = "seats/index.html"
    paginate_by = 10
    model = models.SeatModel
    queryset = models.SeatModel.get_all()


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
class SeatUpdate(generic.UpdateView):
    template_name = "seats/update.html"
    model = models.SeatModel
    form_class = forms.SeatModelForm
    success_url = reverse_lazy('seats_list')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        only_displays = ['count', 'capacity', 'minnum', 'max_count_of_one_reserve']
        ctx['only_displays'] = only_displays
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "更新に成功しました。")
        return super().form_valid(form)


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
class AdminUserList(generic.ListView):
    template_name = "useradmin/user_list.html"
    model = models.CustomUser
    queryset = models.CustomUser.get_no_admin_users()


@login_required
def my_page(request):
    user_message = request.GET.get('user_message')
    reserves = None
    try:
        reserves = models.ReserveModel.get_user_current_reserve(request.user.id)
    except Exception:
        reserves = None
        print("no reserve!!!!")

    return render(request, 'user/index.html', {'user_message': user_message, 'reserves': reserves})


@method_decorator(login_required(), name="dispatch")
class MyReserveList(generic.ListView):
    template_name = "user/reserve_history.html"
    paginate_by = 10
    model = models.ReserveModel

    def get_queryset(self):
        reserves = None
        try:
            reserves = models.ReserveModel.get_user_all_reserve(self.request.user.id)
        except Exception:
            reserves = None

        return reserves


@login_required
def reserve_new(request, select_date=None, number=None):
    # check reserve of existe
    check = logics.ReserveDuplicateCheck(request.user)
    if not check.is_availalble_reserve():
        user_message = "既に予約が存在します。予約は同時に1件のみ可能です。"
        redirect_url = reverse_lazy('my_page')
        parameters = urlencode({'user_message': user_message})
        url = f'{redirect_url}?{parameters}'
        return redirect(url)

    # confirm screen
    errors = None
    if request.method == "POST":
        form = forms.ReserveConfirmForm(request.POST)
        # form = forms.ReserveForm(request.POST)
        # print(form)
        if form.is_valid():
            replace_dict = {"selected_seat": form.get_selected_seat_display()}
            return render(request, 'reserves/confirm.html', {'form': form, 'replace_dict': replace_dict})
        else:
            print(form.errors)
            errors = form.errors

    number = util.NumberUtil.getNumber(number, const.DEFAULT_RESERVE_NUMBER_OF_CUSTOMER, const.MAX_RESERVE_NUMBER_OF_CUSTOMER, 1)
    logic = ReserveCalcLogic(select_date, number, const.OFFSET_DAYS_OF_RESERVE, const.DURATION_MINUTES_OF_RESERVE)
    logic.calc_select_dates()
    logic.calc_reserve_time_list()
    logic.calc_seat_remain()

    # now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    form = forms.ReserveForm()
    if errors:
        form._errors = errors

    form.init_field(number, logic.get_select_date(), logic.get_select_dates_choices(), logic.get_reserve_time_list_choices(), logic.get_all_seats_for_choice())
    form.load_userinfo(request.user.pk)
    # calc remain serat number
    seat_json = json.dumps(logic.get_all_seat_states())
    seat_info_json = json.dumps(logic.get_all_seats_info())

    return render(request, 'reserves/create.html', {'form': form, 'seat_json': seat_json, 'seat_info_json': seat_info_json})


@login_required
def create_new(request):
    if request.method == "POST":
        form = forms.ReserveConfirmForm(request.POST)
        if form.is_valid():
            select_date = form.cleaned_data['start_date']
            number = form.cleaned_data['number']
            start_time = form.cleaned_data['selected_time']
            # check available to reserve again
            with transaction.atomic():
                logic = ReserveCalcLogic(select_date, number, const.OFFSET_DAYS_OF_RESERVE, const.DURATION_MINUTES_OF_RESERVE)
                logic.calc_select_dates()
                logic.calc_reserve_time_list()
                logic.calc_seat_remain()
                if logic.check_availalbe_reserve(start_time):
                    user_message = "予約が完了しました。"
                    try:
                        form.save(request.user)
                    except exceptions.ReserveCanNotSaveError as e:
                        user_message = e

                    redirect_url = reverse_lazy('my_page')
                    parameters = urlencode({'user_message': user_message})
                    url = f'{redirect_url}?{parameters}'
                    return redirect(url)
                else:
                    raise forms.ValidationError("操作中に予約が一杯となりました。お手数ですが、再度予約をお願いします。")
        else:
            print(form.errors)

    redirect_url = reverse_lazy('reserve')
    return redirect(url)


@login_required
def reserve_cancel(request, reserve_pk=None):
    if reserve_pk is None:
        return redirect(reverse_lazy('my_page'))

    if request.method == "GET":
        try:
            form = forms.ReserveConfirmForm()
            form.load_for_cancel(request.user, reserve_pk)
        except Exception:
            user_message = "想定外のエラーが発生しました。"
            redirect_url = reverse_lazy('my_page')
            parameters = urlencode({'user_message': user_message})
            url = f'{redirect_url}?{parameters}'
            return redirect(url)
    elif request.method == "POST":
        form = forms.ReserveConfirmForm(request.POST)
        if form.is_valid():
            user_message = ""
            try:
                form.cancel(request.user, reserve_pk)
                user_message = "キャンセル完了しました。"
            except Exception as e:
                user_message = e

            redirect_url = reverse_lazy('my_page')
            parameters = urlencode({'user_message': user_message})
            url = f'{redirect_url}?{parameters}'
            return redirect(url)

    return render(request, 'reserves/cancel.html', {'form': form, 'reserve_pk': reserve_pk})


class ReserveCalcLogic:
    def __init__(self, select_date, reserve_number, max_days, duration_minutes):
        self.__reserve_number = reserve_number
        self.__max_days = max_days
        self.__duration_minutes = duration_minutes
        # if seelct_date is none set tomorrow and then it is checked by calc_select_dates methods
        self.__select_date = util.DateUtil.get_date(select_date, self.__max_days, const.OFFSET_DAYS_START_RESERVE)

    def calc_select_dates(self):
        """
        set availalbe dates of reserve
        """
        select_dates = []
        # get reservable all days from current date + offset (day) (not using selected_date)
        base_date = datetime.datetime.now().date() + datetime.timedelta(days=const.OFFSET_DAYS_START_RESERVE)
        all_days = util.DateUtil.get_ranges(base_date, self.__max_days)
        # filter actual days by available schedules
        all_days = models.WeeklyScheduleModel.get_filtered_date_by_availalble_dayofweeks(all_days)
        # filter special holiday
        all_days = models.SpecialHolydayModel.get_filtered_day(all_days)
        for dt in all_days:
            select_dates.append(dt)

        self.__select_dates = select_dates
        # select_date is setted without selectable at init, so if it is not match list, select again
        if (self.__select_date not in self.__select_dates) and (len(self.__select_dates) > 0):
            self.__select_date = self.__select_dates[0]

    def get_select_date(self):
        return self.__select_date

    def get_select_dates_choices(self):
        # locale.setlocale(locale.LC_ALL, '')
        locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
        choices = []
        for dt in self.__select_dates:
            frm = dt.strftime('%Y/%m/%d (%A)')
            choices.append((dt, frm))
        return choices

    def calc_reserve_time_list(self):
        """
        set availalble times of resereve from store's schedule
        """
        # week_of_day = 1
        week_of_day = self.__select_date.weekday()
        self.__reserve_time_list = []
        # get available time schedules by selected date' dayofweek
        schedules = models.WeeklyScheduleModel.get_by_dayofweek(week_of_day)
        # divide the schedule by segument of time
        for schedule in schedules:
            # actual end_time is needed to concern offsets
            end_time = util.TimeUtil.add_minutes(schedule.end_time, -const.RESERVE_MINUTES_OFFSET)
            time_results = util.TimeUtil.get_ranges(schedule.start_time, end_time, self.__duration_minutes)
            for time_result in time_results:
                self.__reserve_time_list.append(time_result)
                # self.__reserve_time_list.append((time_result, time_result.strftime('%H:%M')))

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

    def calc_seat_remain(self):
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
