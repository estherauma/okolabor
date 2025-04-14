# from django.db.models.signals import post_save, m2m_changed
# from django.dispatch import receiver
# from django.contrib.auth.models import Group
# from recruiting.models import EmployerRecruiterOrgLink, EmployerRecruiter
# from django.contrib.auth import get_user_model

# User = get_user_model()

# @receiver(m2m_changed, sender=User.organizations.through)
# def recruiter_added_to_organization(sender, instance, action, pk_set, **kwargs):
#     if action == 'post_add':
#         user = instance
#         if user.groups.filter(name='recruiter').exists():
#             for org_id in pk_set:
                
#                 employer_links = EmployerRecruiterOrgLink.objects.filter(
#                     recruiter_org_id=org_id
#                 )
#                 for link in employer_links:
#                     EmployerRecruiter.objects.get_or_create(
#                         recruiter=user,
#                         employer=link.employer_org
#                     )
