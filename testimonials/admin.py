# testimonials/admin.py

from django.contrib import admin
from django.utils.safestring import mark_safe   # ← import mark_safe here
from .models import Testimonial

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "role",
        "rating",
    )
    search_fields = ("name", "role", "quote")
    list_filter = ("rating",)
    readonly_fields = ("avatar_preview",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "role",
                    "avatar_url",
                    "avatar_preview",
                    "quote",
                    "rating",
                )
            },
        ),
    )

    def avatar_preview(self, obj):
        if obj.avatar_url:
            # Render a small circular image if avatar_url is set
            return mark_safe(
                f'<img src="{obj.avatar_url}" '
                f'style="height:50px; width:50px; border-radius:50%; object-fit:cover;" />'
            )
        return "(No avatar)"

    avatar_preview.short_description = "Avatar Preview"
