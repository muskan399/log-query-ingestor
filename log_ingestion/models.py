from django.db import models


class LogEntry(models.Model):
    level = models.CharField(max_length=50)
    message = models.TextField()
    resourceId = models.CharField(max_length=50)
    timestamp = models.DateTimeField()
    traceId = models.CharField(max_length=50, primary_key=True)
    spanId = models.CharField(max_length=50)
    commit = models.CharField(max_length=50)
    parentResourceId = models.CharField(max_length=50, null=True, blank=True)
    projectId = models.CharField(max_length=50)

    class Meta:
        db_table = 'log_data'
