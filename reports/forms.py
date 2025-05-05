import datetime

from django import forms
from .models import Worker,FuelTransaction,Driver,CarRecords,Institution\
    ,Maintenance,Place_Expenses,Expenses_type,\
    Expenses,MaintenanceLocation, MainItem, SubItem, Device

class AddWorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = ["name","id_number", "job", "start_date","salary"]
        fields = ["name","id_number", "job", "start_date","salary"]
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

        }
        labels = {
            'name':'اسم العامل',
            # 'user_name':'اسم المستخدم',
            # 'password':'كلمة السر',
            'id_number': 'رقم الهوية',
            'job':'طبيعة العمل',
            'start_date': 'بداية العمل',
            'salary': 'الراتب',
        }

        # def __init__(self, *args, **kwargs):
        #     super().__init__(*args, **kwargs)
        #     for field in self.fields.values():
        #         field.widget.attrs['class'] = 'form-control'

class FuelTransactionForm(forms.ModelForm):
    class Meta:
        model = FuelTransaction
        fields = ['fuel_type', 'date', 'type', 'quantity', 'price_per_liter','start_time','end_time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'fuel_type': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'كمية السولار'}),
            'price_per_liter': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'سعر اللتر'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),

        }
        labels = {
            'fuel_type': 'نوع السولار',
            'date': 'التاريخ',
            'type': 'نوع العملية',
            'quantity': 'عدد اللترات',
            'price_per_liter': 'سعر اللتر',
            'start_time': 'ساة التشغيل',
            'end_time': ' ساعة الايقاف',
        }


class CarRecordsForm(forms.ModelForm):
    COUNT_CHOICES = [(i, str(i)) for i in range(1, 51)]
    def clean_assistant(self):
        data = self.cleaned_data['assistant']
        return ', '.join(data)
    def clean_documented_for(self):
        data = self.cleaned_data['documented_for']
        return ', '.join(data)

    assistant = forms.MultipleChoiceField(
        choices=[],
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label='اسم مساعد السائق:'
    )
    documented_for = forms.MultipleChoiceField(
        choices=[],
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label='تم التوثيق لـ:'
    )
    car_count = forms.ChoiceField(choices=COUNT_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    documented_count = forms.ChoiceField(choices=COUNT_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
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
            'notes': '  ملاحظات: ',
        }

    def __init__(self, *args, **kwargs):
        super(CarRecordsForm, self).__init__(*args, **kwargs)
        today = datetime.date.today()
        self.fields['date'].initial = today
        self.fields['day'].initial = today.strftime('%A')

        assistants = Worker.objects.values_list('name', flat=True).distinct()
        self.fields['assistant'].choices = [(a, a) for a in assistants if a]

        documented_for = Institution.objects.values_list('name', flat=True).distinct()
        self.fields['documented_for'].choices = [(a, a) for a in documented_for if a]


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