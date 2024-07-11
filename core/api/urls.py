from django.urls import include, path
from django.urls.resolvers import URLResolver

urlpatterns: list[URLResolver] = [
    path("auth/", include(("core.authentication.urls", "authentication"), namespace="authentication")),
    path("feedbacks/", include(("core.feedbacks.urls", "feedbacks"), namespace="feedbacks")),
]
