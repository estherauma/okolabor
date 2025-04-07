from django.contrib import admin

from recruiting.models import Organization, Hours, Role, Wages, WorkRequests,EmployerRecruiter,WorkAssignment

# Register your models here.
admin.site.register(Organization)
admin.site.register(Role)
admin.site.register(Hours)
admin.site.register(Wages)
admin.site.register(EmployerRecruiter)
admin.site.register(WorkRequests)
admin.site.register(WorkAssignment)
