import base64
from celery import shared_task
import os
from account.models import UserDocuments
from django.contrib.auth import get_user_model

User = get_user_model()

@shared_task(bind=True)
def process_file_upload(self, user_id, entity_type, description, file_name, file_path, file_data):
    from django.core.files.base import ContentFile
    from django.contrib.auth import get_user_model

    User = get_user_model()

    # Create folder if missing
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write file to disk
    with open(file_path, 'wb+') as f:
        f.write(ContentFile(base64.b64decode(file_data)).read())

    # Create DB record
    file_extension = os.path.splitext(file_path)[1]
    user = User.objects.get(id=user_id)
    document = UserDocuments.objects.create(
        user=user,
        path=file_path,
        kind=entity_type,
        description=description,
        file_type=file_extension
    )

    return {
        'document_id': document.id,
        'file_location': file_path,
        'file_type': file_extension
    }
