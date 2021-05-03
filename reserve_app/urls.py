from django.urls import path, register_converter
from . import views
from django.utils.timezone import datetime


class DateConverter:
    regex = '[0-9]{4}-[0-9]{2}-[0-9]{2}'

    def to_python(self, value):
        return datetime.strptime(value, "%Y-%m-%d")

    def to_url(self, value):
        return value.strftime("%Y-%m-%d")


register_converter(DateConverter, 'date')

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('contact', views.Contact.as_view(), name='contact'),
    path('user_admin/', views.UserAdminIndex.as_view(), name='user_admin'),
    path('user_admin/debug', views.UserAdminDebug.as_view(), name='user_admin_debug'),
    path('user_admin/debug/<str:mode>', views.UserAdminDebug.as_view(), name='user_admin_debug'),
    path('holidays/', views.SepecialHolidayList.as_view(), name='holidays_list'),
    path('holidays/create', views.SepecialHolidayCreate.as_view(), name='holidays_create'),
    path('holidays/update/<int:pk>', views.SepecialHolidayUpdate.as_view(), name='holidays_update'),
    path('holidays/delete/<int:pk>', views.SepecialHolidayDelete.as_view(), name='holidays_delete'),
    path('schedules/', views.ScheduleList.as_view(), name='schedules_list'),
    path('schedules/create', views.ScheduleCreate.as_view(), name='schedules_create'),
    path('schedules/update/<int:pk>', views.ScheduleUpdate.as_view(), name='schedules_update'),
    path('schedules/delete/<int:pk>', views.ScheduleDelete.as_view(), name='schedules_delete'),
    path('seats/', views.SeatList.as_view(), name='seats_list'),
    path('seats/update/<int:pk>', views.SeatUpdate.as_view(), name='seats_update'),
    path('reserve/', views.reserve_new, name='reserve'),
    path('reserve/<date:select_date>', views.reserve_new, name='reserve'),
    path('reserve/<date:select_date>/<int:number>', views.reserve_new, name='reserve'),
    path('reserve/create/', views.create_new, name='reserve_create'),
    path('reserve/cancel/<int:reserve_pk>', views.reserve_cancel, name='reserve_cancel'),
    path('admin/reserve_calendar/', views.AdminReserveCalendar.as_view(), name='admin_reserve_calendar'),
    path('admin/reserve_calendar/<date:select_date>', views.AdminReserveCalendar.as_view(), name='admin_reserve_calendar'),
    path('my_page/', views.my_page, name='my_page'),
    path('my_page/history', views.MyReserveList.as_view(), name='my_page_history'),
    path('admin/reserves_list/', views.AdminReserveList.as_view(), name='admin_reserves_list'),
    path('admin/reserves_list/<str:mode>', views.AdminReserveList.as_view(), name='admin_reserves_list'),
    path('admin/reserves_list/<str:mode>/<str:param>', views.AdminReserveList.as_view(), name='admin_reserves_list'),
    path('admin/reserves_cancel/<int:reserve_pk>', views.AdminReserveCancel.as_view(), name='admin_reserves_cancel'),
    path('admin/reserves_user_sum_list/', views.AdminReserveUserSumList.as_view(), name='admin_reserves_user_sum_list'),
    path('admin/banned_user_list/', views.AdminBannedUser.as_view(), name='admin_banned_user_list'),
    path('admin/user_list/', views.AdminUserList.as_view(), name='admin_user_list'),
    path('admin/common_settings/', views.AdminCommonSettings.as_view(), name='admin_common_settings'),
]
