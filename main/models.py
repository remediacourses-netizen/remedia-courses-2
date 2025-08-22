# main/models.py
from django.db import models
from django.conf import settings  # используем кастомную модель пользователя
from accounts.models import Subject
import re
from config.storages import GoogleDriveStorage




# 1️⃣ Модель Модуля — теперь привязана к Subject
class Module(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Курс')

    def __str__(self):
        return f'{self.title}'
    class Meta:
        verbose_name_plural = "Модули"   

# 2️⃣ Обновляем Lesson: теперь урок привязан к Module
class Lesson(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    video_url = models.URLField(blank=True, verbose_name='Ссылка на видео')
    task_url = models.URLField(blank=True, verbose_name='Ссылка на практические задания')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, verbose_name='Модуль')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Курс')

    def __str__(self):
        return self.title

    def get_embed_url(self):
        # Для ссылок вида https://www.youtube.com/watch?v=VIDEO_ID
        match_watch = re.match(r".*youtube\.com/watch\?v=([a-zA-Z0-9_-]+)", self.video_url)
        if match_watch:
            video_id = match_watch.group(1)
            return f"https://www.youtube.com/embed/{video_id}"

        # Для коротких ссылок вида https://youtu.be/VIDEO_ID
        match_short = re.match(r".*youtu\.be/([a-zA-Z0-9_-]+)", self.video_url)
        if match_short:
            video_id = match_short.group(1)
            return f"https://www.youtube.com/embed/{video_id}"

        # Если ничего не подошло — возвращаем как есть
        return self.video_url
    class Meta:
        verbose_name = "Урок"            # ← это для единственного числа
        verbose_name_plural = "Уроки"

gd_storage = GoogleDriveStorage()
class LessonTaskFile(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='task_files')
    file = models.FileField(upload_to='lesson_tasks/', storage=gd_storage, verbose_name='Прикрепите файлы домашней работы')
    def __str__(self):
        return str(self.file) if self.file else "Файл не загружен"
    class Meta:
        verbose_name = 'Файл домашней работы'
        verbose_name_plural = 'Файлы домашней работы'
    
# main/models.py
gd_storage = GoogleDriveStorage()
class HomeworkSubmission(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='Урок')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Ученик')
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='checked_homeworks',
        verbose_name='Учитель'
    )
    answer = models.TextField(blank=True, verbose_name='Ответ')  # <-- важно!
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время')
    file = models.FileField(upload_to='homework/', storage=gd_storage, null=False, default='default.pdf', verbose_name='Файл')
    comment = models.TextField(blank=True, verbose_name='Комментарий учителя')
    checked = models.BooleanField(default=False, verbose_name='Проверен: да/нет')
    

    def save(self, *args, **kwargs):
        # Автоматически определяем учителя по предмету
        if not self.teacher:
            student_profile = self.student
            lesson_subject = self.lesson.subject
            self.teacher = student_profile.get_teacher_for_subject(lesson_subject)
        super().save(*args, **kwargs)
    class Meta:
        verbose_name_plural = "Домашние работы"           

gd_storage = GoogleDriveStorage()
class Blogs(models.Model):
    title=models.CharField(max_length=255, verbose_name='Название',  blank=False)
    photo=models.ImageField(upload_to= 'blogs_image/', storage=gd_storage, verbose_name='Фотка',blank=True)
    main_text=models.TextField(blank=True, verbose_name='Главный текст')
    file = models.FileField(upload_to='blogs_file/', storage=gd_storage, null=False, verbose_name='Файл(необязательно)',blank=True)
    def __str__(self):
        return self.title
    class Meta:
        verbose_name_plural = "Блоги"  

class AboutCourses(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Курс')
    description = models.TextField(blank=True, verbose_name='Описание')
    def __str__(self):
        return str(self.subject)
    class Meta:
        verbose_name_plural = "Описание курсов"




class Library(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Курс')
    title = models.CharField(max_length=255, verbose_name='Название', blank=True)
    author = models.CharField(max_length=255, verbose_name='Автор', blank=True)

    def __str__(self):
        return self.title  # лучше выводить название книги, а не курс

    class Meta:
        verbose_name_plural = "Библиотека"

gd_storage = GoogleDriveStorage()
class LibraryFile(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='files', verbose_name='Книга')
    file = models.FileField(upload_to='library_files/', storage=gd_storage, verbose_name='Прикрепите файлы книг')

    def __str__(self):
        return self.file.name

    class Meta:
        verbose_name = 'Файл книги'
        verbose_name_plural = 'Файлы книг'


# Create your models here.
