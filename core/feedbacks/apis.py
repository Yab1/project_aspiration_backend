from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework import status as http_status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from core.common.utils import inline_serializer
from core.users.models import Member

from .models import Feedback
from .services import check_similarity, feedback_create


class CheckSimilarity(APIView):
    class InputSerializer(serializers.Serializer):
        image_1 = Base64ImageField()
        image_2 = Base64ImageField()

    def post(self, request) -> Response:
        input_serializer = self.InputSerializer(data=request.data)

        input_serializer.is_valid(raise_exception=True)

        try:
            similarity = check_similarity(**input_serializer.validated_data)

            response_data = {"data": {"similarity": f"{similarity:.2f}"}}
            return Response(data=response_data, status=http_status.HTTP_200_OK)
        except ValueError as e:
            raise ValidationError(e)

        except Exception as e:
            raise ValidationError(e)


class FeedbackListApi(APIView):
    class OutputSerializer(serializers.Serializer):
        author = inline_serializer(
            fields={"full_name": serializers.CharField()},
        )
        comment = serializers.CharField()
        signature = serializers.URLField()

    def get(self, request) -> Response:
        feedbacks = Feedback.objects.all()

        output_serializer = self.OutputSerializer(feedbacks, many=True)

        response_data = {"data": output_serializer.data}

        return Response(data=response_data, status=http_status.HTTP_200_OK)


class FeedbackCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        comment = serializers.CharField()
        signature = Base64ImageField()

    serializer_class = InputSerializer

    def post(self, request) -> Response:
        current_user = Member.objects.all()[0]
        input_serializer = self.InputSerializer(data=request.data)

        input_serializer.is_valid(raise_exception=True)

        try:
            message = feedback_create(current_user=current_user, **input_serializer.validated_data)

            response_data = {"data": {"message": message}}

            return Response(data=response_data, status=http_status.HTTP_200_OK)

        except ValidationError as ve:
            return Response({"error": str(ve)}, status=http_status.HTTP_400_BAD_REQUEST)

        except PermissionDenied as pd:
            return Response({"error": str(pd)}, status=http_status.HTTP_403_FORBIDDEN)

        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred."}, status=http_status.HTTP_500_INTERNAL_SERVER_ERROR
            )
