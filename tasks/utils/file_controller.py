from django.core.files.uploadedfile import InMemoryUploadedFile
import os
from django.conf import settings

def set_to_media_folder(document: InMemoryUploadedFile) -> None:
    """Set a document to the media folder."""
    file_path = os.path.join(settings.MEDIA_ROOT, document.name)
    with open(f'media/{document.name}', 'wb+') as destination:
        for chunk in document.chunks():
            destination.write(chunk)

    return file_path

def delete_from_media_folder(document_path: str) -> None:
    """Delete a document from the media folder."""
    os.remove(document_path)