from django.db.models.signals import post_save
from account.models import User, UserDocuments
from django.dispatch import receiver
from common.cloud_vision import detect_text_in_image
from common.logger import AppLogger


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
