from core.users.models import Member

from .models import Feedback


def feedback_create(*, current_user: Member, comment: str, signature):
    Feedback.objects.create(author=current_user, comment=comment, signature=signature)
