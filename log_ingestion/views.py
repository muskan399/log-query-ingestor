from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import logging

from .models import LogEntry
import json

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def ingest_log(request):
    try:
        log_data = json.loads(request.body.decode('utf-8'))
        # Retrieve the value of "parentResourceId"
        log_data["parentResourceId"] = log_data.get("metadata", {}).get("parentResourceId", None)
        log_data.pop("metadata")
        LogEntry.objects.create(**log_data)
        return JsonResponse({"status": "success", "message": "Log ingested successfully"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})



