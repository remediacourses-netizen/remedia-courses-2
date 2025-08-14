from django import forms
from .models import CustomUser, Subject, UserSubject
from django.contrib.auth.models import User

class CustomUserStep1Form(forms.ModelForm):
    ROLE_CHOICES = (
        ('student', 'Ученик'),
        ('teacher', 'Преподаватель'),
    )
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect, label='Роль')

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username')
        labels = {
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'username': 'Логин',
    }
        

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        role = self.cleaned_data.get('role')
        if role == 'student':
            user.is_student = True
        elif role == 'teacher':
            user.is_teacher = True
        if commit:
            user.save()
        return user



class CustomLoginForm(forms.Form):
    username = forms.CharField(label="Логин")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)


class SubjectSelectionForm(forms.Form):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Выберите предметы',
        help_text='Вы можете выбрать несколько предметов'
    )

class TeacherSelectionForm(forms.Form):
    # динамически в __init__ добавляем по каждому предмету поле teacher_<id>
    def __init__(self, *args, subjects=None, **kwargs):
        super().__init__(*args, **kwargs)
        if subjects:
            from .models import CustomUser
            for subj in subjects:
                qs = CustomUser.objects.filter(
                    is_teacher=True,
                    usersubject__subject=subj,
                    usersubject__role='teacher'
                ).distinct()
                self.fields[f'teacher_{subj.id}'] = forms.ModelChoiceField(
                    queryset=qs,
                    label=f'Преподаватель по «{subj.name}»',
                    required=True,
                )



class CustomUserAdminForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 
                 'is_teacher', 'is_student', 'subjects_taught',
                 'is_staff', 'is_superuser')  # Добавлены ключевые поля
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'Логин',
            'email': 'Email',
            'subjects_taught': 'Предметы, которые преподаёт',
            'is_teacher': 'Преподаватель',
            'is_student': 'Ученик',
            'is_staff': 'Доступ в админку',
            'is_superuser': 'Суперпользователь',
        }
        widgets = {
            'password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Условное отображение поля subjects_taught
        if 'is_teacher' in self.fields and 'subjects_taught' in self.fields:
            if not self.instance.is_teacher:
                self.fields['subjects_taught'].widget = forms.HiddenInput()
            else:
                self.fields['subjects_taught'].widget = forms.SelectMultiple()






class UserSubjectAdminForm(forms.ModelForm):
    class Meta:
        model = UserSubject
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Только студенты в поле user
        students_qs = CustomUser.objects.filter(is_student=True)
        self.fields['user'].queryset = students_qs
        self.fields['user'].label_from_instance = lambda obj: f"{obj.last_name} {obj.first_name}"

        # Все учителя в поле teacher (будут фильтроваться JS)
        teachers_qs = CustomUser.objects.filter(is_teacher=True)
        self.fields['teacher'].queryset = teachers_qs
        self.fields['teacher'].label_from_instance = lambda obj: f"{obj.last_name} {obj.first_name}"


    
