from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):

    
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Логин обязателен')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название курса')

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Курсы"
    
class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Текущие поля
    is_student = models.BooleanField(default=False, verbose_name='Он/она студент')
    is_teacher = models.BooleanField(default=False, verbose_name='Он/она учитель')
    username = models.CharField(max_length=150, unique=True, null=False, blank=False, verbose_name='Логин')
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # 🔻 Новые поля
    subjects_taught = models.ManyToManyField(Subject, blank=True, related_name='teachers', verbose_name='Предметы, которые он/она будет преподавать')
    subjects = models.ManyToManyField(Subject, blank=True, help_text="Предметы, которые изучает или преподаёт пользователь")
    teachers = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='students', help_text="Учителя, выбранные учеником")

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()
    def mark_as_student(self):
        self.is_student = True
        self.is_teacher = False
        self.save()

    def mark_as_teacher(self):
        self.is_teacher = True
        self.is_student = False
        self.save()

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or None

    def get_teacher_for_subject(self, subject):
        """
        Найти учителя по предмету из тех, кого выбрал ученик
        """
        for teacher in self.teachers.all():
            if subject in teacher.subjects.all():
                return teacher
        return None

    def __str__(self):
        return self.username or "(без логина)"
    
    class Meta:
        verbose_name_plural = "Пользователи"



class UserSubject(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Ученик')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Курс')
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_students',
        verbose_name='Преподаватель'
    )

    def __str__(self):
        if self.user.is_student:
            return f"{self.user.get_full_name()} → {self.subject} (преп: {self.teacher.get_full_name() if self.teacher else 'не назначен'})"
        else:
            return f"{self.user.get_full_name()} → {self.subject} (как преподаватель)"
        
    class Meta:
        verbose_name_plural = "Связь ученик➡️учитель"

# Create your models here.
