from django.contrib import admin
from .models import (
    Attendance, CarRecords, Device, Driver, Expenses, Expenses_type,
    FuelTransaction, Institution, MainItem, Maintenance, MaintenanceLocation,
    Place_Expenses, SubItem, Worker,
)

# admin.site.register(Report)
admin.site.register(Worker)
admin.site.register(Attendance)
admin.site.register(FuelTransaction)
admin.site.register(Driver)
admin.site.register(CarRecords)
admin.site.register(Institution)
@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    autocomplete_fields = ['maintenance_location', 'main_item', 'sub_item', 'device']

@admin.register(MaintenanceLocation)
class MaintenanceLocationAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(MainItem)
class MainItemAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(SubItem)
class SubItemAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    search_fields = ['name']
@admin.register(Expenses)
class ExpensesAdmin(admin.ModelAdmin):
    autocomplete_fields = ['palce', 'expenses_type']

@admin.register(Expenses_type)
class Expenses_typeAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Place_Expenses)
class Palce_ExpensesAdmin(admin.ModelAdmin):
    search_fields = ['name']
