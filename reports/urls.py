from django.urls import path
from . import views

urlpatterns = [

    path('redirect_after_login/', views.redirect_after_login, name='after_login'),

    path('', views.dashboard, name='dashboard'),

    path('workers_list', views.workers_list, name='workers_list'),
    path('add_worker/', views.add_worker, name='add_worker'),

    path('edit-worker/<int:pk>/', views.edit_worker_record, name='edit_worker_record'),
    path('worker-records/delete/<int:record_id>/', views.delete_worker_record, name='delete_worker_record'),
    path('delete-worker-image/<int:pk>/', views.delete_worker_image, name='delete_worker_image'),


    path('attendance_report/', views.attendance_report, name='attendance_report'),
    path('add_attendance/', views.add_attendance, name='add_attendance'),
    path('workers_delays/', views.workers_delays, name='workers_delays'),


    path('add_institution/', views.add_institution, name='add_institution'),
    path('institution_list/', views.institution_list, name='institution_list'),


    path('add_fuel_transaction/', views.add_fuel_transaction, name='add_fuel_transaction'),
    path('fuel_transactions/', views.fuel_transaction_list, name='fuel_transaction_list'),
    path('edit-fuel/<int:pk>/', views.edit_fuel_record, name='edit_fuel_record'),
    path('fuel-records/delete/<int:record_id>/', views.delete_fuel_record, name='delete_fuel_record'),

    path('add_car_record/', views.add_car_record, name='add_car_record'),
    path('car_records_list/', views.car_records_list, name='car_records_list'),
    path('edit/<int:pk>/', views.edit_car_record, name='edit_car_record'),
    path('car-records/delete/<int:record_id>/', views.delete_car_record, name='delete_car_record'),

    path('add_fountain_record/', views.add_fountain_record, name='add_fountain_record'),
    path('fountain_records_list/', views.fountain_records_list, name='fountain_records_list'),
    path('f_edit/<int:pk>/', views.edit_fountain_record, name='edit_fountain_record'),
    path('fountain-records/delete/<int:record_id>/', views.delete_fountain_record, name='delete_fountain_record'),


    path('add_driver/', views.add_driver, name='add_driver'),
    path('drivers_list/', views.drivers_list, name='drivers_list'),

    path('add_maintenance/', views.add_maintenance, name='add_maintenance'),
    path('maintenance_list/', views.maintenance_list, name='maintenance_list'),
    path('add_options/', views.add_options, name='add_options'),
    path('edit-maintenance/<int:pk>/', views.edit_maintenance_record, name='edit_maintenance_record'),
    path('maintenance-records/delete/<int:record_id>/', views.delete_maintenance_record, name='delete_maintenance_record'),



    path('add_expenses/', views.add_expenses, name='add_expenses'),
    path('expenses_list/', views.expenses_list, name='expenses_list'),
    path('add_expenses_options/', views.add_expenses_options, name='add_expenses_options'),
    path('edit-expenses/<int:pk>/', views.edit_expenses_record, name='edit_expenses_record'),
    path('expenses-records/delete/<int:record_id>/', views.delete_expenses_record,name='delete_expenses_record'),



    path('financial_report/', views.financial_report, name='financial_report'),


]
