import os
import uuid

from django.conf import settings
from django.db import models

def results_path():
    return os.path.join(settings.LOCAL_FILE_DIR, "results")

class ExecuteSQL(models.Model):

    StatusType = models.TextChoices("StatusType", "CREATED RUNNING COMPLETED")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    query = models.TextField(blank=True, null=True)
    timeout = models.PositiveSmallIntegerField(null=True, blank=True)
    format = models.CharField(max_length=127, null=True, blank=True)
    status = models.CharField(max_length=127, choices=StatusType.choices, default=StatusType.CREATED)
    created = models.DateTimeField(auto_now_add=True)
    started = models.DateTimeField(null=True, blank=True)
    completed = models.DateTimeField(null=True, blank=True)
    results_file = models.CharField(max_length=1023, blank=True, null=True)
    results_error = models.TextField(blank=True, null=True)

    @property
    def current_status(self):
        if self.status == ExecuteSQL.StatusType.COMPLETED:
            if self.results_error:
                return 'Error'
            else:
                return 'Success'
        elif self.status == ExecuteSQL.StatusType.CREATED:
            return 'Queued'
        return self.get_status_display()

class AnonymousQuery(models.Model):
    sqlquery = models.ForeignKey(ExecuteSQL, on_delete=models.CASCADE)
    slug = models.UUIDField(unique=True, default=uuid.uuid4)