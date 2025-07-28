from django.contrib import admin
from .models import Course, Category, Tag ,Lesson,Assignment,AssignmentSubmission

admin.site.register(Course)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(Lesson)
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)

# @admin.register(Course)
# class CourseAdmin(admin.ModelAdmin):
#     list_display = ('title', 'category', 'instructor', 'created_by_employee', 'created_at')
#     list_filter = ('category', 'tags', 'created_at')
#     search_fields = ('title', 'description')

# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('name',)
#     search_fields = ('name',)

# @admin.register(Tag)
# class TagAdmin(admin.ModelAdmin):
#     list_display = ('name',)
#     search_fields = ('name',)
