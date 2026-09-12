from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "session",
        "rating",
        "would_recommend",
        "created_at",
    )

    list_filter = (
        "rating",
        "would_recommend",
        "created_at",
    )

    search_fields = (
        "comment",
        "session__customer_name",
        "session__table__table_number",
    )

    readonly_fields = (
        "created_at",
    )