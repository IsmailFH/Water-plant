from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime

class AbstractNameModel(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Worker(AbstractNameModel):
    x=[
        ("مشرف","مشرف"),
        ("موظف","موظف"),
        ("مساعد","مساعد"),
    ]
    # user_name=models.CharField(max_length=100)
    # password=models.CharField(max_length=100 ,default="123456")
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    id_number=models.CharField(max_length=9, null=True, blank=True)
    job = models.CharField(max_length=100 ,choices=x,default="موظف" , null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    salary = models.FloatField(null=True, blank=True,default=500)


class Attendance(models.Model):
    employee = models.ForeignKey(Worker, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('employee', 'date')


class FuelTransaction(models.Model):
    FUEL_TYPES = [
        ('Solar', 'سولار'),
        ('gasoline', 'بنزين'),
        ('oil', 'زيت'),
    ]
    TRANSACTION_TYPES = [
        ('in', 'وارد'),
        ('out', 'صادر'),
    ]

    fuel_type = models.CharField(max_length=10, choices=FUEL_TYPES, default='gasoline')
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    date = models.DateField()
    quantity = models.FloatField()
    price_per_liter = models.FloatField()
    total_cost = models.FloatField(blank=True, null=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    def operating_hours(self):
        if self.start_time and self.end_time:
            # start = datetime.combine(datetime.date.today(), self.start_time)
            start = datetime.datetime.combine(datetime.date.today(), self.start_time)
            end = datetime.combine(datetime.date.today(), self.end_time)
            delta = end - start
            return delta.total_seconds() / 3600
        return None

    def save(self, *args, **kwargs):
        if self.quantity is not None and self.price_per_liter is not None:
            self.total_cost = self.quantity * self.price_per_liter
        super().save(*args, **kwargs)


class Driver(AbstractNameModel):
    id_number=models.CharField()


class Institution(AbstractNameModel):
    pass

class CarRecords(models.Model):
    day = models.CharField(max_length=20)
    date = models.DateField()
    name = models.ForeignKey(Driver, on_delete=models.CASCADE)
    assistant = models.CharField(max_length=255)
    car_count = models.PositiveIntegerField()
    documented_count = models.PositiveIntegerField()
    documented_for = models.CharField(max_length=100)
    notes = models.CharField(max_length=300,null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.date}"

class MaintenanceLocation(AbstractNameModel):
    pass

class MainItem(AbstractNameModel):
    pass

class SubItem(AbstractNameModel):
    pass

class Device(AbstractNameModel):
    pass

class Maintenance(models.Model):
    day = models.CharField(max_length=20)
    date = models.DateField()
    maintenance_location = models.ForeignKey(MaintenanceLocation, on_delete=models.SET_NULL, null=True, blank=True)
    main_item = models.ForeignKey(MainItem, on_delete=models.SET_NULL, null=True, blank=True)
    sub_item = models.ForeignKey(SubItem, on_delete=models.SET_NULL, null=True, blank=True)
    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    amount = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.day} - {self.maintenance_location}"

class Expenses_type(AbstractNameModel):
    pass

class Place_Expenses(AbstractNameModel):
    pass

class Expenses(models.Model):
    day = models.CharField(max_length=20)
    date = models.DateField()
    palce = models.ForeignKey(Place_Expenses, on_delete=models.SET_NULL, null=True, blank=True)
    expenses_type = models.ForeignKey(Expenses_type, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.PositiveIntegerField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.day} - {self.palce}"
