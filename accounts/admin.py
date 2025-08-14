from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserSubject
from .forms import CustomUserAdminForm
from .forms import UserSubjectAdminForm
from django.urls import path
from django.http import JsonResponse
@admin.register(CustomUser)

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    form = CustomUserAdminForm

    list_display = ('username', 'first_name', 'last_name', 'is_teacher', 'is_student', 'is_staff')
    ordering = ('username',)
    search_fields = ('username', 'first_name', 'last_name')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Личная информация', {'fields': ('first_name', 'last_name', 'subjects_taught')}),
        ('Роли', {'fields': ('is_teacher', 'is_student')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'password1', 'password2',
                       'is_teacher', 'is_student', 'subjects_taught'),
         }),
    )


    filter_horizontal = ('groups', 'user_permissions',)

    class Media:
        js = ('accounts/js/custom_user_admin.js',)  # Подключаем JS файл для скрытия/показа поля



@admin.register(UserSubject)
class UserSubjectAdmin(admin.ModelAdmin):
    form = UserSubjectAdminForm

    class Media:
        js = ('accounts/admin/js/filter_teachers.js',)  # подключаем JS

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('get_teachers/<int:subject_id>/', self.admin_site.admin_view(self.get_teachers), name='usersubject_get_teachers'),
        ]
        return custom_urls + urls

    def get_teachers(self, request, subject_id):
        print(f'get_teachers called for subject_id={subject_id}')
        teachers = CustomUser.objects.filter(is_teacher=True, subjects_taught__id=subject_id).order_by('last_name', 'first_name')
        data = [{'id': t.id, 'name': f'{t.last_name} {t.first_name}'} for t in teachers]
        return JsonResponse(data, safe=False)

    

# Register your models here.
