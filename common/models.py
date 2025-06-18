from common.push_id import push_id
from django.db import models
from common.middleware import get_current_user
from django.utils import timezone


class BaseModel(models.Model):
    '''Base model'''
    id = models.CharField(max_length=20, primary_key=True,
                          default=push_id)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True


class AuditableModel(BaseModel):
    ''' Auditable base model '''
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_by = models.CharField(max_length=256, null=True, blank=True)
    updated_by = models.CharField(max_length=256, null=True, blank=True)
    deleted_by = models.CharField(max_length=256, null=True, blank=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
              
    def save(self, *args, **kwargs):
        user = get_current_user()
        user_id = getattr(user, 'id', None)

        if self._state.adding and user_id:
            self.created_by = user_id
            self.updated_by = user_id 
        elif user_id:
            self.updated_by = user_id
        
        super().save(*args, **kwargs)


    def delete(self, *args, user=None, **kwargs):
        if user is None:
            user = get_current_user()
        user_id = getattr(user, 'id', None)
        
        if user_id:
            self.deleted_by = user_id
        
        self.deleted = True
        self.deleted_at = timezone.now()

        self.save(update_fields=['deleted', 'deleted_by', 'deleted_at'])  # explicitly save only updated fields

    def hard_delete(self, *args, **kwargs):
        """Hard delete — permanently removes the record"""
        print(f'Hard deleting object: {self.pk}')
        super().delete(*args, **kwargs)



auditable_fields = [
    'created_at',
    'updated_at',
    'deleted_at',
    'created_by',
    'updated_by',
    'deleted_by',
    'deleted',
]


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)