from django.db.models.signals import post_save
from account.models import UserDocuments
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
            instance.save()
    
	    # if instance.kind == 'passport':
        #     print(instance.path)
        #         check_passport = detect_text_in_image(instance.path)
