from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from management.models import Wage_hourly, Employee, Notice, Absenteeism, Schedule_exchange,Schedulefix
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.utils import timezone
from pytz import timezone as tz
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
import datetime
import pytz
from django.http import JsonResponse
from django.views.generic import ListView
from django.db.models import Q
from datetime import datetime, time
from .forms import NoticeWriteForm, ExchangeForm, CustomCsUserChangeForm, EmployeeForm
from collections import defaultdict

# ------------------------------------------------------------------
# ---------------------------- Login ----------------------------
# ------------------------------------------------------------------
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('notice_list')  # 로그인 성공 시 notice_list
        else:
            # 인증 실패 처리
            return render(request, 'management/login.html')
    return render(request, 'management/login.html')

# logout using self-defined function
def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/')

# ------------------------------------------------------------------
# ---------------------------- Employee ----------------------------
# ------------------------------------------------------------------
@login_required
def employee_list(request):
    user = request.user
    if user.username == 'boss':
        employees = Employee.objects.all()
        return render(request, 'employee/employee_list.html', {'employees': employees})
    else:
        email = user.email
        employees = Employee.objects.filter(emp_email=email)
        return render(request, 'employee/profile.html', {'employees': employees})

def employee_create(request):
    form = EmployeeForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect('list_employees')

    return render(request, 'employee/employee_form.html', {'form': form})

@login_required
def employee_update(request, emp_id):
    employee = Employee.objects.get(emp_id=emp_id)
    form = EmployeeForm(request.POST or None, instance=employee)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('list_employees')

    return render(request, 'employee/employee_form.html', {'emp': employee, 'form': form})

@login_required
def employee_delete(request, emp_id):
    if request.method == 'POST' and 'confirm_delete' in request.POST:
        confirm_delete = request.POST['confirm_delete']
        if confirm_delete == 'true':
            employee = Employee.objects.get(emp_id=emp_id)
            employee.delete()
    return redirect('list_employees')

@login_required
def profile_view(request):
    user = request.user

    email = user.email
    employees = Employee.objects.filter(emp_email=email)

    return render(request, 'employee/profile.html', {'employees': employees})

@login_required
def profile_update(request, emp_id):
    employee = Employee.objects.get(emp_id=emp_id)
    emp_change_form = CustomCsUserChangeForm(request.POST or None, instance=employee)

    if request.method == 'POST':
        emp_change_form = CustomCsUserChangeForm(request.POST, instance=employee)
        if emp_change_form.is_valid():
            emp_change_form.save()
            return redirect('profile')

    return render(request, 'employee/profile_update.html', {'employee': employee, 'emp_change_form': emp_change_form})

# ------------------------------------------------------------------
# ---------------------------- Statement ----------------------------
# ------------------------------------------------------------------
def statement_list(request):
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')
    selected_employee_name = request.GET.get('employee')
    user = request.user

    if not selected_year:
        selected_year = datetime.now().year

    if selected_month and selected_year and selected_employee_name:
        selected_employee_id = Employee.objects.get(emp_name=selected_employee_name).emp_id
        message = f'{selected_year}년 {selected_month}월 {selected_employee_name}의 명세서'
        lists = Absenteeism.objects.filter(
            abs_start__year=selected_year,
            abs_start__month=selected_month,
            employee=selected_employee_id
        )
    elif selected_month and selected_year:
        message = f'{selected_year}년 {selected_month}월의 명세서'
        lists = Absenteeism.objects.filter(
            abs_start__year=selected_year,
            abs_start__month=selected_month
        )
    elif selected_year and selected_employee_name:
        selected_employee_id = Employee.objects.get(emp_name=selected_employee_name).emp_id
        message = f'{selected_year}년 {selected_employee_name}의 명세서'
        lists = Absenteeism.objects.filter(
            abs_start__year=selected_year,
            employee=selected_employee_id
        )
    elif selected_year:
        message = f'{selected_year}년의 명세서'
        lists = Absenteeism.objects.filter(
            abs_start__year=selected_year
        )
    else:
        message = '검색어를 입력하세요.'
        lists = Absenteeism.objects.order_by('employee')

    if user.username != 'boss':
        lists = lists.filter(employee__emp_email=user.email)

    total_sum = lists.aggregate(total_sum=Sum('abs_totalmin'))['total_sum'] or 0
    total_wage = lists.aggregate(total_wage=Sum('abs_totalwage'))['total_wage'] or 0

    return render(request, 'statement/statement_list.html', {
        'message': message,
        'lists': lists,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'selected_employee_name': selected_employee_name,
        'total_sum': total_sum,
        'total_wage': total_wage,
        'years': range(2022, datetime.now().year + 1),
        'months': [
            (1, '1월'), (2, '2월'), (3, '3월'), (4, '4월'), (5, '5월'), (6, '6월'),
            (7, '7월'), (8, '8월'), (9, '9월'), (10, '10월'), (11, '11월'), (12, '12월')
        ],
        'employees': Employee.objects.all()
    })

# ------------------------------------------------------------------
# ---------------------------- Schedule ----------------------------
# ------------------------------------------------------------------

def schedule_list(request):
    # Schedulefix 모델에서 데이터 가져오기
    employee_list = Employee.objects.all()  # 모든 직원 가져오기 추가된거
    schedulefix_list = Schedulefix.objects.all()

    # FullCalendar에 전달할 이벤트 리스트 생성
    events = []
    for schedulefix in schedulefix_list:
        event = {
            'id': schedulefix.sch_id,
            'title': schedulefix.employee.emp_name,
            'start': schedulefix.sch_start.strftime('%Y-%m-%d') + 'T' + schedulefix.sch_start.strftime('%H:%M:%S'),
            'end': schedulefix.sch_finish.strftime('%Y-%m-%d') + 'T' + schedulefix.sch_finish.strftime('%H:%M:%S')
        }
        events.append(event)

    context = {
        'events': events,
        'employees': employee_list,
        'username': request.user.username,
    }
    return render(request, 'management/schedule_list.html', context)

@csrf_exempt
def schedulefix_create(request):
    if request.method == 'POST':
        employee_name = request.POST['employee']
        start_date = request.POST['start']
        end_date = request.POST['end']
        timezone_offset = int(request.POST['timezoneOffset'])

        try:
            employee = Employee.objects.get(emp_name=employee_name)

            if start_date:
                start_date = start_date[:-5]  # 밀리초 부분 제거
                start_date = start_date.split('+', 1)[0]
                start_date = datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
                start_date = start_date.replace(tzinfo=pytz.UTC)  # 시간을 UTC로 설정
                # start_date -= timedelta(minutes=timezone_offset)  # 로컬 시간대 오프셋 적용

            if end_date:
                end_date = end_date[:-5]  # 밀리초 부분 제거
                end_date = end_date.split('+', 1)[0]
                end_date = datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
                end_date = end_date.replace(tzinfo=pytz.UTC)  # 시간을 UTC로 설정
                # end_date -= timedelta(minutes=timezone_offset)  # 로컬 시간대 오프셋 적용

            Schedulefix.objects.create(
                sch_start=start_date,
                sch_finish=end_date,
                employee=employee
            )
            return JsonResponse({'status': 'success'})
        except ObjectDoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Employee not found'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@csrf_exempt
def schedulefix_update(request):
    if request.method == 'POST':
        schedulefix_id = request.POST.get('id')
        new_start_date = request.POST.get('start')
        new_end_date = request.POST.get('end')
        timezone_offset = int(request.POST.get('timezoneOffset'))

        try:
            schedulefix = get_object_or_404(Schedulefix, pk=schedulefix_id)

            if new_start_date:
                new_start_date = new_start_date[:-5]  # 밀리초 부분 제거
                new_start_date = datetime.strptime(new_start_date, '%Y-%m-%dT%H:%M:%S')
                new_start_date = new_start_date.replace(tzinfo=pytz.UTC)  # 시간을 UTC로 설정
                new_start_date -= timedelta(minutes=timezone_offset)  # 로컬 시간대 오프셋 적용
                schedulefix.sch_start = new_start_date

            if new_end_date:
                new_end_date = new_end_date[:-5]  # 밀리초 부분 제거
                new_end_date = datetime.strptime(new_end_date, '%Y-%m-%dT%H:%M:%S')
                new_end_date = new_end_date.replace(tzinfo=pytz.UTC)  # 시간을 UTC로 설정
                new_end_date -= timedelta(minutes=timezone_offset)  # 로컬 시간대 오프셋 적용
                schedulefix.sch_finish = new_end_date

            schedulefix.save()
            return JsonResponse({'status': 'success'})
        except ObjectDoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Schedulefix not found'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@csrf_exempt
def schedulefix_delete(request):
    if request.method == 'POST':
        schedulefix_id = request.POST.get('id')

        try:
            schedulefix = Schedulefix.objects.get(sch_id=schedulefix_id)
            schedulefix.delete()
            return JsonResponse({'status': 'success'})
        except ObjectDoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Schedulefix not found'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

# ------------------------------------------------------------------
# ---------------------------- Absenteeism ----------------------------
# ------------------------------------------------------------------

def gowork(request):
    emp_id = request.GET.get('empId')
    emp_phone = request.GET.get('empPhone')

    try:
        employee = Employee.objects.get(emp_id=emp_id, emp_phone=emp_phone)

        if employee.absenteeism_set.filter(abs_finish__isnull=True).exists():
            # 이미 출근 기록이 있는 경우
            return JsonResponse({'success': False, 'message': '이미 출근 기록이 있습니다.'})

        # 출근 시간 설정
        tz_seoul = tz('Asia/Seoul')  # 'Asia/Seoul' 시간대 설정
        abs_start = timezone.now().astimezone(tz_seoul).replace(microsecond=0) + timedelta(
            hours=9)  # astimezone(tz_seoul)
        abs_finish = None
        # 출근 시간 저장
        absenteeism = Absenteeism(employee=employee, abs_start=abs_start, abs_finish=abs_finish)
        absenteeism.save()

        return JsonResponse({'success': True})
    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'message': '직원정보를 찾을 수 없습니다.'})


def gohome(request):
    emp_id = request.GET.get('empId')
    emp_phone = request.GET.get('empPhone')

    try:
        employee = Employee.objects.get(emp_id=emp_id, emp_phone=emp_phone)
        absenteeism = employee.absenteeism_set.filter(abs_start__isnull=False, abs_finish__isnull=True).order_by('-abs_start').first()

        if absenteeism is None:
            # 출근 기록이 없는 경우
            return JsonResponse({'success': False, 'message': '출근 기록이 없습니다.'})

        # 퇴근 시간 저장
        tz_seoul = tz('Asia/Seoul')  # 'Asia/Seoul' 시간대 설정
        abs_finish = timezone.now().astimezone(tz_seoul).replace(microsecond=0) + timedelta(hours=9)  # .
        absenteeism.abs_finish = abs_finish
        absenteeism.save()

        # 적절한 wageinfo 설정
        abs_start_time = absenteeism.abs_start.time()
        abs_finish_time = absenteeism.abs_finish.time()

        if ((abs_start_time >= time(22, 0)) or (abs_start_time < time(6, 0))) \
                and ((abs_finish_time > time(22, 0)) or (abs_finish_time <= time(6, 0))):
            wageinfo = Wage_hourly.objects.get(wag_info="nighttime")
        else:
            wageinfo = Wage_hourly.objects.get(wag_info="daytime")

        absenteeism.wageinfo = wageinfo
        absenteeism.save()

        return JsonResponse({'success': True})
    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'message': '직원정보를 찾을 수 없습니다.'})

# ------------------------------------------------------------------
# ---------------------------- substitution -------------------------
# ------------------------------------------------------------------

@login_required
def substitution_create(request):
    user = request.user
    email = user.email
    employee1 = Employee.objects.get(emp_email=email)

    if request.method == 'POST':
        form = ExchangeForm(employee1,request.POST)

        if form.is_valid():
            schedule_exchange = form.save(commit=False)
            schedule_exchange.employee1 = employee1
            schedule_exchange.save()
            return redirect('schedule_exchange_list')

    else:
        form = ExchangeForm(employee1)

    context = {
        'form': form,
    }
    return render(request, 'management/schedule_exchange_form.html', context)

@login_required
def exchange_create(request):
    user = request.user
    email = user.email
    try:
        employee1 = Employee.objects.get(emp_email=email)
    except Employee.DoesNotExist:
        employee1 = None

    if request.method == 'POST':
        form = ExchangeForm(employee1,request.POST)

        if form.is_valid():
            form.save()
            return redirect('schedule_exchange_list')

    else:
        form = ExchangeForm(employee1)

    context = {
        'form': form,
    }
    return render(request, 'management/schedule_exchange_form.html', context)


def schedule_exchange_confirm(request):
    exchanges = Schedule_exchange.objects.filter(approval=True)
    return render(request, 'management/schedule_exchange_boss.html', {'exchanges': exchanges})


def exchange_list(request):
    exchanges = Schedule_exchange.objects.all()
    return render(request, 'management/schedule_exchange_list.html', {'exchanges': exchanges})

def exchange_reject(request, exchange_id):
    exchange = get_object_or_404(Schedule_exchange, id=exchange_id)
    exchange.delete()
    # 승인 취소 후에 할 작업들을 추가할 수 있습니다.
    return redirect('schedule_exchange_list')  # 테이블 뷰로 리디렉션할 수 있도록 수정해야합니다.

def exchange_approve(request, exchange_id):
    exchange = get_object_or_404(Schedule_exchange, id=exchange_id)
    exchange.approval = True
    exchange.save()

    # 대타 요청
    if exchange.start1 is None and exchange.end1 is None:
        # 새로운 Schedulefix 객체 생성
        schedulefix1 = Schedulefix(employee=exchange.employee1, sch_start=exchange.start2, sch_finish=exchange.end2)
        schedulefix1.save()

        # 기존의 Schedulefix 객체 삭제
        q2 = Q(employee=exchange.employee2) & Q(sch_start=exchange.start2) & Q(sch_finish=exchange.end2)
        existing_schedule2 = Schedulefix.objects.filter(q2).exists()
        if existing_schedule2:

            schedulefix2 = Schedulefix.objects.get(employee=exchange.employee2, sch_start=exchange.start2,
                                                   sch_finish=exchange.end2)
            schedulefix2.delete()

        else:
            q1 = Q(employee=exchange.employee2, sch_start__gte=exchange.start2, sch_start__lt=exchange.end2) \
                 | Q(employee=exchange.employee2, sch_finish__gt=exchange.start2, sch_finish__lte=exchange.end2)

            if Schedulefix.objects.filter(q1).exists():

                # employee2의 스케줄 수정
                schedule1 = Schedulefix.objects.get(employee=exchange.employee2, sch_start__lte=exchange.start2,
                                                    sch_finish__gte=exchange.end2)
                if schedule1.sch_start == exchange.start2:
                    schedule1.sch_start = exchange.end2
                elif schedule1.sch_finish == exchange.end2:
                    schedule1.sch_finish = exchange.start2
                schedule1.save()

        exchange.save()

    elif exchange.start1 is not None and exchange.end1 is not None:

        # 새로운 Schedulefix 객체 생성
        schedulefix1 = Schedulefix(employee=exchange.employee2, sch_start=exchange.start1, sch_finish=exchange.end1)
        schedulefix2 = Schedulefix(employee=exchange.employee1, sch_start=exchange.start2, sch_finish=exchange.end2)
        schedulefix1.save()
        schedulefix2.save()

        # 기존의 Schedulefix 객체 삭제
        q3 = Q(employee=exchange.employee1) & Q(sch_start=exchange.start1) & Q(sch_finish=exchange.end1)
        q4 = Q(employee=exchange.employee2) & Q(sch_start=exchange.start2) & Q(sch_finish=exchange.end2)
        existing_schedule3 = Schedulefix.objects.filter(q3).exists()
        existing_schedule4 = Schedulefix.objects.filter(q4).exists()
        if existing_schedule3 and existing_schedule4:

            schedulefix3 = Schedulefix.objects.get(employee=exchange.employee1, sch_start=exchange.start1,
                                                   sch_finish=exchange.end1)
            schedulefix3.delete()

            schedulefix4 = Schedulefix.objects.get(employee=exchange.employee2, sch_start=exchange.start2,
                                                   sch_finish=exchange.end2)
            schedulefix4.delete()
        else:
            q1 = Q(employee=exchange.employee1, sch_start__gte=exchange.start1, sch_start__lt=exchange.end1) \
                 | Q(employee=exchange.employee1, sch_finish__gt=exchange.start1, sch_finish__lte=exchange.end1)

            q2 = Q(employee=exchange.employee2, sch_start__gte=exchange.start2, sch_start__lt=exchange.end2) \
                 | Q(employee=exchange.employee2, sch_finish__gt=exchange.start2, sch_finish__lte=exchange.end2)

            if Schedulefix.objects.filter(q1).exists():
                if Schedulefix.objects.filter(q2).exists():
                    # employee1의 스케줄 수정
                    schedule1 = Schedulefix.objects.get(employee=exchange.employee1, sch_start__lte=exchange.start1,
                                                        sch_finish__gte=exchange.end1)
                    if schedule1.sch_start == exchange.start1:
                        schedule1.sch_start = exchange.end1
                    elif schedule1.sch_finish == exchange.end1:
                        schedule1.sch_finish = exchange.start1
                    schedule1.save()

                    # employee2의 스케줄 수정
                    schedule2 = Schedulefix.objects.get(employee=exchange.employee2, sch_start__lte=exchange.start2,
                                                        sch_finish__gte=exchange.end2)
                    if schedule2.sch_start == exchange.start2:
                        schedule2.sch_start = exchange.end2
                    elif schedule2.sch_finish == exchange.end2:
                        schedule2.sch_finish = exchange.start2
                    schedule2.save()

        exchange.save()

    return redirect('schedule_exchange_list')

# ----------------------------------------------------------------
# ---------------------------- Notice ----------------------------
# ----------------------------------------------------------------

class NoticeListView(ListView):
    model = Notice
    paginate_by = 10
    template_name = 'notice/notice_list.html'
    context_object_name = 'notice_list'

    def get_queryset(self):
        search_keyword = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', '')
        notice_list = Notice.objects.order_by('-not_id')

        if search_keyword:
            if len(search_keyword) > 1:
                if search_type == 'all':
                    search_notice_list = notice_list.filter(
                        Q(not_title__icontains=search_keyword) | Q(not_content__icontains=search_keyword))
                elif search_type == 'title_content':
                    search_notice_list = notice_list.filter(
                        Q(not_title__icontains=search_keyword) | Q(not_content__icontains=search_keyword))
                elif search_type == 'title':
                    search_notice_list = notice_list.filter(not_title__icontains=search_keyword)
                elif search_type == 'content':
                    search_notice_list = notice_list.filter(not_content__icontains=search_keyword)


                return search_notice_list

        return notice_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = context['paginator']
        page_numbers_range = 5
        max_index = len(paginator.page_range)

        page = self.request.GET.get('page')
        current_page = int(page) if page else 1

        start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range
        end_index = start_index + page_numbers_range
        if end_index >= max_index:
            end_index = max_index

        page_range = paginator.page_range[start_index:end_index]
        context['page_range'] = page_range

        search_keyword = self.request.GET.get('q', '')
        search_type = self.request.GET.get('type', '')

        if len(search_keyword) > 1:
            context['q'] = search_keyword
        context['type'] = search_type

        return context


def notice_detail(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    user = request.user
    email = user.email

    try:
        writer = Employee.objects.get(emp_email=email)
        if user == writer or user.username == 'boss':
            notice_auth = True
        else:
            notice_auth = False
    except ObjectDoesNotExist:
        writer = None
        notice_auth = False
    try:
        employee = Employee.objects.get(emp_email=email)
    except Employee.DoesNotExist:
        employee = None

    context = {
        'notice': notice,
        'notice_auth': notice_auth,
        'writer': writer,
        'employee': employee,
    }
    return render(request, 'notice/notice_detail.html', context)


@login_required
def notice_write(request):
    if request.method == "POST":
        form = NoticeWriteForm(request.POST)
        user = request.user
        email = user.email

        if user.username == 'boss':
            if form.is_valid():
                notice = form.save(commit=False)
                notice.not_writer = user.username
                notice.save()
                return redirect('notice_list')
        elif email:
            writer = Employee.objects.get(emp_email=email)
            if form.is_valid():
                notice = form.save(commit=False)
                notice.not_writer = writer
                notice.save()
                return redirect('notice_list')
    else:
        form = NoticeWriteForm()

    return render(request, "notice/notice_write.html", {'form': form})

@login_required
def notice_edit(request, pk):
    notice = Notice.objects.get(not_id=pk)
    user = request.user
    email = user.email
    try:
        writer = Employee.objects.get(emp_email=email)
    except Employee.DoesNotExist:
        writer = None

    if request.method == "POST":
        if ( user.username == 'boss'):
            form = NoticeWriteForm(request.POST, instance=notice)
            if form.is_valid():
                notice = form.save(commit=False)
                notice.save()
                return redirect('/mgmt/notice_detail/' + str(pk))
        if ( writer.emp_email == user.email and writer.emp_name == notice.not_writer):
            form = NoticeWriteForm(request.POST, instance=notice)
            if form.is_valid():
                notice = form.save(commit=False)
                notice.save()
                return redirect('/mgmt/notice_detail/' + str(pk))
    else:
        notice = Notice.objects.get(not_id=pk)
        if (user.username == 'boss'):
            form = NoticeWriteForm(instance=notice)
            context = {
                'form': form,
                'edit': '수정하기',
            }
            return render(request, "notice/notice_write.html", context)
        if (writer.emp_email == user.email and writer.emp_name == notice.not_writer):
            form = NoticeWriteForm(instance=notice)
            context = {
                'form': form,
                'edit': '수정하기',
            }
            return render(request, "notice/notice_write.html", context)
        else:
            return redirect('/mgmt/notice_detail/' + str(pk))

@login_required
def notice_delete(request, pk):
    notice = Notice.objects.get(not_id=pk)
    user = request.user
    email = user.email
    try:
        writer = Employee.objects.get(emp_email=email)
    except Employee.DoesNotExist:
        writer = None

    if ( user.username == 'boss'):
        notice.delete()
        return redirect('/mgmt/')
    elif(writer.emp_email == user.email and writer.emp_name == notice.not_writer):
        notice.delete()
        return redirect('/mgmt/')
    else:
        return redirect('/mgmt/'+str(pk))

# ------------------------------------------------------------------
# ---------------------------- Chart ----------------------------
# ------------------------------------------------------------------

def statement_chart(request):
    abs_data = Absenteeism.objects.all()

    chartData1 = defaultdict(lambda: {"total_wage": 0, "total_hour": 0})

    for abs in abs_data:
        date = abs.abs_start.date().isoformat()
        chartData1[date]["total_wage"] += abs.abs_totalwage
        chartData1[date]["total_hour"] += abs.abs_totalmin

    chartData1 = [{"date": date, "total_wage": data["total_wage"], "total_hour": data["total_hour"]} for date, data in chartData1.items()]

    context = {
        'chartData1': chartData1,
    }

    return render(request, 'statement/statement_chart.html', context)

