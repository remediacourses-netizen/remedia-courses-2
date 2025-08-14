from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import CustomUserStep1Form, SubjectSelectionForm
from .models import CustomUser, Subject, UserSubject
from django.contrib.auth.decorators import login_required
from .forms import CustomLoginForm
from django.contrib.auth import authenticate, login
from .forms import EditUserForm
from django.views.decorators.http import require_POST
from django.http import JsonResponse

def register_step1(request):
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = CustomUserStep1Form(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = form.cleaned_data.get('role')

            # Установка флагов роли
            user.is_student = (role == 'student')
            user.is_teacher = (role == 'teacher')
            user.save()

            # Вызываем методы для меток, если нужно
            if user.is_student:
                user.mark_as_student()
            elif user.is_teacher:
                user.mark_as_teacher()

            # Сохраняем ID и роль в сессии
            request.session['new_user_id'] = user.id
            request.session['user_role'] = role

            return redirect('subject_selection')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = CustomUserStep1Form()

    return render(request, 'accounts/register_step1.html', {'form': form})


def subject_selection(request):
    if 'new_user_id' not in request.session:
        return redirect('register_step1')

    role = request.session['user_role']
    user = CustomUser.objects.get(id=request.session['new_user_id'])

    if request.method == 'POST':
        form = SubjectSelectionForm(request.POST)
        if form.is_valid():
            subject_ids = [s.id for s in form.cleaned_data['subjects']]
            request.session['selected_subjects'] = subject_ids

            if role == 'teacher':
                user.subjects_taught.set(subject_ids)  # Сохраняем преподавателю выбранные предметы
                login(request, user)
                return redirect('home')

            else:
                return redirect('teacher_selection')
    else:
        form = SubjectSelectionForm()

    return render(request, 'accounts/register_step2.html', {
        'form': form,
        'role': role,
    })


def teacher_selection(request):
    if 'new_user_id' not in request.session or 'selected_subjects' not in request.session:
        return redirect('register_step1')

    user = CustomUser.objects.get(id=request.session['new_user_id'])
    subject_ids = request.session['selected_subjects']
    subjects = Subject.objects.filter(id__in=subject_ids)

    errors = {}

    if request.method == 'POST':
        for subj in subjects:
            key = f'teacher_{subj.id}'
            tid = request.POST.get(key)
            if not tid:
                errors[subj.id] = 'Не выбран преподаватель'
            else:
                UserSubject.objects.create(
                    user=user,
                    subject=subj,
                    teacher_id=tid
                )

        if not errors:
            login(request, user)
            for k in ['new_user_id', 'selected_subjects', 'user_role']:
                request.session.pop(k, None)
            return redirect('home')

    subject_teachers = []
    for subj in subjects:
        teachers = CustomUser.objects.filter(
        is_teacher=True,
        subjects_taught=subj
    ).distinct()
        subject_teachers.append({
            'subject': subj,
            'teachers': teachers
        })

    return render(request, 'accounts/register_step3.html', {
        'subject_teachers': subject_teachers,
        'errors': errors,
    })

@login_required
def profile(request):
    user = request.user

    # Определение роли (лучше привести к machine-readable, например "student" / "teacher")
    if user.is_superuser:
        role = 'Админ'
    elif user.is_teacher:
        role = 'Преподаватель'
    elif user.is_student:
        role = 'Ученик'
    else:
        role = None

    subjects = []
    student_teachers = {}
    

    if role == 'Преподаватель':
        subjects = user.subjects_taught.all()

    elif role == 'Админ':
        subjects = ['Админские'] 

    elif role == 'Ученик':
        user_subjects = UserSubject.objects.filter(user=user).select_related('subject', 'teacher')
        subjects = [us.subject for us in user_subjects]

        # формируем {предмет: преподаватель}
        for us in user_subjects:
            student_teachers[us.subject.name] = us.teacher

    context = {
        'user': user,
        'role': role,
        'subjects': subjects,
        'student_teachers': student_teachers
    }
    return render(request, 'accounts/profile.html', context)


def custom_login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = CustomUser.objects.get(username=username)
                user = authenticate(request, username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('home')  # или куда хочешь после входа
                else:
                    form.add_error(None, 'Неверный пароль')
            except CustomUser.DoesNotExist:
                form.add_error('username', 'Пользователь с таким логином не найден')
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

from django.contrib.auth import logout
from django.shortcuts import redirect

@require_POST
def logout_view(request):
    logout(request)
    return redirect('login')




@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён.')
            # Не редиректим, просто рендерим ту же страницу
        else:
            messages.error(request, 'Проверьте правильность заполнения формы.')
    else:
        form = EditUserForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})



