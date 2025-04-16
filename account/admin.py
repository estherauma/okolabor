from django.contrib import admin

from account.models import (
    LoginEvent, User, UserActivityLog, UserDocuments, UserJobExperienceDetails, UserNotification, UserPreference, UserWorkExperience,
    UserWorkExperienceDocuments, UserJobExperience, UserReportedProblem,Log
)

# Register your models here.
admin.site.register(User)
admin.site.register(UserDocuments)
admin.site.register(UserPreference)
admin.site.register(UserWorkExperience)
admin.site.register(UserWorkExperienceDocuments)
admin.site.register(UserJobExperience)
admin.site.register(UserJobExperienceDetails)
admin.site.register(UserReportedProblem)
admin.site.register(UserNotification)
admin.site.register(UserActivityLog)
admin.site.register(LoginEvent)
admin.site.register(Log)