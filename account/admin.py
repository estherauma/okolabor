from django.contrib import admin

from account.models import (
    User, UserDocuments, UserPreference, UserWorkExperience, UserWorkExperienceDocuments, UserCropExperience, UserReportedProblem
)

# Register your models here.
admin.site.register(User)
admin.site.register(UserDocuments)
admin.site.register(UserPreference)
admin.site.register(UserWorkExperience)
admin.site.register(UserWorkExperienceDocuments)
admin.site.register(UserCropExperience)
admin.site.register(UserReportedProblem)
