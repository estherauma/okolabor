import base64
from celery import shared_task
import os
from account.models import UserDocuments, UserNotification
from django.contrib.auth import get_user_model
from common.cloud_vision import detect_text_in_image
from common.logger import AppLogger
from django.utils.translation import gettext as _

User = get_user_model()

@shared_task(bind=True)
def process_file_upload(self, user_id, entity_type, description, file_name, file_path, file_data, document_id):
    from django.core.files.base import ContentFile
    from django.contrib.auth import get_user_model
    from account.models import UserDocuments  # Adjust import as needed

    User = get_user_model()

    # Create folder if missing
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write file to disk
    with open(file_path, 'wb+') as f:
        f.write(ContentFile(base64.b64decode(file_data)).read())

    # Retrieve the document to update it
    document = UserDocuments.objects.get(id=document_id)
    
    # Update document record after file processing
    document.path = file_path
    document.file_type = os.path.splitext(file_path)[1]
    document.save()
    logger = AppLogger(log_file='logs/file_processing.log')
    
    # passport verification for with cloud vision 
    # passport verification for with cloud vision 
    if entity_type == 'passport':
        logger.info(f'Running cloud vision for : {document.path}')
        cloud_response = detect_text_in_image(document.path)
        document.cloud_vision_response = cloud_response

        user_details = extract_current_details(user_id)
        logger.info(f'User details: {user_details}')
        details_match = check_details_match(user_details, cloud_response)
        document.cloud_vision_match = details_match
        document.save()
        
        if details_match:
            message = _('passportVerifiedNotificationBody')
        else:
            message = _('passportNotVerifiedNotificationBody')

        UserNotification.objects.create(
            user=document.user,
            title=_('passportVerifiedNotificationTitle'),
            message=message
        )

    return {
        'document_id': document.id,
        'file_location': file_path,
        'file_type': document.file_type
    }


def extract_current_details(user_id):
    user = User.objects.get(id=user_id)
    user_details = []
    if ' ' in user.first_name:
        user_details.extend(user.first_name.split())
    else: 
        user_details.append(user.first_name)
    if ' ' in user.last_name:
        user_details.extend(user.last_name.split())
    else: 
        user_details.append(user.last_name)
        
    return user_details


def check_details_match(user_details, cloud_vision_response):
    logger = AppLogger(log_file='logs/file_processing.log')
    user_details_upper = [detail.upper() for detail in user_details]
    cloud_vision_response_upper = [
        response.upper() for response in cloud_vision_response]
    return all(
        detail in cloud_vision_response_upper for detail in user_details_upper)

def check_passport_match(instance, **kwargs):
    logger = AppLogger(log_file='logs/django_signal.log')
    logger.info(f'Running cloud vision for : {instance}')
    check_passport = detect_text_in_image(instance.path)
    instance.cloud_vision_response = check_passport

    user_details = extract_current_details(instance.user_id)
    details_match = check_details_match(
        user_details, instance.cloud_vision_response)

    instance.cloud_vision_match = details_match

    # Send notification if details match
    # When the details do not match, the notification would have been sent during initial upload
    if details_match:
        # Create passport verifed notification
        # Your passsword has been verified
        message = _('passportVerifiedNotificationBody')
        UserNotification.objects.create(
            user=instance.user,
            title=_('passportVerifiedNotificationTitle'), message=message)

    instance.save()
