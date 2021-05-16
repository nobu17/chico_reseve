# from django.shortcuts import render
from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
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
from django.http import HttpResponseRedirect
# import pytz
# Create your views here.


class IndexView(generic.TemplateView):
    template_name = "index.html"


class Contact(generic.TemplateView):
    template_name = "contact/index.html"


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
@method_decorator(staff_member_required(login_url="/"), name="dispatch")
class UserAdminIndex(generic.TemplateView):
    template_name = "useradmin/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        user_message = self.request.GET.get('user_message')

        today_date = util.DateUtil.get_date_from_now(0)
        tomorrow_date = util.DateUtil.get_date_from_now(1)

        today_reserve_count = models.ReserveModel.get_reserve_count_by_date(today_date)
        tomorrow_reserve_count = models.ReserveModel.get_reserve_count_by_date(tomorrow_date)

        ctx['user_message'] = user_message
        ctx['today_reserve_count'] = today_reserve_count
        ctx['tomorrow_reserve_count'] = tomorrow_reserve_count
        ctx['tomorrow_date'] = tomorrow_date.strftime('%Y-%m-%d')
        return ctx


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
@method_decorator(staff_member_required(login_url="/"), name="dispatch")
class UserAdminDebug(generic.TemplateView):
    template_name = "useradmin/debug.html"

    def get(self, request, **kwargs):
        mode = self.kwargs.get('mode', '')
        debug = logics.DebugData(mode)
        if debug.do_task():
            messages.success(self.request, "削除に成功しました。")
        context = {}
        return self.render_to_response(context)


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
@method_decorator(staff_member_required(login_url="/"), name="dispatch")
class AdminCommonSettings(generic.View):
    template_name = "useradmin/common_settings.html"
    model = models.CommonSettingModel
    form_class = forms.CommonSettingsModelForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        form.load()

        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user_message = ""
            try:
                form.save()
                user_message = "データの更新が完了しました。"
            except Exception as e:
                user_message = e

            redirect_url = reverse_lazy('user_admin')
            parameters = urlencode({'user_message': user_message})
            url = f'{redirect_url}?{parameters}'
            return redirect(url)

        return render(request, self.template_name, {'form': form})

    def form_invalid(self, form):
        messages.error(self.request, "データの更新に失敗しました。", extra_tags='danger')
        return super().form_invalid(form)


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
@method_decorator(staff_member_required(login_url="/"), name="dispatch")
class AdminBannedUser(generic.View):
    template_name = "useradmin/banned_user_list.html"
    model = models.CustomUser

    def get(self, request, *args, **kwargs):
        check = logics.UserBanCheck(request.user)
        banned_users = check.get_banned_users()
        return render(request, self.template_name, {'banned_users': banned_users})

    def post(self, request, *args, **kwargs):
        user_pk = request.POST.get("user", None)
        if user_pk:
            try:
                user = models.CustomUser.get(user_pk)
                check = logics.UserBanCheck(user)
                check.delete_banned_data()
                user_message = "データの更新が完了しました。"
            except Exception as e:
                user_message = e
        else:
            user_message = "ユーザが見つかりませんでした。"

        redirect_url = reverse_lazy('user_admin')
        parameters = urlencode({'user_message': user_message})
        url = f'{redirect_url}?{parameters}'
        return redirect(url)


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
@method_decorator(staff_member_required(login_url="/"), name="dispatch")
class SepecialHolidayList(generic.ListView):
    template_name = "holidays/index.html"
    queryset = models.SpecialHolydayModel.get_all()


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
@method_decorator(staff_member_required(login_url="/"), name="dispatch")
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
@method_decorator(staff_member_required(login_url="/"), name="dispatch")
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
@method_decorator(staff_member_required(login_url="/"), name="dispatch")
class SepecialHolidayDelete(generic.DeleteView):
    template_name = "holidays/delete.html"
    model = models.SpecialHolydayModel
    success_url = reverse_lazy('holidays_list')

    def form_valid(self, form):
        messages.success(self.request, "削除しました。")
        return super().form_valid(form)


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
@method_decorator(staff_member_required(login_url="/"), name="dispatch")
class ScheduleList(generic.ListView):
    template_name = "schedules/index.html"
    queryset = models.WeeklyScheduleModel.get_all()


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
@method_decorator(staff_member_required(login_url="/"), name="dispatch")
class ScheduleCreate(generic.CreateView):
    template_name = "schedules/create.html"
    model = models.WeeklyScheduleModel
    form_class = forms.WeeklyScheduleModelForm
    success_url = reverse_lazy('schedules_list')

    def form_valid(self, form):
        messages.success(self.request, "作成に成功しました。")
        return super().form_valid(form)


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
@method_decorator(staff_member_required(login_url="/"), name="dispatch")
class ScheduleUpdate(generic.UpdateView):
    template_name = "schedules/update.html"
    model = models.WeeklyScheduleModel
    form_class = forms.WeeklyScheduleModelForm
    success_url = reverse_lazy('schedules_list')

    def form_valid(self, form):
        messages.success(self.request, "更新に成功しました。")
        return super().form_valid(form)


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
@method_decorator(staff_member_required(login_url="/"), name="dispatch")
class ScheduleDelete(generic.DeleteView):
    template_name = "schedules/delete.html"
    model = models.WeeklyScheduleModel
    success_url = reverse_lazy('schedules_list')

    def delete(self, request, *args, **kwargs):
        target = self.get_object()
        check = logics.WeeklyScheduleCheck()
        if check.is_reservation_exists(target.pk):
            messages.error(self.request, "指定時間に予約が存在するので削除できません。", extra_tags='danger')
            return HttpResponseRedirect(self.success_url)

        return(super().delete(request, *args, **kwargs))


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
@method_decorator(staff_member_required(login_url="/"), name="dispatch")
class AdminReserveUserSumList(generic.ListView):
    template_name = "useradmin/reserve_user_sum_list.html"
    paginate_by = 100
    model = models.ReserveModel

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = "ユーザー別集計"
        return ctx

    def get_queryset(self):
        result = models.ReserveModel.get_reserve_sum_by_user()
        return result


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
@method_decorator(staff_member_required(login_url="/"), name="dispatch")
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
@method_decorator(staff_member_required(login_url="/"), name="dispatch")
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
@method_decorator(staff_member_required(login_url="/"), name="dispatch")
class AdminReserveCancel(generic.View):
    template_name = "useradmin/reserve_cancel.html"
    model = models.ReserveModel
    form_class = forms.ReserveConfirmForm

    def get(self, request, *args, **kwargs):
        reserve_pk = self.kwargs.get('reserve_pk', '')
        backurl = request.GET.get('backurl', '/user_admin/')
        form = self.form_class()
        form.load_for_cancl_admin(reserve_pk)
        replace_dict = {"selected_seat": form.selected_seat_name}

        return render(request, self.template_name, {'form': form, 'replace_dict': replace_dict, 'reserve_pk': reserve_pk, 'backurl': backurl})

    def post(self, request, *args, **kwargs):
        reserve_pk = self.kwargs.get('reserve_pk', '')
        form = self.form_class(request.POST)
        if form.is_valid():
            user_message = ""
            try:
                reserve = form.cancel_admin(reserve_pk)
                send_mail = logics.SendEmail()
                send_mail.send_cancel_completed(reserve)
                user_message = "キャンセル完了しました。"
            except Exception as e:
                user_message = e

            redirect_url = reverse_lazy('user_admin')
            parameters = urlencode({'user_message': user_message})
            url = f'{redirect_url}?{parameters}'
            return redirect(url)

        return render(request, self.template_name, {'form': form, 'reserve_pk': reserve_pk})


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
@method_decorator(staff_member_required(login_url="/"), name="dispatch")
class SeatList(generic.ListView):
    template_name = "seats/index.html"
    paginate_by = 10
    model = models.SeatModel
    queryset = models.SeatModel.get_all()


@method_decorator(login_required(login_url="/accounts/admin_login/"), name="dispatch")
@method_decorator(staff_member_required(login_url="/"), name="dispatch")
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
@method_decorator(staff_member_required(login_url="/"), name="dispatch")
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
    # check reserve of exists and ban
    check = logics.ReserveDuplicateCheck(request.user)
    if not check.is_availalble_reserve():
        user_message = check.get_duplicated_error_message()
        redirect_url = reverse_lazy('my_page')
        parameters = urlencode({'user_message': user_message})
        url = f'{redirect_url}?{parameters}'
        return redirect(url)

    # check user is banned
    ban_check = logics.UserBanCheck(request.user)
    if ban_check.is_banned():
        user_message = ban_check.get_user_banned_message()
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
    logic = logics.ReserveCalcLogic(select_date, number, const.OFFSET_DAYS_OF_RESERVE, const.DURATION_MINUTES_OF_RESERVE, request.user.is_superuser)
    logic.calc_info()

    # now = datetime.datetime.now(pytz.timezone('Asia/Tokyo'))
    form = forms.ReserveForm()
    if errors:
        form._errors = errors

    form.init_field(number, logic.get_select_date(), logic.get_reserve_time_list_choices(), logic.get_all_seats_for_choice())
    form.load_userinfo(request.user.pk)
    # calc remain serat number
    seat_json = json.dumps(logic.get_all_seat_states())
    seat_info_json = json.dumps(logic.get_all_seats_info())
    # disabled_dates_json = json.dumps(logic.get_disabled_select_date(), cls=encode.ModelEncoder)
    # selectable_dates = logic.get_select_dates()
    selectable_dates_json = json.dumps(logic.get_select_dates(), cls=encode.ModelEncoder)

    return render(request, 'reserves/create.html', {'form': form, 'seat_json': seat_json, 'seat_info_json': seat_info_json, 'selectable_dates_json': selectable_dates_json})


@ login_required
def create_new(request):
    if request.method == "POST":
        form = forms.ReserveConfirmForm(request.POST)
        if form.is_valid():
            select_date = form.cleaned_data['start_date']
            number = form.cleaned_data['number']
            start_time = form.cleaned_data['selected_time']
            # check available to reserve again
            with transaction.atomic():
                logic = logics.ReserveCalcLogic(select_date, number, const.OFFSET_DAYS_OF_RESERVE, const.DURATION_MINUTES_OF_RESERVE, request.user.is_superuser)
                logic.calc_info()
                if logic.check_availalbe_reserve(start_time):
                    user_message = "予約が完了しました。"
                    try:
                        reserve = form.save(request.user)
                        send_email = logics.SendEmail()
                        send_email.send_reserve_complete(reserve)
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


@ login_required
def reserve_cancel(request, reserve_pk=None):
    if reserve_pk is None:
        return redirect(reverse_lazy('my_page'))

    if request.method == "GET":
        try:
            form = forms.ReserveConfirmForm()
            form.load_for_user(request.user, reserve_pk)
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
                reserve = form.cancel(request.user, reserve_pk)
                send_mail = logics.SendEmail()
                send_mail.send_cancel_completed(reserve)
                user_message = "キャンセル完了しました。"
            except Exception as e:
                user_message = e

            redirect_url = reverse_lazy('my_page')
            parameters = urlencode({'user_message': user_message})
            url = f'{redirect_url}?{parameters}'
            return redirect(url)

    replace_dict = {"selected_seat": form.selected_seat_name}
    return render(request, 'reserves/cancel.html', {'form': form, 'replace_dict': replace_dict, 'reserve_pk': reserve_pk})


@ login_required
def reserve_edit(request, reserve_pk=None):
    if reserve_pk is None:
        return redirect(reverse_lazy('my_page'))
    if request.method == "GET":
        try:
            form = forms.ReserveConfirmForm()
            form.load_for_user(request.user, reserve_pk)
            print("form is loaded!!!!")
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
                reserve = form.update(request.user, reserve_pk)
                send_mail = logics.SendEmail()
                send_mail.send_update_completed(reserve)
                user_message = "変更が完了しました。"
            except Exception as e:
                user_message = e

            redirect_url = reverse_lazy('my_page')
            parameters = urlencode({'user_message': user_message})
            url = f'{redirect_url}?{parameters}'
            return redirect(url)

    return render(request, 'reserves/edit.html', {'form': form, 'reserve_pk': reserve_pk})
