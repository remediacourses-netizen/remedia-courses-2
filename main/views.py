# main/views.py
# main/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from .models import Lesson, HomeworkSubmission,  Module, Blogs, AboutCourses, Library
from django.conf import settings
from accounts.models import CustomUser, UserSubject, Subject
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator


def home(request):
    return render(request, 'main/home.html')

def about(request):
    return render(request, 'main/about.html')

@login_required
def modules(request):
    if request.user.profile.role == 'teacher':
        return render(request, 'main/modules_teacher.html')
    else:
        return render(request, 'main/modules_student.html')

@login_required
def library_subject_list(request):
    """Показывает список предметов, к которым есть доступ в библиотеке"""
    if request.user.is_student:
        user_subjects = UserSubject.objects.filter(user=request.user)
        subjects = [us.subject for us in user_subjects]
    else:
        subjects = Subject.objects.all()  # если надо, чтобы учителя видели всё
    return render(request, 'main/library_subject_list.html', {'subjects': subjects})


@login_required
def library_by_subject(request, subject_id):
    """Показывает материалы библиотеки по выбранному предмету"""
    subject = get_object_or_404(Subject, id=subject_id)
    materials = Library.objects.filter(subject=subject).select_related('subject').prefetch_related('files')
    return render(request, 'main/library_by_subject.html', {
        'subject': subject,
        'materials': materials
    })



def blog(request):
    blog = Blogs.objects.all().order_by('-id')
    paginator = Paginator(blog, 4)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/blog.html', {
    'page_obj': page_obj
})

def about_courses(request):
    info=AboutCourses.objects.all().order_by('id')
    paginator = Paginator(info, 4)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'main/about_courses.html', {
    'page_obj': page_obj
})




@login_required
def modules(request):
    user = request.user

    if user.is_teacher:
        # получаем студентов, у которых он указан как преподаватель
        student_links = UserSubject.objects.filter(teacher=user, role='student')
        student_ids = student_links.values_list('user_id', flat=True)

        # Получаем все ДЗ только от этих учеников
        submissions = HomeworkSubmission.objects.filter(
            student_id__in=student_ids
        ).select_related('lesson', 'student').order_by('-submitted_at')

        return render(request, 'main/modules_teacher.html', {
            'submissions': submissions
        })

    elif user.is_student:
        subject_links = UserSubject.objects.filter(user=user, role='student').values_list('subject_id', flat=True)

    # Ищем уроки, где subject — это ForeignKey, фильтруем по subject_id
        lessons = Lesson.objects.filter(subject_id__in=subject_links).order_by('-id')

        return render(request, 'main/modules_student.html', {
        'lessons': lessons
    })



        

    else:
        return HttpResponse("Неизвестная роль пользователя", status=403)


@login_required
def submit_homework(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)

    if request.method == 'POST':
        # Проверяем, что пользователь действительно студент
        if not request.user.is_student:
            messages.error(request, "Только студенты могут отправлять домашние задания.")
            return redirect('lesson_detail', lesson_id=lesson.id)

        # Находим учителя, к которому прикреплён ученик по этому предмету
        try:
            link = UserSubject.objects.get(user=request.user, subject=lesson.subject)
            teacher = link.teacher
        except UserSubject.DoesNotExist:
            messages.error(request, "Вы не прикреплены к преподавателю по этому предмету.")
            return redirect('lesson_detail', lesson_id=lesson.id)

        answer = request.POST.get('answer')
        file = request.FILES.get('file')

        HomeworkSubmission.objects.create(
            student=request.user,
            lesson=lesson,
            teacher=teacher,
            answer=answer,
            file=file
        )

        messages.success(request, "Домашка успешно отправлена!")
        return redirect('lesson_detail', lesson_id=lesson.id)

    return redirect('lesson_detail', lesson_id=lesson.id)





@login_required
def check_homework(request, submission_id):
    submission = get_object_or_404(
        HomeworkSubmission,
        id=submission_id,
        teacher=request.user
    )
    return render(request, 'main/check_homework.html', {'submission': submission})




@require_POST
@login_required
def submit_homework_check(request, submission_id):
    submission = get_object_or_404(
        HomeworkSubmission,
        id=submission_id,
        teacher=request.user
    )
    submission.comment = request.POST.get('comment', '')
    submission.checked = True
    submission.save()
    messages.success(request, 'Домашка проверена!')
    list(messages.get_messages(request))
    return redirect('teacher_homework_list')

@login_required
def teacher_homework_list(request):
    if not request.user.is_teacher:
        return redirect('modules')   # сюда попадут все, кто не преподаватель

    submissions = HomeworkSubmission.objects.filter(
        teacher=request.user
    ).select_related('lesson', 'student').order_by('-submitted_at')

    return render(request, 'main/modules_teacher.html', {
        'submissions': submissions
    })


@login_required
def my_submissions(request):
    user = request.user  # Обязательно первым делом определить user
    print(f"User: {user.username}, is_student: {user.is_student}, is_teacher: {user.is_teacher}")

    if user.is_student:
        submissions = HomeworkSubmission.objects.filter(student=user).select_related('lesson')
        return render(request, 'main/my_submissions.html', {
            'submissions': submissions
        })
    else:
        return HttpResponse("У вас нет доступа к этой странице.", status=403)


def subject_list(request):
    if request.user.is_student:
        user_subjects = UserSubject.objects.filter(user=request.user)
        subjects = [us.subject for us in user_subjects]
    return render(request, 'main/subject_list.html', {'subjects': subjects})



def module_list(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    modules = Module.objects.filter(subject=subject)
    return render(request, 'main/module_list.html', {
        'subject': subject,
        'modules': modules
    })


def lesson_list(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    lessons = Lesson.objects.filter(module=module)
    return render(request, 'main/lesson_list.html', {
        'module': module,
        'lessons': lessons
    })




@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    user = request.user

    if user.is_student:
        # Проверяем, связан ли студент с этим предметом
        if not UserSubject.objects.filter(user=user, subject=lesson.subject).exists():
            return render(request, 'access_denied.html')

    elif user.is_teacher:
        # Проверяем, действительно ли преподаватель преподаёт этот предмет
        if not user.subjects_taught.filter(id=lesson.subject.id).exists():
            return HttpResponse("У вас нет доступа к этой странице.", status=403)

    else:
        return HttpResponse("У вас нет доступа к этой странице.", status=403)

    return render(request, 'main/lesson_detail.html', {'lesson': lesson})

