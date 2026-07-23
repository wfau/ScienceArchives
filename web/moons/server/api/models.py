import uuid
from django.db import models

class SQLGenerationTask(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        SUCCESS = 'SUCCESS', 'Completed successfully'
        FAILED = 'FAILED', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    # Input parameters
    prompt = models.TextField()
    data_release = models.CharField(max_length=255, blank=True, null=True) # Maps to active Schema key
    tables = models.JSONField(default=list)  # Explicitly selected tables (optional)

    # Outputs
    generated_sql = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
