from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_griot', 'reputation_score', 'location', 'created_at')
    list_filter = ('is_griot',)
    search_fields = ('user__username', 'user__email', 'location')
    readonly_fields = ('created_at',)

    # Griot promotion is intentionally manual at MVP (TSD Section 12 / 16
    # Architect's Note): this is the one and only place that flag gets flipped.
    fields = ('user', 'is_griot', 'reputation_score', 'bio', 'avatar', 'location', 'created_at')
