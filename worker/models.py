from django.db import models
from account.models import User
from common.models import AuditableModel


class UserPreferences(AuditableModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=256, null=False, blank=False)
    value = models.CharField(max_length=256, null=False, blank=False)

    def __str__(self):
        return f'{self.user.curp} - {self.key}'

    class Meta:
        db_table = 'user_preferences'
