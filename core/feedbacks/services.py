import os
import tempfile

from django.conf import settings
from rest_framework.exceptions import PermissionDenied, ValidationError

from core.users.models import Member

from .models import Feedback
from .utils import compare_images


def feedback_create(*, current_user: Member, comment: str, e_signature):
    try:
        reference_signature_full_path = os.path.join(settings.MEDIA_ROOT, current_user.e_signature.path)

        # Save the uploaded signature to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_signature:
            temp_signature.write(e_signature.read())
            uploaded_signature_path = temp_signature.name

        similarity = compare_images(image1_path=reference_signature_full_path, image2_path=uploaded_signature_path)

        if similarity <= 80:
            raise PermissionDenied("Signature verification failed. You are not authorized to create feedback.")

        Feedback.objects.create(author=current_user, comment=comment, e_signature=e_signature)

        return "Signature verified successfully. Feedback has been created."

    except PermissionDenied as pd:
        raise pd

    except ValueError as ve:
        raise ValidationError(f"Validation error: {ve}")

    except Exception as e:
        print(e)
        raise ValidationError(f"Unexpected error: {e}")


def check_similarity(*, image_1, image_2):
    # Save the uploaded images to a temporary files
    with (
        tempfile.NamedTemporaryFile(delete=False) as temp_file_1,
        tempfile.NamedTemporaryFile(delete=False) as temp_file_2,
    ):
        # Write the content of image_1 to temp_file_1
        temp_file_1.write(image_1.read())
        image1_path = temp_file_1.name

        # Write the content of image_2 to temp_file_2
        temp_file_2.write(image_2.read())
        image2_path = temp_file_2.name

    return compare_images(image1_path, image2_path)
