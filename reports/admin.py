from django.contrib import admin
from .models import  Worker,Attendance,FuelTransaction,Driver,CarRecords,Institution

# admin.site.register(Report)
admin.site.register(Worker)
admin.site.register(Attendance)
admin.site.register(FuelTransaction)
admin.site.register(Driver)
admin.site.register(CarRecords)
admin.site.register(Institution)


from django.contrib import admin
from .models import Maintenance, MaintenanceLocation, MainItem, SubItem, Device

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



from django.contrib import admin
from .models import Expenses,Expenses_type,Place_Expenses

@admin.register(Expenses)
class ExpensesAdmin(admin.ModelAdmin):
    autocomplete_fields = ['palce', 'expenses_type']

@admin.register(Expenses_type)
class Expenses_typeAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Place_Expenses)
class Palce_ExpensesAdmin(admin.ModelAdmin):
    search_fields = ['name']

