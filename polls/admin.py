# standard libraries
from django.contrib import admin
# local libraries
from .models import Question, Choice

admin.site.register(Question)
admin.site.register(Choice)
