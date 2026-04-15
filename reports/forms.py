import datetime

from django import forms
from .models import Worker,FuelTransaction,Driver,CarRecords,Institution\
    ,Maintenance,Place_Expenses,Expenses_type,\
    Expenses,MaintenanceLocation, MainItem, SubItem, Device,VehicleFuelRecord

class AddWorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ["name","id_number", "job", "start_date","salary"]
        # fields = ["name","id_number", "job", "start_date","salary"]

        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'الاسم',
                }
            ),
            # 'user_name': forms.TextInput(
            #     attrs={
            #         'class': 'form-control',
            #         'placeholder': 'اسم المستخدم في النظام',
            #     }
            # ),
            # 'password': forms.TextInput(
            #     attrs={
            #         'class': 'form-control',
            #     }
            # ),

            'id_number': forms.NumberInput(
                attrs={
                    'type': 'number',
                    'class': 'form-control',
                    'placeholder': 'رقم الهوية'

                }
            ),

            'job': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),

            'start_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),

            'salary': forms.NumberInput(
                attrs={

                    'class': 'form-control',
                    'placeholder': 'الراتب'
                }
            ),
            # 'worker_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),  # ✅ هنا نضيف الكلاس



        }
        labels = {
            'name':'اسم العامل',
            # 'user_name':'اسم المستخدم',
            # 'password':'كلمة السر',
            'id_number': 'رقم الهوية',
            'job':'طبيعة العمل',
            'start_date': 'بداية العمل',
            'salary': 'الراتب',
            # 'worker_image': 'صورة الموظف',
        }

        # def __init__(self, *args, **kwargs):
        #     super().__init__(*args, **kwargs)
        #     for field in self.fields.values():
        #         field.widget.attrs['class'] = 'form-control'

# class FuelTransactionForm(forms.ModelForm):
#     class Meta:
#         model = FuelTransaction
#         fields = ['fuel_type', 'date', 'type', 'quantity', 'fuel_transaction_source','start_time','end_time']
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'type': forms.Select(attrs={'class': 'form-control'}),
#             'fuel_type': forms.Select(attrs={'class': 'form-control'}),
#             'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'كمية السولار'}),
#             'fuel_transaction_source': forms.Select(attrs={'class': 'form-control', 'placeholder': 'مصدر السولار'}),
#             'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
#             'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
#
#         }
#         labels = {
#             'fuel_type': 'نوع السولار',
#             'date': 'التاريخ',
#             'type': 'نوع العملية',
#             'quantity': 'عدد اللترات',
#             'fuel_transaction_source ': 'مصدر السولار',
#             'start_time': 'ساة التشغيل',
#             'end_time': ' ساعة الايقاف',
#         }
#
class FuelTransactionForm(forms.ModelForm):
    class Meta:
        model = FuelTransaction
        fields = [
            'fuel_type',
            'date',
            'type',
            'quantity',
            'fuel_transaction_source',
            'usage_type',
            'driver',
            'vehicle_type',
            'notes',
            'start_time',
            'end_time',
            'meter_reading',
        ]

        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_type'
            }),
            'fuel_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'كمية المحروقات'
            }),
            'fuel_transaction_source': forms.Select(attrs={
                'class': 'form-control'
            }),
            'usage_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_usage_type'
            }),
            'driver': forms.Select(attrs={
                'class': 'form-control'
            }),
            'vehicle_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'نوع السيارة'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات'
            }),
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'meter_reading': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'القراءة',
                'min': '0',
                'step': '1'
            }),
        }

        labels = {
            'fuel_type': 'نوع المحروقات',
            'date': 'التاريخ',
            'type': 'نوع العملية',
            'quantity': 'الكمية',
            'fuel_transaction_source': 'مصدر المحروقات',
            'usage_type': 'الجهة',
            'driver': 'اسم السائق',
            'vehicle_type': 'نوع السيارة',
            'notes': 'ملاحظات',
            'start_time': 'ساعة التشغيل',
            'end_time': 'ساعة الإيقاف',
            'meter_reading': 'القراءة',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['driver'].empty_label = "اختر السائق"

    def clean(self):
        cleaned_data = super().clean()

        transaction_type = cleaned_data.get('type')
        usage_type = cleaned_data.get('usage_type')
        driver = cleaned_data.get('driver')
        vehicle_type = cleaned_data.get('vehicle_type')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        meter_reading = cleaned_data.get('meter_reading')

        # إذا العملية صادر
        if transaction_type == 'out':
            if not usage_type:
                self.add_error('usage_type', 'يجب تحديد الجهة')

            # سيارة
            if usage_type == 'vehicle':
                if not driver:
                    self.add_error('driver', 'يجب اختيار السائق')

                if not vehicle_type:
                    self.add_error('vehicle_type', 'يجب إدخال نوع السيارة')

                if meter_reading is None:
                    self.add_error('meter_reading', 'القراءة مطلوبة')

                # حقول الماتور لا تلزم السيارة
                cleaned_data['start_time'] = None
                cleaned_data['end_time'] = None

            # ماتور
            elif usage_type == 'motor':
                if not start_time:
                    self.add_error('start_time', 'ساعة التشغيل مطلوبة')

                if not end_time:
                    self.add_error('end_time', 'ساعة الإيقاف مطلوبة')

                if start_time and end_time and end_time == start_time:
                    self.add_error('end_time', 'ساعة الإيقاف يجب أن تختلف عن ساعة التشغيل')

                if meter_reading is None:
                    self.add_error('meter_reading', 'القراءة مطلوبة')

                # حقول السيارة لا تلزم الماتور
                cleaned_data['driver'] = None
                cleaned_data['vehicle_type'] = None

        # إذا العملية وارد
        else:
            cleaned_data['usage_type'] = None
            cleaned_data['driver'] = None
            cleaned_data['vehicle_type'] = None
            cleaned_data['start_time'] = None
            cleaned_data['end_time'] = None
            cleaned_data['meter_reading'] = None
            cleaned_data['notes'] = cleaned_data.get('notes')

        return cleaned_data

class CarRecordsForm(forms.ModelForm):
    COUNT_CHOICES = [(i, str(i)) for i in range(1, 51)]
    COUNT_CHOICES_DOUC = [(i, str(i)) for i in range(0, 50)]

    assistant = forms.MultipleChoiceField(
        choices=[],
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label='اسم مساعد السائق:'
    )

    documented_for = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'تم التوثيق لـ'
        }),
        label='تم التوثيق لـ:'
    )

    car_count = forms.ChoiceField(
        label='عدد السيارات',
        choices=COUNT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    documented_count = forms.ChoiceField(
        label='عدد السيارات الموثقة',
        choices=COUNT_CHOICES_DOUC,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CarRecords
        fields = '__all__'
        widgets = {
            'day': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'date': 'التاريخ',
            'day': 'اليوم',
            'name': 'اسم السائق',
            'car_count': 'عدد السيارات',
            'documented_count': 'عدد السيارات الموثقة',
            'notes': 'ملاحظات:',
        }

    def clean_assistant(self):
        data = self.cleaned_data.get('assistant', [])
        if not data:
            return ''
        return ', '.join(data)

    def clean_documented_for(self):
        data = self.cleaned_data.get('documented_for', '')
        if not data:
            return 'لا يوجد'
        return data.strip()

    def __init__(self, *args, **kwargs):
        super(CarRecordsForm, self).__init__(*args, **kwargs)
        today = datetime.date.today()
        self.fields['date'].initial = today
        self.fields['day'].initial = today.strftime('%A')

        assistants = Worker.objects.values_list('name', flat=True).distinct()
        self.fields['assistant'].choices = [(a, a) for a in assistants if a]


from django import forms
from .models import FountainRecords
import datetime

class FountainRecordsForm(forms.ModelForm):
    COUNT_CHOICES = [(i, str(i)) for i in range(1, 51)]

    car_count = forms.ChoiceField(
        initial=2,
        label='عدد السيارات',
        choices=COUNT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Liters = forms.IntegerField(
    #     initial=0,
    #     widget=forms.NumberInput(attrs={'class': 'form-control'})
    # )
    class Meta:
        model = FountainRecords
        fields = '__all__'
        widgets = {
            'day': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),

            'notes': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'day': 'اليوم',
            'date': 'التاريخ',
            'Liters': 'عدد الليترات',
            'car_count': 'عدد السيارات',
            'notes': 'ملاحظات',
        }

    def __init__(self, *args, **kwargs):
        super(FountainRecordsForm, self).__init__(*args, **kwargs)
        today = datetime.date.today()
        self.fields['date'].initial = today
        self.fields['day'].initial = today.strftime('%A')




class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={ 'class': 'form-control'}),
            'id_number': forms.NumberInput(attrs={'class': 'form-control'}),
        }

        labels = {
            'name': 'الاسم',
            'id_number': 'رقم الهوية',
        }


class InstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={ 'class': 'form-control'}),
        }
        labels = {
            'name': 'الاسم',
        }

class MaintenanceLocationForm(forms.ModelForm):
    class Meta:
        model = MaintenanceLocation
        fields = ['name']

class MainItemForm(forms.ModelForm):
    class Meta:
        model = MainItem
        fields = ['name']

class SubItemForm(forms.ModelForm):
    class Meta:
        model = SubItem
        fields = ['name']

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['name']


class MaintenanceForm(forms.ModelForm):
    class Meta:
        model = Maintenance
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control' }),
            'day': forms.TextInput(attrs={'class': 'form-control'}),
            'maintenance_location': forms.Select(attrs={'class': 'form-select'}),
            'main_item': forms.Select(attrs={'class': 'form-select'}),
            'sub_item': forms.Select(attrs={'class': 'form-select'}),
            'device': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }

        labels = {
            'date': 'التاريخ',
            'day': 'اليوم',
            'maintenance_location': 'مكان الصيانة',
            'main_item': 'البند الرئيسي',
            'sub_item': 'البند الفرعي',
            'device': 'الجهاز',
            'notes': 'ملاحظات',
            'amount': 'المبلغ',
        }
    def __init__(self, *args, **kwargs):
        super(MaintenanceForm, self).__init__(*args, **kwargs)
        today = datetime.date.today()
        self.fields['date'].initial = today
        self.fields['day'].initial = today.strftime('%A')



class Expenses_typeForm(forms.ModelForm):
    class Meta:
        model = Expenses_type
        fields = ['name']

class place_ExpensesForm(forms.ModelForm):
    class Meta:
        model = Place_Expenses
        fields = ['name']

class ExpensesFrom(forms.ModelForm):
    class Meta:
        model = Expenses
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control' }),
            'day': forms.TextInput(attrs={'class': 'form-control'}),
            'palce': forms.Select(attrs={'class': 'form-select'}),
            'expenses_type': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-select'}),
            'notes': forms.TextInput(attrs={'class': 'form-select'}),
   }

        labels = {
            'date': 'التاريخ',
            'day': 'اليوم',
            'palce': 'مكان الصرف',
            'expenses_type': 'نوع المصروف ',
            'notes': 'ملاحظات',
            'amount': 'المبلغ',
        }
    def __init__(self, *args, **kwargs):
        super(ExpensesFrom, self).__init__(*args, **kwargs)
        today = datetime.date.today()
        self.fields['date'].initial = today
        self.fields['day'].initial = today.strftime('%A')


class VehicleFuelRecordForm(forms.ModelForm):
    class Meta:
        model = VehicleFuelRecord
        fields = [
            'date',
            'driver',
            'fuel_quantity',
            'odometer_before',
            'odometer_after',
            'notes',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'driver': forms.Select(attrs={'class': 'form-control'}),
            'fuel_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'كمية السولار'}),
            'odometer_before': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'قراءة العداد قبل'}),
            'odometer_after': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'قراءة العداد بعد'}),
            'notes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ملاحظات اختيارية'}),
        }
        labels = {
            'date': 'التاريخ',
            'driver': 'اسم السائق',
            'fuel_quantity': 'كمية السولار',
            'odometer_before': 'قراءة العداد قبل',
            'odometer_after': 'قراءة العداد بعد',
            'notes': 'ملاحظات',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['driver'].empty_label = "اختر السائق"

    def clean(self):
        cleaned_data = super().clean()
        odometer_before = cleaned_data.get('odometer_before')
        odometer_after = cleaned_data.get('odometer_after')

        if odometer_before is not None and odometer_after is not None:
            if odometer_after < odometer_before:
                self.add_error('odometer_after', 'قراءة العداد بعد يجب أن تكون أكبر من أو تساوي قراءة العداد قبل')

        return cleaned_data