# standard libraries
import datetime
# standard libraries
from django.contrib import admin
from django.utils import timezone
# local libraries
from .models import Question, Choice


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class RecentFilter(admin.SimpleListFilter):
    title = 'recently published'
    parameter_name = 'published'

    def lookups(self, request, model_admin):
        return (
            ('recently', 'Published Recently'),
            ('not_recently', 'Dont\'t Published Recently'),
            ('future', 'Published In The Future')
        )

    def queryset(self, request, queryset):
        one_day_ago = timezone.now() - datetime.timedelta(days=1)
        if self.value() == 'recently':
            return queryset.filter(
                published_date__lte=timezone.now(),
                published_date__gte=one_day_ago
            )
        if self.value() == 'not_recently':
            return queryset.filter(
                published_date__lt=one_day_ago
            )
        if self.value() == 'future':
            return queryset.filter(
                published_date__gt=timezone.now()
            )


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None, {
                'fields': ['question_text']
            }
        ),
        (
            'Date Information', {
                'fields': ['published_date']
            }
        )
    ]
    inlines = [ChoiceInline]
    list_display = (
        'question_text', 'id',
        'published_date', 'was_published_recently'
    )
    list_filter = ['published_date', RecentFilter]
    search_fields = ['question_text']


admin.site.register(Question, QuestionAdmin)
