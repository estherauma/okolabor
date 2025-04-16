from django.db.models.signals import post_save,post_delete
from django.dispatch import Signal, receiver
from account.models import User, UserDocuments, UserNotification
from common.cloud_vision import detect_text_in_image
from common.logger import AppLogger
from django.contrib.contenttypes.models import ContentType
from account.models import Log
from django.contrib.auth import get_user_model
from account.middleware import get_current_user
import sys



@receiver(post_save, sender=UserDocuments)
def upload_document(sender, instance, created, **kwargs):
    if created:
        if instance.kind == 'passport':
            logger = AppLogger(log_file='logs/django_signal.log')
            logger.info(f'Running cloud vision for : {instance}')
            check_passport = detect_text_in_image(instance.path)
            instance.cloud_vision_response = check_passport

            user_details = extract_current_details(instance.user_id)
            logger.info(f'User details: {user_details}')
            details_match = check_details_match(
                user_details, instance.cloud_vision_response)
            instance.cloud_vision_match = details_match
            # ToDo: Update notifications
            if details_match:
                # Your passsword has been verified
                message = '¡Su pasaporte ha sido verificado!'
            else:
                message = (
                    'No se ha podido verificar su pasaporte.'
                    'Asegúrese de que sus datos coincidan'
                    'lo que esta en su pasaporte.'
                )
            UserNotification.objects.create(
                user=instance.user,
                title='Verificación de pasaporte', message=message)
            instance.save()


def extract_current_details(user_id):
    user = User.objects.get(id=user_id)
    user_details = []
    user_details.append(user.first_name)
    user_details.append(user.last_name)
    return user_details


def check_details_match(user_details, cloud_vision_response):
    user_details_upper = [detail.upper() for detail in user_details]
    cloud_vision_response_upper = [
        response.upper() for response in cloud_vision_response]
    return all(
        detail in cloud_vision_response_upper for detail in user_details_upper)


check_passport_match_signal = Signal(providing_args=["user", "request"])


@receiver(check_passport_match_signal)
# instance is passport doc instance
def check_passport_match(sender, instance, **kwargs):
    logger = AppLogger(log_file='logs/django_signal.log')
    logger.info(f'Running cloud vision for : {instance}')
    check_passport = detect_text_in_image(instance.path)
    instance.cloud_vision_response = check_passport

    user_details = extract_current_details(instance.user_id)
    # logger.info(f'User details: {user_details}')
    details_match = check_details_match(
        user_details, instance.cloud_vision_response)

    instance.cloud_vision_match = details_match

    # Send notification if details match
    # When the details do not match, the notification would have been sent during initial upload
    if details_match:
        # Create passport verifed notification
        # Your passsword has been verified
        message = '¡Su pasaporte ha sido verificado!'
        UserNotification.objects.create(
            user=instance.user,
            title='Verificación de pasaporte', message=message)

    instance.save()




User = get_user_model()

# def is_migration_running():
#     return 'makemigrations' in sys.argv or 'migrate' in sys.argv
def is_migration_running():
    return any(cmd in sys.argv for cmd in ['makemigrations', 'migrate', 'test', 'collectstatic', 'flush', 'loaddata'])


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

def log_change(instance, action):
    content_type = ContentType.objects.get_for_model(instance)
    user = get_current_user()

    if not user or not user.is_authenticated:
        if hasattr(instance, 'user'):
            user = instance.user
        elif hasattr(instance, 'created_by'):
            user = instance.created_by
        elif hasattr(instance, 'updated_by'):
            user = instance.updated_by

    if user is None:
        user = User.objects.filter(is_superuser=True).first()
    
    if not user:
        print(f"Warning: No valid user found for instance {instance}. Log entry will not be created.")
        return  

    object_id = str(instance.pk)

    post_save.disconnect(log_create_update, sender=Log)
    post_delete.disconnect(log_delete, sender=Log)

    try:
        Log.objects.create(
            user=user,
            content_type=content_type,
            object_id=object_id,
            action=action
        )
    finally:
        post_save.connect(log_create_update, sender=Log)
        post_delete.connect(log_delete, sender=Log)

