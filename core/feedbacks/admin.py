from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ["id", "author", "created_at"]
    readonly_fields = [
        "digital_signature",
        "public_key",
        "created_at",
        "updated_at",
    ]
    ordering = ["-created_at"]
