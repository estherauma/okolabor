from django.urls import path, re_path
from account.models import UserCropExperience
from account.views.api import (
    RegisterView, LoginView, ResetAccountProfile, UserCropExperienceView,
    UserDocumentDetailsView,
    UserPreferencesUpdateView, UserReportProblem, UserWorkExperienceDetailsView, UserWorkExperienceView,
    GetOTP, VerifyOTP,
    RegisterView, LoginView, ResetAccountProfile, UserDocumentDetailsView,
    UserDocumentsView, UserPreferencesUpdateView, UserWorkExperienceView
)

app_name = 'account'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='api-register'),
    path('login', LoginView.as_view(), name='api-login'),
    re_path(
        r'(?P<user_id>[-\w]+)/preferences/$',
        UserPreferencesUpdateView.as_view(), name='update-user-preferences'),
    # re_path(
    #     r'(?P<user_id>[-\w]+)/work-experience/$',
    #     UserWorkExperienceView.as_view(), name='api-work-experience'),
    re_path(
        r'(?P<user_id>[-\w]+)/reset-profile/$',
        ResetAccountProfile.as_view(), name='reset-profile'),
    re_path(
        r'(?P<user_id>[-\w]+)/preferences/$',
        UserPreferencesUpdateView.as_view(),
        name='update-user-preferences'
    ),
    re_path(
        r'(?P<user_id>[-\w]+)/work-experience/$',
        UserWorkExperienceView.as_view(),
        name='api-work-experience'
    ),
    re_path(
        r'(?P<user_id>[-\w]+)/work-experience/(?P<experience_id>[-\w]+)/$',
        UserWorkExperienceDetailsView.as_view(),
        name='api-single-experience'
    ),
    re_path(
        r'(?P<user_id>[-\w]+)/documents/$',
        UserDocumentsView.as_view(),
        name='api-documents'
    ),
    re_path(
        r'(?P<document_id>[-\w]+)/document/$',
        UserDocumentDetailsView.as_view(),
        name='api-single-document'
    ),
    path('otp-generate/', GetOTP.as_view(), name='otp-generate'),
    path('otp-verify/', VerifyOTP.as_view(), name='otp-verify'),
    re_path(
        r'(?P<user_id>[-\w]+)/crop-experience/$',
        UserCropExperienceView.as_view(),
        name='api-crop-experience'
    ),
    re_path(
        r'(?P<user_id>[-\w]+)/report-problem/$',
        UserReportProblem.as_view(),
        name='api-report-problem'
    ),
]
