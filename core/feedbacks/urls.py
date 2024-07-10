from django.urls import path
from django.urls.resolvers import URLPattern

from .apis import FeedbackCreate

app_name = "feedbacks"

urlpatterns: list[URLPattern] = [
    path("create/", FeedbackCreate.as_view(), name=""),
]
