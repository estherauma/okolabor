from django.contrib import admin

from recruiting.models import Employer, Hours, Role, Wages, WorkRequests,WorkAssignment

# Register your models here.
admin.site.register(Employer)
admin.site.register(Role)
admin.site.register(Hours)
admin.site.register(Wages)


@admin.register(WorkRequests)
class WorkRequestsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'created_at')  # Adjust fields as per your model
    search_fields = ('name', 'status')  # Enables search functionality
    list_filter = ('status',)  # Adds filter options in the admin panel
    ordering = ('-created_at',)  # Orders by most recent
    list_per_page = 20  # Limits number of records per page

@admin.register(WorkAssignment)
class WorkAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'worker', 'display_work_requests', 'status', 'assigned_date')
    search_fields = ('worker__first_name', 'worker__last_name', 'status')
    list_filter = ('status',)
    ordering = ('-assigned_date',)

    def display_work_requests(self, obj):
        return ", ".join([wr.name for wr in obj.work_request.all()])
    display_work_requests.short_description = "Work Requests"
