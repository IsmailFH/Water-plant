from datetime import datetime, time, date, timedelta

from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncDate, TruncMonth, TruncYear, TruncDay

from .models import (
    Worker, Attendance, Driver, FuelTransaction, Institution, CarRecords,
    Maintenance, Expenses, Expenses_type, Place_Expenses, Device,
    MainItem, SubItem, MaintenanceLocation
)
from .forms import (
    AddWorkerForm, FuelTransactionForm, DriverForm, CarRecordsForm, InstitutionForm,
    MaintenanceForm, ExpensesFrom, Expenses_typeForm, place_ExpensesForm,
    MaintenanceLocationForm, MainItemForm, SubItemForm, DeviceForm
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


@login_required
@manager_only
def dashboard(request):
    total_reports_cars = CarRecords.objects.count()
    today = date.today()
    total_reports_cars_for_today = CarRecords.objects.filter(date=today).count()


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

    # today = date.today()
    # last_7_days = today - timedelta(days=6)
    #
    # data = (
    #     CarRecords.objects
    #         .filter(date__range=(last_7_days, today))
    #         .annotate(day_only=TruncDate('date'))
    #         .values('day_only')
    #         .annotate(total=Sum('car_count'))
    #         .order_by('day_only')
    # )
    #
    # # ✅ معالجة اليوم بشكل آمن
    # def safe_date_format(d):
    #     if isinstance(d, str):
    #         try:
    #             d = datetime.strptime(d, "%Y-%m-%d").date()
    #         except Exception:
    #             return d  # في حال فشل التحويل
    #     return d.strftime("%d/%m")
    #
    # dates = [safe_date_format(item['day_only']) for item in data]
    # car_counts = [item['total'] for item in data]


    context = {
        'total_reports_cars': total_reports_cars,
        'total_reports_cars_for_today': total_reports_cars_for_today,
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

        # "chart_labels": dates,
        # "chart_data": car_counts,

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
        worker_form = AddWorkerForm(request.POST)
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
def add_attendance(request):
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
        selected_date = datetime.strptime(selected_date_post.strip(), '%Y-%m-%d').date()

        for emp in employees:
            check_in = request.POST.get(f'check_in_{emp.id}')
            check_out = request.POST.get(f'check_out_{emp.id}')

            attendance, created = Attendance.objects.get_or_create(employee=emp, date=selected_date)
            attendance.check_in = check_in if check_in else None
            attendance.check_out = check_out if check_out else None
            attendance.save()
        return redirect(f"{reverse('add_attendance')}?date={selected_date}")

    return render(request, 'attendance/add_attendance.html', {
        'selected_date': selected_date,
        'attendance_data': attendance_data,
    })


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

                    expected_start = time(6, 0)
                    expected_end = time(15, 0)


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
        result = FuelTransaction.objects.filter(fuel_type=fuel_type, type=trans_type).aggregate(total=Sum('quantity'))
        return result['total'] or 0
    transactions = FuelTransaction.objects.all().order_by('date')

    if request.GET.get('start_date') and request.GET.get('end_date'):
        start_date = request.GET['start_date']
        end_date = request.GET['end_date']
        transactions = transactions.filter(date__range=[start_date, end_date])

    fuel_filter = request.GET.get('fuel_type')
    if fuel_filter:
        transactions = transactions.filter(fuel_type=fuel_filter)

    transaction_type_filter = request.GET.get('transaction_type')
    if transaction_type_filter:
        transactions = transactions.filter(type=transaction_type_filter)

    total_costs = {
        'Solar': FuelTransaction.objects.filter(fuel_type='Solar', type='in').aggregate(Sum('total_cost'))['total_cost__sum'] or 0,
        'gasoline': FuelTransaction.objects.filter(fuel_type='gasoline', type='in').aggregate(Sum('total_cost'))['total_cost__sum'] or 0,
        'oil': FuelTransaction.objects.filter(fuel_type='oil', type='in').aggregate(Sum('total_cost'))['total_cost__sum'] or 0,
    }

    total_in_quantity = transactions.filter(type='in').aggregate(total=Sum('quantity'))['total'] or 0
    total_out_quantity = transactions.filter(type='out').aggregate(total=Sum('quantity'))['total'] or 0

    total_in_cost = transactions.filter(type='in').aggregate(total=Sum('total_cost'))['total'] or 0

    balance = {
        'Solar': get_quantity('Solar', 'in') - get_quantity('Solar', 'out'),
        'gasoline': get_quantity('gasoline', 'in') - get_quantity('gasoline', 'out'),
        'oil': get_quantity('oil', 'in') - get_quantity('oil', 'out'),
    }

    total_run_time_seconds = sum(
        (datetime.combine(datetime.today(), t.end_time) - datetime.combine(datetime.today(), t.start_time)).seconds
        for t in transactions if t.start_time and t.end_time
    )

    total_hours = total_run_time_seconds // 3600
    total_minutes = (total_run_time_seconds % 3600) // 60

    total_run_time_display = f"{total_hours} ساعة {total_minutes} دقيقة"

    processed = []
    current_balances = {'Solar': 0, 'gasoline': 0, 'oil': 0}
    for t in transactions:
        fuel = t.fuel_type
        if t.type == 'in':
            current_balances[fuel] += t.quantity
        else:
            current_balances[fuel] -= t.quantity

        if t.start_time and t.end_time:
            start = datetime.combine(datetime.today(), t.start_time)
            end = datetime.combine(datetime.today(), t.end_time)
            diff = end - start
            total_minutes = diff.seconds // 60
            hours = total_minutes // 60
            minutes = total_minutes % 60
            run_time_hours = f"{hours} ساعات {minutes} دقيقة"
        else:
            run_time_hours = "لا يوجد"

        processed.append({
            'date': t.date.strftime('%d-%m-%Y'),
            'type': t.type,
            'quantity': t.quantity,
            'fuel_type': t.get_fuel_type_display(),
            'price_per_liter': t.price_per_liter,
            'total_cost': t.total_cost,
            'day': arabic_days[t.date.strftime('%A')],
            'current_balance': current_balances[fuel],
            'run_time_hours': run_time_hours,

        })

    context = {
        'transactions': processed,
        'total_in_quantity': total_in_quantity,
        'total_out_quantity': total_out_quantity,
        'total_in_cost': total_in_cost,
        'total_run_time_display': total_run_time_display,
        'final_balance': balance,
        'total_costs':total_costs
    }

    return render(request, 'fuel/fuel_transaction_list.html', context)

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

    total_car_count = records.aggregate(total=Sum('car_count'))['total'] or 0
    total_documented_count = records.aggregate(total=Sum('documented_count'))['total'] or 0

    drivers = Driver.objects.all()
    assistants = Worker.objects.all()
    companies=Institution.objects.all()

    context = {
        'records': records,
        'start_date': start_date,
        'end_date': end_date,
        'drivers': drivers,
        'assistants': assistants,
        'selected_driver_id': selected_driver_id,
        'selected_assistant_id': selected_assistant_id,
        'selected_institutions': selected_institutions,
        'companies':companies,
        'selected_documented_for': selected_documented_for,
        'selected_notes': selected_notes,
        'total_car_count': total_car_count,
        'total_documented_count': total_documented_count,

    }
    return render(request, 'cars/car_records_list.html', context)


@login_required
@manager_only
def add_driver(request):
    if request.method == 'POST':
        form = DriverForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('drivers_list')
    else:
        form = DriverForm()
    return render(request, 'driver/add_driver.html', {'form': form})

@login_required
@manager_only
def drivers_list(request):
    institution_filter = request.GET.get('institution', '')

    records = Driver.objects.exclude()
    if institution_filter:
        records = records.filter(institution=institution_filter)

    return render(request, 'driver/drivers_list.html', {
        'records': records,
    })

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

