from datetime import datetime, time, date, timedelta

from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncDate, TruncMonth, TruncYear, TruncDay
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import CarRecords, FountainRecords

from .models import (
    Worker, Attendance, Driver, FuelTransaction, Institution, CarRecords,
    Maintenance, Expenses, Expenses_type, Place_Expenses, Device,
    MainItem, SubItem, MaintenanceLocation,VehicleFuelRecord
)
from .forms import (
    AddWorkerForm, FuelTransactionForm, DriverForm, CarRecordsForm, InstitutionForm,
    MaintenanceForm, ExpensesFrom, Expenses_typeForm, place_ExpensesForm,
    MaintenanceLocationForm, MainItemForm, SubItemForm, DeviceForm, FountainRecordsForm,VehicleFuelRecordForm
)
from .decorators import manager_only, worker_only

# from reports.constant import *

arabic_days = {
    'Saturday': 'السبت',
    'Sunday': 'الأحد',
    'Monday': 'الاثنين',
    'Tuesday': 'الثلاثاء',
    'Wednesday': 'الأربعاء',
    'Thursday': 'الخميس',
    'Friday': 'الجمعة',
}

def custom_logout(request):
    logout(request)
    return redirect('login')

@login_required
def redirect_after_login(request):
    user = request.user
    if user.is_superuser or user.is_staff:
        return redirect('dashboard')
    else:
        return redirect('worker_dashboard')
from django.db.models import Sum
from datetime import datetime, time, timedelta
@login_required
@manager_only
def dashboard(request):
    total_car_count = CarRecords.objects.aggregate(Sum('car_count'))['car_count__sum'] or 0
    total_fountain_count=FountainRecords.objects.aggregate(Sum('car_count'))['car_count__sum'] or 0
    now = datetime.now()
    cutoff_time = time(22, 0)  # 10 مساءً
    today = date.today()
    # تحديد تاريخ التقرير بناءً على الوقت الحالي
    if now.time() >= cutoff_time:
        report_date = now.date()  # اليوم الحالي
    else:
        report_date = now.date() - timedelta(days=1)

    # فلترة السجلات حسب حقل التاريخ فقط
    total_car_count_today = CarRecords.objects.filter(date=report_date).aggregate(Sum('car_count'))[
                                'car_count__sum'] or 0
    total_fountain_today = FountainRecords.objects.filter(date=report_date).aggregate(Sum('car_count'))[
                               'car_count__sum'] or 0

    fuel_types = ['Solar', 'gasoline', 'oil']
    fuel_in = {}
    fuel_out = {}

    for ftype in fuel_types:
        fuel_in[ftype] = FuelTransaction.objects.filter(type='in', fuel_type=ftype).aggregate(total=Sum('quantity'))[
                             'total'] or 0
        fuel_out[ftype] = FuelTransaction.objects.filter(type='out', fuel_type=ftype).aggregate(total=Sum('quantity'))[
                              'total'] or 0

    total_fuel_in = sum(fuel_in.values())
    total_fuel_out = sum(fuel_out.values())
    total_fuel = total_fuel_in - total_fuel_out

    total_workers = Worker.objects.count()

    a=total_car_count+total_fountain_count
    b=total_car_count_today+total_fountain_today
    print("total_fountain_today: ",total_fountain_today)
    print("total_car_count_today: ",total_car_count_today)
    print("b: ",b)
    context = {
        'total_reports_cars': a,
        'total_reports_cars_for_today':b ,
        'total_fuel_in': total_fuel_in,

        'total_Solar_in': fuel_in['Solar'],
        'total_gasoline_in': fuel_in['gasoline'],
        'total_oil_in': fuel_in['oil'],
        'total_Solar_out': fuel_out['Solar'],
        'total_gasoline_out': fuel_out['gasoline'],
        'total_oil_out': fuel_out['oil'],
        'total_fuel_out': total_fuel_out,
        'total_fuel': total_fuel,
        'total_workers': total_workers,

    }
    return render(request, 'reports/dashboard.html', context)


@login_required
@manager_only
def workers_list(request):
    workers = Worker.objects.all()
    return render(request, 'workers/workers_list.html', {'workers': workers})


@login_required
@manager_only
def add_worker(request):
    if request.method == 'POST':
        worker_form = AddWorkerForm(request.POST, request.FILES)
        if worker_form.is_valid():
            worker = worker_form.save(commit=False)

            # user = User.objects.create_user(username=worker.user_name, password=worker.password)
            # user.save()

            # group = Group.objects.get(name='workers')
            # user.groups.add(group)
            # worker.user = user

            worker.save()

            return redirect('workers_list')
    else:
        worker_form = AddWorkerForm()

    return render(request, 'workers/add_worker.html', {'worker_form': worker_form})



@login_required
@manager_only
def edit_worker_record(request, pk):
    worker_record = get_object_or_404(Worker, pk=pk)

    if request.method == 'POST':
        form = AddWorkerForm(request.POST,request.FILES, instance=worker_record)
        if form.is_valid():
            form.save()
            return redirect('workers_list')
        else:
            print(form.errors)
    else:
        form = AddWorkerForm(instance=worker_record)

    return render(request, 'workers/edit_worker_record.html', {'form': form})

from django.http import HttpResponseRedirect
from django.urls import reverse

def delete_worker_image(request, worker_id):
    worker = get_object_or_404(Worker, pk=worker_id)
    if worker.worker_image:
        worker.worker_image.delete()
        worker.worker_image = None
        worker.save()
    return HttpResponseRedirect(reverse('edit_worker_record', args=[worker.id]))



@require_POST
def delete_worker_record(request, record_id):
    record = get_object_or_404(Worker, id=record_id)
    record.delete()
    return redirect('workers_list')


import traceback


@login_required
@manager_only
def add_attendance(request):
    try:
        print("ENTERED add_attendance")
        print("METHOD =", request.method)
        print("GET date =", request.GET.get("date"))
        print("POST selected_date =", request.POST.get("selected_date"))

        selected_date_str = request.GET.get('date')
        if selected_date_str:
            selected_date = datetime.strptime(selected_date_str.strip(), '%Y-%m-%d').date()
        else:
            selected_date = timezone.now().date()

        employees = Worker.objects.all()
        attendance_data = []

        if request.method == 'GET':
            for emp in employees:
                try:
                    attendance = Attendance.objects.get(employee=emp, date=selected_date)
                except Attendance.DoesNotExist:
                    attendance = None

                attendance_data.append({
                    'employee': emp,
                    'attendance': attendance
                })

        elif request.method == 'POST':
            selected_date_post = request.POST.get('selected_date')
            print("POST selected_date raw =", selected_date_post)

            selected_date = datetime.strptime(selected_date_post.strip(), '%Y-%m-%d').date()

            for emp in employees:
                check_in = request.POST.get(f'check_in_{emp.id}')
                check_out = request.POST.get(f'check_out_{emp.id}')
                print("EMP", emp.id, check_in, check_out)

                attendance, created = Attendance.objects.get_or_create(
                    employee=emp,
                    date=selected_date
                )
                attendance.check_in = check_in if check_in else None
                attendance.check_out = check_out if check_out else None
                attendance.save()

            return redirect(f"{reverse('add_attendance')}?date={selected_date}")

        return render(request, 'attendance/add_attendance.html', {
            'selected_date': selected_date,
            'attendance_data': attendance_data,
        })

    except Exception as e:
        print("===== add_attendance ERROR =====")
        print(str(e))
        traceback.print_exc()
        raise
@login_required
@manager_only
def workers_delays(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    employees = Worker.objects.all()
    delay_results = []

    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        total_days = (end - start).days + 1

        for emp in employees:
            total_delay = 0
            total_early_leave = 0
            absence_days = 0

            attendances = Attendance.objects.filter(employee=emp, date__range=[start, end])
            att_dict = {att.date: att for att in attendances}

            for i in range(total_days):
                current_day = start + timedelta(days=i)
                att = att_dict.get(current_day)

                if att and att.check_in and att.check_out:

                    expected_start = time(7, 0)
                    expected_end = time(17, 0)


                    if att.check_in > expected_start:
                        print("att.check_in : ",att.check_in )
                        delay = datetime.combine(att.date, att.check_in) - datetime.combine(att.date, expected_start)
                        total_delay += delay.total_seconds() / 60

                    if att.check_out < expected_end:
                        early = datetime.combine(att.date, expected_end) - datetime.combine(att.date, att.check_out)
                        total_early_leave += early.total_seconds() / 60

                else:
                    absence_days += 1

            delay_results.append({
                'employee': emp,
                'total_delay': int(total_delay),
                'total_early_leave': int(total_early_leave),
                'absence_days': absence_days,
            })

    return render(request, 'attendance/workers_delays.html', {
        'delay_results': delay_results,
        'start_date': start_date,
        'end_date': end_date,
    })

@login_required
@manager_only
def attendance_report(request):
    employees = Worker.objects.all()
    selected_employee_id = request.GET.get('employee')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    attendance_data = []
    selected_employee = None
    total_delay = 0
    total_early_leave = 0

    if selected_employee_id and start_date and end_date:
        selected_employee = Worker.objects.get(id=selected_employee_id)
        records = Attendance.objects.filter(
            employee=selected_employee,
            date__range=[start_date, end_date]
        ).order_by('date')

        official_start_time = time(6, 0)
        official_end_time = time(15, 0) #3PM

        for record in records:
            delay = 0
            early_leave = 0
            if record.check_in and record.check_in > official_start_time:
                delay_timedelta = datetime.combine(datetime.today(), record.check_in) - datetime.combine(datetime.today(), official_start_time)
                delay = int(delay_timedelta.total_seconds() // 60)
                total_delay += delay

            if record.check_out and record.check_out < official_end_time:
                early_leave_timedelta = datetime.combine(datetime.today(), official_end_time) - datetime.combine(datetime.today(), record.check_out)
                early_leave = int(early_leave_timedelta.total_seconds() // 60)
                total_early_leave += early_leave

            attendance_data.append({

                'date': record.date .strftime('%d-%m-%Y'),
                'check_in': record.check_in,
                'check_out': record.check_out,
                'delay': delay,
                'early_leave': early_leave
            })

    return render(request, 'attendance/attendance_report.html', {
        'employees': employees,
        'attendance_data': attendance_data,
        'selected_employee': selected_employee,
        'start_date': start_date,
        'end_date': end_date,
        'total_delay': total_delay,
        'total_early_leave': total_early_leave,
    })


@login_required
@manager_only
def add_fuel_transaction(request):
    if request.method == 'POST':
        form = FuelTransactionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fuel_transaction_list')
    else:
        form = FuelTransactionForm()
    return render(request, 'fuel/add_fuel_transaction.html', {'form': form})

@login_required
@manager_only
def fuel_transaction_list(request):
    def get_quantity(fuel_type, trans_type):
        result = FuelTransaction.objects.filter(
            fuel_type=fuel_type,
            type=trans_type
        ).aggregate(total=Sum('quantity'))
        return result['total'] or 0

    # نفلتر أولاً
    transactions_qs = FuelTransaction.objects.select_related('driver').all()

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    fuel_filter = request.GET.get('fuel_type')
    usage_type_filter = request.GET.get('usage_type')
    transaction_type_filter = request.GET.get('transaction_type')

    if start_date and end_date:
        transactions_qs = transactions_qs.filter(date__range=[start_date, end_date])

    if fuel_filter:
        transactions_qs = transactions_qs.filter(fuel_type=fuel_filter)

    if usage_type_filter:
        transactions_qs = transactions_qs.filter(usage_type=usage_type_filter)

    if transaction_type_filter:
        transactions_qs = transactions_qs.filter(type=transaction_type_filter)

    total_costs = {
        'Solar': FuelTransaction.objects.filter(fuel_type='Solar', type='in').aggregate(total=Sum('total_cost'))['total'] or 0,
        'gasoline': FuelTransaction.objects.filter(fuel_type='gasoline', type='in').aggregate(total=Sum('total_cost'))['total'] or 0,
        'oil': FuelTransaction.objects.filter(fuel_type='oil', type='in').aggregate(total=Sum('total_cost'))['total'] or 0,
    }

    total_in_quantity = transactions_qs.filter(type='in').aggregate(total=Sum('quantity'))['total'] or 0
    total_out_quantity = transactions_qs.filter(type='out').aggregate(total=Sum('quantity'))['total'] or 0
    total_in_cost = transactions_qs.filter(type='in').aggregate(total=Sum('total_cost'))['total'] or 0

    vehicle_out_quantity = transactions_qs.filter(type='out', usage_type='vehicle').aggregate(total=Sum('quantity'))[
                               'total'] or 0
    motor_out_quantity = transactions_qs.filter(type='out', usage_type='motor').aggregate(total=Sum('quantity'))[
                             'total'] or 0

    vehicle_out_count = transactions_qs.filter(type='out', usage_type='vehicle').count()
    motor_out_count = transactions_qs.filter(type='out', usage_type='motor').count()
    in_count = transactions_qs.filter(type='in').count()
    out_count = transactions_qs.filter(type='out').count()




    balance = {
        'Solar': get_quantity('Solar', 'in') - get_quantity('Solar', 'out'),
        'gasoline': get_quantity('gasoline', 'in') - get_quantity('gasoline', 'out'),
        'oil': get_quantity('oil', 'in') - get_quantity('oil', 'out'),
    }

    # الترتيب التصاعدي مهم للحساب الصحيح
    transactions_for_calc = transactions_qs.order_by('date', 'id')

    total_run_time_seconds = 0
    for t in transactions_for_calc:
        if t.start_time and t.end_time:
            start_dt = datetime.combine(t.date, t.start_time)
            end_dt = datetime.combine(t.date, t.end_time)
            if end_dt < start_dt:
                end_dt += timedelta(days=1)
            total_run_time_seconds += int((end_dt - start_dt).total_seconds())

    total_hours = total_run_time_seconds // 3600
    total_minutes = (total_run_time_seconds % 3600) // 60
    total_run_time_display = f"{total_hours} ساعة {total_minutes} دقيقة"

    processed = []
    current_balances = {'Solar': 0, 'gasoline': 0, 'oil': 0}

    # حفظ آخر قراءة وآخر تاريخ لكل سائق
    previous_meter_by_driver = {}
    previous_date_by_driver = {}

    for t in transactions_for_calc:
        fuel = t.fuel_type

        if t.type == 'in':
            current_balances[fuel] += t.quantity
        else:
            current_balances[fuel] -= t.quantity

        if t.start_time and t.end_time:
            start_dt = datetime.combine(t.date, t.start_time)
            end_dt = datetime.combine(t.date, t.end_time)
            if end_dt < start_dt:
                end_dt += timedelta(days=1)

            diff = end_dt - start_dt
            total_minutes_rt = int(diff.total_seconds() // 60)
            hours = total_minutes_rt // 60
            minutes = total_minutes_rt % 60
            run_time_hours = f"{hours} ساعات {minutes} دقيقة"
        else:
            run_time_hours = "لا يوجد"

        previous_meter = None
        meter_difference = None
        previous_date = None
        date_difference = None

        driver_id = t.driver.id if t.driver else None

        # الحساب فقط لنفس السائق، وعند وجود قراءة، ويفضل في السجلات الصادرة فقط
        if t.type == 'out' and driver_id and t.meter_reading is not None:
            previous_meter = previous_meter_by_driver.get(driver_id)
            previous_date = previous_date_by_driver.get(driver_id)

            if previous_meter is not None:
                meter_difference = t.meter_reading - previous_meter

            if previous_date is not None:
                date_difference = (t.date - previous_date).days

            previous_meter_by_driver[driver_id] = t.meter_reading
            previous_date_by_driver[driver_id] = t.date

        processed.append({
            'id': t.id,
            'date': t.date.strftime('%d-%m-%Y'),
            'day': arabic_days.get(t.date.strftime('%A'), t.date.strftime('%A')),
            'type': t.type,
            'fuel_type': t.get_fuel_type_display(),
            'quantity': t.quantity,
            'fuel_transaction_source': t.fuel_transaction_source,
            'total_cost': t.total_cost,
            'current_balance': current_balances[fuel],
            'run_time_hours': run_time_hours,
            'usage_type': t.usage_type,
            'driver': t.driver,
            'vehicle_type': t.vehicle_type,
            'notes': t.notes,
            'start_time': t.start_time,
            'end_time': t.end_time,
            'previous_meter': previous_meter,
            'meter_reading': t.meter_reading,
            'meter_difference': meter_difference,
            'previous_date': previous_date,
            'date_difference': date_difference,
        })

    # للعرض من الأحدث إلى الأقدم
    processed.reverse()

    paginator = Paginator(processed, 20)
    page = request.GET.get('page')
    transactions = paginator.get_page(page)

    context = {
        'transactions': transactions,
        'total_in_quantity': total_in_quantity,
        'total_out_quantity': total_out_quantity,
        'total_in_cost': total_in_cost,
        'total_run_time_display': total_run_time_display,
        'final_balance': balance,
        'total_costs': total_costs,

        'vehicle_out_quantity': vehicle_out_quantity,
        'motor_out_quantity': motor_out_quantity,
        'vehicle_out_count': vehicle_out_count,
        'motor_out_count': motor_out_count,
        'in_count': in_count,
        'out_count': out_count,

    }

    return render(request, 'fuel/fuel_transaction_list.html', context)

@login_required
@manager_only
def edit_fuel_record(request, pk):
    fuel_record = get_object_or_404(FuelTransaction, pk=pk)

    if request.method == 'POST':
        form = FuelTransactionForm(request.POST, instance=fuel_record)
        if form.is_valid():
            form.save()
            return redirect('fuel_transaction_list')
        else:
            print(form.errors)
    else:
        form = FuelTransactionForm(instance=fuel_record)

    return render(request, 'fuel/edit_fuel_transaction.html', {'form': form})


@require_POST
def delete_fuel_record(request, record_id):
    record = get_object_or_404(FuelTransaction, id=record_id)
    record.delete()
    return redirect('fuel_transaction_list')




@login_required
@manager_only
def add_car_record(request):
    if request.method == 'POST':
        form = CarRecordsForm(request.POST)
        if form.is_valid():
            print("formy: ",form)
            form.save()
            return redirect('car_records_list')
        else:
            print(form.errors)
    else:
        form = CarRecordsForm()
    return render(request, 'cars/add_car_record.html', {'form': form})

from django.shortcuts import render
from django.db.models import Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from .models import CarRecords, Driver, Worker, Institution
from .decorators import manager_only  # حسب مشروعك
from django.db.models import Sum
@login_required
@manager_only
def car_records_list(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    selected_driver_id = request.GET.get('driver')
    selected_assistant_id = request.GET.get('assistant')
    selected_institutions = request.GET.getlist('institutions')
    selected_documented_for = request.GET.get('documented_for')
    selected_notes = request.GET.get('notes')

    records = CarRecords.objects.all()

    if start_date:
        records = records.filter(date__gte=start_date)
    if end_date:
        records = records.filter(date__lte=end_date)
    if selected_driver_id:
        records = records.filter(name__id=selected_driver_id)
    if selected_assistant_id:
        assistant_name = Worker.objects.filter(id=selected_assistant_id).values_list("name", flat=True).first()
        if assistant_name:
            records = records.filter(assistant__icontains=assistant_name)
    if selected_institutions:
        records = records.filter(name__institution__in=selected_institutions)
    if selected_documented_for:
        records = records.filter(documented_for__icontains=selected_documented_for)
    if selected_notes:
        records = records.filter(notes__icontains=selected_notes)

    records = records.order_by('-date')

    total_car_count = records.aggregate(total=Sum('car_count'))['total'] or 0
    total_documented_count = records.aggregate(total=Sum('documented_count'))['total'] or 0
    total_cups = records.aggregate(Sum('cups'))['cups__sum'] or 0
    # ✨ Pagination
    paginator = Paginator(records, 20)
    page = request.GET.get('page')
    try:
        records = paginator.page(page)
    except PageNotAnInteger:
        records = paginator.page(1)
    except EmptyPage:
        records = paginator.page(paginator.num_pages)

    drivers = Driver.objects.all()
    assistants = Worker.objects.all()
    companies = Institution.objects.all()

    context = {
        'records': records,
        'start_date': start_date,
        'end_date': end_date,
        'drivers': drivers,
        'assistants': assistants,
        'companies': companies,
        'selected_driver_id': selected_driver_id,
        'selected_assistant_id': selected_assistant_id,
        'selected_institutions': selected_institutions,
        'selected_documented_for': selected_documented_for,
        'selected_notes': selected_notes,

        'total_car_count': total_car_count,
        'total_documented_count': total_documented_count,
        'total_cups': total_cups,

    }
    return render(request, 'cars/car_records_list.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from .models import CarRecords
from .forms import CarRecordsForm

def edit_car_record(request, pk):
    car_record = get_object_or_404(CarRecords, pk=pk)

    if request.method == 'POST':
        form = CarRecordsForm(request.POST, instance=car_record)
        if form.is_valid():
            form.save()
            return redirect('car_records_list')
        else:
            print(form.errors)
    else:
        form = CarRecordsForm(instance=car_record)

    return render(request, 'cars/edit_car_record.html', {'form': form})


@require_POST
def delete_car_record(request, record_id):
    record = get_object_or_404(CarRecords, id=record_id)
    record.delete()
    return redirect('car_records_list')



@login_required
@manager_only
def add_fountain_record(request):
    if request.method == 'POST':
        form = FountainRecordsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fountain_records_list')
        else:
            print(form.errors)
    else:
        form = FountainRecordsForm()
    return render(request, 'fountain/add_fountain_record.html', {'form': form})



@login_required
@manager_only
def fountain_records_list(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    selected_day = request.GET.get('day')
    selected_notes = request.GET.get('notes')

    records = FountainRecords.objects.all()

    if start_date:
        records = records.filter(date__gte=start_date)
    if end_date:
        records = records.filter(date__lte=end_date)
    if selected_day:
        records = records.filter(day__icontains=selected_day)
    if selected_notes:
        records = records.filter(notes__icontains=selected_notes)

    records = records.order_by('-date')

    # total_liters = records.aggregate(total=Sum('Liters'))['total'] or 0
    total_car_count = records.aggregate(total=Sum('car_count'))['total'] or 0

    paginator = Paginator(records, 20)
    page = request.GET.get('page')
    try:
        records = paginator.page(page)
    except PageNotAnInteger:
        records = paginator.page(1)
    except EmptyPage:
        records = paginator.page(paginator.num_pages)

    context = {
        'records': records,
        'start_date': start_date,
        'end_date': end_date,
        'selected_day': selected_day,
        'selected_notes': selected_notes,
        # 'total_liters': total_liters,
        'total_car_count': total_car_count,
    }
    return render(request, 'fountain/fountain_recordes_list.html', context)



@login_required
@manager_only
def edit_fountain_record(request, pk):
    record = get_object_or_404(FountainRecords, pk=pk)

    if request.method == 'POST':
        form = FountainRecordsForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('fountain_records_list')
        else:
            print(form.errors)
    else:
        form = FountainRecordsForm(instance=record)

    return render(request, 'fountain/edit_fountain_record.html', {'form': form})



@require_POST
@login_required
@manager_only
def delete_fountain_record(request, record_id):
    record = get_object_or_404(FountainRecords, id=record_id)
    record.delete()
    return redirect('fountain_records_list')















@login_required
@manager_only
def add_driver(request):
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('drivers_list')
        else:
            print(form.errors)
    else:
        form = DriverForm()

    return render(request, 'driver/add_driver.html', {'form': form})


@login_required
@manager_only
def drivers_list(request):
    records = Driver.objects.all().order_by('name')

    return render(request, 'driver/drivers_list.html', {
        'records': records,
    })


@login_required
@manager_only
def edit_driver(request, pk):
    driver = get_object_or_404(Driver, pk=pk)

    if request.method == 'POST':
        form = DriverForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()
            return redirect('drivers_list')
        else:
            print(form.errors)
    else:
        form = DriverForm(instance=driver)

    return render(request, 'driver/edit_driver.html', {
        'form': form,
        'driver': driver,
    })


@login_required
@manager_only
@require_POST
def delete_driver(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    driver.delete()
    return redirect('drivers_list')



@login_required
@manager_only
def add_institution(request):
    if request.method == 'POST':
        form = InstitutionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('institution_list')
    else:
        form = InstitutionForm()
    return render(request, 'Institution/add_institution.html', {'form': form})

@login_required
@manager_only
def institution_list(request):
    records = Institution.objects.all()
    return render(request, 'Institution/institution_list.html', {
        'records': records,
    })

def add_maintenance(request):
    if request.method == 'POST':
        form = MaintenanceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_maintenance')
    else:
        form = MaintenanceForm()
    return render(request, 'maintenance/add_maintenance.html', {'form': form})


@login_required
@manager_only
def maintenance_list(request):
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    maintenance_location = request.GET.get('maintenance_location', '')
    main_item = request.GET.get('main_item', '')
    sub_item = request.GET.get('sub_item', '')
    device = request.GET.get('device', '')


    records = Maintenance.objects.all()
    total_amount = records.aggregate(Sum('amount'))['amount__sum'] or 0
    if start_date:
        records = records.filter(date__gte=start_date)
    if end_date:
        records = records.filter(date__lte=end_date)
    if maintenance_location:
        records = records.filter(maintenance_location__id=maintenance_location)
    if main_item:
        records = records.filter(main_item__id=main_item)
    if sub_item:
        records = records.filter(sub_item__id=sub_item)
    if device:
        records = records.filter(device__id=device)

    locations = MaintenanceLocation.objects.all()
    main_items = MainItem.objects.all()
    sub_items = SubItem.objects.all()
    devices = Device.objects.all()

    return render(request, 'maintenance/maintenance_list.html', {
        'records': records,
        'total_amount': total_amount,
        'start_date': start_date,
        'end_date': end_date,
        'maintenance_location': maintenance_location,
        'main_item': main_item,
        'sub_item': sub_item,
        'device': device,
        'locations': locations,
        'main_items': main_items,
        'sub_items': sub_items,
        'devices': devices,
    })

@login_required
@manager_only
def add_options(request):
    loc_form = MaintenanceLocationForm(request.POST or None, prefix='loc')
    main_form = MainItemForm(request.POST or None, prefix='main')
    sub_form = SubItemForm(request.POST or None, prefix='sub')
    dev_form = DeviceForm(request.POST or None, prefix='dev')

    if request.method == 'POST':
        if 'submit_loc' in request.POST and loc_form.is_valid():
            loc_form.save()
        elif 'submit_main' in request.POST and main_form.is_valid():
            main_form.save()
        elif 'submit_sub' in request.POST and sub_form.is_valid():
            sub_form.save()
        elif 'submit_dev' in request.POST and dev_form.is_valid():
            dev_form.save()
        return redirect('add_options')

    context = {
        'loc_form': loc_form,
        'main_form': main_form,
        'sub_form': sub_form,
        'dev_form': dev_form,
    }
    return render(request, 'maintenance/add_options.html', context)



@login_required
@manager_only
def edit_maintenance_record(request, pk):
    maintenance_record = get_object_or_404(Maintenance, pk=pk)

    if request.method == 'POST':
        form = MaintenanceForm(request.POST, instance=maintenance_record)
        if form.is_valid():
            form.save()
            return redirect('maintenance_list')
        else:
            print(form.errors)
    else:
        form = MaintenanceForm(instance=maintenance_record)

    return render(request, 'maintenance/edit_maintenance.html', {'form': form})


@require_POST
def delete_maintenance_record(request, record_id):
    record = get_object_or_404(Maintenance, id=record_id)
    record.delete()
    return redirect('maintenance_list')


@login_required
@manager_only
def add_expenses(request):
    if request.method == 'POST':
        form = ExpensesFrom(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_expenses')
        else:
            print(form.errors)
    else:
        form = ExpensesFrom()
    return render(request, 'expenses/add_expenses.html', {'form': form})


@login_required
@manager_only
def expenses_list(request):
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    place_form = request.GET.get('Place', '')
    expenses_type_form = request.GET.get('expenses_type', '')

    records = Expenses.objects.all()
    total_amount = records.aggregate(Sum('amount'))['amount__sum'] or 0

    if start_date:
        records = records.filter(date__gte=start_date)
    if end_date:
        records = records.filter(date__lte=end_date)
    if place_form:
        records = records.filter(place__id=place_form)
    if expenses_type_form:
        records = records.filter(expenses_type__id=expenses_type_form)

    places = Place_Expenses.objects.all()
    expenses_types = Expenses_type.objects.all()

    print("records: ",records)
    return render(request, 'expenses/expenses_list.html', {
        'records': records,
        'total_amount': total_amount,
        'start_date': start_date,
        'end_date': end_date,
        'expenses_type_form': expenses_type_form,
        'place_form': place_form,
        'places': places,
        'expenses_types': expenses_types,

    })

def add_expenses_options(request):
    place_form = place_ExpensesForm(request.POST or None, prefix='place')
    type_expenses_form = Expenses_typeForm(request.POST or None, prefix='type_expenses')

    if request.method == 'POST':
        if 'submit_loc' in request.POST and place_form.is_valid():
            place_form.save()
        elif 'submit_main' in request.POST and type_expenses_form.is_valid():
            type_expenses_form.save()
        return redirect('add_expenses_options')

    context = {
        'place_form': place_form,
        'type_expenses_form': type_expenses_form,

    }
    return render(request, 'expenses/add_expenses_options.html', context)




@login_required
@manager_only
def edit_expenses_record(request, pk):
    expenses_record = get_object_or_404(Expenses, pk=pk)

    if request.method == 'POST':
        form = ExpensesFrom(request.POST, instance=expenses_record)
        if form.is_valid():
            form.save()
            return redirect('expenses_list')
        else:
            print(form.errors)
    else:
        form = ExpensesFrom(instance=expenses_record)

    return render(request, 'expenses/edit_expenses.html', {'form': form})


@require_POST
def delete_expenses_record(request, record_id):
    record = get_object_or_404(Expenses, id=record_id)
    record.delete()
    return redirect('expenses_list')




def financial_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    report_type = request.GET.get('report_type')

    fuel_qs = FuelTransaction.objects.all()
    if start_date and end_date:
        fuel_qs = fuel_qs.filter(date__gte=start_date, date__lte=end_date)


    if report_type == 'daily':
        trunc_fn = TruncDay
    elif report_type == 'monthly':
        trunc_fn = TruncMonth
    elif report_type == 'yearly':
        trunc_fn = TruncYear
    else:
        trunc_fn = TruncDay

    fuel_data = fuel_qs.annotate(period=trunc_fn('date')) \
                        .values('period') \
                        .annotate(total_fuel=Sum('total_cost')) \
                        .order_by('period')

    worker_qs = Worker.objects.all()
    if start_date and end_date:
        worker_qs = worker_qs.filter(start_date__gte=start_date, start_date__lte=end_date)

    worker_data = worker_qs.annotate(period=trunc_fn('start_date')) \
                            .values('period') \
                            .annotate(total_worker=Sum('salary')) \
                            .order_by('period')

    maintenance_qs = Maintenance.objects.all()
    if start_date and end_date:
        maintenance_qs = maintenance_qs.filter(date__gte=start_date, date__lte=end_date)

    maintenance_data = maintenance_qs.annotate(period=trunc_fn('date')) \
                      .values('period') \
                      .annotate(total_maintenance=Sum('amount')) \
                      .order_by('period')


    expenses_qs = Expenses.objects.all()
    if start_date and end_date:
        expenses_qs = expenses_qs.filter(date__gte=start_date, date__lte=end_date)

    expenses_data = expenses_qs.annotate(period=trunc_fn('date')) \
                      .values('period') \
                      .annotate(total_expenses=Sum('amount')) \
                      .order_by('period')

    merged_data = []
    all_periods = set(fuel_data.values_list('period', flat=True)) | \
                  set(worker_data.values_list('period', flat=True)) | \
                  set(maintenance_data.values_list('period', flat=True)) | \
                  set(expenses_data.values_list('period', flat=True))

    for period in all_periods:
        fuel_total = next((item['total_fuel'] for item in fuel_data if item['period'] == period), 0)
        worker_total = next((item['total_worker'] for item in worker_data if item['period'] == period), 0)
        maintenance_total = next((item['total_maintenance'] for item in maintenance_data if item['period'] == period), 0)
        expenses_total = next((item['total_expenses'] for item in expenses_data if item['period'] == period), 0)

        merged_data.append({
            'period': period,
            'fuel_total': fuel_total,
            'worker_total': worker_total,
            'maintenance_total': maintenance_total,
            'expenses_total': expenses_total,
            'total': fuel_total + worker_total + maintenance_total
        })

    total_fuel = sum(item['fuel_total'] for item in merged_data)
    total_worker = sum(item['worker_total'] for item in merged_data)
    total_maintenance = sum(item['maintenance_total'] for item in merged_data)
    total_expenses = sum(item['expenses_total'] for item in merged_data)
    total_all = total_fuel + total_worker + total_maintenance+total_expenses

    context = {
        'merged_data': merged_data,
        'total_fuel': total_fuel,
        'total_worker': total_worker,
        'total_maintenance': total_maintenance,
        'total_expenses': total_expenses,
        'total_all': total_all
    }

    return render(request, 'reports/financial_report.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum

@login_required
@manager_only
def add_vehicle_fuel_record(request):
    if request.method == 'POST':
        form = VehicleFuelRecordForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vehicle_fuel_list')
        else:
            print(form.errors)
    else:
        form = VehicleFuelRecordForm()

    context = {
        'form': form
    }
    return render(request, 'vehicle_fuel/add_vehicle_fuel_record.html', context)


@login_required
@manager_only
def vehicle_fuel_list(request):
    records = VehicleFuelRecord.objects.select_related('driver').all()

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    driver_id = request.GET.get('driver')

    if start_date:
        records = records.filter(date__gte=start_date)

    if end_date:
        records = records.filter(date__lte=end_date)

    if driver_id:
        records = records.filter(driver_id=driver_id)

    records = records.order_by('-date', '-id')

    total_fuel_quantity = records.aggregate(total=Sum('fuel_quantity'))['total'] or 0

    total_distance = 0
    for record in records:
        total_distance += record.distance_difference

    paginator = Paginator(records, 20)
    page = request.GET.get('page')

    try:
        records = paginator.page(page)
    except PageNotAnInteger:
        records = paginator.page(1)
    except EmptyPage:
        records = paginator.page(paginator.num_pages)

    context = {
        'records': records,
        'total_fuel_quantity': total_fuel_quantity,
        'total_distance': total_distance,
        'start_date': start_date,
        'end_date': end_date,
        'driver_id': driver_id,
        'drivers': Driver.objects.all(),
    }

    return render(request, 'vehicle_fuel/vehicle_fuel_list.html', context)


@login_required
@manager_only
def edit_vehicle_fuel_record(request, pk):
    record = get_object_or_404(VehicleFuelRecord, pk=pk)

    if request.method == 'POST':
        form = VehicleFuelRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('vehicle_fuel_list')
        else:
            print(form.errors)
    else:
        form = VehicleFuelRecordForm(instance=record)

    context = {
        'form': form,
        'record': record,
    }
    return render(request, 'vehicle_fuel/edit_vehicle_fuel_record.html', context)


@login_required
@manager_only
@require_POST
def delete_vehicle_fuel_record(request, record_id):
    record = get_object_or_404(VehicleFuelRecord, id=record_id)
    record.delete()
    return redirect('vehicle_fuel_list')


from django.db.models import Sum, Q
from django.db.models.functions import Cast
from django.db.models import IntegerField

def reports_summary(request):

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # ======================
    # 🚗 السيارات
    # ======================
    car_records = CarRecords.objects.all()

    # ✅ فلترة ذكية (ما تضيع بيانات)
    if start_date:
        car_records = car_records.filter(date__gte=start_date)
    if end_date:
        car_records = car_records.filter(date__lte=end_date)

    total_cars = car_records.aggregate(
        total=Sum(Cast('car_count', IntegerField()))
    )['total'] or 0

    total_documented = car_records.aggregate(
        total=Sum(Cast('documented_count', IntegerField()))
    )['total'] or 0

    total_cups = car_records.aggregate(
        total=Sum('cups')
    )['total'] or 0


    # ======================
    # ⛽ الوقود
    # ======================
    fuel = FuelTransaction.objects.all()

    if start_date:
        fuel = fuel.filter(date__gte=start_date)
    if end_date:
        fuel = fuel.filter(date__lte=end_date)

    # ✅ لا تفقد بيانات بدون usage_type
    total_fuel_in = fuel.filter(type='in').aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_fuel_out = fuel.filter(type='out').aggregate(Sum('quantity'))['quantity__sum'] or 0

    # ⚠️ أهم نقطة: بعض السجلات usage_type فاضي
    motor_fuel = fuel.filter(
        Q(type='out') & Q(usage_type='motor')
    ).aggregate(Sum('quantity'))['quantity__sum'] or 0

    vehicle_fuel = fuel.filter(
        Q(type='out') & Q(usage_type='vehicle')
    ).aggregate(Sum('quantity'))['quantity__sum'] or 0

    # 🔥 الباقي (بدون تصنيف)
    unknown_fuel = fuel.filter(
        Q(type='out') & (Q(usage_type__isnull=True) | Q(usage_type=''))
    ).aggregate(Sum('quantity'))['quantity__sum'] or 0


    # ======================
    # ⏱ ساعات التشغيل (ماتور فقط)
    # ======================
    total_seconds = 0

    motor_records = fuel.filter(
        Q(usage_type='motor') |
        Q(start_time__isnull=False, end_time__isnull=False)
    )

    for f in motor_records:
        hours = f.operating_hours()
        if hours:
            total_seconds += hours * 3600

    total_hours = int(total_seconds // 3600)
    total_minutes = int((total_seconds % 3600) // 60)


    context = {
        'total_cars': total_cars,
        'total_documented': total_documented,
        'total_cups': total_cups,

        'total_fuel_in': total_fuel_in,
        'total_fuel_out': total_fuel_out,

        'motor_fuel': motor_fuel,
        'vehicle_fuel': vehicle_fuel,
        'unknown_fuel': unknown_fuel,  # 🔥 مهم

        'total_hours': total_hours,
        'total_minutes': total_minutes,

        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'reports/summary.html', context)



from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse

from django.db.models import Sum, Q
from django.db.models.functions import Cast
from django.db.models import IntegerField

def summary_pdf(request):

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    car_records = CarRecords.objects.all()
    fuel = FuelTransaction.objects.all()

    # ✅ فلترة صح
    if start_date:
        car_records = car_records.filter(date__gte=start_date)
        fuel = fuel.filter(date__gte=start_date)

    if end_date:
        car_records = car_records.filter(date__lte=end_date)
        fuel = fuel.filter(date__lte=end_date)

    # 🚗 السيارات
    total_cars = car_records.aggregate(
        total=Sum(Cast('car_count', IntegerField()))
    )['total'] or 0

    total_documented = car_records.aggregate(
        total=Sum(Cast('documented_count', IntegerField()))
    )['total'] or 0

    total_cups = car_records.aggregate(
        total=Sum('cups')
    )['total'] or 0

    # ⛽ الوقود
    total_fuel_in = fuel.filter(type='in').aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_fuel_out = fuel.filter(type='out').aggregate(Sum('quantity'))['quantity__sum'] or 0

    motor_fuel = fuel.filter(Q(type='out') & Q(usage_type='motor')).aggregate(Sum('quantity'))['quantity__sum'] or 0
    vehicle_fuel = fuel.filter(Q(type='out') & Q(usage_type='vehicle')).aggregate(Sum('quantity'))['quantity__sum'] or 0
    unknown_fuel = fuel.filter(
        Q(type='out') & (Q(usage_type__isnull=True) | Q(usage_type=''))
    ).aggregate(Sum('quantity'))['quantity__sum'] or 0

    # ⏱ ساعات التشغيل
    total_seconds = 0
    for f in fuel.filter(Q(usage_type='motor') | Q(start_time__isnull=False, end_time__isnull=False)):
        h = f.operating_hours()
        if h:
            total_seconds += h * 3600

    total_hours = int(total_seconds // 3600)
    total_minutes = int((total_seconds % 3600) // 60)

    # 📄 HTML
    html_string = render_to_string('reports/summary_pdf.html', {
        'total_cars': total_cars,
        'total_documented': total_documented,
        'total_cups': total_cups,
        'total_fuel_in': total_fuel_in,
        'total_fuel_out': total_fuel_out,
        'motor_fuel': motor_fuel,
        'vehicle_fuel': vehicle_fuel,
        'unknown_fuel': unknown_fuel,
        'total_hours': total_hours,
        'total_minutes': total_minutes,
        'start_date': start_date,
        'end_date': end_date,
    })

    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'

    return response