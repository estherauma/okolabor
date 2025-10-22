from django.db.models.signals import post_save,post_delete
from django.dispatch import Signal, receiver
from account.models import User, UserDocuments, UserNotification, MessageRecipient
from common.cloud_vision import detect_text_in_image
from common.logger import AppLogger
from django.contrib.contenttypes.models import ContentType
from django.utils.functional import SimpleLazyObject
from account.models import Log
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model
from account.middleware import get_current_user
from datetime import datetime, date
import sys
from django.contrib.auth.models import AnonymousUser
import json
from django.db.models import Model, ManyToManyField, ForeignKey, OneToOneField
from datetime import datetime, date

User = get_user_model()

def serialize_instance(instance):
    data = {}

    for field in instance._meta.get_fields():
        try:
            value = getattr(instance, field.name)

            if isinstance(field, ManyToManyField):
                # Convert related objects to a list of string representations
                data[field.name] = [str(obj) for obj in value.all()]

            elif isinstance(field, (ForeignKey, OneToOneField)):
                # Store a string representation of related objects
                data[field.name] = str(value) if value else None

            elif isinstance(value, (datetime, date)):
                data[field.name] = value.isoformat()

            else:
                # Try to JSON serialize the value, else convert to string
                try:
                    json.dumps(value)
                    data[field.name] = value
                except TypeError:
                    data[field.name] = str(value)

        except Exception:
            # Safely handle missing or inaccessible fields
            data[field.name] = None

    return data

def is_migration_running():
    return any(cmd in sys.argv for cmd in ['makemigrations', 'migrate', 'test', 'collectstatic', 'flush', 'loaddata'])

def log_change(instance, action):
    content_type = ContentType.objects.get_for_model(instance)
    user = get_current_user()

    if isinstance(user, SimpleLazyObject):
        user = user._wrapped

    # Fallbacks: try instance fields like user/created_by/updated_by
    if not user or not getattr(user, 'is_authenticated', False):
        user = None
        for attr in ['user', 'created_by', 'updated_by']:
            possible_user = getattr(instance, attr, None)
            if getattr(possible_user, 'is_authenticated', False):
                user = possible_user
                break

    # Final fallback to first superuser (use with caution!)
    if user is None:
        user = User.objects.filter(is_superuser=True).first()

    if not user:
        return  # Don't log if no user is found

    object_id = str(instance.pk)
    data_before, data_after = None, None

    try:
        if action == 'Updated':
            old_instance = instance.__class__.objects.get(pk=instance.pk)
            data_before = serialize_instance(old_instance)
        elif action == 'Deleted':
            data_before = serialize_instance(instance)
        elif action == 'Created':
            data_after = serialize_instance(instance)
    except Exception as e:
        pass  # Silently ignore if any serialization issue

    # Avoid recursion
    post_save.disconnect(log_create_update, sender=Log)
    post_delete.disconnect(log_delete, sender=Log)

    try:
        Log.objects.create(
            user=user,
            content_type=content_type,
            object_id=object_id,
            action=action,
            data_before=data_before,
            data_after=data_after if data_after else serialize_instance(instance)
        )
    finally:
        # Reconnect signals
        post_save.connect(log_create_update, sender=Log)
        post_delete.connect(log_delete, sender=Log)

@receiver(post_save)
def log_create_update(sender, instance, created, **kwargs):
    if is_migration_running() or sender.__name__ == 'Log':
        return
    action = "Created" if created else "Updated"
    log_change(instance, action)

@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if is_migration_running() or sender.__name__ == 'Log':
        return
    log_change(instance, "Deleted")


@receiver(post_save, sender=UserNotification)
def create_or_update_message_recipient(sender, instance, created, **kwargs):
    MessageRecipient.objects.update_or_create(
        notification=instance,
        recipient=instance.user,
        defaults={}
    )