# main/admin.py

from django.contrib import admin
from .models import Lesson, HomeworkSubmission, Module, LessonTaskFile, Blogs, AboutCourses, Library, LibraryFile
from accounts.models import Subject
# Inline уроков для Module
# Inline уроков для Module
class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    show_change_link = True
    fields = ('title', 'video_url')

# Inline модулей для Subject
class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    show_change_link = True
    fields = ('title', 'description')

# Админка предметов (Subject)
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name']

# Админка модулей
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject']


class LessonTaskFileInline(admin.TabularInline):
    model = LessonTaskFile
    extra = 1

    
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'module', 'task_url')
    inlines = [LessonTaskFileInline]
    list_filter = ('subject', 'module')
    search_fields = ('title',)
    fields = ('title', 'subject', 'module', 'video_url', 'task_url')  # показываем в форме редактирования
    raw_id_fields = ()

@admin.register(HomeworkSubmission)
class HomeworkSubmissionAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'get_student_name', 'submitted_at', 'checked')
    list_filter = ('checked',)
    search_fields = ('student__first_name', 'student__last_name', 'lesson__title')

    def get_student_name(self, obj):
        return obj.student.get_full_name()
    get_student_name.short_description = 'Ученик'

@admin.register(Blogs)
class BlogsAdmin(admin.ModelAdmin):
    list_display = ('title', 'photo', 'short_main_text', 'file' )
    def short_main_text(self, obj):
        return (obj.main_text[:75] + '...') if len(obj.main_text) > 75 else obj.main_text
    short_main_text.short_description = 'Главный текст'

@admin.register(AboutCourses)
class AboutCoursesAdmin(admin.ModelAdmin):
    list_display = ('subject', 'short_description')
    def short_description(self, obj):
        return (obj.description[:75] + '...') if len(obj.description) > 75 else obj.description
    short_description.short_description = 'Описание'

class LibraryFileInline(admin.TabularInline):
    model = LibraryFile
    extra = 1


@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'subject')
    inlines = [LibraryFileInline]
    list_filter = ('subject', 'author')
    search_fields = ('title', 'author')
# Register your models here.
