from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import BaseModel
from core.users.models import Member


class Feedback(BaseModel):
    author = models.ForeignKey(Member, on_delete=models.CASCADE)
    comment = models.TextField(
        "Your Comment",
        help_text=_("Type your feedback here..."),
    )
    signature = models.ImageField(
        "Your Signature",
        upload_to="feedbacks/signature/",
        help_text=_("Upload the author signature."),
    )

    def __str__(self) -> str:
        return self.author.full_name

    def save(self, *args, **kwargs):
        self.signature.name = "signature.png"

        super().save(*args, **kwargs)
