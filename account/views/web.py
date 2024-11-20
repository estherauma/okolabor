from django.shortcuts import render
from django.views import View
from account.models import User


# create a class based view to display users
class UserListView(View):
    def get(self, request):
        users = User.objects.filter(groups__name='recruiter')
        pending = User.objects.filter(
            is_active=False,
            groups__name='recruiter')
        context = {'users': users, 'pending_users': pending}
        return render(request, 'recruiter/manage_users.html', context)
    
