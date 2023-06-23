from django.urls import path
from management import views

urlpatterns = [

# boss가 보는 employee list
    path('employee_list/', views.employee_list, name='list_employees'),
    # boss / employee 관련
    path('empupdate/<int:emp_id>/', views.employee_update, name='update_employee'),
    path('empdelete/<int:emp_id>/', views.employee_delete, name='delete_employee'),
    path('empcreate/', views.employee_create, name='create_employee'),
    # 추가 !!/ employee가 보는 개인정보관련
    path('profile/', views.profile_view, name='profile'),
    path('profile_update/<int:emp_id>', views.profile_update, name='profile_update'),
    # 명세서
    path('statement_list/', views.statement_list, name="list_statement"),
    path('statement_chart/', views.statement_chart, name='chart_view'),
    #schedule 관련
    path('schedule_list/', views.schedule_list, name='schedule_list'),
    path('schedulefix_create/', views.schedulefix_create, name='create_schedulefix'),
    path('schedulefix_update/', views.schedulefix_update, name='update_schedulefix'),
    path('schedulefix_delete/', views.schedulefix_delete, name='delete_schedulefix'),
    # 대타 & 교대
    path('schedule_exchange/', views.exchange_list, name='schedule_exchange_list'),
    path('approve-exchange/<int:exchange_id>/', views.exchange_approve, name='approve-exchange'),
    path('reject-exchange/<int:exchange_id>/', views.exchange_reject, name='reject-exchange'),
    # url 주소 변경 / boss뿐만 아니라 employee도 포함
    path('schedule_exchange_confirm', views.schedule_exchange_confirm, name='schedule_exchange_boss'),
    path('schedule_exchange_form/', views.exchange_create, name='schedule_exchange_form'),
    # 추가 / 대타관련 url
    path('schedule_substitution/', views.substitution_create, name='schedule_substitution'),
    # 게시판 관련
    path('', views.NoticeListView.as_view(), name='notice_list'),
    path('notice_detail/<int:pk>/', views.notice_detail, name='notice_detail'),
    path('notice_write/', views.notice_write, name='notice_write'),
    path('notice_update/<int:pk>/', views.notice_edit, name='notice_edit'),
    path('notice_delete/<int:pk>/', views.notice_delete, name='notice_delete'),


    # path('list_employees/', views.list_employees, name='list_employees'),
    # # path('login/', views.login, name='login'),
    # path('empupdate/<int:emp_id>/', views.update_employee, name='update_employee'),
    # path('empdelete/<int:emp_id>/', views.delete_employee, name='delete_employee'),
    # path('empcreate/', views.create_employee, name='create_employee'),
    # path('sta/', views.list_statement, name="list_statement"),
    # path('schedule/', views.schedule_list, name='schedule_list'),
    # path('create_schedulefix/', views.create_schedulefix, name='create_schedulefix'),
    # path('update_schedulefix/', views.update_schedulefix, name='update_schedulefix'),
    # path('delete_schedulefix/', views.delete_schedulefix, name='delete_schedulefix'),
    # path('schedule_exchange/', views.exchange_list, name='schedule_exchange_list'),
    # path('approve-exchange/<int:exchange_id>/', views.approve_exchange, name='approve-exchange'),
    # path('reject-exchange/<int:exchange_id>/', views.reject_exchange, name='reject-exchange'),
    # path('confirm_boss_exchange/', views.schedule_exchange_confirm, name='confirm_boss_exchange'),
    # path('exchange_form/', views.create_exchange, name='schedule_exchange_form'),
    # path('', views.NoticeListView.as_view(), name='notice_list'),
    # path('notice_detail/<int:pk>/', views.notice_detail_view, name='notice_detail'),
    # path('notice_write/', views.notice_write_view, name='notice_write'),
    # path('notice_update/<int:pk>/', views.notice_edit_view, name='notice_edit'),
    # path('notice_delete/<int:pk>/', views.notice_delete_view, name='notice_delete'),
    # # path('schedule_exchange_confirm/', views.schedule_exchange_confirm, name='schedule_exchange_confirm'),

]
