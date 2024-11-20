from django.shortcuts import render
from django.views import View
from account.models import User


class UserListView(View):
    def get(self, request):
        users = User.objects.filter(groups__name='recruiter')
        pending = User.objects.filter(
            is_active=False,
            groups__name='recruiter')
        context = {'users': users, 'pending_users': pending}
        return render(request, 'recruiter/manage_users.html', context)


class UserActivitLogView(View):
    def get(self, request):
        user = User.objects.get(pk=request.user.id)
        logs = user.audit_logs.all()
        context = {'logs': logs, 'user': user}
        return render(request, 'activity_log.html', context)    
