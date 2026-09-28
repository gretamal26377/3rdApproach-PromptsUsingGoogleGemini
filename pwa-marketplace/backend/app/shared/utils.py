import os
# from exceptions import ConfigurationError
from .models import EntityStatuses
from temporalio.client import Client

class ConfigurationError(RuntimeError):
    """Raised when required reference data is missing or configuration is invalid"""

TEMPORAL_HOST = os.environ.get('TEMPORAL_HOST', "localhost:7233")

def get_active_status():
    status = EntityStatuses.query.filter_by(status_code='active').first()
    if not status:
        raise ConfigurationError("Active Status not found")
    return status

# Temporal Client connection helper
async def get_temporal_client():
    return await Client.connect(TEMPORAL_HOST)
