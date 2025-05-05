from django.urls import path
from . import views

urlpatterns = [

    path('redirect_after_login/', views.redirect_after_login, name='after_login'),

    path('', views.dashboard, name='dashboard'),

    path('workers_list', views.workers_list, name='workers_list'),
    path('add_worker/', views.add_worker, name='add_worker'),
    path('attendance_report/', views.attendance_report, name='attendance_report'),
    path('add_attendance/', views.add_attendance, name='add_attendance'),
    path('workers_delays/', views.workers_delays, name='workers_delays'),


    path('add_institution/', views.add_institution, name='add_institution'),
    path('institution_list/', views.institution_list, name='institution_list'),


    path('add_fuel_transaction/', views.add_fuel_transaction, name='add_fuel_transaction'),
    path('fuel_transactions/', views.fuel_transaction_list, name='fuel_transaction_list'),


    path('add_car_record/', views.add_car_record, name='add_car_record'),
    path('car_records_list/', views.car_records_list, name='car_records_list'),


    path('add_driver/', views.add_driver, name='add_driver'),
    path('drivers_list/', views.drivers_list, name='drivers_list'),

    path('add_maintenance/', views.add_maintenance, name='add_maintenance'),
    path('maintenance_list/', views.maintenance_list, name='maintenance_list'),
    path('add_options/', views.add_options, name='add_options'),

    path('add_expenses/', views.add_expenses, name='add_expenses'),
    path('expenses_list/', views.expenses_list, name='expenses_list'),
    path('add_expenses_options/', views.add_expenses_options, name='add_expenses_options'),


    path('financial_report/', views.financial_report, name='financial_report'),


]
