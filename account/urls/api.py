from django.urls import path, re_path
from account.views.api import RegisterView, LoginView, ResetAccountProfile, UserPreferencesUpdateView, UserWorkExperienceView

app_name = 'account'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='api-register'),
    path('login', LoginView.as_view(), name='api-login'),
    re_path(r'(?P<user_id>[-\w]+)/preferences/$', UserPreferencesUpdateView.as_view(), name='update-user-preferences'),
    re_path(r'(?P<user_id>[-\w]+)/work-experience/$', UserWorkExperienceView.as_view(), name='api-work-experience'),
    re_path(r'(?P<user_id>[-\w]+)/reset-profile/$', ResetAccountProfile.as_view(), name='reset-profile'),
]
