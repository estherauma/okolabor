from django.contrib import admin

from account.models import (
    LoginEvent, User, UserActivityLog, UserDocuments, 
    UserJobExperienceDetails, UserNotification, UserPreference,
    UserWorkExperience, UserWorkExperienceDocuments, UserJobExperience,
    Log
)

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('curp','email', 'first_name', 'last_name', 'is_active', 'created_at')
    ordering = ('-created_at',)

admin.site.register(UserDocuments)
@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'kind', 'key', 'value', 'created_at')
    ordering = ('-created_at',) 
admin.site.register(UserWorkExperience)
admin.site.register(UserWorkExperienceDocuments)
admin.site.register(UserJobExperience)
admin.site.register(UserJobExperienceDetails)
@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'category', 'created_at', 'message', 'status')
    ordering = ('-created_at',)
admin.site.register(UserActivityLog)
admin.site.register(LoginEvent)
admin.site.register(Log)
