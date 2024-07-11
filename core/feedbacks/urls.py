from django.urls import path
from django.urls.resolvers import URLPattern

from .apis import CheckSimilarity, FeedbackCreateApi, FeedbackListApi

app_name = "feedbacks"

urlpatterns: list[URLPattern] = [
    path("", FeedbackListApi.as_view(), name="feedback-list"),
    path("create/", FeedbackCreateApi.as_view(), name="feedback-create"),
    path("check_similarity/", CheckSimilarity.as_view(), name="feedback-check_similarity"),
]
