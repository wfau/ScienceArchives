from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission

from .models import SQLGenerationTask
from .tasks import generate_sql_celery_task
from .helpers import has_perm_proprietary


class IsProprietaryUser(BasePermission):
    """
    Custom DRF permission class wrapping has_perm_proprietary.
    The message dict is serialised as-is into the 403 JSON response body,
    giving the frontend a structured, actionable payload on every denied request.
    """
    message = {
        "error": "You don't have permissions to use this.",
        "code": "permission_denied",
        "detail": (
            "Access to the SQL generation feature requires the proprietary "
            "permission flag. Contact your administrator if you believe this "
            "is a mistake."
        ),
    }

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and has_perm_proprietary(request.user)
        )


class SubmitSQLJobView(APIView):
    """
    GET  - Lightweight permission probe.
            The frontend calls this on mount to decide whether to render
            the form at all.  Returns 200 {"access": true} or 403.

    POST - Validates input, saves a task checkpoint to the DB, and
           dispatches a Celery worker to handle SQL generation.
    """
    permission_classes = [IsProprietaryUser]

    # ------------------------------------------------------------------ #
    # GET – permission probe (called by the Vue component on mount)        #
    # ------------------------------------------------------------------ #
    def get(self, request, *args, **kwargs):
        return Response({"access": True}, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------ #
    # POST – submit job                                                    #
    # ------------------------------------------------------------------ #
    def post(self, request, *args, **kwargs):
        prompt       = request.data.get('description', '').strip()
        tables       = request.data.get('tables', [])
        data_release = request.data.get('data_release', '').strip()

        if not prompt:
            return Response(
                {"error": "Prompt description is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Store state checkpoint
        task = SQLGenerationTask.objects.create(
            prompt=prompt,
            data_release=data_release,
            tables=tables,
            status=SQLGenerationTask.Status.PENDING,
        )

        # 2. Dispatch to Celery broker
        generate_sql_celery_task.delay(str(task.id))

        return Response(
            {"task_id": str(task.id), "status": task.status},
            status=status.HTTP_202_ACCEPTED,
        )


class PollSQLJobStatusView(APIView):
    """
    Fast DB-polling endpoint for Celery task status.
    Deliberately reads from the DB rather than the Celery broker
    to avoid leaking internal queue details to the client.
    """
    permission_classes = [IsProprietaryUser]

    def get(self, request, task_id, *args, **kwargs):
        try:
            task = SQLGenerationTask.objects.get(id=task_id)
        except SQLGenerationTask.DoesNotExist:
            return Response(
                {"error": "Generation task could not be tracked."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response({
            "task_id":  str(task.id),
            "status":   task.status,
            "sql":      task.generated_sql,
            "error":    task.error_message,
        }, status=status.HTTP_200_OK)
