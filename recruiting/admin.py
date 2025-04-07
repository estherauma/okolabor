from django.contrib import admin

from recruiting.models import Employer, Hours, Role, Wages, WorkRequests,EmployerRecruiter,WorkAssignment,EmployerContact

# Register your models here.
admin.site.register(Employer)
admin.site.register(Role)
admin.site.register(Hours)
admin.site.register(Wages)
admin.site.register(EmployerRecruiter)
admin.site.register(WorkRequests)
admin.site.register(WorkAssignment)
admin.site.register(EmployerContact)
