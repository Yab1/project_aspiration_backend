from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ["author", "created_at"]
    readonly_fields = ["created_at", "updated_at"]
